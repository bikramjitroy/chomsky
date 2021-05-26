from graph_traverse import populateGraphFromJson
import json
import pathlib

import shutil
import os

from jinja2 import Template
from graph_structure import Node, Edge


# %%

start_node = populateGraphFromJson('sample_json/Bot-Json_mod.json')
base_dir = "rasa_config/"


pathlib.Path(base_dir).mkdir(parents=True, exist_ok=True)

data_dir = base_dir + '/data/'
action_dir = base_dir + '/actions/'
#custom_slots = base_dir + '/addons/'

pathlib.Path(data_dir).mkdir(parents=True, exist_ok=True)
pathlib.Path(action_dir).mkdir(parents=True, exist_ok=True)
#pathlib.Path(custom_slots).mkdir(parents=True, exist_ok=True)

shutil.copyfile('resources/endpoints.yml', base_dir + 'endpoints.yml')
shutil.copyfile('resources/credentials.yml', base_dir + 'credentials.yml')
shutil.copyfile('resources/config.yml', base_dir + 'config.yml')
#shutil.copyfile('resources/action/action.py', action_dir + '/action.py')
#shutil.copyfile('resources/action/addons/custom_slots.py', custom_slots + 'custom_slots.py')

pathlib.Path(action_dir + '__init__.py').touch()
#pathlib.Path(custom_slots + '__init__.py').touch()


domain_file_name = base_dir + '/domain.yml'
story_file_name = data_dir + '/stories.yml'
nlu_file_name = data_dir + '/nlu.yml'
config_file_name = action_dir + '/configs.py'



#print("Start Node", start_node)
#print('stories:')

#%%

story_counter = 0

action_nodes = ['suggestionchip', 'text', 'closenode', 'apicalling']

rasa_intents = {}
rasa_actions = {}
rasa_slots = {}
rasa_entities = {}

story_file = open(story_file_name, "w")
story_file.write('version: "2.0"\n')
story_file.write('stories:\n')

#all edges with subCategory intent -- will be in NLU file
def processFlow(story_traverse_list):
    global story_counter
    #print("Story Start->")
    story_flow = []

    story_flow.append('\n- story: story of Hi and Bye ' + str(story_counter))
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
                    rasa_intents[intent_name] = {"name": intent_name, "data" : nodes_and_edges.data}
                    #In this actions all slots default value is set

                    #SLOTS extraction from start node
                    variables = nodes_and_edges.data['description']
                    for variable in variables.splitlines():
                        key_value = variable.split('=')
                        slot_name = key_value[0]
                        slot_value = None
                        if len(key_value) > 1:
                            slot_value = key_value[1]
                        rasa_slots[slot_name] = {"name": slot_name, "value": slot_value, "type": "any"}
                        rasa_entities[slot_name] = {"name": slot_name}

                    #print("START DATA", rasa_slots)





            if nodes_and_edges.data['subtype'] == 'userinput':
                #print("**Comment-User-Response**", nodes_and_edges.data['description'])
                #Multiple incoming edges -- create a checkpoint
                if len(nodes_and_edges.incoming_edges) > 1 :
                    story_flow.append('  - checkpoint: check_flow_finished')



            if nodes_and_edges.data['subtype'] == 'initialize':
                action_name = 'initialize'
                story_flow.append('  - action: action_' + action_name)
                if rasa_actions.get(action_name) == None:
                    rasa_actions[action_name] = {"name": action_name, "data" : nodes_and_edges.data, "type" : action_name}


            #Handle all actions 
            if nodes_and_edges.data['subtype'] in action_nodes:
                #Get the name of suggestion chip and its data
                action_name = nodes_and_edges.data.get('var_name')

                if rasa_actions.get(action_name) == None:
                    rasa_actions[action_name] = {"name": action_name, "data" : nodes_and_edges.data, "type" : nodes_and_edges.data['subtype']}
                
                story_flow.append('  - action: action_' + rasa_actions[action_name]["name"])



        if nodes_and_edges.data['type'] == 'edge':
            if nodes_and_edges.data['label'] != '':
                intent_name = nodes_and_edges.data['label']
                story_flow.append('  - intent: ' + intent_name)

                #NLU items to be created  from user input
                if rasa_intents.get(intent_name) == None:
                    rasa_intents[intent_name] = {"name": intent_name, "data" : nodes_and_edges.data}

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
        #print("This is intent", edge.edge_id)
        current_append_node = []
        current_append_node.append(edge)
        current_append_node.append(edge.destination_node)
        destination_node = edge.destination_node

        #For consecutive actions - Add next_node_data 
        if node.data.get('subtype') in action_nodes and destination_node.data.get('subtype') in action_nodes:
            node.data['next_node_data'] = destination_node.data

        if destination_node.traversed == True:
            #print("Loopback - New Story:: ", edge.source_node.node_id, "->" , edge.edge_id ,"->",edge.destination_node.node_id)

            processFlow(list(list_of_prev_nodes) + list([edge]) + list([destination_node]))
        else:
            destination_node.traversed = True
            traverse_graph(destination_node, list(list_of_prev_nodes), list(current_append_node))

    return

