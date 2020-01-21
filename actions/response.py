""" Auxiliary functions """


def make_card_response(title, text, speech, formatted_text, suggestions=[]):
    """ Returns a response object with Basic Card """

    response = {
        "fulfillmentText": speech,
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [speech + " " + text]
                }
            }
        ],
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": speech
                            }
                        },
                        {
                            "basicCard": {
                                "title": title,
                                "image": {
                                    "url": "",
                                    "accessibilityText": ""
                                },
                                "formattedText": formatted_text
                            }
                        }
                    ],
                    "suggestions": [{"title": x} for x in suggestions]
                }
            }
        }
    }

    return response


def make_simple_response(text, suggestions=[]):
    """ Returns a response object with simple text """

    response = {
        "fulfillmentText": text,
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [text]
                }
            }
        ],
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": text
                            }
                        }
                    ],
                    "suggestions": [{"title": x} for x in suggestions]
                }
            }
        }
    }

    return response


def reset_output_context(request, response):
    """ Reset output context to the input response and returns it """

    response["outputContexts"] = []
    output_contexts = request["queryResult"]["outputContexts"]
    for out in output_contexts:
        out["lifespanCount"] = 0
        response["outputContexts"].append(out)

    return response


def add_output_context(response, session, output_context, output_params):
    """ Add output context to the input response and returns it """

    if response and output_params and output_context:
        response["outputContexts"] = [
            {
                "name": "{}/contexts/{}".format(session, output_context),
                "lifespanCount": 2,
                "parameters": {}
            }
        ]

        for (key, value) in output_params.items():
            response["outputContexts"][0]["parameters"][key] = value

    return response
