""" Auxiliary functions """


def make_card_response(title, text, speech, formatted_text):
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
                                "formattedText": formatted_text
                            }
                        }
                    ]
                }
            }
        }
    }

    return response


def make_simple_response(text):
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
                    ]
                }
            }
        }
    }

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
