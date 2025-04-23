from __future__ import annotations
from cxlparser import Cxl, Connection
import networkx

class ScoredCxl:
    def __init__(self, c: Cxl):
        self.cmap = c
        self.density: float = None
        self.distance_array: list[list[float]] = None
        self.clusters = None
        self.center = None
        self.leaves = None

    def score_density(self):
        self.density = networkx.density(self.cmap.graph)
    
    def find_centers(self, barycenter = True, center = True, eigenvector_center = True, page_rank = True):
        if not barycenter and not center:
            return None
        self.center = {}
        if barycenter:
            self.center['barycenter'] = networkx.barycenter(self.cmap.graph.to_undirected())
        if center:
            self.center['center'] = networkx.center(self.cmap.graph.to_undirected())
        if eigenvector_center:
            self.center['eigenvector_center'] = networkx.eigenvector_centrality(self.cmap.graph.to_undirected())
        if page_rank:
            self.center['page_rank'] = networkx.pagerank(self.cmap.graph)
        if len(self.center) ==1 or (self.center['center'] == self.center['barycenter'] and self.center['eigenvector_center'] == self.center['barycenter']):
            self.center = self.center['center']
    
    def _generate_nearness_array(self, convert_to_undirected: bool = True):
        nodes = list(self.cmap.concepts_by_id.keys())
        """"""
        l = []
        for i in nodes:
            l.append([])
            for j in nodes:
                try: 
                    p = networkx.shortest_path_length(self.cmap.graph.to_undirected() if convert_to_undirected else self.cmap.graph,i, j)
                    l[-1].append(float(1/p) if p != 0 else None)
                except networkx.NetworkXNoPath:
                    l[-1].append(0)
        return l
        """"""
        # return [[networkx.shortest_path_length(self.cmap.graph,i, j) for j in nodes] for i in nodes]

    def score(self, res):
        self.find_centers()
        return self.cmap._list_clusters(res)

    def show_map_coloring(self, index: str = 'eigenvector_center'):
        if not self.center:
            raise Exception("run find_centers()")
        print(self.center[index])
        m = max(self.center[index].values())
        self.cmap.show_map(self.cmap, False, colors=[(float(self.center[index][i])/m, float(self.center[index][i])/m, float(self.center[index][i])/m) for i in self.center[index]])
    
        


    def compare(self, other: ScoredCxl):
        pass
        

