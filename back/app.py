from flask import Flask, render_template, flash, request, send_from_directory, jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS
import os
import subprocess
import utils
import json
from concept_feature import ConceptFeatureExtractor
from knowledge_point_extractor import KnowledgePointExtractor
from comic_generator import ComicGenerator
import inflect
inflect_engine = inflect.engine()

CACHE_FOLDER = 'cache'

DEFAULT_CONCEPT_NUM = 20
DEFAULT_IMPORTANT_CONCEPT_NUM = 10
DEFAULT_CHALLENGING_CONCEPT_NUM = 10

important_color_hex = "#FF9E4A"
challenge_color_hex = "#AD8BC9"
regular_node_color_hex = "#A2A2A2"
regular_edge_color_hex = "#C2C2C2"

app = Flask(__name__,
            static_folder="../front/dist",
            template_folder="../front/dist")


CORS(app, resources={r"/api/*": {"origins": "*"}})
api = Api(app)
@app.route('/')
def index():
    print("!!!!!!!!!!!!!!!!!index")
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/cache/<path:filename>')
def get_cache_file(filename):
    print("!!!!!!!!!!!!!!!!!get_image", filename)
    return send_from_directory(CACHE_FOLDER, filename)


@app.route('/<path:path>')
def static_proxy(path):
    # Serve static files (JS, CSS, etc.)
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


def filter_triples(triples, initial_speech_doc):
    ret = []
    for tr in triples:
        h, r, t = tr
        if len(h.split(' ')) > 4 or len(t.split(' ')) > 4:
            continue
        if h.lower() in utils.STOP_WORDS or inflect_engine.singular_noun(h.lower()) in utils.STOP_WORDS:
            continue

        if h.lower() in initial_speech_doc.lower():
            index = initial_speech_doc.lower().index(h.lower())
            real_label = initial_speech_doc[index: index+len(h.lower())]
            h = real_label
        if t.lower() in initial_speech_doc.lower():
            index = initial_speech_doc.lower().index(t.lower())
            real_label = initial_speech_doc[index: index+len(t.lower())]
            t = real_label

        ret.append([h, r, t])
    ret = utils.remove_isolated_triples(ret)
    return ret

@app.route('/api/getNodeData', methods=['POST']) 
def getNodeData():
    if 'task_name' in request.form:
        task_name = request.form['task_name']

    cache_file = CACHE_FOLDER + "/{}/concept_nodes.json".format(task_name)
    node_data = utils.load_cache(cache_file)

    return jsonify({
        'node_data': node_data
    }), 200, 



@app.route('/api/getComicPath', methods=['POST']) 
def getComicPath():
    if 'concept_name' in request.form and 'task_name' in request.form:
        concept_name = request.form['concept_name']
        task_name = request.form['task_name']
    else:
        return jsonify({'error': 'No concept name provided'}), 400

    path_dict = {}
    for root, dirs, files in os.walk("cache/{}/comic/diagram".format(task_name)):
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            if concept_name.lower() == file_name.lower():
                svg_file_path = "cache/{}/comic/diagram/{}".format(task_name, file)
                # png_file_path = "cache/{}/comic/diagram/{}.png".format(task_name, file_name)
                # if not os.path.exists(png_file_path):
                #     utils.svg_to_png(svg_file_path, png_file_path)
                path_dict['diagram_comic'] = svg_file_path
                break
    dialogue_file = []
    for root, dirs, files in os.walk("cache/{}/comic/dialogue".format(task_name)):
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            if concept_name.lower() in file_name.lower():
                svg_file_path = "cache/{}/comic/dialogue/{}".format(task_name, file)
                # png_file_path = "cache/{}/comic/dialogue/{}.png".format(task_name, file_name)
                # if not os.path.exists(png_file_path):
                #     utils.svg_to_png(svg_file_path, png_file_path)
                dialogue_file.append(svg_file_path)
    if len(dialogue_file) > 0:
        path_dict['dialogue_comic'] = {str(i):p for i, p in enumerate(dialogue_file)}

    print("----getComicPath", task_name, concept_name, path_dict)

    return jsonify({
        'path_dict': path_dict
    }), 200, 


def get_node_color(is_important, is_challenging):
    if is_important:
        return important_color_hex
    elif is_challenging:
        return challenge_color_hex
    else:
        return regular_node_color_hex


