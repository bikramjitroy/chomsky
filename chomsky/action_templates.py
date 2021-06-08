
headers_raw = '''
#!/usr/bin/env python3
from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher

import requests
import json

from actions import configs

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
        {{transition_logic}}
        return slots
    '''


initialize_variable_raw = '''
        if tracker.get_slot("{{name}}") is None:
            slots.append(SlotSet("{{name}}", "{{value}}"))
        '''


suggestion_template_raw = '''
class ActionSuggestionChip{{ counter }}(Action):
    def name(self) -> Text:
        return "action_{{ name }}"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        suggestion_chip_options_json = configs.data['suggestions_options_{{ name }}']
        suggestion_chip_text = configs.data['suggestions_text_{{ name }}']
        print("SuggestionText", suggestion_chip_text)
        suggestion_chip_text = resolve_response(suggestion_chip_text, tracker)
        data = {"dialogflow_responses": [{"text": suggestion_chip_text, "fallback": suggestion_chip_text, "suggestions": suggestion_chip_options_json}]}
        dispatcher.utter_message(json_message = data)

        slots = []
        {{transition_logic}}
        return slots
        '''


carousel_template_raw = '''
class ActionCarouselChip{{ counter }}(Action):
    def name(self) -> Text:
        return "action_{{ name }}"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        carousel_chip_options_json = configs.data['carousel_options_{{ name }}']
        data = {"dialogflow_responses": [{"fallback": "carousel cards", "richCard": carousel_chip_options_json}]}
        dispatcher.utter_message(json_message = data)

        slots = []
        {{transition_logic}}
        return slots
        '''

text_template_raw = '''
class ActionTextResponse{{ counter }}(Action):
    def name(self) -> Text:
        return "action_{{ name }}"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        text_response_text = configs.data['text_{{ name }}']
        text_response_text = resolve_response(text_response_text, tracker)
        dispatcher.utter_message(text=text_response_text, platform_json=None)

        slots = []
        {{transition_logic}}
        return slots
            '''


dispose_template_raw = '''
class ActionDispose{{ counter }}(Action):
    def name(self) -> Text:
        return "action_{{ name }}"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispose_name = configs.data['disposition_{{ name }}']
        print("Dispose: ", dispose_name)

        slots = []
        {{transition_logic}}
        return slots
        '''

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
        {{transition_logic}}
        return slots     
        '''

script_template_raw = '''
class ActionScript{{ counter }}(Action):
    def name(self) -> Text:
        return "action_{{ name }}"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        slots = []
        {{transition_logic}}
        return slots
    '''

followup_conditional_action_raw = """
        if tracker.get_slot('{{slot_name}}') {{comparison}} "{{slot_value}}":
            slots.append(FollowupAction("action_{{followup_action}}"))
            return slots
    """

followup_action_raw = """   
        slots.append(FollowupAction("action_{{followup_action}}"))
    """       





