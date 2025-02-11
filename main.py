from cxlparser import cxl
import networkx as nx
import defusedxml.ElementTree as ET
import xml
import matplotlib.pyplot as plt

# https://cmap.ihmc.us/xml/CXL.html
test = cxl("AeroCapture.cxl")
test.parse_map()
#print(test.concepts_by_label)
#print({i:test.concepts_by_id[i]["label"] for i in test.concepts_by_id})
#print(test.graph.nodes.items())
cxl.show_map(test)
