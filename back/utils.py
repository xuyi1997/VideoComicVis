import json
import os
import networkx as nx
import shutil
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
import freetype

STOP_WORDS = list(ENGLISH_STOP_WORDS) + ['question', 'course', 'work', 'lecture', 'topic', 'introduction', 'overview', 'instructor', 'chapter', 'syllabus', 'section', 'unit', 'lecture', 'class', 'session', 'seminar', 'workshop', 'schedule', 'topic', 'resource', 'material', 'institution','knowledge', 'objective', 'observation']


# import cairosvg

# def svg_to_png(svg_file, png_file):
#     cairosvg.svg2png(url=svg_file, write_to=png_file)


def parse_llm_context(path):
    document = ""
    triples = []
    with open(path, "r") as file:
        document = file.read()
        data = eval(document)
        islist = isinstance(data,list)
        for item in data:
            if item['role'] == 'assistant'and '{' in item['content'][0:3]:
                data = json.loads(item['content'])
                triples += list(data.values())
    return triples

def get_text_dimensions(text, font_size, font_path):
    face = freetype.Face(font_path)
    face.set_char_size(font_size * 64)
    
    width, height, baseline = 0, 0, 0
    previous = 0
    for char in text:
        face.load_char(char)
        bitmap = face.glyph.bitmap
        height = max(height, bitmap.rows + max(0, -(face.glyph.bitmap_top - bitmap.rows)))
        baseline = max(baseline, max(0, -(face.glyph.bitmap_top - bitmap.rows)))
        kerning = face.get_kerning(previous, char)
        width += (face.glyph.advance.x >> 6) + (kerning.x >> 6)
        previous = char

    return width, height, baseline

def get_combination(in_nodes, c_path, out_nodes):
    ret = []
    if len(in_nodes) == 0 and len(out_nodes) == 0:
        ret = [c_path]
    elif len(in_nodes) == 0:
        ret = [c_path + [out_node] for out_node in out_nodes]
    elif len(out_nodes) == 0:
        ret = [[in_node] + c_path for in_node in in_nodes]
    else:
        ret = [[in_node] + c_path + [out_node] for in_node in in_nodes for out_node in out_nodes]
    return ret

def getNumofCommonSubstr(str1, str2):
    lstr1 = len(str1)
    lstr2 = len(str2)
    record = [[0 for i in range(lstr2+1)] for j in range(lstr1+1)]
    maxNum = 0  
    p = 0  
  
    for i in range(lstr1):
        for j in range(lstr2):
            if str1[i] == str2[j]:
                record[i+1][j+1] = record[i][j] + 1
                if record[i+1][j+1] > maxNum:
                     maxNum = record[i+1][j+1]
                     p = i + 1
    return maxNum
  


def remove_isolated_triples(initial_triples):
    cm = []
    G = nx.Graph()
    for edge in initial_triples:
        G.add_edge(edge[0], edge[2], relationship = edge[1])
    ccs = list(nx.connected_components(G))
    largest_clusters_count = len(max(ccs, key=len))
    isolate_nodes = []
    for cc in ccs:
        if len(cc) != largest_clusters_count:
            for item in cc:
                isolate_nodes.append(item)

    isolate_nodes = list(set(isolate_nodes))
    
    
    for index in range(len(initial_triples)):
        tr = initial_triples[index]
        if tr[0] not in isolate_nodes and tr[1] not in isolate_nodes:
            cm.append(tr)

    return cm



def getTaskFilesList(path: str):
    res_dict = {}
    for _, _, files  in os.walk(path):
        for file in files:
            filepath = "{}/{}".format(path, file) 
            if 'video' in file or '.mp4' in file:
                res_dict['video_file'] = filepath
            elif 'audio' in file or '.wav' in file:
                res_dict['audio_file'] = filepath
            elif 'speech' in file and '.txt' in file:
                res_dict['speech_file'] = filepath
            elif 'timestamp' in file and '.json' in file:
                res_dict['timestamp_file'] = filepath
            elif 'chunk' in file:
                res_dict['chunk_file'] = filepath
            elif 'concept_map' in file and '.txt' in file:
                res_dict['concept_map_file'] = filepath
            elif 'merge_pairs' in file:
                res_dict['merge_pairs_file'] = filepath
    return res_dict

def create_relationship_query(id1, id2, relationship_type):
    query_template = (
        "MATCH (u:__mg_vertex__), (v:__mg_vertex__) "
        "WHERE u.__mg_id__ = {id1} AND v.__mg_id__ = {id2} "
        "CREATE (u)-[:`{relationship_type}`]->(v);"
    )
    query = query_template.format(id1=id1, id2=id2, relationship_type=relationship_type)
    return query

