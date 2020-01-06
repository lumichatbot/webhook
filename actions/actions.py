""" Network Wizard Webhook actions """

import requests
import traceback

from nile import interpreter
from contradictions import inspector
from utils import config
from database import client

from .parser import parse_intent, parse_feedback
from .api import Dialogflow
from .response import make_card_response, make_simple_response
from .beautifier import beautify, beautify_intent


# TODO: remove this to make service stateless, always fetching feedback from session
training_feedback = {}


def build_nile_intent(request):
    """ Webhook action to build Nile intent from Dialogflow request """

    uuid = request.get("session").split('/')[-1]
    text = request.get("queryResult").get("queryText")
    entities = parse_intent(request)
    response = {}
    try:
        intent = interpreter.translate(entities)

        speech = "Is this what you want?"

        global training_feedback
        training_feedback[uuid] = {}
        training_feedback[uuid]["original_intent"] = text
        training_feedback[uuid]["nile_intent"] = intent
        training_feedback[uuid]["entities"] = entities
        training_feedback[uuid]["missing_entities"] = {}

        response = make_card_response("Nile Intent", intent, speech, beautify_intent(intent))

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
    global training_feedback

    uuid = request.get("session").split('/')[-1]
    original_intent = training_feedback[uuid]['original_intent']
    nile_intent = training_feedback[uuid]['nile_intent']
    entities = training_feedback[uuid]["entities"]

    # tracking
    db = client.Database()
    db.insert_confirmed_intent(uuid, original_intent, entities, nile_intent)

    contradiction = inspector.check(nile_intent)
    if contradiction:
        text = "The intent you described probably contradictions a previous one. Do you want to deploy it anyway or remove the old one?"
        return make_card_response("Possible contradiction", text, text, beautify_intent(contradiction))

    # deploy
    # res = requests.post(config.DEPLOY_URL, {"intent": nile_intent})
    # if res.status['code'] == 200:
    #     return make_simple_response("Okay! Intent compiled and deployed!")

    return make_simple_response("Sorry. Something went wrong during deployment. :(")


def build_feedback(request):
    """ Webhook action to receive feedback from user after rejecting built intent """
    global training_feedback

    uuid = request.get("session").split('/')[-1]
    feedback = parse_feedback(request)
    for entity, values in feedback.items():
        if entity not in training_feedback["entities"]:
            training_feedback[uuid]["missing_entities"][entity] = {}
        for value in values.keys():
            training_feedback[uuid]["missing_entities"][entity][value] = True

    print("training feedback", uuid, training_feedback[uuid])
    return make_simple_response("Okay! And is there anything else I missed?")


def feedback_confirm(request):
    """ Webhook action to confirm feedback received from the user """
    global training_feedback

    uuid = request.get("session").split('/')[-1]
    words_to_highlight = []
    response_text = "In the phrase '<b>{}</b>', the words:  <br>&nbsp;&nbsp;&nbsp;&nbsp;".format(
        training_feedback[uuid]['original_intent'])

    for entity, values in training_feedback[uuid]["missing_entities"].items():
        response_text += ", and ".join(value for value in values.keys())
        response_text += "  <br>must be considered {}(s);".format(entity)
        words_to_highlight = values.keys()
        print('words', words_to_highlight)

    response_text += "  <br>Is that right?"

    response = make_card_response("Feedback confirmation", response_text, "Can you confirm your feedback then?",
                                  beautify(response_text, words_to_highlight))
    return response


def feedback_train(request):
    """ Webhook action to train chatbot with feedback information """
    global training_feedback

    uuid = request.get("session").split('/')[-1]
    dialogflow = Dialogflow()
    for entity, values in training_feedback[uuid]["missing_entities"].items():
        try:
            entity_type_id = dialogflow.get_entity_type_id(entity)
            print("entity_type_id", entity_type_id)
            for value in values.keys():
                dialogflow.create_entity(entity_type_id, value, [])
        except:
            traceback.print_exc()
    #dialogflow.update_intent("build", [feedback['original_intent']])

    response = make_simple_response("Okay! Feedback received. Please start over.")
    return response


def error(request):
    """ Webhook action to generate an error response in case of execption """
    return make_simple_response("Sorry, something went wrong. Please try again.")


ACTIONS = {
    "build.nile": build_nile_intent,
    "build.build-accepted": build_accepted,
    "build.build-rejected.feedback": build_feedback,
    "build.build-rejected.feedback.confirm": feedback_confirm,
    "build.build-rejected.feedback.train": feedback_train,
    "error": error,
}
