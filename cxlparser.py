from __future__ import annotations 

import xml.etree
import xml.etree.ElementTree
import defusedxml.ElementTree as ET
import defusedxml.minidom as minidom
import xml
import networkx as nx
import matplotlib.pyplot as plt
class InvalidCmapFileException(Exception):
    def __init__(self, message, file_path):
        super().__init__(message)
        self.file_path = file_path


class cxl:
    def __init__(self, path: str) -> None:
        self._tree = ET.parse(path)
        self.concepts_by_id: dict = None
        self.concepts_by_label: dict = None
        self.connections_by_id: dict = None
        self.connections_by_from_id: dict = None
        self.connections_by_to_id: dict = None
        self.graph = nx.DiGraph()
        self.phrases_by_id: dict = None
        self.phrases_by_label: dict = None
        self._file_path = ""

    
    def import_data(self, path: str) -> None:
        self._file_path = path
        self._tree = ET.parse(path)


    def _fix_connections(self):
        l = []
        for i in self.connections_by_id:
            item = self.connections_by_id[i]
            if item["to-id"] in self.phrases_by_id:
                self.connections_by_id[i]["to-id"] = self.connections_by_from_id[item["to-id"]]["to-id"]
            elif item["from-id"] in self.phrases_by_id:
                l.append(item["from-id"])
        for i in l:
            if not i in self.connections_by_from_id.keys():
                print(i in self.connections_by_from_id.keys(), i, self.connections_by_from_id.keys())
            item = self.connections_by_from_id[i]
            del self.connections_by_id[item["id"]]
            del self.connections_by_from_id[item["from-id"]]
            
                
            # print("THIS ONE -> "+str(item))
    @staticmethod
    def show_map(g: cxl) -> None:
        nx.draw_networkx(g.graph, with_labels=True, labels={i:g.concepts_by_id[i]["label"] for i in g.concepts_by_id})
        plt.show()
        
    def parse_map(self):
        concept_list = []
        for i in self._tree.getroot()[1][0].iter():
            if i.attrib == {}:
                continue
            concept_list.append(i.attrib)
        self.concepts_by_id = {x["id"]:x for x in concept_list}
        clm = [x["label"] for x in concept_list]
        if len(clm) == len(set(clm)):
            self.concepts_by_label = {x["label"]:x for x in concept_list}
        else:
            self.concepts_by_label = None

        connection_list = []
        for i in self._tree.getroot()[1][2].iter():
            if i.attrib == {}:
                continue
            connection_list.append(i.attrib)
        self.connections_by_id = {x["id"]:x for x in connection_list}
        self.connections_by_from_id = {x["from-id"]:x for x in connection_list}
        self.connections_by_to_id = {x["to-id"]:x for x in connection_list}

        '''for i in self.concepts_by_id:
            self.graph.add_node(i)'''
        phrase_list = []
        for i in self._tree.getroot()[1][1].iter():
            if i.attrib == {}:
                continue
            phrase_list.append(i.attrib)
        self.phrases_by_id = {x["id"]:x for x in phrase_list}
        clm = [x["label"] for x in phrase_list]
        if len(clm) == len(set(clm)):
            self.phrases_by_label = {x["label"]:x for x in phrase_list}
        self._fix_connections()
        for i in self.connections_by_id.values():
            if i["from-id"] in self.phrases_by_id:
                continue
            #print(i)
            if i["from-id"] in self.concepts_by_id and i["to-id"] in self.concepts_by_id:
                #print("Direct!")
                self.graph.add_edge(i["from-id"], i["to-id"])
            elif i["from-id"] in self.concepts_by_id: 
                #print("from")
                if i["to-id"] in self.phrases_by_id:
                    self.graph.add_edge(i["from-id"], self.connections_by_from_id[i["to-id"]]['id'])
                else:
                    raise InvalidCmapFileException("", self._file_path)
            elif i["to-id"] in self.concepts_by_id: 
                #print("to")
                if i["from-id"] in self.phrases_by_id:
                    self.graph.add_edge(i["to-id"], self.connections_by_from_id[i["from-id"]]['id'])
                else:
                    raise InvalidCmapFileException("", self._file_path)
            else:
                print("Floating >:(")
        """print(self.graph)
        for i in self.concepts_by_id:
            self.graph.nodes[i] = self.concepts_by_id[i]
        for i in self.graph.nodes.items():
            print(i)
        print(len(concept_list))"""
        


# Comp: # of nodes
# Org: Density
