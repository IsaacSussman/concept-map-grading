from __future__ import annotations
from cxlparser import Cxl, Connection
import networkx

class ScoredCxl:
    def __init__(self, c: Cxl):
        self.cmap = c
        self.density: float = None
        self.distance_array: list[list[float]] = None
        self.clusters = None

    def score_density(self):
        self.density = networkx.density(self.cmap.graph)
    
    def _generate_distance_array(self):

    def score(self):
        self.score_density()
    
    def compare(self, other: ScoredCxl):
        pass
        

