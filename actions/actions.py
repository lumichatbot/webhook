""" Network Wizard Webhook actions """
# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# import requests
import traceback
import json

from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# from utils import config
from database import client
from nile import builder, compiler


from .parser import parse_feedback
from .response import make_card_response, make_simple_response, reset_output_context
from .beautifier import beautify_intent

import datetime as dt


class ActionHelloWorld(Action):
    def name(self) -> Text:
        return "action_show_time"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print("TRACKER", json.dumps(tracker, indent=4, sort_keys=True))
        dispatcher.utter_message(text=f"{dt.datetime.now()}")

        return []


class ActionBuild(Action):
    def name(self) -> Text:
        return "action_build"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Webhook action to build Nile intent from Dialogflow request"""
        print("TRACKER", json.dumps(tracker, indent=4, sort_keys=True))

        uuid = ""  # request.get("session").split("/")[-1]
        text = ""  # request.get("queryResult").get("queryText")

        response = {}
        try:
            entities = tracker.latest_message["entities"]
            print("ENTITIES", json.dumps(entities, indent=4, sort_keys=True))

            for entity in entities:
                print(
                    "Entity: {},  Value: {}, Start: {}, End: {}".format(
                        entity["entity"],
                        entity["value"],
                        entity["start"],
                        entity["end"],
                    )
                )

            intent = builder.build(entities)
            speech = "Is this what you want?"
            response = make_card_response(
                "Nile Intent",
                intent,
                speech,
                beautify_intent(intent),
                suggestions=["Yes", "No"],
            )

            # tracking
            db = client.Database()
            db.insert_intent(uuid, text, entities, intent)
        except ValueError as err:
            traceback.print_exc()
            # TODO: use slot-filling to get the missing info
            # TODO: use different exceptions to figure out whats missing
            response = make_simple_response("{}".format(err))

        dispatcher.utter_message(text="Under construction...")

        return response


class ActionDeploy(Action):
    def name(self) -> Text:
        return "action_deploy"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Webhook action to deploy Nile intent after user confirmation"""
        uuid = ""  # request.get("session").split("/")[-1]

        db = client.Database()
        intent = db.get_latest_intent(uuid)
        db.update_intent(intent["_id"], {"status": "confirmed"})

        merlin_program, _ = compiler.compile(intent["nile"])
        if merlin_program:
            db.update_intent(
                intent["_id"], {"status": "compiled", "merlin": merlin_program}
            )
            return make_simple_response("Okay! Intent compiled and deployed!")

        # TODO: fix deploy API after user study
        # res = requests.post(config.DEPLOY_URL, {"intent": intent["nile"]})
        # if res.status["code"] == 200:
        #     return make_simple_response("Okay! Intent compiled and deployed!")
        #     db.update_intent(intent["_id"], {"status": "deployed"})

        return make_simple_response("Sorry. Something went wrong during deployment. :(")


class ActionFeedback(Action):
    def name(self) -> Text:
        return "action_feedback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Webhook action to receive feedback from user after rejecting built intent"""
        uuid = ""  # request.get("session").split("/")[-1]
        db = client.Database()
        intent = db.get_latest_intent(uuid)

        feedback = parse_feedback(tracker)
        entity_types = ["Location", "Group", "Middlebox", "Service", "Traffic"]

        query = tracker["queryResult"]["queryText"].lower()
        if "cancel" in query or "start over" in query:
            response = make_simple_response("Okay, cancelled. Please start over.")
            return reset_output_context(tracker, response)

            # slot-filling
        if "entity" not in feedback and "value" not in feedback:
            return make_simple_response(
                "First of all, what entity did I miss?", suggestions=entity_types
            )
        elif "entity" not in feedback:
            return make_simple_response(
                "What type of entity is '{}'?".format(feedback["value"]),
                suggestions=entity_types,
            )
        elif "value" not in feedback:
            suggestions = []
            for word in intent["text"].split():
                entities = intent["entities"].values()
                if word not in entities:
                    suggestions.append(word)
            return make_simple_response(
                "Great! And what word is a {}?".format(feedback["entity"]),
                suggestions=suggestions,
            )

        missing_entities = {}
        if "missingEntities" in intent:
            missing_entities = intent["missingEntities"]

        if feedback["entity"] not in missing_entities:
            missing_entities[feedback["entity"]] = {}
        missing_entities[feedback["entity"]][feedback["value"]] = True

        db.update_intent(
            intent["_id"], {"status": "declined", "missingEntities": missing_entities}
        )

        dispatcher.utter_message(text="Under construction...")
        print("training feedback", uuid, intent)
        return make_simple_response(
            "Okay! And is there anything else I missed?", suggestions=["Yes", "No"]
        )


class ActionFeedbackConfirm(Action):
    def name(self) -> Text:
        return "action_feedback_confirm"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Webhook action to confirm feedback received from the user"""
        extracted_entities = tracker.latest_message["entities"]
        print("ENTITIES", json.dumps(extracted_entities, indent=4, sort_keys=True))

        dispatcher.utter_message(text="Under construction...")

        uuid = ""  # request.get("session").split("/")[-1]
        db = client.Database()
        intent = db.get_latest_intent(uuid)

        print("INTENT CONFIRM", intent)
        entities = intent["entities"]
        for entity, values in intent["missingEntities"].items():
            entity_key = entity
            if entity == "middlebox":
                entity_key = "middleboxes"
            elif entity == "service":
                entity_key = "services"
            elif entity == "traffic":
                entity_key = "traffics"
            elif entity == "protocol":
                entity_key = "protocols"
            elif entity == "operation":
                entity_key = "operations"
            elif entity == "location":
                entity_key = "locations"

            if entity_key not in entities:
                entities[entity_key] = list(values.keys())
            else:
                entities[entity_key] += list(values.keys())

        try:
            nile = builder.build(entities)
            speech = "So, is this what you want then?"
            response = make_card_response(
                "Nile Intent",
                nile,
                speech,
                beautify_intent(nile),
                suggestions=["Yes", "No"],
            )

            # tracking
            db.update_intent(intent["_id"], {"status": "pending", "nileFeedback": nile})
        except ValueError as err:
            traceback.print_exc()
            # TODO: use slot-filling to get the missing info
            # TODO: use different exceptions to figure out whats missing
            response = make_simple_response("{}".format(err))

        return response
