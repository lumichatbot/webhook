""" Nile interpreter """


def check_syntax(entities):
    """
        Check if entities extracted have the minimum syntax requirements to build a Nile intent.
        Returns any error encoutered.
    """
    if "destination" not in entities:
        if "group" not in entities and "targets" not in entities:
            return "The intent needs a clear target."

    return None


def translate(entities):
    """ Translates extracted entities into a Nile intent """

    print(entities)

    error = check_syntax(entities)
    if error:
        raise ValueError(error)

    intent = "define intent {}Intent:".format(entities["id"])

    if "origin" in entities and "destination" in entities:
        if isinstance(entities["origin"], str):
            intent += " from endpoint('{}')".format(entities["origin"])
        if isinstance(entities["destination"], str):
            intent += " to endpoint('{}')".format(entities["destination"])

        if "service" in entities["origin"]:
            intent += "from service('{}')".format(entities["origin"]["service"])
        elif "location" in entities["origin"]:
            intent += "from endpoint('{}')".format(entities["origin"]["location"])

        if "service" in entities["destination"]:
            intent += "to service('{}')".format(entities["destination"]["service"])
        elif "location" in entities["destination"]:
            intent += "to endpoint('{}')".format(entities["destination"]["location"])
    # elif ("origin" in entities and "destination" not in entities) or ("origin" not in entities and "destination" in entities):
    #     raise ValueError("Origin cannot be used without destination, and vice-versa.")
    # ask for missing info

    if "group" in entities:
        intent += " for group('{}')".format(entities['group'])

    if "middleboxes" in entities:
        if "operation" in entities and ('add' in entities["operation"] or 'remove' in entities["operation"]):
            intent += " {}".format(next((x for x in entities["operation"] if x == 'add' or x == 'remove'), "add"))
        else:
            intent += " add"
        for middlebox in entities["middleboxes"]:
            intent += " middlebox('{}'),".format(middlebox)
        intent = intent.rstrip(',')

    if "qos" in entities:
        if "operation" in entities and ('set' in entities["operation"] or 'unset' in entities['operation']):
            intent += " {}".format(next((x for x in entities["operation"] if x == 'set' or x == 'unset'), "add"))
        else:
            intent += " set"
        for metric in entities["qos"]:
            if "name" in metric and ("constraint" in metric and "value" in metric and "unit" in metric):
                if metric['constraint']:
                    intent += " {}('{}', '{}', '{}'),".format(metric['name'],
                                                              metric['constraint'], metric['value'], metric['unit'])
                else:
                    intent += " {}('{}', '{}'),".format(metric['name'], metric['value'], metric['unit'])
            elif "name" in metric and "value" in metric and metric['value'] == 'none':
                intent += " {}('{}'),".format(metric['name'], metric['value'])
            # else:
            #     raise ValueError("Missing qos metric parameters.")
            # ask for missing info
        intent = intent.rstrip(',')

    if "targets" in entities:
        if "operation" in entities and ('allow' in entities["operation"] or 'block' in entities['operation']):
            intent += " {}".format(next((x for x in entities["operation"] if x == 'allow' or x == 'block'), "add"))
        else:
            intent += " for"

        for target in entities["targets"]:
            if isinstance(target, str):
                intent += " service('{}'),".format(target)
            elif "service" in target:
                intent += " service('{}'),".format(target['service'])
            elif "protocol" in target:
                intent += " protocol('{}'),".format(target['protocol'])
            elif "traffic" in target:
                intent += " traffic('{}'),".format(target['traffic'])
            elif "location" in target:
                intent += " endpoint('{}'),".format(target['location'])

        intent = intent.rstrip(',')

    # elif ("start" in entities and "end" not in entities) or ("start" not in entities and "end" in entities):
    #     raise ValueError("Start cannot be used without end, and vice-versa.")
    # ask for missing info
    if "start" in entities and "end" in entities:
        intent += " start hour('{}:{}') end hour('{}:{}')".format(entities["start"].hour, entities["start"].minute,
                                                                  entities["end"].hour, entities["end"].minute)
    # elif ("start" in entities and "end" not in entities) or ("start" not in entities and "end" in entities):
    #     raise ValueError("Start cannot be used without end, and vice-versa.")
    # ask for missing info

    return intent