def gen_network_attributes(triples, concept_features, control_params = {}):
    index = 0
    vnodes = []
    edges = []
    challenging_criteria = control_params['challenging_criteria']
    importance_criteria = control_params['importance_criteria']
    important_concept_num = control_params['important_concept_num']
    challenging_concept_num = control_params['challenging_concept_num']

    concept_list = utils.get_nodes_from_triples(triples)
    concept_index_dict = {str(value): str(i) for i, value in enumerate(concept_list)}
    
    imp_dict = {cp:float(concept_features[cp]['importance_score'][importance_criteria]) for cp in concept_list}
    important_highest_score = sorted(imp_dict.values(), reverse=True)[0]
    important_thres = sorted(imp_dict.values(), reverse=True)[important_concept_num-1]

    challenging_rank_dict = {cp:concept_features[cp]['challenging_rank'][challenging_criteria] for cp in concept_list}
    challenging_rank_thres = sorted(challenging_rank_dict.values(), reverse=False)[challenging_concept_num-1]

    both_important_and_challenging = sum(
        1 for cp in concept_list
        if imp_dict[cp] >= important_thres and challenging_rank_dict[cp] <= challenging_rank_thres
    )
    challenging_rank_thres += both_important_and_challenging

    for cp in concept_list:

        imp_score = float(concept_features[cp]['importance_score'][importance_criteria])
        is_important = imp_score >= important_thres
        challenging_rank = concept_features[cp]['challenging_rank'][challenging_criteria]
        is_challenging = challenging_rank >= 0 and challenging_rank <= challenging_rank_thres

        if is_important:
            node_value = 25 * (1 + (imp_score - important_thres) / (important_highest_score - important_thres))
        else:
            node_value = 20

        color = get_node_color(is_important, is_challenging)
        degree = len(list([tr for tr in triples if cp == tr[0] or cp == tr[2]]))
        attr = {'id': concept_index_dict[cp], 'label': cp, 'value': str(node_value), 'color': color, 'is_important': str(is_important), "is_challenging": str(is_challenging), 'features': concept_features[cp], 'degree': degree}
        attr['timestamp'] = concept_features[cp]['timestamps']
        vnodes.append(attr)
    
    for tr in triples:
        h,r,t = tr
        h_index = concept_index_dict[h]
        t_index = concept_index_dict[t]
        edges.append({'from': h_index, 'to': t_index, 'title': r, 'color': regular_edge_color_hex})
    return vnodes, edges

def prepareFeatures(task_name, imp_alg='frequency', cha_alg='unfamiliar'):
    # files = utils.getTaskFilesList("/Users/xuyi/Project/vis/ComicVisSystem/front/public/assets/task/{}".format(task_name))

    files = utils.getTaskFilesList(os.path.abspath("../front/public/assets/task/{}".format(task_name)))

    with open(files['speech_file'],'r', encoding='UTF-8') as file:
        document = file.read()
        initial_speech_doc = document

    with open(files['concept_map_file'], "r") as file:
        document = file.read()
        document = document.lower()
        triples = eval(document)
        triples = filter_triples(triples, initial_speech_doc)

    with open(files['timestamp_file'],'r', encoding='UTF-8') as f:
        ts_dict = json.load(f)

    video_duration = -1
    if ts_dict:
        video_duration = max([v['end'] for k, v in ts_dict.items()])

    with open(files['chunk_file'],'r', encoding='UTF-8') as file:
        document = file.read()
        speech_segment_dict = json.loads(document)
        
    concept_list = utils.get_nodes_from_triples(triples)
    print(concept_list)

    feature_dict_cache_file = CACHE_FOLDER + "/{}/concept_feature_dict.json".format(task_name)
    feature_dict = utils.load_cache(feature_dict_cache_file)

    if not feature_dict:
        feature_extractor = ConceptFeatureExtractor(triples, initial_speech_doc, speech_segment_dict)
        feature_dict = feature_extractor.get_features(concept_list)
        utils.save_cache(feature_dict, feature_dict_cache_file)


    concept_features_dict = {}
    for cp in concept_list:
        features = {
            "timestamps": {}, 
            "importance_score" : feature_dict[cp]['importance_score'], 
            "challenging_rank" : feature_dict[cp]['challenging_rank']
        }
        timestamps = []
        for key, value in ts_dict.items():
            if cp.lower() in value['text'].lower():
                timestamps.append(value['start'])
        if not timestamps:
            d = {}
            for key, value in ts_dict.items():
                d[key] = utils.getNumofCommonSubstr(value['text'].lower(), cp.lower())
            m_key =  max(d, key=lambda x: d[x])
            timestamps.append(ts_dict[m_key]['start'])
        for i, v in enumerate(timestamps):
            features['timestamps'][str(i)] = str(v)
            
        
        
        concept_features_dict[cp] = features

    # neo_con.load_triples(triples, concept_features_dict)
    
    importance_criteria = imp_alg
    challenging_criteria = cha_alg
    print("importance_criteria", importance_criteria)
    print("challenging_criteria", challenging_criteria)

    challenging_rank_dict = {cp:concept_features_dict[cp]['challenging_rank'][challenging_criteria] for cp in concept_list if concept_features_dict[cp]['challenging_rank'][challenging_criteria] >= 0}
    max_challenging_count = len(challenging_rank_dict)
    challenging_count = min(max_challenging_count, DEFAULT_CHALLENGING_CONCEPT_NUM)

    importance_score_dict = {cp:float(concept_features_dict[cp]['importance_score'][importance_criteria]) for cp in concept_list}
    max_important_count = min(len(importance_score_dict), len(concept_list))
    important_count = min(max_challenging_count, DEFAULT_CHALLENGING_CONCEPT_NUM)

            
    control_params = {"important_concept_num": important_count, "importance_criteria": importance_criteria, "challenging_concept_num": challenging_count, "challenging_criteria": challenging_criteria}

    nodes, edges = gen_network_attributes(triples, concept_features_dict, control_params)
    nodes_json = {i: value for i, value in enumerate(nodes)}
    edges_json = {i: value for i, value in enumerate(edges)}


    important_list = {n['label']:n['value'] for n in nodes if n['is_important'] == 'True'}
    sorted_important_list = sorted(important_list, key=important_list.get, reverse=True)
    challenging_list = {n['label']:concept_features_dict[n['label']]['challenging_rank'][challenging_criteria] for n in nodes if n['is_challenging'] == 'True'}
    sorted_challenging_list = sorted(challenging_list, key=challenging_list.get, reverse=False)
    print("Select Important Nodes:", sorted_important_list)
    print("Select Challenging Nodes:", sorted_challenging_list)
    knowledge_point_dict_cache_file = CACHE_FOLDER + "/{}/knowledge_point_dict.json".format(task_name)
    knowledge_point_dict = utils.load_cache(knowledge_point_dict_cache_file)
    if not knowledge_point_dict:
        knowledge_point_extractor = KnowledgePointExtractor(triples, initial_speech_doc, speech_segment_dict, concept_features_dict)
        knowledge_point_dict = knowledge_point_extractor.get_kp(list(set(sorted_important_list + sorted_challenging_list)))
        utils.save_cache(knowledge_point_dict, knowledge_point_dict_cache_file)


    comic_path_dict_cache_file = CACHE_FOLDER + "/{}/comic_path_dict.json".format(task_name)
    comic_path_dict = utils.load_cache(comic_path_dict_cache_file)
    if not comic_path_dict:
        comic_generator = ComicGenerator(task_name, knowledge_point_dict)
        comic_path_dict = comic_generator.run()
        utils.save_cache(comic_path_dict, comic_path_dict_cache_file)

    return nodes_json, edges_json, video_duration, comic_path_dict


