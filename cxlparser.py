from __future__ import annotations 

import xml.etree.ElementTree
import defusedxml.ElementTree as ET
import xml
import networkx as nx
import matplotlib.pyplot as plt
import os
from warnings import warn

# Systenmatic lit review

class InvalidCmapFileException(Exception):
    def __init__(self, message, file_path):
        super().__init__(message)
        self.file_path = file_path

class Connection:
    def __init__(self, from_id, to_id, id:str = None, label: str = None):
        self.label = label
        self.id = id
        self.from_id = from_id
        self.to_id = to_id
    
    def __str__(self):
        return f"Label: {self.label} id:{self.id} {self.from_id}->{self.to_id}"


        

class BundlePhrase:
    ### doesn't work w/ phrase-phrase connections ###
    def __init__(self, label: str, id:str, from_list = [], to_list = []):
        self.from_list = from_list
        self.to_list = to_list
        self.label = label
        self.id = id
    
    def add_connection(self, from_id:str = None, to_id: str = None):
        if from_id:
            self.from_list.append(from_id)
        if to_id:
            self.to_list.append(to_id)
    
    def list_connections(self)->list[dict[str:str]]:
        connections = []
        for f in self.from_list:
            for t in self.to_list:
                connections.append(Connection(f, t, label=self.label))
        return connections
    
    def __str__(self):
        s = ""
        for i in self.list_connections():
            s+=f"{i}\n"
        return s


class Cxl:
    def __init__(self, path: str = "", fuzzy:bool = False, nname = "Untitled") -> None:
        self._tree = ET.parse(path)
        self.concepts_by_id: dict = None
        self.concepts_by_label: dict = None
        self.connections: list[Connection] = None
        # self.connections_by_from_id: dict = None
        # self.connections_by_to_id: dict = None
        self.graph = nx.DiGraph(name=nname) if not fuzzy else nx.Graph(name = nname)
        self.phrases_by_id: dict = None
        # self.phrases_by_label: dict = None
        self.fuzzy = fuzzy
        self._file_path = path
        self.name = nname
        self._parsed = False
        if path != "":
            self.import_data(path)
        

    
    def import_data(self, path: str = None) -> None:
        if path:
            self._file_path = path
        else:
            raise FileNotFoundError(path)

        if (not self._file_path) or self._file_path == "" or not os.path.exists(self._file_path):
            raise FileNotFoundError(self._file_path)
        
        self._parsed = False
        self._tree = ET.parse(path)
        self.concepts_by_id: dict = None
        self.concepts_by_label: dict = None
        self.connections: list[Connection] = None
        self.graph = nx.DiGraph(name = self.name) if not self.fuzzy else nx.Graph(name = self.name)
        self.phrases_by_id: dict = None

        self._tree = ET.parse(path)


    """def _fix_connections(self):
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
            del self.connections_by_from_id[item["from-id"]]"""
            
                
    @staticmethod
    def show_map(map: Cxl) -> None:
        d = {i:map.concepts_by_id[i]["label"] for i in map.concepts_by_id}
        e = {i:map.phrases_by_id[i]['label'] for i in map.phrases_by_id}
        G = map.graph
        nx.draw_networkx(map.graph, with_labels=True, labels=d, font_size = 8, pos=nx.shell_layout(G, scale=2))
        nx.draw_networkx_edge_labels(map.graph,nx.shell_layout(map.graph, scale=2), edge_labels=nx.get_edge_attributes(map.graph,'label'))
        plt.show()
        

    def parse_map(self):
        self._parsed = True
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

        # PHRASE LIST
        phrase_list = []
        for i in self._tree.getroot()[1][1].iter():
            if i.attrib == {}:
                continue
            phrase_list.append(i.attrib)
        self.phrases_by_id = {x["id"]:x for x in phrase_list}
        clm = [x["label"] for x in phrase_list]
            # BY LABEL
        if len(clm) == len(set(clm)):
            self.phrases_by_label = {x["label"]:x for x in phrase_list}

        # ALL LISTED CONNECTIONS
        intital_connection_ids = []
        for i in self._tree.getroot()[1][2].iter():
            if i.attrib == {}:
                continue
            intital_connection_ids.append(i.attrib)
        initial_connections_by_id = {x["id"]:x for x in intital_connection_ids} ### MARKED FOR DELETION ###
        # FINDING CONNECTIONS 
        connections_by_interaction: list[Connection] = []
        self.connections = []

        for i in self.phrases_by_id:
            storage = {'from': [], 'to': []}
            for j in initial_connections_by_id:
                if initial_connections_by_id[j]["to-id"] == i:
                    storage['from'].append(initial_connections_by_id[j]["from-id"])
                if initial_connections_by_id[j]["from-id"] == i:
                    storage['to'].append(initial_connections_by_id[j]["to-id"])
                if initial_connections_by_id[j]["from-id"] == i and initial_connections_by_id[j]["to-id"] == i:
                    raise InvalidCmapFileException("Connections between linking phrases aren't supported at this time", self._file_path)
            bund = BundlePhrase(self.phrases_by_id[i]["label"], i, storage["from"], storage["to"]) 
            self.connections.extend(bund.list_connections())

        # self._fix_connections() ### MARKED FOR DELETION ###
        d = {i:self.concepts_by_id[i]["label"] for i in self.concepts_by_id}
        d.update({i:i for i in self.phrases_by_id})
        for i in self.connections:
            self.graph.add_edge(i.from_id, i.to_id, id=i.id, label = i.label)
            if self.fuzzy:
                self.graph[i.from_id][i.to_id].update({'weight':i.label})

    def __str__(self):
        return "Unparsed Map" if not self._parsed else f"{self.name}: {len(self.graph.nodes())} nodes with {len(self.graph.edges())} connections between them"
        


# Comp: # of nodes
# Org: Density
if __name__ == "__main__":
    test = Cxl("cmaps/Bacterial Characteristics.cxl")
    test.parse_map()
#   print(test.concepts_by_label)
#   print({i:test.concepts_by_id[i]["label"] for i in test.concepts_by_id})
#   print(test.graph.nodes.items())
    Cxl.show_map(test)