def create_node_query(tid, name):
    query_template = (
        f"CREATE (:__mg_vertex__:`Part` {{__mg_id__: {tid}, `name`: \"{name}\"}});"
    )
    return query_template

def convert_to_cypher(cm):
    cypher_node_statements = []
    cypher_relation_statements = []
    cypher_statements = []
    concept_dict = {}
    nodes = set()
    
    for start_node, relationship, end_node in cm:
        start_node_index  = 0
        end_node_index = 0
        if start_node in concept_dict.keys():
            start_node_index = concept_dict[start_node]
        else:
            start_node_index = len(concept_dict.keys())
            concept_dict[start_node] = start_node_index
            cypher_node_statements.append(create_node_query(str(start_node_index), start_node))
        
        if end_node in concept_dict.keys():
            end_node_index = concept_dict[end_node]
        else:
            end_node_index = len(concept_dict.keys())
            concept_dict[end_node] = end_node_index
            cypher_node_statements.append(create_node_query(str(end_node_index), end_node))
        
        q = create_relationship_query(str(start_node_index), str(end_node_index), relationship)
        cypher_relation_statements.append(q)
    # Create unique nodes
    
    cypher_statements.append(f"CREATE INDEX ON :`Part`(`name`);")
    cypher_statements.append(f"CREATE INDEX ON :`Component`(`name`);")
    cypher_statements.append(f"CREATE INDEX ON :__mg_vertex__(__mg_id__);")
    cypher_statements += cypher_node_statements
    cypher_statements += cypher_relation_statements
    cypher_statements.append(f"DROP INDEX ON :__mg_vertex__(__mg_id__);")
    cypher_statements.append(f"MATCH (u) REMOVE u:__mg_vertex__, u.__mg_id__;")
    cypher = "\n".join(cypher_statements)
    
    return cypher



def find_triple(n1, n2, G:nx.DiGraph):
    edge = G.get_edge_data(n1, n2)
    if edge:
        return (n1, edge['relationship'], n2)
    edge = G.get_edge_data(n2, n1)
    if edge:
        return (n2, edge['relationship'], n1)
    return ()

def write_cypher_file(triples = [], path = ""):
    cypher_script = convert_to_cypher(triples)
    fh = open(path, 'w', encoding='utf-8')
    fh.write(cypher_script)
    fh.close()

def get_nodes_from_triples(triples = []):
    concept_list = []
    for triple in triples:
        h, r, t = triple
        concept_list.append(h)
        concept_list.append(t)
    concept_list = list(set(concept_list))
    return concept_list

def get_network_graph(triples = []):
    G = nx.Graph()
    for edge in triples:  
        G.add_edge(edge[0], edge[2], relationship = edge[1])
    return G

def get_network_di_graph(triples = []):
    G = nx.DiGraph()
    for edge in triples:  
        G.add_edge(edge[0], edge[2], relationship = edge[1])
    return G


def get_combination(in_nodes, c_path, out_nodes):
    ret = []
    if len(in_nodes) == 0 and len(out_nodes) == 0:
        ret = [c_path]
    elif len(in_nodes) == 0:
        ret = [c_path + [out_node] for out_node in out_nodes]
    elif len(out_nodes) == 0:
        ret = [[in_node] + c_path for in_node in in_nodes]
    else:
        ret = [[in_node] + c_path + [out_node] for in_node in in_nodes for out_node in out_nodes]
    return ret


def save_cache(data, file_path, file_type = 'json'):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(file_path, 'w') as file:
        if file_type == 'json':
            json.dump(data, file)
        elif file_type == 'txt':
            file.write(data)
        elif file_type == 'list':
            print(data, file=file)


def is_plural(w1, w2):
    a = w1.lower()
    b = w2.lower()
    f1 = a == b + 's' or a == b + 'es'
    f2 = b == a + 's' or b == a + 'es'
    return f1 or f2


def load_cache(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return None

def delete_cache(cache_dir): 
    if os.path.exists(cache_dir) and os.path.isdir(cache_dir):
        shutil.rmtree(cache_dir)
    
if __name__ == "__main__":
    getTaskFilesList("Transformer")
    # get_concept_timestamps('bert', "/Users/xuyi/Project/vis/ComicVisSystem/front/public/assets/task/Transformer/speech_transformer_wit_timestamps.json")