#Add initialize action
initialize_node = Node("initialize_node", "node")
initialize_node.data = {"name":"initialize", "type":"node", "subtype": "initialize", "label":"initialize" ,"data": start_node.data}
initialize_node.data["next_node_data"] = start_node.outgoing_edges[0].destination_node.data
#print("daaa",  start_node.outgoing_edges[0].destination_node.data)

initialize_edge = Edge("initialize_edge", "edge")
initialize_edge.data = {"type":"edge", "subtype": "edge", "label": ""}


traverse_graph(start_node, list([]), list([start_node, initialize_node, initialize_edge]))
story_file.close()


def generate_nlu(rasa_intents):
    with open(nlu_file_name, 'w') as f:
        f.write('version: "2.0"\n')
        f.write('\n')
        f.write('nlu:\n')
        for rasa_intent_key in rasa_intents:
            intent_name = rasa_intents[rasa_intent_key]['name']
            f.write('- intent: ' + intent_name  +'\n')
            f.write('  examples: |\n')
            f.write('    - ' + intent_name + '\n')
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

                configs.write('data["suggestions_text_' + name + '"] = "' + data['description'] + '"\n')
                configs.write('data["suggestions_options_' + name + '"] = ' + json.dumps(data['rowChip']) + '\n')

            if rasa_actions[rasa_actions_key].get('type') and rasa_actions[rasa_actions_key].get('type') == "text" :
                data = rasa_actions[rasa_actions_key]['data']
                name = rasa_actions[rasa_actions_key]['name']

                configs.write('data["text_' + name + '"] = "' + data['description'] + '"\n')

            if rasa_actions[rasa_actions_key].get('type') and rasa_actions[rasa_actions_key].get('type') == "closenode" :
                data = rasa_actions[rasa_actions_key]['data']
                name = rasa_actions[rasa_actions_key]['name']
                configs.write('data["disposition_' + name + '"] = "' + data['dispositionName'] + '"\n')            

generate_action_slots(rasa_actions)



