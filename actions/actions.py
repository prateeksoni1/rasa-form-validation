from typing import Any, Text, Dict, List
from petl.io import text

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from . import Repo


class ActionSaveDetails(Action):
    def name(self) -> Text:
        return "action_add_candidate"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        Repo.insertCandidate(
            tracker.get_slot("name"),
            tracker.get_slot("emp_code"),
            tracker.get_slot("number"),
            tracker.get_slot("email"),
        )

        dispatcher.utter_message(response="utter_display_details")

        return []


class ActionSelectAll(Action):
    def name(self) -> Text:
        return "action_select_all"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        rows = Repo.select()

        dispatcher.utter_message(text=rows)

        return []


class ActionShowNominees(Action):
    def name(self) -> Text:
        return "action_show_nominees"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        rows = Repo.selectNominees()

        dispatcher.utter_message(text=rows)

        return []


class ActionDeleteCandidate(Action):
    def name(self) -> Text:
        return "action_delete_candidate"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        value = tracker.latest_message["entities"][0]["value"]

        isDeleted = Repo.delete(value)

        if isDeleted == False:
            dispatcher.utter_message(text="No records found")
        else:
            dispatcher.utter_message(text="Deleted successfully")

        return []


class ActionRenameColumn(Action):
    def name(self) -> Text:
        return "action_rename_column"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # try:
        name = tracker.latest_message["entities"][0]["value"]
        new_name = tracker.latest_message["entities"][1]["value"]
        table = Repo.rename_column(name, new_name)
        dispatcher.utter_message(text=f"Renamed column {name} with {new_name}\n{table}")
        # except:
        #     dispatcher.utter_message(text="Unable to rename column")

        return []


class ActionRemoveColumn(Action):
    def name(self) -> Text:
        return "action_remove_column"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        try:
            name = tracker.latest_message["entities"][0]["value"]
            table = Repo.remove_column(name)
            dispatcher.utter_message(text=f"Removed column {name}\n{table}")
        except:
            dispatcher.utter_message(text="Could not remove column")

        return []


class ActionAddNominees(Action):
    def name(self) -> Text:
        return "action_add_nominees"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        nominees = tracker.get_slot("nominees")

        for nominee in nominees:
            Repo.insertNominee(nominee, tracker.get_slot("justification"))

        dispatcher.utter_message(text="Nominees added successfully")

        return []


class ValidateRestaurantForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_nominate_ops_form"

    def validate_nominees(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate nominees array"""

        nominees = []

        print(slot_value)

        if len(slot_value) == 0:
            dispatcher.utter_message(text="Could not identify name")
            return {
                "nominees": None,
            }

        for nominee in slot_value:
            if Repo.exists(nominee) == False:
                return {
                    "nominees": None,
                }

        return {
            "nominees": slot_value,
        }

    def validate_justification(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate justification"""

        if len(slot_value) > 3:
            return {
                "justification": slot_value,
            }

        dispatcher.utter_message(text="Justification cannot be too short")
        return {
            "justification": None,
        }

