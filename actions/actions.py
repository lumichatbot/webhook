""" Network Wizard Webhook actions """

import requests
import traceback

from nile import builder, compiler
from contradictions import inspector
from utils import config
from database import client

from .parser import parse_entities, parse_feedback
from .api import Dialogflow
from .response import make_card_response, make_simple_response
from .beautifier import beautify, beautify_intent


def build_nile_intent(request):
    """ Webhook action to build Nile intent from Dialogflow request """
    uuid = request.get("session").split("/")[-1]
    text = request.get("queryResult").get("queryText")

    response = {}
    try:
        entities = parse_entities(request)
        intent = builder.build(entities)
        speech = "Is this what you want?"
        response = make_card_response("Nile Intent", intent, speech, beautify_intent(intent),
                                      suggestions=["Yes", "No"])

        # tracking
        db = client.Database()
        db.insert_intent(uuid, text, entities, intent)
    except ValueError as err:
        traceback.print_exc()
        # TODO: use slot-filling to get the missing info
        # TODO: use different exceptions to figure out whats missing
        response = make_simple_response("{}".format(err))

    return response


def build_accepted(request):
    """ Webhook action to deploy Nile intent after user confirmation """
    uuid = request.get("session").split("/")[-1]

    db = client.Database()
    intent = db.get_latest_intent(uuid)
    db.update_intent(intent["_id"], {"status": "confirmed"})

    # TODO: fix contradiction after user study
    # contradiction = inspector.check(intent, uuid)
    # if contradiction:
    #     text = "The intent you described probably contradictions a previous one. Do you want to deploy it anyway or remove the old one?"
    #     return make_card_response("Possible contradiction", text, text, beautify_intent(contradiction["nile"]),
    #                               suggestions=["Deploy it anyway", "Remove old one and deploy new", "Keep old one"])

    merlin_program, compilation_time = compiler.compile(intent["nile"])
    if merlin_program:
        db.update_intent(intent["_id"], {"status": "compiled", "merlin": merlin_program})
        return make_simple_response("Okay! Intent compiled and deployed!")

    # TODO: fix deploy API after user study
    # res = requests.post(config.DEPLOY_URL, {"intent": intent["nile"]})
    # if res.status["code"] == 200:
    #     return make_simple_response("Okay! Intent compiled and deployed!")
    #     db.update_intent(intent["_id"], {"status": "deployed"})

    return make_simple_response("Sorry. Something went wrong during deployment. :(")


def build_feedback(request):
    """ Webhook action to receive feedback from user after rejecting built intent """
    uuid = request.get("session").split("/")[-1]
    db = client.Database()
    intent = db.get_latest_intent(uuid)
    print("INTENT", intent)

    feedback = parse_feedback(request)
    print("FEEDBACK", feedback)
    entity_types = ["Location", "Group", "Middlebox", "Service", "Traffic"]

    # slot-filling
    if "entity" not in feedback and "value" not in feedback:
        return make_simple_response("First of all, what entity did I miss?", suggestions=entity_types)
    elif "entity" not in feedback:
        return make_simple_response("What type of entity is '{}'?".format(feedback["value"]), suggestions=entity_types)
    elif "value" not in feedback:
        suggestions = []
        for word in intent['text'].split():
            entities = intent['entities'].values()
            if word not in entities:
                suggestions.append(word)
        return make_simple_response("Great! And what word is a {}?".format(feedback["entity"]), suggestions=suggestions)

    missing_entities = {}
    if "missingEntities" in intent:
        missing_entities = intent["missingEntities"]

    if feedback["entity"] not in missing_entities:
        missing_entities[feedback["entity"]] = {}
    missing_entities[feedback["entity"]][feedback["value"]] = True

    db.update_intent(intent["_id"], {"status": "declined", "missingEntities": missing_entities})

    print("training feedback", uuid, intent)
    return make_simple_response("Okay! And is there anything else I missed?", suggestions=["Yes", "No"])


def feedback_confirm(request):
    """ Webhook action to confirm feedback received from the user """

    uuid = request.get("session").split("/")[-1]
    db = client.Database()
    intent = db.get_latest_intent(uuid)

    print("INTENT CONFIRM", intent)
    entities = intent['entities']
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
            entities[entity_key].append(list(values.keys()))

    try:
        nile = builder.build(entities)
        speech = "So, is this what you want then?"
        response = make_card_response("Nile Intent", nile, speech, beautify_intent(nile),
                                      suggestions=["Yes", "No"])

        # tracking
        db.update_intent(intent["_id"], {"status": "pending", "nileFeedback": nile})
    except ValueError as err:
        traceback.print_exc()
        # TODO: use slot-filling to get the missing info
        # TODO: use different exceptions to figure out whats missing
        response = make_simple_response("{}".format(err))

    return response

    # words_to_highlight = []
    # response_text = "In the phrase '<b>{}</b>':".format(intent["text"])
    # for entity, values in intent["missingEntities"].items():
    #     response_text += "&nbsp;&nbsp;&nbsp;&nbsp;"
    #     response_text += ", and ".join(value for value in values.keys())
    #     response_text += "  <br>must be considered <b>{}</b>(s);<br>".format(entity)
    #     words_to_highlight = values.keys()
    # response_text += "  <br>Is that right?"
    # response = make_card_response("Feedback confirmation", response_text, "Can you confirm your feedback then?",
    #                               beautify(response_text, words_to_highlight),
    #                               suggestions=["Yes", "No"])
    # return response


def feedback_train(request):
    """ Webhook action to train chatbot with feedback information """
    uuid = request.get("session").split("/")[-1]
    db = client.Database()
    intent = db.get_latest_intent(uuid)

    dialogflow = Dialogflow()
    for entity, values in intent["missingEntities"].items():
        try:
            entity_type_id = dialogflow.get_entity_type_id(entity)
            for value in values.keys():
                dialogflow.create_entity(entity_type_id, value, [])
        except:
            traceback.print_exc()

    merlin_program, compilation_time = compiler.compile(intent["nileFeedback"])
    if merlin_program:
        db.update_intent(intent["_id"], {"status": "compiled", "merlin": merlin_program})
        return make_simple_response("Okay! Feedback received. Intent compiled and deployed!")

    return make_simple_response("Sorry. Something went wrong during deployment. :(")


def error(request):
    """ Webhook action to generate an error response in case of execption """
    return make_simple_response("Sorry, something went wrong. Please try again.")


ACTIONS = {
    "build.nile": build_nile_intent,
    "build.accepted": build_accepted,
    "build.rejected.feedback": build_feedback,
    "build.rejected.feedback.confirm": feedback_confirm,
    "build.rejected.feedback.train": feedback_train,
    "error": error,
}
