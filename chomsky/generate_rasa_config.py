from graph_traverse import populateGraphFromJson
import json
import pathlib

import shutil
import os
import re

from jinja2 import Template
from graph_structure import Node, Edge

import distutils
from distutils import dir_util

# %%

# def loadConfigurationJson(filePath):
#     with open(filePath, 'r') as myfile:
#         data=myfile.read()
#     obj = json.loads(data)
#     return obj

# parsedJson = loadConfigurationJson('sample_json/Bot-Json_mod.json')

def bot_generation(json_bot_diagram, base_dir):

    start_node = populateGraphFromJson(json_bot_diagram)

    #pathlib.Path(base_dir).mkdir(parents=True, exist_ok=True)

    distutils.dir_util.copy_tree("resources", base_dir)

    domain_file_name = base_dir + '/rasa/domain.yml'

    data_dir = base_dir + '/rasa/data/'
    pathlib.Path(data_dir).mkdir(parents=True, exist_ok=True)
    story_file_name = data_dir + '/stories.yml'
    nlu_file_name = data_dir + '/nlu.yml'


    action_dir = base_dir + '/actions/'
    pathlib.Path(action_dir + '__init__.py').touch()
    config_file_name = action_dir + '/configs.py'
    actions_file_name = action_dir + '/actions.py'



    #print("Start Node", start_node)
    #print('stories:')

    #%%

    story_counter = 0

    action_nodes = ['suggestionchip', 'text', 'closenode', 'apicalling','carousel','scriptnode']

    rasa_intents = {}
    rasa_actions = {}
    rasa_slots = {}
    rasa_entities = {}

    story_file = open(story_file_name, "w")
    story_file.write('version: "2.0"\n')
    story_file.write('stories:\n')

    #all edges with subCategory intent -- will be in NLU file
    def processFlow(story_traverse_list):
        #print("Story Start->")
        story_flow = []

        nonlocal story_counter

        story = '\n- story: Generated ' + str(story_counter)
        story_flow.append(story)
        story_counter = story_counter + 1


        next_of_initialize = True
        for nodes_and_edges in story_traverse_list:
            if nodes_and_edges.data['type'] == 'node':
                if nodes_and_edges.data['label'] == 'Start':
                    story_flow.append('  steps:')
                    story_flow.append('  - intent: start')

                    # Create a triggeting intent which will start the BOT
                    intent_name = "start"
                    if rasa_intents.get(intent_name) == None:
                        rasa_intents[intent_name] = {"name": intent_name, "data" : nodes_and_edges.data, "nlu": ["start"]}
                        #In this actions all slots default value is set
                        #SLOTS extraction from start node
                        slot_json = nodes_and_edges.data['bot_slots']
                        for slot in slot_json:
                            slot_name = slot['slot_name']
                            slot_value = slot['slot_value']
                            if slot_value == '':
                                slot_value = None
                            rasa_slots[slot_name] = {"name": slot_name, "value": slot_value, "type": "any"}
                            rasa_entities[slot_name] = {"name": slot_name}

                #Edges of userinput are intents - Handle that in Edges - This is a marker Node
                elif nodes_and_edges.data['subtype'] == 'userinput':
                    dummy= 1

                #Handle all actions 
                elif nodes_and_edges.data['subtype'] == 'initialize':
                    action_name = nodes_and_edges.data.get('var_name')
                    if rasa_actions.get(action_name) == None:
                        rasa_actions[action_name] = {"name": action_name, "data" : nodes_and_edges.data, "type" : nodes_and_edges.data['subtype']}
                    story_flow.append('  - action: action_' + rasa_actions[action_name]["name"])

                elif nodes_and_edges.data['subtype'] in action_nodes:
                    #Get the name of suggestion chip and its data
                    action_name = nodes_and_edges.data.get('var_name')
                    if rasa_actions.get(action_name) == None:
                        rasa_actions[action_name] = {"name": action_name, "data" : nodes_and_edges.data, "type" : nodes_and_edges.data['subtype']}
                    story_flow.append('  - action: action_' + rasa_actions[action_name]["name"])
                else:
                    print("Subtype not handled", nodes_and_edges.data['subtype'])


            if nodes_and_edges.data['type'] == 'edge':
                #Transitions from Action Nodes
                if nodes_and_edges.source_node.data['subtype'] in action_nodes or nodes_and_edges.source_node.data['subtype']=='initialize':
                    if nodes_and_edges.destination_node.data['subtype'] in action_nodes:
                        #Conditional transition
                        if nodes_and_edges.data.get('subtype') == 'Conditional':
                            #print("Conditional Edge", nodes_and_edges.data, story)
                            slot_variable = nodes_and_edges.data.get('Slot_Variable')
                            comparison_type = nodes_and_edges.data.get('Comparison_Type')
                            comparison_value = nodes_and_edges.data.get('Comparison_Value')

                            destination_action_name = nodes_and_edges.destination_node.data['var_name']
                            source_action_name = nodes_and_edges.source_node.data['var_name']
                            condition_config = {"slot_name": slot_variable, "comparison": comparison_type, "slot_value": comparison_value, "followup_action": destination_action_name}               

                            if rasa_actions[source_action_name].get('conditional_transitions'):
                                #Check if transition already added
                                found = False
                                for transition in rasa_actions[source_action_name].get('conditional_transitions'):
                                    if transition["followup_action"] == condition_config["followup_action"]:
                                        found = True
                                if found == False:
                                    rasa_actions[source_action_name]["conditional_transitions"].append(condition_config)
                            else:
                                rasa_actions[source_action_name]["conditional_transitions"] = [condition_config]

                            continue
                        # else:
                        #     print("Types", nodes_and_edges.data.get('subtype'))

                        #Unconditional Transtions are from Action Nodes to other Action Nodes except towards "USER_INPUT" node
                        if nodes_and_edges.data.get('subtype') == 'Normal':
                            #transition with no label - unconditional transition ---- Node before user input should be unconditional
                            source_action_name = nodes_and_edges.source_node.data['var_name']
                            destination_action_name = nodes_and_edges.destination_node.data['var_name']
                            condition_config = {"type": "unconditional", "followup_action": destination_action_name}

                            if rasa_actions[source_action_name].get('unconditional_transitions'):
                                #Check if transition already added
                                found = False
                                for transition in rasa_actions[source_action_name].get('unconditional_transitions'):
                                    if transition["followup_action"] == condition_config["followup_action"]:
                                        found = True
                                if found == False:
                                    rasa_actions[source_action_name]["unconditional_transitions"].append(condition_config)
                            else:
                                rasa_actions[source_action_name]["unconditional_transitions"] = [condition_config]
                            
                            continue


                #Transitions from USER_INPUT nodes are always INTENTS
                if nodes_and_edges.source_node.data['subtype'] == 'userinput':
                    #Transition after userinput node is always Intent Edges
                    intent_name = nodes_and_edges.data['label']
                    #print("Intent-Name", nodes_and_edges.data, story)
                    story_flow.append('  - intent: ' + intent_name)


                    #Entity examples:
                    first_example = nodes_and_edges.data['examples'][0]
                    entities_arr = re.findall('\[(.+?)\)', first_example)

                    if len(entities_arr) > 0:
                        story_flow.append('    entities:')
                    for entities_str in entities_arr:
                        ent_ex = entities_str.split('](')
                        story_flow.append('    - ' + ent_ex[1] + ': ' + ent_ex[0])

                    for entities_str in entities_arr:
                        ent_ex = entities_str.split('](')
                        story_flow.append('  - slot_was_set:')
                        story_flow.append('    - ' + ent_ex[1] + ': ' + ent_ex[0])               

                    #NLU items to be created  from user input
                    if rasa_intents.get(intent_name) == None:
                        rasa_intents[intent_name] = {"name": intent_name, "data" : nodes_and_edges.data, "nlu": nodes_and_edges.data.get('examples')}

                    continue



                

        story_file.write('\n'.join(story_flow) + '\n')


    # %%

    ##-- doing a depth first search -- every path is a story
    def traverse_graph(node, list_of_prev_nodes, append_nodes):
        list_of_prev_nodes = list_of_prev_nodes + append_nodes

        #End of path
        if len(node.outgoing_edges) == 0:
            #print("End of path", node.node_id)
            processFlow(list_of_prev_nodes)
            return                                                                            

        for edge in node.outgoing_edges:
            #print("This is intent", edge.edge_id, edge.data)
            current_append_node = []
            current_append_node.append(edge)
            current_append_node.append(edge.destination_node)
            destination_node = edge.destination_node

            if destination_node.traversed == True:
                #print("Loopback - New Story:: ", edge.source_node.node_id, "->" , edge.edge_id ,"->",edge.destination_node.node_id)

                processFlow(list(list_of_prev_nodes) + list([edge]) + list([destination_node]))
            else:
                destination_node.traversed = True
                traverse_graph(destination_node, list(list_of_prev_nodes), list(current_append_node))

        return




    #Add initialize to graph of Start Node -> {start_dest_edge} converted into below
    #start_node -> initialize_edge -> initialize_node  [start_node.outgoing_edges]=> {start_dest_edge}
    #Add initialize action
    def add_initialize(start_node):
        initialize_node = Node("initialize_node", "node")
        initialize_node.data = {"var_name":"initialize", "type":"node", "subtype": "initialize", "label":"initialize" ,"data": start_node.data}
        #Set incoming and outgoing edges
        initialize_node.outgoing_edges = start_node.outgoing_edges


        initialize_edge = Edge("initialize_edge", "edge")
        initialize_edge.data = {"type":"edge", "subtype": "edge", "label": ""}
        initialize_edge.source_node = start_node
        initialize_edge.destination_node = initialize_node

        initialize_node.incoming_edges = [initialize_edge]

        for edges in initialize_node.outgoing_edges:
            edges.source_node = initialize_node

        start_node.outgoing_edges = [initialize_edge]

        return start_node


    start_node = add_initialize(start_node)
    traverse_graph(start_node, list([]), list([start_node]))
    story_file.close()


    def generate_nlu(rasa_intents):
        with open(nlu_file_name, 'w') as f:
            f.write('version: "2.0"\n')
            f.write('\n')
            f.write('nlu:\n')
            for rasa_intent_key in rasa_intents:
                #print("Intent:-", rasa_intents[rasa_intent_key])
                intent_name = rasa_intents[rasa_intent_key]['name']
                f.write('- intent: ' + intent_name  +'\n')
                f.write('  examples: |\n')
                if rasa_intents[rasa_intent_key].get('nlu'):
                    for example in rasa_intents[rasa_intent_key]['nlu']:
                        f.write('    - ' + example + '\n')
                else:
                    print("Mussing NLU", rasa_intents[rasa_intent_key])
        return

    generate_nlu(rasa_intents)

    def generate_domain(rasa_intents, rasa_actions):

        with open(domain_file_name, 'w') as f:
            f.write('version: "2.0"\n')

            f.write('\nintents:\n')
            for rasa_intent_key in rasa_intents:
                intent_name = rasa_intents[rasa_intent_key]['name']
                f.write('  - ' + intent_name  +'\n')
    
            #Response slots are fixed and logic control by slots value
            f.write('\nentities:\n')        
            for rasa_entity_key in rasa_entities:
                rasa_entity = rasa_entities[rasa_entity_key]
                f.write('  - ' + rasa_entity['name'] + '\n')

            #Response slots are fixed and logic control by slots value
            f.write('\nslots:\n')        
            for rasa_slot_key in rasa_slots:
                rasa_slot = rasa_slots[rasa_slot_key]
                f.write('  ' + rasa_slot['name'] + ':\n')
                f.write('    type: ' + rasa_slot['type'] + '\n')
                f.write('    influence_conversation: false\n')

            #Action responses are fixed and logic control by slots
            f.write('\nactions:\n')
            for rasa_actions_key in rasa_actions:
                action_name = rasa_actions[rasa_actions_key]['name']
                #print(action_name, rasa_actions[rasa_actions_key])
                f.write('  - action_' + action_name  +'\n')

            # f.write('\responses:\n')
            # f.write('  utter_suggestion_chip:\n')
            # f.write('  - custom:\n')
            # f.write('      text: "Hello response"\n')
            # f.write('      json: "Hello response"\n')

            f.write('\nsession_config:\n')
            f.write('  session_expiration_time: 30\n')
            f.write('  carry_over_slots_to_new_session: true\n')
            f.write('\nconfig:\n')
            f.write('  store_entities_as_slots: true\n')
        return

    generate_domain(rasa_intents, rasa_actions)


    def generate_action_slots(rasa_actions):

        with open(config_file_name, 'w') as configs:
            configs.write("#GENERATED FILE\n\n")
            configs.write("data={}\n")
            for rasa_actions_key in rasa_actions:

                if rasa_actions[rasa_actions_key].get('type') and rasa_actions[rasa_actions_key].get('type') == "suggestionchip" :
                    data = rasa_actions[rasa_actions_key]['data']
                    name = rasa_actions[rasa_actions_key]['name']

                    chips = []
                    for suggestion in data['rowChip']:
                        chips.append({"reply":{"postbackData": suggestion["description"], "text": suggestion["text"]}})
                    
                    configs.write('data["suggestions_text_' + name + '"] = """' + data['description'] + '"""\n')
                    configs.write('data["suggestions_options_' + name + '"] = ' + json.dumps(chips) + '\n')


                if rasa_actions[rasa_actions_key].get('type') and rasa_actions[rasa_actions_key].get('type') == "carousel" :
                    data = rasa_actions[rasa_actions_key]['data']
                    name = rasa_actions[rasa_actions_key]['name']

                    chips = []
                    for card_data in data['rowChip']:
                        new_data = {}
                        new_data['title'] = card_data["text"]
                        new_data['description'] = card_data["text"]
                        new_data['suggestions'] = [{"reply":{"postbackData": card_data["description"], "text": card_data["text"]}}]
                        new_data['media'] = {'height': 'MEDIUM', 'contentInfo': {'fileUrl':card_data['image'], 'forceRefresh': 'false'}}                        
                        chips.append(new_data)

                    carousel_cards = { 'carouselCard': {'cardWidth': 'MEDIUM', 'cardContents': chips}}
                    
                    #configs.write('data["carousel_text_' + name + '"] = """' + data['description'] + '"""\n')
                    configs.write('data["carousel_options_' + name + '"] = ' + json.dumps(carousel_cards) + '\n')

                    #configs.write('data["carousel_options_' + name + '"] = ' + json.dumps(data['rowChip']) + '\n')


                if rasa_actions[rasa_actions_key].get('type') and rasa_actions[rasa_actions_key].get('type') == "text" :
                    data = rasa_actions[rasa_actions_key]['data']
                    name = rasa_actions[rasa_actions_key]['name']
                    configs.write('data["text_' + name + '"] = """' + data['description'] + '"""\n')

                if rasa_actions[rasa_actions_key].get('type') and rasa_actions[rasa_actions_key].get('type') == "closenode" :
                    data = rasa_actions[rasa_actions_key]['data']
                    name = rasa_actions[rasa_actions_key]['name']
                    configs.write('data["disposition_' + name + '"] = "' + data['dispositionName'] + '"\n')            

    generate_action_slots(rasa_actions)


    def generate_action_class_file(rasa_actions):

        from action_templates import headers_raw, initialize_template_raw, initialize_variable_raw, suggestion_template_raw, carousel_template_raw, text_template_raw, dispose_template_raw, api_template_raw, script_template_raw, followup_conditional_action_raw, followup_action_raw

        header_tm = Template(headers_raw)
        initialize_tm = Template(initialize_template_raw)
        initialize_var_tm = Template(initialize_variable_raw)
        suggestion_tm = Template(suggestion_template_raw)
        carousel_tm = Template(carousel_template_raw)
        text_tm = Template(text_template_raw)
        dispose_tm = Template(dispose_template_raw)
        api_tm = Template(api_template_raw)
        script_tm = Template(script_template_raw)
        followup_conditional_tm = Template(followup_conditional_action_raw)
        followup_tm = Template(followup_action_raw)

        with open(actions_file_name, 'w') as configs:
            header_msg = header_tm.render()
            configs.write(header_msg)

            class_counter = 0
            for rasa_actions_key in rasa_actions:
                class_counter = class_counter + 1

                #Handle transition logic from action
                transition_logic = ""
                if rasa_actions[rasa_actions_key].get('type') in action_nodes or rasa_actions[rasa_actions_key].get('type') == "initialize":
                
                    if rasa_actions[rasa_actions_key].get('conditional_transitions'):
                        for transiton in rasa_actions[rasa_actions_key]['conditional_transitions']:
                            condition = followup_conditional_tm.render(slot_name=transiton["slot_name"], comparison=transiton["comparison"], slot_value=transiton["slot_value"], followup_action=transiton["followup_action"])
                            transition_logic = transition_logic + condition

                    if rasa_actions[rasa_actions_key].get('unconditional_transitions'):
                        for transiton in rasa_actions[rasa_actions_key]['unconditional_transitions']:
                            condition = followup_tm.render(followup_action=transiton["followup_action"])
                            transition_logic = transition_logic + condition
                        
                #INITIALIZE THE SLOTS in action_initialize - set default values if its not set 
                if rasa_actions[rasa_actions_key].get('type') == "initialize" :

                    #print("Init", rasa_actions[rasa_actions_key])
                    all_slot_str = []
                    for slot in rasa_slots:
                        if rasa_slots[slot].get("value"):
                            slot_name =  rasa_slots[slot]["name"]
                            slot_value = rasa_slots[slot]["value"]

                            if_cond = initialize_var_tm.render(name=slot_name, value=slot_value)
                            all_slot_str.append(if_cond)

                    final_slots = ''.join(all_slot_str)
                    i_msg = initialize_tm.render(value_set=final_slots, transition_logic=transition_logic)
                    configs.write(i_msg)
                    continue

                elif rasa_actions[rasa_actions_key].get('type') == "suggestionchip" :
                    s_msg = suggestion_tm.render(name=rasa_actions[rasa_actions_key]['name'], counter=class_counter, transition_logic=transition_logic)
                    configs.write(s_msg)

                elif rasa_actions[rasa_actions_key].get('type') == "carousel" :
                    #print("Carausel", rasa_actions[rasa_actions_key]["data"])
                    c_msg = carousel_tm.render(name=rasa_actions[rasa_actions_key]['name'], counter=class_counter, transition_logic=transition_logic)
                    configs.write(c_msg)  

                elif rasa_actions[rasa_actions_key].get('type') == "text" :
                    t_msg = text_tm.render(name=rasa_actions[rasa_actions_key]['name'], counter=class_counter, transition_logic=transition_logic)
                    configs.write(t_msg)

                elif rasa_actions[rasa_actions_key].get('type') and rasa_actions[rasa_actions_key].get('type') == "closenode" :
                    d_msg = dispose_tm.render(name=rasa_actions[rasa_actions_key]['name'], counter=class_counter, transition_logic=transition_logic)
                    configs.write(d_msg)  

                elif rasa_actions[rasa_actions_key].get('type') == "apicalling" :
                    #print("API Calling", rasa_actions[rasa_actions_key]["data"])
                    api_msg = api_tm.render(name=rasa_actions[rasa_actions_key]['name'], counter=class_counter, url=rasa_actions[rasa_actions_key]["data"]["url"], request_data=rasa_actions[rasa_actions_key]["data"]["request_json"], response_json=rasa_actions[rasa_actions_key]["data"]["response_json"], transition_logic=transition_logic)
                    configs.write(api_msg)  

                elif rasa_actions[rasa_actions_key].get('type') == "scriptnode" :
                    d_msg = script_tm.render(name=rasa_actions[rasa_actions_key]['name'], counter=class_counter, transition_logic=transition_logic)
                    configs.write(d_msg)
                else:
                    print("Unghandled Action Type", rasa_actions[rasa_actions_key].get('type'))


        return

    generate_action_class_file(rasa_actions)