def generate_action_class_file(rasa_actions):

    headers = '''
#!/usr/bin/env python3
from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher

import requests
import json

import configs

def resolve_response(response_text, tracker):
   found_var = False
   start_index = 0
   count = 0

   slot_str = None
   slot_value = None
   for x in response_text:

      if found_var == True and x == '}' and response_text[count + 1]== '}':
         found_var = False
         
         slot_name = response_text[start_index:count].strip()
         slot_str = response_text[start_index-2:count+2]
         #fetch value from tracker - make it a string for correct replacement
         slot_value = str(tracker.get_slot(slot_name))
         print("Var-", slot_name, slot_str, slot_value)
         break

      if x == '{' and response_text[count + 1]== '{':
         found_var = True
         start_index = count + 2

      count = count + 1

   if slot_str:
      response_text = response_text.replace(slot_str, slot_value)
      response_text = resolve_response(response_text, tracker)

   return response_text

def resolve_json(response_text, tracker):
   found_var = False
   start_index = 0
   count = 0

   slot_str = None
   slot_value = None
   for x in response_text:

      if found_var == True and x == '}' and response_text[count + 1]== '}':
         found_var = False
         
         slot_name = response_text[start_index:count].strip()
         slot_str = response_text[start_index-2:count+2]
         #fetch value from tracker - make it a string for correct replacement
         slot_value = str(tracker.get_slot(slot_name))
         print("Var-", slot_name, slot_str, slot_value)
         break

      if x == '{' and response_text[count + 1]== '{':
         found_var = True
         start_index = count + 2

      count = count + 1

   if slot_str:
      response_text = response_text.replace(slot_str, '"' + slot_value + '"')
      response_text = resolve_json(response_text, tracker)

   return response_text

    '''
    header_tm = Template(headers)
    header_msg = header_tm.render()


    initialize_template_raw = '''
class ActionInitialize(Action):
   def name(self) -> Text:
      return "action_initialize"

   def run(self,
           dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

      slots = []
      {{value_set}}
      
      next_is_action = True
      if next_is_action == {{next_is_action}}:
          #Action name which will execute next
          slots.append(FollowupAction("{{followup_action_name}}"))

      return slots
    '''
    initialize_tm = Template(initialize_template_raw)

    initialize_variable_raw = '''
      if tracker.get_slot("{{name}}") is None:
           slots.append(SlotSet("{{name}}", "{{value}}"))
    '''
    initialize_var_tm = Template(initialize_variable_raw)



    suggestion_template_raw = '''
class ActionSuggestionChip{{ counter }}(Action):
   def name(self) -> Text:
      return "action_{{ name }}"

   def run(self,
           dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

      suggestion_chip = "{{ name }}"

      suggestion_chip_options_json = configs.data['suggestions_options_' + suggestion_chip]
      suggestion_chip_text = configs.data['suggestions_text_' + suggestion_chip]
      suggestion_chip_text = resolve_response(suggestion_chip_text, tracker)

      dispatcher.utter_message(text=suggestion_chip_text, platform_json=suggestion_chip_options_json)

      slots = []

      next_is_action = True
      if next_is_action == {{next_is_action}}:
          #Action name which will execute next
          slots.append(FollowupAction("{{followup_action_name}}"))

      return slots
    '''
    suggestion_tm = Template(suggestion_template_raw)

    text_template_raw = '''
class ActionTextResponse{{ counter }}(Action):
   def name(self) -> Text:
      return "action_{{ name }}"

   def run(self,
           dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

      text_response = "{{ name }}"
      text_response_text = configs.data['text_' + text_response]
      text_response_text = resolve_response(text_response_text, tracker)


      dispatcher.utter_message(text=text_response_text, platform_json=None)

      slots = []

      next_is_action = True
      if next_is_action == {{next_is_action}}:
          #Action name which will execute next
          slots.append(FollowupAction("{{followup_action_name}}"))

      return slots
    '''
    text_tm = Template(text_template_raw)

    dispose_template_raw = '''
class ActionDispose{{ counter }}(Action):
   def name(self) -> Text:
      return "action_{{ name }}"

   def run(self,
           dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

      dispose = "{{ name }}"
      dispose_name = configs.data['disposition_' + dispose]
      print("Dispose: ", dispose, dispose_name)

      #dispatcher.utter_message(text=suggestion_chip_text, platform_json=suggestion_chip_options_json)

      slots = []

      next_is_action = True
      if next_is_action == {{next_is_action}}:
          #Action name which will execute next
          slots.append(FollowupAction("{{followup_action_name}}"))

      return slots
    '''
    dispose_tm = Template(dispose_template_raw)



    api_template_raw = '''
class ActionAPICall{{ counter }}(Action):
   def name(self) -> Text:
      return "action_{{ name }}"

   def run(self,
           dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

      #URL could be static or pick up from SLOT
      #url = tracker.get_slot('{{url}}')
      url = "{{url}}"

      #url = "http://localhost:9076/test"
      request_json = '{{request_data}}'
      payload = resolve_json(request_json, tracker)

      print("API payload:", url, payload)

      req = requests.post(url, json=json.loads(payload))
      print("API response code:", req.status_code)

      result = req.json()

      response_json_data = {{response_json}}

      slots = []
      for key in response_json_data:
           slots.append(SlotSet(key, response_json_data[key]))

      next_is_action = True
      if next_is_action == {{next_is_action}}:
          #Action name which will execute next
          slots.append(FollowupAction("{{followup_action_name}}"))

      return slots     
    '''
    api_tm = Template(api_template_raw)


    with open(action_dir + 'action.py', 'w') as configs:
        configs.write(header_msg)

        class_counter = 0
        for rasa_actions_key in rasa_actions:
            class_counter = class_counter + 1

            next_is_action = False
            followup_action_name = None

            #INITIALIZE THE SLOTS in action_initialize - set default values if its not set 


            if rasa_actions[rasa_actions_key].get('type') and rasa_actions[rasa_actions_key].get('type') == "initialize" :
 
                if rasa_actions[rasa_actions_key]["data"].get('next_node_data'):
                    next_is_action = True
                    followup_action_name =  "action_" + rasa_actions[rasa_actions_key]["data"].get('next_node_data')['var_name']

                all_slot_str = []
                for slot in rasa_slots:
                    if rasa_slots[slot].get("value"):
                        slot_name =  rasa_slots[slot]["name"]
                        slot_value = rasa_slots[slot]["value"]

                        if_cond = initialize_var_tm.render(name=slot_name, value=slot_value)
                        all_slot_str.append(if_cond)

                final_slots = ''.join(all_slot_str)
                i_msg = initialize_tm.render(value_set=final_slots, next_is_action=next_is_action, followup_action_name=followup_action_name)
                configs.write(i_msg)
                continue



            if rasa_actions[rasa_actions_key].get('type') and rasa_actions[rasa_actions_key].get('type') in action_nodes:

                #If next node data is defined, then next node is action node to be treated as FollowupAction
                if rasa_actions[rasa_actions_key]["data"].get('next_node_data'):
                    #print(rasa_actions_key, rasa_actions[rasa_actions_key])
                    next_is_action = True
                    followup_action_name = "action_" + rasa_actions[rasa_actions_key]['data'].get('next_node_data')['var_name']

                if rasa_actions[rasa_actions_key].get('type') == "suggestionchip" :
                    #print("Suggestion Chip -",   rasa_actions[rasa_actions_key]['name'], rasa_actions[rasa_actions_key].get('next_node_data'))
                    s_msg = suggestion_tm.render(name=rasa_actions[rasa_actions_key]['name'], counter=class_counter, next_is_action=next_is_action, followup_action_name=followup_action_name)
                    configs.write(s_msg)

                if rasa_actions[rasa_actions_key].get('type') == "text" :
                    t_msg = text_tm.render(name=rasa_actions[rasa_actions_key]['name'], counter=class_counter, next_is_action=next_is_action, followup_action_name=followup_action_name)
                    configs.write(t_msg)

                if rasa_actions[rasa_actions_key].get('type') and rasa_actions[rasa_actions_key].get('type') == "closenode" :
                    d_msg = dispose_tm.render(name=rasa_actions[rasa_actions_key]['name'], counter=class_counter, next_is_action=next_is_action, followup_action_name=followup_action_name)
                    configs.write(d_msg)  

                if rasa_actions[rasa_actions_key].get('type') == "apicalling" :
                    #print("API Calling", rasa_actions[rasa_actions_key]["data"])
                    api_msg = api_tm.render(name=rasa_actions[rasa_actions_key]['name'], counter=class_counter, url=rasa_actions[rasa_actions_key]["data"]["url"], request_data=rasa_actions[rasa_actions_key]["data"]["request_json"], response_json=rasa_actions[rasa_actions_key]["data"]["response_json"], next_is_action=next_is_action, followup_action_name=followup_action_name)
                    configs.write(api_msg)  


    return

generate_action_class_file(rasa_actions)

