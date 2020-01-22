""" Entities parser """


def to_camel_case(string):
    """ Converts string to camel case """
    output = ''.join(x for x in string.title() if x.isalnum())
    return output[0].lower() + output[1:]


def parse_output_context(request, context_name):
    """ Finds and returns a given output context """
    output_contexts = request["queryResult"]["outputContexts"]
    for context in output_contexts:
        if context_name in context["name"]:
            return context
    return None


def parse_entities(request):
    """ Parses extracted entities from Dialogflow build_intent request """

    result = request["queryResult"]
    entities = {}
    entities["id"] = result["intent"]["displayName"]

    parameters = result["parameters"]

    if "origin" in parameters and parameters["origin"]:
        entities["origin"] = parameters["origin"]
        if isinstance(entities["origin"], dict):
            entities["origin"] = next(iter(parameters["origin"].values()), "").strip()

    if "destination" in parameters and parameters["destination"]:
        entities["destination"] = parameters["destination"]
        if isinstance(entities["destination"], dict):
            entities["destination"] = next(iter(parameters["destination"].values()), "").strip()

    if "target" in parameters and parameters["target"]:
        entities["targets"] = parameters["target"]

    if "operation" in parameters and parameters["operation"]:
        entities["operations"] = parameters["operation"]
        if isinstance(entities["operations"], dict):
            entities["operations"] = next(iter(parameters["operation"].values()), "").strip()

    if "middlebox" in parameters and parameters["middlebox"]:
        entities["middleboxes"] = parameters["middlebox"]

    if "service" in parameters and parameters["service"]:
        entities["services"] = parameters["service"]

    if "traffic" in parameters and parameters["traffic"]:
        entities["traffics"] = parameters["traffic"]

    if "protocol" in parameters and parameters["protocol"]:
        entities["protocols"] = parameters["protocol"]

    if "qos_unit" in parameters:
        if "qos_metric" not in parameters or ("qos_metric" in parameters and not parameters["qos_metric"]):
            parameters["qos_metric"] = []
            for unit in parameters["qos_unit"]:
                if "ps" in unit:
                    parameters["qos_metric"].append("bandwidth")
                else:
                    parameters["qos_metric"].append("quota")

    if "qos_metric" in parameters and parameters["qos_metric"] and "qos_value" in parameters and parameters["qos_value"]:
        entities["qos"] = []
        for i, (metric, value) in enumerate(zip(parameters["qos_metric"], parameters["qos_value"])):
            qos_metric = {}
            qos_metric["name"] = to_camel_case(metric)
            qos_metric["value"] = value
            if isinstance(value, dict):
                qos_metric["value"] = value["number-integer"]

            if "qos_unit" in parameters and parameters["qos_unit"]:
                if i < len(parameters["qos_unit"]):
                    qos_metric["unit"] = parameters["qos_unit"][i]
                    if "ps" in qos_metric["unit"] and qos_metric["name"] != "bandwidth":
                        qos_metric["name"] = "bandwidth"
                    elif "ps" not in qos_metric["unit"]:
                        qos_metric["name"] = "quota"
            else:
                qos_metric["constraint"] = "mbps" if qos_metric["name"] == "bandwidth" else "gb/wk"

            if "qos_constraint" in parameters and parameters["qos_constraint"]:
                if i < len(parameters["qos_constraint"]):
                    constraint = parameters["qos_constraint"][i]
                    print("Contraint", constraint)
                    if qos_metric["name"] == "bandwidth":
                        if constraint == "max" or constraint == "min":
                            qos_metric["constraint"] = constraint
                        else:
                            qos_metric["constraint"] = "max"
                    elif qos_metric["name"] == "quota":
                        if constraint == "download" or constraint == "upload":
                            qos_metric["constraint"] = constraint
                        else:
                            qos_metric["constraint"] = "download"
            else:
                qos_metric["constraint"] = "max" if qos_metric["name"] == "bandwidth" else "download"

            entities["qos"].append(qos_metric)

    if "start" in parameters and parameters["start"]:
        entities["start"] = parameters["start"]
        if isinstance(entities["start"], dict):
            entities["start"] = next(iter(parameters["start"].values()), "").strip()

    if "end" in parameters and parameters["end"]:
        entities["end"] = parameters["end"]
        if isinstance(entities["end"], dict):
            entities["end"] = next(iter(parameters["end"].values()), "").strip()

    return entities


def parse_feedback(request):
    """ Parses entities from Dialogflow user_feedback request to train agent """

    result = request["queryResult"]
    parameters = result["parameters"]

    missing_entity = {}
    if "entity" in parameters and parameters["entity"]:
        missing_entity["entity"] = parameters["entity"]

    if "value" in parameters and parameters["value"]:
        missing_entity["value"] = parameters["value"]

    return missing_entity
