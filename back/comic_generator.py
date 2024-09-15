import os
import utils
import networkx as nx
import graphviz
import matplotlib.pyplot as plt
import subprocess
import sys
import json

Global_temp = 1

text_svg_temp = """
    <text x="{x}" y="{y}" font-family="Virgil, Segoe UI Emoji" font-size="{font_size}px" fill="#000000" text-anchor="start" style="white-space: pre; font-weight: 200;" direction="ltr">{text}</text>
    """

line_svg_template = """
<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" stroke-width="2"/>
"""
    
with open(os.path.abspath("../front/public/assets/template/dialogue-1-1-1-1.svg"), 'r', encoding='utf-8') as file:
    dg_1_1_1_1_svg_content = file.read()

with open(os.path.abspath("../front/public/assets/template/dialogue-2-1-1.svg"), 'r', encoding='utf-8') as file:
    dg_2_1_1_svg_content = file.read()

with open(os.path.abspath("../front/public/assets/template/dialogue-up2-down2.svg"), 'r', encoding='utf-8') as file:
    dg_up2_down2_content = file.read()

class ComicGenerator:
    def __init__(self, task_name = "", knowledge_point_dict = {}):
        self.task_name = task_name
        self.knowledge_point_dict = knowledge_point_dict
    
    def split_svg_text_3(self, x=0, y=0, font=20, text = "", offset_bidirection = False):
        # return y offset and svg content
        words = list(text.split(' '))
        if len(words) <= 2:
            return self.split_svg_text(x, y, font, text, offset_bidirection)
        h1 = words[:int(len(words)/3)]
        h2 = words[int(len(words)/3):int(len(words)*2/3)]
        h3 = words[int(len(words)*2/3):]
        if offset_bidirection:
            y1 = y - 10
            y2 = y + 15
            y3 = y + 35
            y_offset = 50
        else:
            y1 = y
            y2 = y + 25
            y3 = y + 50
            y_offset = 50
        h1_svg = text_svg_temp.format(x=x, y=y1, font_size=font, text=' '.join(h1))
        h2_svg = text_svg_temp.format(x=x, y=y2, font_size=font, text=' '.join(h2))
        h3_svg = text_svg_temp.format(x=x, y=y3, font_size=font, text=' '.join(h3))
        return y_offset, h1_svg + h2_svg + h3_svg
    

    def split_svg_text(self, x=0, y=0, font=20, text = "", offset_bidirection = False):
        # return y offset and svg content
        words = list(text.split(' '))
        if len(words) == 1:
            return 0, text_svg_temp.format(x=x-10, y=y, font_size=font, text=text)
        h1 = words[:int(len(words)/2)]
        h2 = words[int(len(words)/2):]
        if offset_bidirection:
            y1 = y - 10
            y2 = y + 15
            y_offset = 15
        else:
            y1 = y
            y2 = y + 25
            y_offset = 25
        h1_svg = text_svg_temp.format(x=x, y=y1, font_size=font, text=' '.join(h1))
        h2_svg = text_svg_temp.format(x=x, y=y2, font_size=font, text=' '.join(h2))
        return y_offset, h1_svg + h2_svg

    def generate_svg_element(self, start_x, start_y, text_list, w_limit = 200):
        ret = ""
        y = start_y
        x = start_x
        for font_size, text in text_list:
            if len(text) <= w_limit/12:
                ret += text_svg_temp.format(x=x, y=y, font_size=font_size, text=text)
                y += 25
            elif len(text) <= w_limit/6:
                y_offset, s = self.split_svg_text(x, y, font_size,text, len(text_list) == 1)
                y += y_offset
                y += 25
                ret += s
            else:
                y_offset, s = self.split_svg_text_3(x, y, font_size,text, len(text_list) == 1)
                y += y_offset
                y += 25
                ret += s
        return ret

    def gen_initial_question(self, concept, path_triples):
        if path_triples and path_triples[0] and concept == path_triples[0][0]:
            return "What is ”{}“?".format(concept)
        else:
            return "”{}“...?".format(concept)
    def generate_dialogue_svg(self, path_triples, target_concept, save_path, pattern='up2-down2'):
        default_font = 18
        highlight_font = 21
        if pattern == 'up2-down2':
            default_font = 16
            highlight_font = 20
        text_list = []
        if len(path_triples) == 2:
            pattern = "dg_2_1_1"
            A, ab, B = path_triples[0]
            B, bc, C = path_triples[1]
            text_list.append([[highlight_font, target_concept]])
            text_list.append([[default_font, "What is {}?".format(target_concept)]])
            text_list.append([[default_font, " ".join(path_triples[0]) + ' ,'], [20, "which {}...".format(bc)]])
            text_list.append([[default_font, C + " !"]])

        elif len(path_triples) == 3:
            A, ab, B = path_triples[0]
            B, bc, C = path_triples[1]
            C, cd, D = path_triples[2]
            text_list.append([[default_font, self.gen_initial_question(target_concept, path_triples)]])
            text_list.append([[default_font, ' '.join(path_triples[0]) + ' .'], [20, "Then..."]])
            text_list.append([[default_font, " ".join(path_triples[1])], [20, "which " + cd + "..."]])
            text_list.append([[highlight_font, D + " !"]])
        elif len(path_triples) == 4:
            h1, r1, t1 = path_triples[0]
            h2, r2, t2 = path_triples[1]
            h3, r3, t3 = path_triples[2]
            h4, r4, t4 = path_triples[3]
            text_list.append([[default_font, self.gen_initial_question(target_concept, path_triples)]])
            text_list.append([
                [20, ' '.join(path_triples[0]) + " ."], 
                [20, "Then what happens?"]
                ])
            text_list.append([[default_font, " ".join(path_triples[1])], [20, ",which {}...".format(r3)]])
            text_list.append([[highlight_font, "{}, {} {}!".format(t3, r4, t4)]])

        elif len(path_triples) == 5:
            if pattern == "dg_2_1_1":
                pattern = 'up2-down2'
            h1, r1, t1 = path_triples[0]
            text_list.append([[default_font, self.gen_initial_question(target_concept, path_triples)]])
            h2, r2, t2 = path_triples[1]
            h3, r3, t3 = path_triples[2]
            h4, r4, t4 = path_triples[3]
            h5, r5, t5 = path_triples[4]

            text_list.append([
                [default_font, ' '.join(path_triples[0])], 
                [default_font, 'which {} {}'.format(r2, t2)],
                [default_font, "Then what happens?"]
                ])

            text_list.append([[default_font, ' '.join(path_triples[2])], [default_font, "{} {}, then...".format(r4, t4)]])
            text_list.append([[default_font, "{} {} {}!".format(h5, r5, t5)]])

        svg_content = ""
        if pattern == 'up2-down2' and len(text_list) == 4:
            svg_content = dg_up2_down2_content
            placeholder = ["__STRIP_1__", "__STRIP_2__", "__STRIP_3__", "__STRIP_4__"]
            for i, text in enumerate(text_list):
                if i == 0 or i == 3:
                    w_limit = 150
                else:
                    w_limit = 500
                strip = self.generate_svg_element(-20, 15, text, w_limit)
                svg_content = svg_content.replace(placeholder[i], strip)
            utils.save_cache(svg_content, save_path, file_type='txt')
            return save_path
        if pattern == "dg_2_1_1" and len(text_list) == 4:
            svg_content = dg_2_1_1_svg_content
            strip_1_left = self.generate_svg_element(-5, 10, text_list[0], 200)
            strip_1_right = self.generate_svg_element(-30, -10, text_list[1], 200)
            strip_2 = self.generate_svg_element(20, 10, text_list[2], 200)
            strip_3 = self.generate_svg_element(-20, -10, text_list[3], 200)
            svg_content = svg_content.replace("__STRIP_1_LEFT__", strip_1_left)
            svg_content = svg_content.replace("__STRIP_1_RIGHT__", strip_1_right)
            svg_content = svg_content.replace("__STRIP_2__", strip_2)
            svg_content = svg_content.replace("__STRIP_3__", strip_3)
            utils.save_cache(svg_content, save_path, file_type='txt')
            return save_path
        if pattern == "dg_1_1_1_1" and len(text_list) == 4:
            svg_content = dg_1_1_1_1_svg_content
            strip_1 = self.generate_svg_element(0, 20, text_list[0], 200)
            strip_2 = self.generate_svg_element(30, 20, text_list[1], 200)
            strip_3 = self.generate_svg_element(-20, -20, text_list[2], 200)
            strip_4 = self.generate_svg_element(10, 10, text_list[3], 150)
            svg_content = svg_content.replace("__STRIP_1__", strip_1)
            svg_content = svg_content.replace("__STRIP_2__", strip_2)
            svg_content = svg_content.replace("__STRIP_3__", strip_3)
            svg_content = svg_content.replace("__STRIP_4__", strip_4)
            utils.save_cache(svg_content, save_path, file_type='txt')
            return save_path
            #[h1, t1;] [what t1 do;] [t1, t2, t3] (111)
    def gen_diagram_svg_vis(self, center_concept, triples, type):
        temp_triples = []
        for tr in triples:
            temp_tr = []
            for text in tr:
                if len(text) > 16: 
                    text = text[::-1].replace(" ", " \n", 1)[::-1]
                temp_tr.append(text)
            temp_triples.append(temp_tr)
        triples = temp_triples

        G = utils.get_network_di_graph(triples)
        save_file_path = "cache/{}/comic/diagram/{}.svg".format(self.task_name, center_concept)
        directory = os.path.dirname(save_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        save_path = os.path.abspath(save_file_path)
        A = nx.nx_agraph.to_agraph(G)
        for u, v, data in G.edges(data=True):
            if 'relationship' in data:
                A.get_edge(u, v).attr['label'] = data['relationship']
                A.get_edge(u, v).attr['fontsize'] = "25"
        args = []
        if type == '1-n':
            layout_algorithm = '-Ktwopi'
            args = ['-Nfontsize=30', '-Nmargin=0.4,0.3', '-Earrowhead=none', '-Estyle=bold','-Nshape=rect', '-Gsep=0.8', '-Goverlap=voronoi']
        else:
            layout_algorithm = "-Kdot"
            args = ['-Nfontsize=30', '-Nshape="rect"', '-Nmargin=0.9,0.3', '-Earrowhead=none', '-Earrowsize=3.0', '-Estyle=bold', '-Granksep=1.5', '-Gnodesep=2']
        # A.layout(layout_algorithm, args=args)
        fh = open("testdot.dot", 'w', encoding='utf-8')
        print(A.to_string(),file=fh)
        fh.close()
        ret = subprocess.run(['dot', layout_algorithm, '-Tsvg'] + args + ["testdot.dot"], capture_output=True)
        graphviz_svg_content = ret.stdout.decode('utf-8')
        tmpInputSVGPath = os.path.abspath("tempInput.svg".format(center_concept))
        fh = open(tmpInputSVGPath, 'w', encoding='utf-8')
        print(graphviz_svg_content,file=fh)
        fh.close()
        subprocess.run(['/usr/local/bin/node', '../ComicJsServer/main.js', tmpInputSVGPath, save_path], 
                                capture_output=True, 
                                text=True, 
                                check=True)
            


    def run(self):
        ret = {}
        global_comic_template_shuffle = 0
        for center_concept, kp in self.knowledge_point_dict.items():
            # diagrams
            net_kp = kp['network']
            line_kp = kp['linear']
            diagram_comic_save_path = ""
            if len(net_kp['type']) > 0 and len(net_kp['triples']) > 0:
                diagram_comic_save_path = self.gen_diagram_svg_vis(center_concept, net_kp['triples'], net_kp['type'])

            # INPUT: template, data(concept, knowledge points) 
            template = ['up2-down2', 'dg_2_1_1', 'dg_1_1_1_1']
            dialogue_comic_save_paths = []
            for i, p in line_kp.items():
                save_path = "cache/{}/comic/dialogue/{}_{}.svg".format(self.task_name, center_concept, i)
                self.generate_dialogue_svg(p, center_concept, save_path, template[int(global_comic_template_shuffle)%3])
                global_comic_template_shuffle += 1
                dialogue_comic_save_paths.append(save_path)
            
            dialogue_comic_save_paths_dict = {i:v for i, v in enumerate(dialogue_comic_save_paths)}
            ret[center_concept] = {
                'diagram': diagram_comic_save_path,
                'dialogues': dialogue_comic_save_paths_dict
            }
        return ret