@app.route('/api/prepareConcpetMapAndFeatures', methods=['POST']) 
def prepareConcpetMapAndFeatures():
    if 'task_name' in request.form:
        task_name = request.form['task_name']
        imp_alg = request.form['imp_alg']
        cha_alg = request.form['cha_alg']
    else:
        return jsonify({'error': 'No task name provided'}), 400

    if 'graph' in imp_alg.lower():
        importance_criteria = 'graph'
    elif 'tf' in imp_alg.lower():
        importance_criteria = 'tfidf'
    else:
        importance_criteria = 'frequency'

    if 'amb' in cha_alg.lower():
        challenging_criteria = 'ambiguity'
    else:
        challenging_criteria = 'unfamiliar'



    nodes_json, edge_json, video_duration, comic_path_dict = prepareFeatures(task_name, importance_criteria, challenging_criteria)

    ret_data = {
        'network_nodes': nodes_json,
        'network_edges': edge_json,
        'video_duration': video_duration,
        'comic_path_dict': comic_path_dict
    }
    
    utils.save_cache(ret_data, CACHE_FOLDER + "/{}/concept_nodes.json".format(task_name))


    return jsonify(ret_data), 200, 
    

    

@app.route('/api/fetchTasks') 
def get_init_resources():
    res_root_dir = "../front/public/assets/task"
    resource_json = {}
    for _, task_names, _ in os.walk(res_root_dir):
        for task_name in task_names:
            res_dict = {}
            for _, _, files  in os.walk(res_root_dir + "/" + task_name):
                for file in files:
                    if 'video' in file or '.mp4' in file:
                        res_dict['video_file'] = file
                    elif 'audio' in file or '.wav' in file:
                        res_dict['audio_file'] = file
                    elif 'speech' in file or '.mp4' in file:
                        res_dict['speech_file'] = file
                    elif 'chunk' in file:
                        res_dict['chunk_file'] = file
                    elif 'concept_map' in file:
                        res_dict['concept_map_file'] = file
                    elif 'merge_pairs' in file:
                        res_dict['merge_pairs_file'] = file
            resource_json[task_name] = res_dict
    print("fetchTasks: ", resource_json)
    response = {
        'response': resource_json
    }    
    return jsonify(response)

if __name__ == "__main__":
    # utils.delete_cache(CACHE_FOLDER)
    # task_name = 'Industry 4.0'
    # prepareFeatures('Industry 4.0')
    # knowledge_point_dict_cache_file = CACHE_FOLDER + "/{}/knowledge_point_dict.json".format(task_name)
    # knowledge_point_dict = utils.load_cache(knowledge_point_dict_cache_file)
    # comic_generator = ComicGenerator(task_name, knowledge_point_dict)
    # comic_path_dict = comic_generator.run()

    # print(" ")
    app.run()