
import networkx as nx
import utils
import os

def is_valid_hrt(hrt):
    if len(hrt) != 3:
        return False
    h, r, t = hrt
    hl = h.split(" ")
    tl = t.split(" ")
    if len(hl) > 3 or len(tl) > 3:
        return False

    return True

def link_related_concepts(concept_map = []):
    concept_list = utils.get_nodes_from_triples(concept_map)
    add_triples = []
    for c1 in concept_list:
        for c2 in concept_list:
            if c1 != c2 and c1[0] == c2[0]:
                head = min(c1, c2)
                tail = max(c1, c2)
                if head not in tail:
                    continue
                l1 = c1.split(' ')
                l2 = c2.split(' ')
                if l1[0].lower() == l2[0].lower():
                    is_existed = False
                    for triple in concept_map:
                        if (head == triple[0] and tail == triple[2]) or (head == triple[2] and tail == triple[0]):
                            is_existed = True
                            break
                    if not is_existed: add_triples.append([head, " ", tail])
    return add_triples


def merge_relations(concept_map):
    cm = []
    for triple in concept_map:
        if triple[0] == triple[2]:
            continue
        is_append = True
        for index in range(len(cm)):
            tr = cm[index]
            if triple[0] == tr[0] and triple[2] == tr[2]:
                is_append = False
                break
        if is_append: cm.append(triple)
    return cm



def split_link(concept_map = []):
    concept_list = map_utils.get_nodes_from_triples(concept_map)
    cm = concept_map.copy()
    del_list = []
    add_list = []
    for head, rel, tail in concept_map:
        if len(rel.split(' ')) == 1:
            continue
        cp = [concept for concept in concept_list if concept.lower() in rel.lower()]
        for c in cp:
            rel_0 = " "
            rel_1 = " "
            start_index = rel.lower().index(c.lower())
            if start_index - 1 > 0 and rel[start_index - 1] == ' ':
                rel_0 = rel[0:start_index - 1]
            end_index = rel.lower().index(c.lower()) + len(c)
            if end_index + 1 < len(rel) and rel[end_index] == ' ':
                rel_1 = rel[end_index + 1:]
            del_list.append([head, rel, tail])
            add_list.append([head, rel_0, c])
            add_list.append([c, rel_1, tail])
    print("delete: ", del_list)
    print("add: ", add_list)
    for dl in del_list:
        cm.remove(dl)
    for al in add_list:
        cm.append(al)
    return cm


def remove_isolated_triples(llm_triple_list):
    cm = []
    G = nx.Graph()
    for edge in llm_triple_list:
        G.add_edge(edge[0], edge[2], relationship = edge[1])
    ccs = list(nx.connected_components(G))
    largest_clusters_count = len(max(ccs, key=len))
    isolate_nodes = []
    for cc in ccs:
        if len(cc) != largest_clusters_count:
            for item in cc:
                isolate_nodes.append(item)

    isolate_nodes = list(set(isolate_nodes))
    
    
    for index in range(len(llm_triple_list)):
        tr = llm_triple_list[index]
        if tr[0] not in isolate_nodes and tr[1] not in isolate_nodes:
            cm.append(tr)

    return cm
def check_llm_merge(llm_triple_list, merge_pairs_file = ""):
    match_list = []
    with open(merge_pairs_file, "r") as file:
        document = file.read()
        dl = eval(document)
        for pair in dl:
            append_flag = False
            for index in range(len(match_list)):
                ml = match_list[index]
                for e in ml:
                    if pair[0].lower() == e.lower() or pair[1].lower() == e.lower():
                        match_list[index].append(pair[0])
                        match_list[index].append(pair[1])
                        append_flag = True
                        break
                match_list[index] = list(set(match_list[index]))
                if append_flag: break
            if not append_flag: match_list.append(pair)
    match_dict = {}
    for ml in match_list:
        shortest_string = min(ml, key=len)
        match_dict[shortest_string] = [s.lower() for s in ml]

    ret = []
    for triple in llm_triple_list:
        h, r, t = triple
        for k, v in match_dict.items():
            if h.lower() in v:
                h = k
            if t.lower() in v:
                t = k
        ret.append([h, r, t])
    return ret


class ConceptMapPostProcessor:

    def __init__(self, llm_context_path = "", llm_merge_pairs_file = ""):
        self.ori_triples = utils.parse_llm_context(llm_context_path)
        self.llm_merge_pairs_file = llm_merge_pairs_file

    def process(self):
        triples = check_llm_merge(self.ori_triples, self.llm_merge_pairs_file)
        concept_list = utils.get_nodes_from_triples(triples)
        # deplural
        plural_dict = self.get_plurals(concept_list)
        for index in range(len(triples)):
            h, r, t = triples[index]
            if h in plural_dict.keys(): h = plural_dict[h]
            if t in plural_dict.keys(): t = plural_dict[t]
            triples[index] = [h.lower(), r.lower(), t.lower()]

        # multi relation between two concepts
        triples = merge_relations(triples)
        triples = remove_isolated_triples(triples)
        return triples



    def get_plurals(self, words = []):
        plural_dict = {}
        post_words = []
        for w in words:
            added = False
            for pw in post_words:
                if utils.is_plural(pw, w):
                    added = True
                    plural_dict[pw] = w
            if not added: post_words.append(w)
        return plural_dict



if __name__ == "__main__":
    task_name = "PsychologyB"
    llm_context_file_name = "/Users/xuyi/Project/vis/ComicVisSystem/back/cache/llm_context_PsychologyB.txt"
    llm_merge_pairs_file_name = "/Users/xuyi/Project/vis/ComicVisSystem/back/cache/llm_merge_pairs_PsychologyB.txt"
    postprocessor = ConceptMapPostProcessor(llm_context_file_name, llm_merge_pairs_file_name)

    save_post_file_name = "/Users/xuyi/Project/vis/ComicVisSystem/back/cache/concept_map_after_postprocess_{}.txt".format(task_name)
    
    save_post_graph_name = "/Users/xuyi/Project/vis/ComicVisSystem/back/cache/concept_map_after_postprocess_{}.cypherl".format(task_name)
    
    triples = postprocessor.process()
    utils.save_cache(triples, save_post_file_name, file_type='list')
    
    path = os.path.join('save', save_post_graph_name)
    utils.write_cypher_file(triples, path)