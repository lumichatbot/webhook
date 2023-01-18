""" Dialogflow Webhook API server for Lumi """

from __future__ import print_function

import json
import traceback
import requests

from flask import Flask, make_response, request
from flask_cors import CORS
from future.standard_library import install_aliases

from google.protobuf.text_format import MessageToString
from google.protobuf.json_format import MessageToJson

from src.actions import api
from src.actions.actions import ACTIONS
from src.database import client
from src.utils import timer
from src.study import tasks

install_aliases()

# Flask app should start in global layout
app = Flask(__name__)
CORS(app)
# keep alive for herokuapp
timer.set_interval(
    lambda: print(requests.get("https://lumi-webhook.herokuapp.com")), 300
)


@app.route("/", methods=["GET"])
def home():
    """Blank page to check if APIs are running"""
    return "Lumi Webhook APIs"


@app.route("/finish/<session>", methods=["GET"])
def finish(session):
    """
    API to finish session and record end timestamp
    """
    print("Session: {}".format(session))
    try:
        db = client.Database()
        res = db.finish_session(session)
        if res:
            res = "Session {} finished and recorded.".format(session)
        else:
            res = "Session {} does not exist or was already finished.".format(session)
    except Exception as err:
        traceback.print_exc()
        res = "{}".format(err)

    print("Response: {}".format(res))
    return make_response(res)


@app.route("/check/<session>/<task>", methods=["GET"])
def check(session, task):
    """
    API to check if user has completed give task
    """
    print("Session: {} , Task: {}".format(session, task))
    try:
        res = tasks.check(session, int(task))
    except Exception as err:
        traceback.print_exc()
        res = "{}".format(err)

    print("Response: {}".format(res))
    return make_response(json.dumps(res))


@app.route("/webhook", methods=["POST"])
def webhook():
    """Dialogflow Webhook API"""
    req = request.get_json(silent=True, force=True)

    print("Request: {}".format(json.dumps(req, indent=4)))
    try:
        res = ACTIONS[req.get("queryResult").get("action")](req)
    except Exception:
        traceback.print_exc()
        res = ACTIONS["error"](req)

    res = json.dumps(res, indent=4)
    print("Response: {}".format(json.dumps(res, indent=4)))

    response = make_response(res)
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/agent", methods=["GET"])
def agent():
    """Returns Dialogflow Agent information"""
    agent = api.Dialogflow().get_agent()
    response = make_response(MessageToJson(agent))
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/gateway", methods=["POST"])
def gateway():
    """
    Gateway for Dialogflow API
    request = {
        session: <uuid>,
        live: <true/false>,
        queryInput: {
            text: {
                text: <text>,
                languageCode: 'en'
            }
        }
    }
    """
    req = request.get_json(silent=True, force=True)

    # print("Request: {}".format(json.dumps(req, indent=4)))
    try:
        dialogflow = api.Dialogflow()
        session = req.get("session")
        live = req.get("live")
        text = req.get("queryInput").get("text").get("text")

        res = dialogflow.detect_intent(text, session)

        # tracking
        db = client.Database()
        db.insert_session(session, live)

        query_result_text = res.query_result.fulfillment_text
        if res.query_result.fulfillment_messages:
            query_result_text = ", ".join(
                [MessageToString(x.text) for x in res.query_result.fulfillment_messages]
            )

        db.insert_message(
            session, text, query_result_text, res.query_result.intent.display_name
        )
    except Exception as err:
        traceback.print_exc()
        res = "{}".format(err)

    res = MessageToJson(res)
    # print("Response: {}".format(json.dumps(res, indent=4)))

    response = make_response(res)
    response.headers["Content-Type"] = "application/json"
    return response


def init():
    """Initialize Flask server"""
    print("Starting app on port %d" % 9000)
    app.run(debug=True, port=9000, host="0.0.0.0")


if __name__ == "__main__":
    init()
