from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

import configs

class ActionSuggestionChip(Action):
   def name(self) -> Text:
      return "action_suggestions_response"

   def run(self,
           dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

      suggestion_chip = tracker.get_slot('suggestion_chip')

      suggestion_chip_options_json = configs.data['suggestions_options_' + suggestion_chip]
      suggestion_chip_text = configs.data['suggestions_text_' + suggestion_chip]

      dispatcher.utter_message(text=suggestion_chip_text, platform_json=suggestion_chip_options_json)

      return []

class ActionTextResponse(Action):
   def name(self) -> Text:
      return "action_text_response"

   def run(self,
           dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

      text_response = tracker.get_slot('text_response')
      text_response_text = configs.data['text_' + text_response]

      dispatcher.utter_message(text=text_response_text, platform_json=None)

      return []


class ActionDispose(Action):
   def name(self) -> Text:
      return "action_dispose"

   def run(self,
           dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

      dispose = tracker.get_slot('dispose')
      dispose_name = configs.data['disposition_' + dispose]
      print("Dispose: ", dispose, dispose_name)

      #dispatcher.utter_message(text=suggestion_chip_text, platform_json=suggestion_chip_options_json)

      return []
