from langchain.text_splitter import CharacterTextSplitter
from openai import OpenAI
import numpy as np
import json
import os


def llm_assisstant(content = ""):
    return {"role": "assistant", "content": content}

def llm_get_response(model_name = "gpt-4o", temperature = 0, max_tokens = 2048, messages = [], response_format = "text"):
    response = client.chat.completions.create(
        model=model_name,
        temperature = temperature,
        max_tokens = max_tokens,
        messages=messages,
        response_format={"type": response_format}
    )
    if len(response.choices) > 0:
        resp = response.choices[0].message.content
        return resp
    return ""



def longest_common_substring(str1, str2):
    len1, len2 = len(str1), len(str2)

    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    max_length = 0

    end_pos = 0

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_length:
                    max_length = dp[i][j]
                    end_pos = i
            else:
                dp[i][j] = 0

    longest_substring = str1[end_pos - max_length: end_pos]
    return longest_substring
def get_matched_pair(ta, tb, la, lb):
    if ta in lb.values() and tb in lb.values():
        return []
    if isinstance(ta, list) and isinstance(tb, list) and len(ta) == 3 and len(tb) == 3:
        h1, r1, t1 = ta
        h2, r2, t2 = tb
        if h1 == h2 and r1 == r2 and t1 != t2:
            if (len(t1) < len(t2) and t1.lower() in t2.lower()) or (len(t2) <= len(t1) and t2.lower() in t1.lower()):
                return [t1, t2]
            cs = longest_common_substring(t1.lower(), t2.lower())
            if len(cs) > 0.6 * len(t1) or len(cs) > 0.6 * len(t2):
                return [t1, t2]
        if t1 == t2 and r1 == r2 and h1 != h2:
            if (len(h1) < len(h2) and h1.lower() in h2.lower()) or (len(h2) <= len(h1) and h2.lower() in h1.lower()):
                return [h1, h2]
            cs = longest_common_substring(h1.lower(), h2.lower())
            if len(cs) > 0.6 * len(h1) or len(cs) > 0.6 * len(h2):
                return [h1, h2]
    return []

def compare_merging(l1, l2):
    merging_list = []
    
    if isinstance(l1, dict) and isinstance(l2, dict):
        if len(l1) == len(l2):
            for index in range(len(l1)):
                ta = list(l1.values())[index]
                tb = list(l2.values())[index]
                pair = get_matched_pair(ta, tb, l1, l2)
                if len(pair) == 2:
                    merging_list.append(pair)
        else:
            for ta in list(l1.values()):
                for tb in list(l2.values()):
                    pair = get_matched_pair(ta, tb, l1, l2)
                    if len(pair) == 2:
                        merging_list.append(pair)

    return merging_list

