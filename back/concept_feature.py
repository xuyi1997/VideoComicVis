import networkx as nx
import utils
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import brown
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation


class ConceptFeatureExtractor:

    def __init__(self, triples = [], doc = "", chunk_dict = {}):
        self.triples = triples
        self.doc = doc
        self.chunk_dict = chunk_dict

    def get_features(self, concept_list: list):
        ret = {}
        frequency_importance_score_dict = self.get_frequency_score(concept_list)
        tfidf_importance_score_dict = self.get_tfidf_score(concept_list)
        graph_importance_score_dict = self.get_graph_central_degree_score(concept_list)
        unfamiliar_words = self.get_unfamiliar_words(concept_list)
        print("--------------------------------------unfamiliar_words--------------------------------------")
        print(unfamiliar_words)
        amibiguous_words = self.get_amibiguous_words(concept_list)
        print("--------------------------------------amibiguous_words--------------------------------------")
        print(amibiguous_words)
        
        for cp in concept_list:
            ret[cp] = {'importance_score': {
                    'graph': str(graph_importance_score_dict[cp]),
                    'frequency': str(frequency_importance_score_dict[cp]),
                    'tfidf': str(tfidf_importance_score_dict[cp])
                },'challenging_rank':{
                    'unfamiliar': unfamiliar_words.index(cp) if cp in unfamiliar_words else 999,
                    'ambiguity': amibiguous_words.index(cp) if cp in amibiguous_words else 999
                }}
        return ret





    def get_tfidf_score(self, concept_list: list):
        sw = list(utils.STOP_WORDS)
        vectorizer = TfidfVectorizer(ngram_range=(1,3), stop_words=sw)
        tfidf_matrix = vectorizer.fit_transform(list(self.chunk_dict.values()))
        feature_names = vectorizer.get_feature_names_out()
        feature_names = list(feature_names)

        lda = LatentDirichletAllocation(n_components=1, random_state=0)  # 选择主题数
        lda.fit(tfidf_matrix)

        # 获取主题-词矩阵
        topic_word_matrix = lda.components_

        # 输出每个主题下的重要词汇
        for index, topic in enumerate(topic_word_matrix): 
            concept_tfidf_dict = {}
            l = list(topic.argsort()[0:][::-1])
            for concept in concept_list:
                if concept.lower() in feature_names:
                    ci = feature_names.index(concept.lower())
                    rank = len(l) - l.index(ci)
                    concept_tfidf_dict[concept] = rank
                else:
                    concept_tfidf_dict[concept] = 0
            break
        sorted_keys = sorted(concept_tfidf_dict, key=concept_tfidf_dict.get, reverse=False)
        return concept_tfidf_dict

    def get_frequency_score(self, concept_list: list):
        sw = list(utils.STOP_WORDS)
        vectorizer = TfidfVectorizer(ngram_range=(1,3), stop_words=sw)
        tfidf_matrix = vectorizer.fit_transform([self.doc])
        feature_names = vectorizer.get_feature_names_out()
        feature_names = list(feature_names)
        dense = tfidf_matrix.todense()
        tfidf_dict = {}
        for i, d in enumerate(dense):
            l = d.tolist()[0]
            for j, value in enumerate(l):
                w = feature_names[j].lower()
                tfidf_dict[w] = value
        concept_tfidf_dict = {}
        for concept in concept_list:
            if concept.lower() in tfidf_dict.keys():
                concept_tfidf_dict[concept] = tfidf_dict[concept.lower()]
            else:
                concept_tfidf_dict[concept] = 0
        sorted_keys = sorted(concept_tfidf_dict, key=concept_tfidf_dict.get, reverse=False)
        return concept_tfidf_dict


        

    def get_graph_central_degree_score(self, concept_list: list):
        G = utils.get_network_graph(self.triples)
        diG = utils.get_network_di_graph(self.triples)
        betweenness_centrality = nx.betweenness_centrality(G)
        eigenvector_centrality = nx.eigenvector_centrality(G)
        closeness_centrality = nx.closeness_centrality(G)
        degree_centrality = nx.degree_centrality(G)
        return betweenness_centrality

        
    def get_unfamiliar_words(self, concept_list: list):
        G = utils.get_network_graph(self.triples)
        freq_score_dict = {}
        degree_thres = 2
        number_limit = len(concept_list)/10
        nltk.download('wordnet')
        nltk.download('brown')
        nltk_words = brown.words()
        nltk_word_count = Counter(nltk_words)
        for cp in concept_list:
            words = list(cp.split(' '))
            freq = min(nltk_word_count[w.lower()] for w in words) 
            graph_degree = len(list(G.neighbors(cp)))
            if freq <= 0 and graph_degree > 1 and not cp.isdigit():
                freq_score_dict[cp] = {'freq': freq, 'degree': graph_degree}
        # for i in range(0, 3):
        #     count = sum(1 for value in freq_score_dict.values() if value['degree'] > i)
        #     count_next = sum(1 for value in freq_score_dict.values() if value['degree'] > i+1)
        #     if count_next < number_limit:
        #         degree_thres = i
        #         break
        sl = sorted(freq_score_dict.items(), key=lambda item: (item[1]['freq'], -item[1]['degree']))
        ret = [i[0] for i in sl]
        return ret


        
    def get_amibiguous_words(self, concept_list: list):
        G = utils.get_network_graph(self.triples)
        am_score_dict = {}
        for cp in concept_list:
            words = list(cp.split(' '))
            if len(words) == 1:
                synsets = wn.synsets(cp)
                syn_count = len(synsets)
                graph_degree = len(list(G.neighbors(cp)))
                if syn_count > 2 and graph_degree > 1 and not cp.isdigit():
                    am_score_dict[cp] = {'syn_count': syn_count, 'degree': graph_degree}
        
        sl = sorted(am_score_dict.items(), key=lambda item: (-item[1]['degree'], -item[1]['syn_count']))
        ret = [i[0] for i in sl]
        return ret