""" Dialogflow Webhook API server for Network Wizard """

from __future__ import print_function

import json
import os
import traceback

from flask import Flask, make_response, request
from future.standard_library import install_aliases

from actions import ACTIONS

install_aliases()

# Flask app should start in global layout
app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    """ Blank page to check if APIs are running """
    return "Lumi Webhook APIs"


@app.route("/webhook", methods=["POST"])
def webhook():
    """ Dialogflow Webhook API """
    req = request.get_json(silent=True, force=True)

    print("Request: {}".format(json.dumps(req, indent=4)))
    try:
        res = ACTIONS[req.get("queryResult").get("action")](req)
    except Exception as err:
        traceback.print_exc()
        res = ACTIONS['error'](req)

    res = json.dumps(res, indent=4)
    print("Response: {}".format(json.dumps(res, indent=4)))

    response = make_response(res)
    response.headers["Content-Type"] = "application/json"
    return response


def init():
    """ Initialize Flask server """
    port = int(os.getenv("PORT", 9000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host="0.0.0.0")


if __name__ == "__main__":
    init()
