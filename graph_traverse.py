# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import json
from graph_structure import Node, Edge


# %%
def loadConfigurationJson(filePath):
    with open(filePath, 'r') as myfile:
        data=myfile.read()
    obj = json.loads(data)
    return obj


# %%
#parsedJson = loadConfigurationJson('Bot-Json.json')
#print(parsedJson)

def populateGraphFromJson(jsonFile):
    parsedJson = loadConfigurationJson(jsonFile)

    node_maps = {}
    start_node = None
    for i in range(len(parsedJson)):
        #print(parsedJson[i])

        #The Nodes
        if parsedJson[i]['data']['type'] == "node":
            #Sample node data
            #{'id': 'dndnode_0', 'type': 'selectorNodeStart', 'position': {'x': -60, 'y': -360}, 'label': 'Start', 'data': {'label': 'Start', 'description': 'Start Point', 'subtype': '', 'type': 'node', 'image': 'eye.svg', 'class': 'blockyGrey'}}
            nodeData = parsedJson[i]
            #print(nodeData)
            node = Node(nodeData['id'], nodeData['type'])
            node.data = nodeData['data']
            node_maps[nodeData['id']] = node

            if node.node_type == 'selectorNodeStart':
                start_node = node

        elif parsedJson[i]['data']['type'] == "edge":
            #Sample edge data
            #{'source': 'dndnode_0', 'sourceHandle': 'a', 'target': 'dndnode_1', 'targetHandle': 'a', 'type': 'smoothstep', 'animated': False, 'label': '', 'data': {'label': '', 'type': 'edge'}, 'id': 'react_edge_edge_1', 'arrowHeadType': 'arrow'}
            edgeData = parsedJson[i]
            #print(edgeData)
            #create edge object
            #{"source":"dndnode_28","sourceHandle":"b","target":"dndnode_4","targetHandle":"d","animated":true,"label":"modify_order","data":{"label":"modify_order","type":"edge"},"id":"intent_edge_39","arrowHeadType":"arrowclosed","type":"step","style":{"stroke":"#f6ab6c"}}
            edge = Edge(edgeData['id'], edgeData['type'])
            edge.data = edgeData['data']
            source_node = node_maps[edgeData['source']]

            #print(source_node.node_id, edge.edge_id)
            edge.setSourceNode(source_node)
            source_node.addOutgoingEdge(edge)

            destination_node = node_maps[edgeData['target']]
            edge.setDestinationNode(destination_node)
            destination_node.addIncomingEdge(edge)
        else:
             print("Unhandled Items: ", parsedJson[i])

    return start_node


