""" Nile intent builder """

from .exceptions import MissingTargetError, MissingOperationError


def slot_filling(entities):
    """ Given extracted entities, fills missing slots with some assumptions  """

    if "origin" in entities and "destination" not in entities:
        if "targets" not in entities:
            entities["targets"] = [entities["origin"]]

    if "origin" not in entities and "destination" in entities:
        if "targets" not in entities:
            entities["targets"] = [entities["destination"]]

    if "origin" not in entities and "destination" not in entities:
        if "targets" not in entities:
            entities["targets"] = [{"location": "network"}]

    if "operations" not in entities:
        entities["operations"] = []
        if "qos" in entities:
            entities["operations"].append("set")

        if "middleboxes" in entities:
            entities["operations"].append("add")

        if "services" in entities or "traffics" in entities or "protocols" in entities:
            entities["operations"].append("allow")

    return entities


def build(entities):
    """ Build extracted entities into a Nile intent """
    print("ENTITIES", entities)

    entities = slot_filling(entities)

    intent = "define intent {}Intent:".format(entities["id"])

    if "origin" in entities and "destination" in entities:
        if isinstance(entities["origin"], str):
            intent += " from endpoint('{}')".format(entities["origin"])
        if isinstance(entities["destination"], str):
            intent += " to endpoint('{}')".format(entities["destination"])

        if "location" in entities["origin"]:
            intent += "from endpoint('{}')".format(entities["origin"]["location"])

        if "location" in entities["destination"]:
            intent += "to endpoint('{}')".format(entities["destination"]["location"])

    if "targets" in entities:
        intent += " for"

        for target in entities["targets"]:
            if isinstance(target, str) and target not in intent:
                intent += " endpoint('{}'),".format(target)
            elif "service" in target and target["service"] not in intent:
                intent += " service('{}'),".format(target["service"])
            elif "protocol" in target and target["protocol"] not in intent:
                intent += " protocol('{}'),".format(target["protocol"])
            elif "traffic" in target and target["traffic"] not in intent:
                intent += " traffic('{}'),".format(target["traffic"])
            elif "location" in target and target["location"] not in intent:
                intent += " endpoint('{}'),".format(target["location"])
            elif "group" in target and target["group"] not in intent:
                intent += " group('{}'),".format(target["group"])

        intent = intent.rstrip(',')

    for operation in entities["operations"]:
        if operation == "add" or operation == "remove":
            intent += " {}".format(operation)

            if "middleboxes" in entities:
                for middlebox in entities["middleboxes"]:
                    if middlebox not in intent:
                        intent += " middlebox('{}'),".format(middlebox)
                intent = intent.rstrip(',')

            # if no parameters for the action were given, we remove the action
            intent = intent.rstrip(operation)

        if operation == "allow" or operation == "block":
            intent += " {}".format(operation)

            if "services" in entities:
                for service in entities["services"]:
                    if service not in intent:
                        intent += " service('{}'),".format(service)
                intent = intent.rstrip(',')

            if "traffics" in entities:
                for traffic in entities["traffics"]:
                    if traffic not in intent:
                        intent += " traffic('{}'),".format(traffic)
                intent = intent.rstrip(',')

            if "protocols" in entities:
                for protocol in entities["protocols"]:
                    if protocol not in intent:
                        intent += " protocol('{}'),".format(protocol)
                intent = intent.rstrip(',')

            # if no parameters for the action were given, we remove the action
            intent = intent.rstrip(operation)

        if operation == "set" or operation == "unset":
            intent += " {}".format(operation)

            if "qos" in entities:
                for metric in entities["qos"]:
                    if "name" in metric and "value" in metric and "unit" in metric:
                        if 'constraint' in metric and metric['constraint']:
                            intent += " {}('{}', '{}', '{}'),".format(metric["name"],
                                                                      metric["constraint"], metric["value"], metric["unit"])
                        else:
                            intent += " {}('{}', '{}'),".format(metric["name"], metric["value"], metric["unit"])

                intent = intent.rstrip(',')

            # if no parameters for the action were given, we remove the action
            intent = intent.rstrip(operation)

    if "start" in entities and "end" in entities:
        intent += " start hour('{}') end hour('{}')".format(entities["start"], entities["end"])

    return intent