class ConceptMapLLMGenerator:
    def __init__(self, chunk_path = ""):
        self.task_name = os.path.splitext(chunk_file.split('_')[-1])[0]
        with open("/Users/xuyi/Project/vis/ComicVisSystem/back/prompt_flow.json", "r") as file:
            prompt_json = file.read()
            self.prompt_data = json.loads(prompt_json)

        with open(chunk_path, "r") as file:
            chunk_doc = file.read()
            self.chunk_dict = json.loads(chunk_doc)

        self.save_file_context = "/Users/xuyi/Project/vis/ComicVisSystem/back/cache/llm_context_{}.txt".format(self.task_name)
        self.save_file_merge_pairs = "/Users/xuyi/Project/vis/ComicVisSystem/back/cache/llm_merge_pairs_{}.txt".format(self.task_name)
        self.save_file_triples_before_merge = "/Users/xuyi/Project/vis/ComicVisSystem/back/cache/llm_triples_before_merge_{}.txt".format(self.task_name)

    def run(self, iteration = 0):
        triples_before_merge_list = []
        merging_list = []
        global_context = []
        
        chunk_list = list(self.chunk_dict.values())[1:]
        if iteration > 0:
            #load global context
            with open(self.save_file_context, "r") as file:
                fc = file.read()
                fc_list = eval(fc)
                if isinstance(fc_list,list):
                    global_context = fc_list
            with open(self.save_file_merge_pairs, "r") as file:
                fc = file.read()
                fc_list = eval(fc)
                if isinstance(fc_list,list):
                    merging_list = fc_list
                    
            with open(self.save_file_triples_before_merge, "r") as file:
                fc = file.read()
                fc_list = eval(fc)
                if isinstance(fc_list,list):
                    triples_before_merge_list = fc_list
        else:
            system_prompt = {"role": "system", "content": self.prompt_data["system_prompt"]}
            global_context.append(system_prompt)
            
            # provide whole document as background
            # user_prompt = {"role": "user", "content": prompt_dict["document_prompt"]}
            # global_context.append(user_prompt)
            # resp = llm_get_response(messages=global_context)
            # global_context.append(llm_assisstant(resp))

            # user_prompt = {"role": "user", "content": document}
            # global_context.append(user_prompt)
            # resp = llm_get_response(messages=global_context)
            # global_context.append(llm_assisstant(resp))

        
            
        for index in range(iteration, len(chunk_list)):
            # if index == 0:
            #     user_prompt = {"role": "user", "content": prompt_dict["document_finish_prompt"] + prompt_dict["extract_concept_prompt"]}
            # else:
            user_prompt = {"role": "user", "content": self.prompt_data["extract_concept_prompt"]}
            global_context.append(user_prompt)
            user_prompt = {"role": "user", "content": chunk_list[index]}
            global_context.append(user_prompt)
            resp = llm_get_response(messages=global_context)
            global_context.append(llm_assisstant(resp))

            user_prompt = {"role": "user", "content": self.prompt_data["extract_triple_prompt"]}
            global_context.append(user_prompt)
            resp_before_check = llm_get_response(messages=global_context)
            local_context = global_context.copy()
            local_context.append(llm_assisstant(resp_before_check))

            user_prompt = {"role": "user", "content": self.prompt_data["check_proposition_triple_prompt"]}
            local_context.append(user_prompt)
            resp_check_proposition = llm_get_response(messages=local_context)
            local_context.append(llm_assisstant(resp_check_proposition))
            
            user_prompt = {"role": "user", "content": self.prompt_data["check_missing_triple_prompt"]}
            local_context.append(user_prompt)
            resp_check_missing = llm_get_response(messages=local_context, response_format="json_object")
            local_context.append(llm_assisstant(resp_check_missing))
            
            # user_prompt = {"role": "user", "content": prompt_dict["check_concept_prompt"]}
            # local_context.append(user_prompt)
            # resp_check_concept = llm_get_response(messages=local_context)
            # local_context.append(llm_assisstant(resp_check_concept))

            
            # user_prompt = {"role": "user", "content": prompt_dict["output_json_prompt"]}
            resp_before_merge = resp_check_missing#llm_get_response(messages=local_context + [user_prompt], response_format="json_object")
            triples_before_merge = json.loads(resp_before_merge)
            triples_before_merge_list += list(triples_before_merge.values())
            
            user_prompt = {"role": "user", "content": self.prompt_data["check_merging_within_chunk_prompt"]}
            local_context.append(user_prompt)
            resp_check_merging_within_chunk = llm_get_response(messages=local_context)
            local_context.append(llm_assisstant(resp_check_merging_within_chunk))

            user_prompt = {"role": "user", "content": self.prompt_data["check_merging_across_chunk_prompt"]}
            local_context.append(user_prompt)
            resp_check_merging_across_chunk = llm_get_response(messages=local_context, response_format="json_object")
            local_context.append(llm_assisstant(resp_check_merging_across_chunk))

            
            # user_prompt = {"role": "user", "content": prompt_dict["output_json_prompt"]}
            # local_context.append(user_prompt)
            resp_final = resp_check_merging_across_chunk#llm_get_response(messages=local_context, response_format="json_object")
            global_context.append(llm_assisstant(resp_final))
            local_context.clear()
            triples_after_merge = json.loads(resp_final)

            merging_list += compare_merging(triples_before_merge, triples_after_merge)

            print("----------------------chunk result----------------------")
            print(triples_before_merge)
            print(triples_after_merge)
            print(merging_list)
        
            # save middle results
            fh = open(self.save_file_context, 'w', encoding='utf-8')
            print(global_context, file=fh)
            fh.close()

            fh = open(self.save_file_triples_before_merge, 'w', encoding='utf-8')
            print(triples_before_merge_list, file=fh)
            fh.close()

            fh = open(self.save_file_merge_pairs, 'w', encoding='utf-8')
            print(merging_list, file=fh)
            fh.close()

if __name__ == "__main__":
    chunk_file = "/Users/xuyi/Project/vis/Data/DataGallery/Psychology_Freud_B/chunk_Psychology_Freud_B.json"
    generator = ConceptMapLLMGenerator(chunk_path=chunk_file)
    generator.run(20)
    # triples = parse_llm_context("C:\Repo\ConceptVisDemo\save\llm_context.txt")

    # match_dict = {}
    # with open("C:\Repo\ConceptVisDemo\save\llm_merging_pairs.txt", "r") as file:
    #     document = file.read()
    #     merge_list = eval(document)
    #     for pair in merge_list:
    #         if pair[0] not in match_dict.keys():
    #             match_dict[pair[0].lower()] = []
    #         match_dict[pair[0].lower()].append(pair[1].lower())
    #     for p in match_dict.keys():
    #         match_dict[p] = list(set(match_dict[p]))

    # apply_match = []
    # for tr in triples:
    #     h, r, t = tr
    #     h = h.lower()
    #     t = t.lower()
    #     if h.lower() in match_dict.keys():
    #         h = match_dict[h][0]
    #     if t.lower() in match_dict.keys():
    #         t = match_dict[t][0]
    #     apply_match.append([h, r, t])

    # with open("C:\Repo\ConceptVisDemo\save\llm_result_map_after_merge.txt", "r") as file:
    #     document = file.read()
    #     map_after_merge = eval(document)
    #     islist = isinstance(map_after_merge,list)
    #     remove_list = []
    #     if isinstance(map_before_merge,list):
    #         for triple in map_before_merge:
    #             if isinstance(triple,list):
    #                 if triple[0] not in concepts or triple[1] not in concepts:
    #                     remove_list.append(triple)
    #             else:
    #                 print(triple)
    #     print(remove_list)
        