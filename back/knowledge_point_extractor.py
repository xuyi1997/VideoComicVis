import utils
import networkx as nx
from collections import defaultdict



class KnowledgePointExtractor:

    def __init__(self, triples = [], doc = "", split_doc = {}, concept_features_dict = {}):
        self.triples = triples
        self.doc = doc
        self.split_doc = split_doc
        biG = nx.Graph()
        for edge in self.triples:  
            biG.add_edge(edge[0], edge[2], relationship = edge[1])
        self.biGraph = biG

        diG = nx.DiGraph()
        for edge in self.triples:  
            diG.add_edge(edge[0], edge[2], relationship = edge[1])
        self.diGraph = diG
        self.concept_features_dict = concept_features_dict

    def is_path_satisfy(self, path, center_node = ""):
        if len(path) > 6:
            return False
        if len(path) != len(set(path)):
            return False
        # center_node_ts = self.concept_features_dict[center_node]['timestamps']
        # for cp in path:
        #     if cp == center_node: continue
        #     ts_list = self.concept_features_dict[cp]['timestamps']
        #     min_diff_ts = min([abs(float(ts0) - float(ts1)) for ts0 in ts_list.values() for ts1 in center_node_ts.values()])
        #     if min_diff_ts > 30: return False
        return True


    def co_occur(self, node_list = []):
        return True

    def prioritize_paths(self, paths, center_node = ""):
        path_dict = {i: value for i, value in enumerate(paths)}
        pattern_dict = {}
        pattern_path_dict = {}
        for path_index, path in path_dict.items():
            extracted_patterns = [(path[i], path[i+1], path[i+2]) for i in range(0, len(path) - 2, 3)]
            for pt in extracted_patterns:
                if pt not in pattern_dict.values():
                    p_k = len(pattern_dict.values())
                    pattern_dict[p_k] = pt
                else:
                    p_k = list(pattern_dict.values()).index(pt)
                if p_k in pattern_path_dict.keys():
                    pattern_path_dict[p_k].append(path_index)
                else:
                    pattern_path_dict[p_k] = [path_index]

        print("=============={}==============".format(center_node))
        print(pattern_dict)
        print(pattern_path_dict)
        return paths
            
            

    def filter_paths(self, paths, center_node = ""):
        ret = []
        for path in paths:
            if len(path) <= 2: continue
            if path.index(center_node) > 2: 
                crop_path = path[path.index(center_node)-2:]
                ret.append(crop_path)
                continue
            ret.append(path)
        return ret

    def get_out_nodes(self, node):
        successors = list(self.diGraph.successors(node))
        if len(successors) <= 1:
            return successors
        ret = []
        for sn in successors:
            sn_suc = list(self.diGraph.successors(sn))
            if len(sn_suc) <= len(successors):
                ret.append(sn)

        return ret#list(self.diGraph.successors(node))

    def get_in_nodes(self, node):
        cur_suc_degree = len(list(self.diGraph.successors(node)))
        predecessors = list(self.diGraph.predecessors(node))
        if len(predecessors) <= 1:
            return predecessors
        ret = []
        for pn in predecessors:
            pn_suc = list(self.diGraph.successors(pn))
            if len(pn_suc) >= cur_suc_degree:
                ret.append(pn)

        return ret#list(self.diGraph.predecessors(node))

    def recursive_search(self, candidate_path = [], center_node = ""):
        graph = self.diGraph
        new_candidates = []
        is_finish = True
        for c_path in candidate_path:
            if len(c_path) == 1:
                node = c_path[0]
                in_nodes = []
                out_nodes = self.get_out_nodes(node) 
                if len(out_nodes) == 0:
                    in_nodes = self.get_in_nodes(node) 
                comb = utils.get_combination(in_nodes, c_path, out_nodes)
                if len(comb) > 1 or len(comb[0]) > len(c_path): 
                    is_finish = False
                for p in comb:
                    if self.is_path_satisfy(p, center_node):
                        new_candidates.append(p)
            elif len(c_path) > 1:
                left_node = c_path[0]
                right_node = c_path[-1]
                in_nodes = []
                out_nodes = self.get_out_nodes(right_node)
                if len(out_nodes) == 0:
                    in_nodes = self.get_in_nodes(left_node) 
                    if len(in_nodes) == 0:
                        new_candidates.append(c_path)
                        continue

                comb = utils.get_combination(in_nodes, c_path, out_nodes)
                can_comb = False
                for p in comb:
                    if self.is_path_satisfy(p, center_node):
                        new_candidates.append(p)
                        can_comb = True
                        is_finish = False
                if not can_comb:
                    new_candidates.append(c_path)
        if is_finish:
            return new_candidates
        return self.recursive_search(new_candidates, center_node)

    def recursive_search_bi(self, graph: nx.Graph, candidate_path = [], center_node = ""):
        new_candidates = []
        is_finish = True
        for c_path in candidate_path:
            if len(c_path) == 1:
                node = c_path[0]
                neighbors = nx.neighbors(graph, node)
                for n in neighbors:
                    if self.co_occur([n] + [center_node]) and n not in c_path:
                        is_finish = False
                        new_candidates.append([center_node, n])
            elif len(c_path) > 1:
                right_node = c_path[-1]
                next_nodes = [ne for ne in nx.neighbors(graph, right_node) if ne not in c_path ]
                if len(next_nodes) == 0: 
                    if self.is_path_satisfy(c_path, center_node):
                        new_candidates.append(c_path)
                        continue
                if len(c_path) > 5:
                    continue
                comb = map_utils.get_combination([], c_path, next_nodes)
                can_comb = False
                for p in comb:
                    if self.is_path_satisfy(p, center_node):
                        new_candidates.append(p)
                        can_comb = True
                        is_finish = False
                if not can_comb:
                    new_candidates.append(c_path)

        if is_finish:
            return new_candidates
        return self.recursive_search_bi(graph, new_candidates, center_node)
    

    def get_triple_path(self, path):
        ret = []
        for i, c in enumerate(path):
            if i + 1 < len(path):
                rel = self.diGraph.get_edge_data(path[i], path[i+1])
                h = path[i]
                t = path[i+1]
                ret.append([h, rel['relationship'], t])
        return ret

    def rank_net_nodes(self, center_concept, nodes):
        imp_score_dict = {n:self.concept_features_dict[n]['importance_score']['graph'] for n in nodes}
        sl = sorted(imp_score_dict, key=imp_score_dict.get, reverse=True)
        return sl


    def get_network_triples(self, center_concept, other_nodes, is_hierarchy_type):
        ret = []
        if not is_hierarchy_type:
            for n in other_nodes:
                t = utils.find_triple(center_concept, n, self.diGraph)
                if t: ret.append(t) 
        else:
            pre_nodes = [center_concept]
            for h_nodes in other_nodes:
                for n in h_nodes:
                    for pn in pre_nodes:
                        t = utils.find_triple(n, pn, self.diGraph)
                        if t: 
                            ret.append(t) 
                    for k in h_nodes:
                        t = utils.find_triple(n, k, self.diGraph)
                        if t: 
                            ret.append(t) 
                pre_nodes = h_nodes
        return ret




    def get_network_from_cluster(self, center_concept, nodes, is_last = False):
        neighbor_nodes = [n for n in nodes if n in self.biGraph.neighbors(center_concept)]
        pre_nodes = [n for n in nodes if n in self.diGraph.predecessors(center_concept)]
        suc_nodes = [n for n in nodes if n in self.diGraph.successors(center_concept)]
        if len(neighbor_nodes) >= 4:
            #1-n type
            neighbor_nodes = self.rank_net_nodes(center_concept, neighbor_nodes)
            return '1-n', self.get_network_triples(center_concept, neighbor_nodes[0:5], is_hierarchy_type = False)
        elif len(neighbor_nodes) == 3:
            if len(pre_nodes) >= 2:
                #1-n type
                return '1-n',self.get_network_triples(center_concept, neighbor_nodes, is_hierarchy_type = False)
            else:
                #hierarchy type
                ssn = self.get_successors_layer(suc_nodes, nodes)
                return 'hierarchy', self.get_network_triples(center_concept, [neighbor_nodes, ssn], is_hierarchy_type = True)
        elif len(neighbor_nodes) == 2:
            if len(pre_nodes) == 0:
                #hierarchy type
                ssn = self.get_successors_layer(suc_nodes, nodes)
                return 'hierarchy', self.get_network_triples(center_concept, [neighbor_nodes, ssn], is_hierarchy_type = True)
        
        if is_last:
            return '', []
        else:
            return self.get_network_from_cluster(center_concept, utils.get_nodes_from_triples(self.triples), is_last=True)


    def get_successors_layer(self, suc_nodes, nodes):
        ssn = []
        for sn in suc_nodes:
            suc_sn = [n for n in nodes if n in self.diGraph.successors(sn)]
            if len(suc_sn) == 0:
                suc_sn = list(self.diGraph.successors(sn))
            if suc_sn:
                suc_sn = self.rank_net_nodes(sn, suc_sn)
                ssn.append(suc_sn[0])
        return ssn

    def get_network_kp(self, target_concepts = []):
        G = self.diGraph
        comm_list = nx.community.louvain_communities(G,seed=123)
        community_dict = {}
        for index in range(len(comm_list)):
            community = comm_list[index]
            for node in community:
                community_dict[node] = index
        ret = {}
        for center_node in target_concepts:
            comm_nodes = [n for n in community_dict if community_dict[n] == community_dict[center_node]]
            comm_nodes = [n for n in comm_nodes if nx.shortest_path_length(self.biGraph, source=center_node, target=n) <= 2]
            net_type, net_triples = self.get_network_from_cluster(center_node, comm_nodes)
            ret[center_node] = {'type': net_type, 'triples': net_triples}
            print(center_node, ret[center_node])
        return ret

    def get_linear_kp(self, target_concepts = []):
        ret = {}
        for center_node in target_concepts:
            print("---------------------------", center_node, "--------------------------")
            paths = self.recursive_search([[center_node]], center_node)
            paths = self.filter_paths(paths, center_node)
            # paths = self.prioritize_paths(paths, center_node)
            path_dict = {}
            for i, path in enumerate(paths[:5]):
                path_dict[str(i)] = {'triple_paths': self.get_triple_path(path), 'node_paths': path}
            ret[center_node] = path_dict
            # paths = self.recursive_search_bi(self.biGraph, [[center_node]], center_node)
        return ret
    def calculate_similarity(self, list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        similarity = len(intersection) / len(union) if union else 1.0
        
        return similarity
    def optimize_topic_distribution(self, linear_path_dict):
        original_dict = {}
        for k, v in linear_path_dict.items():
            tconcept = k
            for i, p in v.items():
                sp = "<->".join(p['node_paths'])
                if sp not in original_dict.keys():
                    original_dict[sp] = []
                original_dict[sp].append(tconcept)

        pool = [k for k in original_dict.keys()]
        pool = sorted(pool)
        copy_pool = pool.copy()
        list_pool = [k.split("<->") for k in pool]
        sim_dict = {}
        index = 0
        for i in range(len(pool)):
            sim_dict[index] = []
            sim_dict[index].append(pool[index])
            cnt = 0
            for j in range(index+1, len(pool)):
                if ''.join(list_pool[index][:2]) == ''.join(list_pool[j][:2]):
                    sim_dict[index].append(pool[j])
                    cnt += 1
                else:
                    break
            index += cnt + 1
            if index >= len(pool):
                break
        filter_dict = {}
        selected_concept_dict = {}
        for k, v in sim_dict.items():
            p = max(v, key=lambda t: len(list(t.split("<->"))))
            mt = min(original_dict[p], key=lambda t: p.index(t))
            filter_dict[p] = mt
            if mt not in selected_concept_dict:
                selected_concept_dict[mt] = []
            selected_concept_dict[mt].append(p)
        
        all_topics = set(linear_path_dict.keys())
        unused_topics = all_topics - set(selected_concept_dict.keys())
        for ut in unused_topics:
            possible_paths = [k for k, v in original_dict.items() if ut in v]
            unchosen = [p for p in possible_paths if p not in filter_dict.keys()]
            if unchosen:
                selected_concept_dict[ut] = [unchosen[0]]
            elif possible_paths:
                selected_concept_dict[ut] = [possible_paths[0]]
            else:
                selected_concept_dict[ut] = {}

        ret = {}
        for k, v in selected_concept_dict.items():
            ret[k] = {}
            for i, p in enumerate(v):
                ret[k][i] = self.get_triple_path(p.split("<->"))
        return ret

            
        # for k, v in original_dict.items():

        # sorted_items = sorted(original_dict.items(), key=lambda x: x[0], reverse=False)
        # print(sorted_items)

    
            


    def get_kp(self, target_concepts = []):
        linear_path_dict = self.get_linear_kp(target_concepts)
        filter_linear_path_dict = self.optimize_topic_distribution(linear_path_dict)
        network_kp_dict = self.get_network_kp(target_concepts)
        ret = {}
        for center_node in target_concepts:
            ret[center_node] = {
                'linear': filter_linear_path_dict[center_node],
                'network': network_kp_dict[center_node]
            }
        return ret

