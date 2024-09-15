
from py2neo import Graph, Node, Relationship
import neo4j

class Neo4jVisTool:

    
    def __init__(self):
        print("Initialize Neo4j tools...")
        self.graph = None

    def connect2neo4j(self):
        self.graph = Graph("bolt://localhost:7687", user='neo4j', password='12345678')

    def load_triples(self, file_path):
        # Open the Cypher file and read its contents
        self.graph.delete_all()
        with open(file_path, "r") as file:
            document = file.read()
            document = document.lower()
            triples = eval(document)
    
        for tr in triples:
            h,r,t = tr
            score = 5
            # Check if the head node exists
            merged_head_node = self.graph.nodes.match("concept", name=h).first()
            if not merged_head_node:
                merged_head_node = Node("concept", name=h, score=score)
                self.graph.create(merged_head_node)
            
            # Check if the tail node exists
            merged_tail_node = self.graph.nodes.match("concept", name=t).first()
            if not merged_tail_node:
                merged_tail_node = Node("concept", name=t, score=score)
                self.graph.create(merged_tail_node)
            
            # Create the relationship
            relationship = Relationship(merged_head_node, r, merged_tail_node)
            self.graph.create(relationship)


if __name__ == "__main__":
    path = '/Users/xuyi/Project/vis/ComicVisSystem/back/cache/concept_map_after_postprocess_PsychologyB.txt'
    neo = Neo4jVisTool()
    neo.connect2neo4j()
    neo.load_triples(path)
