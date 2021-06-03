

class Base(object):
    def __init__(self, object_id, object_type):
        self.object_id = object_id
        self.object_type = object_type


class Node(Base):
    def __init__(self, node_id, node_type):
        super().__init__(node_id, "Node")
        self.node_id = node_id
        self.node_type = node_type
        self.incoming_edges = []
        self.outgoing_edges = []
        self.properties = {}
        self.traversed = False
    
    def addIncomingEdge(self, incoming_edge):
        self.incoming_edges.append(incoming_edge)
    
    def addOutgoingEdge(self, outgoing_edge):
        self.outgoing_edges.append(outgoing_edge)

    def setProperties(self, properties):
        self.properties = properties


class Edge(Base):
    def __init__(self, edge_id, edge_type):
        super().__init__(edge_id, "Edge")
        self.edge_id = edge_id
        self.edge_type = edge_type
        self.source_node = None
        self.destination_node = None
        self.data = None
    
    def setSourceNode(self, source_node):
        self.source_node = source_node
    
    def setDestinationNode(self, destination_node):
        self.destination_node = destination_node   

# edge = Edge('a','b')
# edge.setSourceNode(None)
# print(edge)