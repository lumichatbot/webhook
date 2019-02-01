""" Dataset generator sampler """


from random import sample, randint, randrange, choice

from datetime import datetime, timedelta

from manager import topology

from config import (DATASET_ACTIONS_MBS,
                    DATASET_ACTIONS_ACL,
                    DATASET_ACTIONS_QOS,
                    DATASET_GROUPS,
                    DATASET_SYNONYMS,
                    DATASET_MIDDLEBOXES,
                    DATASET_SERVICES,
                    DATASET_TRAFFIC,
                    DATASET_PROTOCOLS,
                    DATASET_QOS_METRICS,
                    DATASET_QOS_CONSTRAINTS,
                    DATASET_SERVICE_ASSOCIATIONS,
                    DATASET_TRAFFIC_ASSOCIATIONS)


def timerange_overlap(sentence_entities, hypothesis_entities):
    """ checks if two time ranges overlap """
    return sentence_entities['start'] <= hypothesis_entities['end'] and sentence_entities['end'] >= hypothesis_entities['start']


def target_match(sentence_target, hypothesis_target, sentece_action, hypothesis_action):
    """ given two targets, return True if they match and False if not """

    # direct matching
    if 'traffic' in sentence_target and 'traffic' in hypothesis_target and sentence_target['traffic'] == hypothesis_target['traffic']:
        return True

    if 'service' in sentence_target and 'service' in hypothesis_target and sentence_target['service'] == hypothesis_target['service']:
        return True

    if 'protocol' in sentence_target and 'protocol' in hypothesis_target and sentence_target['protocol'] == hypothesis_target['protocol']:
        return True

    # hierarchy
    if 'traffic' in sentence_target:
        # higher level, no problem
        if 'service' in hypothesis_target and sentece_action == 'block' and hypothesis_action == 'allow':
            return next((True for x in DATASET_TRAFFIC_ASSOCIATIONS[sentence_target['traffic']]['service'] if x == hypothesis_target['service']), False)

        if 'protocol' in hypothesis_target and sentece_action == 'allow' and hypothesis_action == 'block':
            return next((True for x in DATASET_TRAFFIC_ASSOCIATIONS[sentence_target['traffic']]['protocol'] if x == hypothesis_target['protocol']), False)
    elif 'service' in sentence_target and sentece_action == 'allow' and hypothesis_action == 'block':
        # since protocol is the highet level, it will only be a problem if the sentence action is to allow and the hypothesis to block
        if 'protocol' in hypothesis_target:
            return next((True for x in DATASET_SERVICE_ASSOCIATIONS[sentence_target['service']]['protocol'] if x == hypothesis_target['protocol']), False)
        if 'traffic' in hypothesis_target:
            return next((True for x in DATASET_SERVICE_ASSOCIATIONS[sentence_target['service']]['traffic'] if x == hypothesis_target['traffic']), False)
    elif 'protocol' in sentence_target and sentece_action == 'block' and hypothesis_action == 'allow':
        # since protocol is the lowest level, it will only be a problem if the sentence action is to block and the hypothesis to allow
        if 'service' in hypothesis_target:
            return next((True for x in DATASET_SERVICE_ASSOCIATIONS[hypothesis_target['service']]['protocol'] if x == sentence_target['protocol']), False)
        if 'traffic' in hypothesis_target:
            return next((True for x in DATASET_TRAFFIC_ASSOCIATIONS[hypothesis_target['traffic']]['protocol'] if x == sentence_target['protocol']), False)
    else:
        return False


def is_bandwidth_available(source, target, bandwidth, constraint):
    """ checks if given bandwidth is available in given path """
    path_capacity = topology.get_path_capacity(source, target)
    return path_capacity >= bandwidth if constraint == 'min' else bandwidth >= path_capacity


def fetch_group_path(group):
    """ given a group, finds the path in the Network that corresponds to it """
    # check synonym
    group_key = group if group in DATASET_SYNONYMS else next((key for (key, synonyms) in DATASET_SYNONYMS.items() if group in synonyms), group)

    return topology.get_node_tree().id, topology.get_group_ip(group_key)


def qos_path_embedding(sentence_entities, hypothesis_entities):
    """ checks if given qos constraints can be embedded in the given pathes """
    if 'group' in sentence_entities:
        stn_origin, stn_destination = fetch_group_path(sentence_entities['group'])
    else:
        stn_origin, stn_destination = sentence_entities['origin'], sentence_entities['destination']

    if 'group' in hypothesis_entities:
        hyp_origin, hyp_destination = fetch_group_path(hypothesis_entities['group'])
    else:
        hyp_origin, hyp_destination = hypothesis_entities['origin'], hypothesis_entities['destination']

    sentence_path = (stn_origin, stn_destination)
    hypothesis_path = (hyp_origin, hyp_destination)

    sentence_action = sentence_entities['actions'][0]
    hypothesis_action = hypothesis_entities['actions'][0]
    sentence_qos = sentence_entities['qos'][0]
    hypothesis_qos = hypothesis_entities['qos'][0]

    if sentence_action == 'set' and hypothesis_action == 'set':
        if sentence_qos['name'] == 'bandwidth' and hypothesis_qos['name'] == 'bandwidth':
            # check individually
            if not is_bandwidth_available(sentence_path[0], sentence_path[1], sentence_qos['value'], sentence_qos['constraint']):
                return False

            if not is_bandwidth_available(hypothesis_path[0], hypothesis_path[1], hypothesis_qos['value'], hypothesis_qos['constraint']):
                return False

            # check combined
            if sentence_qos['constraint'] == hypothesis_qos['constraint']:
                common_path_src, common_path_tgt = topology.get_common_path(sentence_path, hypothesis_path)
                if not common_path_src or not common_path_tgt:
                    return True
                return is_bandwidth_available(common_path_src, common_path_tgt, sentence_qos['value'] + hypothesis_qos['value'], hypothesis_qos['constraint'])

            return ((sentence_qos['constraint'] == 'min' and sentence_qos['value'] < hypothesis_qos['value'])
                    or (sentence_qos['constraint'] == 'max' and sentence_qos['value'] > hypothesis_qos['value']))
        elif sentence_qos['name'] == 'quota' and hypothesis_qos['name'] == 'quota':
            return sentence_qos['value'] == hypothesis_qos['value']
        else:
            return True
    elif (sentence_action == 'set' and hypothesis_action) == 'unset' or (sentence_action == 'unset' and hypothesis_action == 'set'):
        if ((sentence_qos['name'] == 'bandwidth' and hypothesis_qos['name'] == 'bandwidth') or
                (sentence_qos['name'] == 'quota' and hypothesis_qos['name'] == 'quota')):
            return stn_destination != hyp_destination
        return True

    return True


def sample_path():
    """ sample origin and destination from topology """
    node_tree = topology.get_node_tree()
    core_switches = node_tree.children
    aggr_switches = choice(core_switches).children
    edge_switches = choice(aggr_switches).children
    hosts = choice(edge_switches).children

    origin = node_tree.id
    destination = choice(edge_switches + hosts).id

    return origin, destination


def sample_hierarchy():
    """ sample origin and destination from topology """
    node_tree = topology.get_node_tree()
    core_switches = node_tree.children
    aggr_switches = choice(core_switches).children
    edge_switches = choice(aggr_switches).children
    hosts = choice(edge_switches).children

    child = choice(hosts)
    parent = child.parent

    return parent.id, child.id


def sample_target():
    """ sample target from contants """
    target_type = randint(1, 4)
    if target_type == 1:
        target = {
            "service": choice(DATASET_SERVICES)
        }
    elif target_type == 2:
        target = {
            "traffic": choice(DATASET_TRAFFIC)
        }
    elif target_type == 3:
        target = {
            "protocol": choice(DATASET_PROTOCOLS)
        }
    else:
        target = {
            "service": choice(DATASET_SERVICES)
        }
    return target


def sample_group():
    """ sample group from topology """
    return choice(DATASET_GROUPS)


def sample_synonym(group):
    """ given a group, sample a synonym """
    return choice(DATASET_SYNONYMS[group])


def sample_time_range(span_s, span_e):
    """ sample a start and end timestamps """
    start = datetime.now() - timedelta(hours=span_s) - timedelta(minutes=randint(1, 120))
    end = datetime.now() + timedelta(hours=span_e) + timedelta(minutes=randint(1, 120))
    return start, end


def sample_qos():
    """ sample a qos metric, constraint and value """
    qos_metric = choice(DATASET_QOS_METRICS)
    qos_constraint = choice(DATASET_QOS_CONSTRAINTS)
    qos = {
        'name': qos_metric[0],
        'unit': qos_metric[1],
        'constraint': qos_constraint if qos_metric[0] == 'bandwidth' else "",
        'value': randrange(10, 100, 10) if qos_metric[0] == 'bandwidth' else randrange(1, 10, 1)
    }
    return qos


def sample_entailing_endpoints(sentence_entities, hypothesis_entities, mixed=False):
    """ samples target entities from topology for intent that cannot contradict each other """
    option = randint(0, 3)
    if option == 0 or mixed:
        sentence_entities['origin'], sentence_entities['destination'] = sample_path()
        group = sample_group()
        hypothesis_entities['group'] = group
        group_key = group if group in DATASET_SYNONYMS else next((key for (key, synonyms) in DATASET_SYNONYMS.items() if group in synonyms), group)
        group_destination = topology.get_group_ip(group_key)

        while sentence_entities['destination'].rsplit('.', 1)[0] == group_destination.rsplit('.', 1)[0]:
            sentence_entities['origin'], sentence_entities['destination'] = sample_path()
            group = sample_group()
            hypothesis_entities['group'] = group
            group_key = group if group in DATASET_SYNONYMS else next(
                (key for (key, synonyms) in DATASET_SYNONYMS.items() if group in synonyms), group)
            group_destination = topology.get_group_ip(group_key)
    elif option == 1:
        sentence_entities['origin'], sentence_entities['destination'] = sample_path()
        hypothesis_entities['origin'], hypothesis_entities['destination'] = sample_path()
        while sentence_entities['destination'].rsplit('.', 1)[0] == hypothesis_entities['destination'].rsplit('.', 1)[0]:
            sentence_entities['origin'], sentence_entities['destination'] = sample_path()
            hypothesis_entities['origin'], hypothesis_entities['destination'] = sample_path()
    else:
        sentence_entities['group'] = sample_group()
        hypothesis_entities['group'] = sample_group()
        while sentence_entities['group'] == hypothesis_entities['group']:
            sentence_entities['group'] = sample_group()
            hypothesis_entities['group'] = sample_group()

    return sentence_entities, hypothesis_entities


def sample_contradicting_endpoints(sentence_entities, hypothesis_entities, mixed=False):
    """ samples target entities from topology for intent that may contradict each other """
    option = randint(0, 3)
    if option == 0 or mixed:
        sentence_entities['origin'], sentence_entities['destination'] = sample_path()
        group = sample_group()
        hypothesis_entities['group'] = group
        group_key = group if group in DATASET_SYNONYMS else next((key for (key, synonyms) in DATASET_SYNONYMS.items() if group in synonyms), group)
        group_destination = topology.get_group_ip(group_key)

        while sentence_entities['destination'].rsplit('.', 1)[0] != group_destination.rsplit('.', 1)[0]:
            sentence_entities['origin'], sentence_entities['destination'] = sample_path()
            group = sample_group()
            hypothesis_entities['group'] = group
            group_key = group if group in DATASET_SYNONYMS else next(
                (key for (key, synonyms) in DATASET_SYNONYMS.items() if group in synonyms), group)
            group_destination = topology.get_group_ip(group_key)
    elif option == 1:
        sentence_entities['origin'], sentence_entities['destination'] = sample_path()
        hypothesis_entities['origin'], hypothesis_entities['destination'] = sample_path()
        while sentence_entities['destination'].rsplit('.', 1)[0] != hypothesis_entities['destination'].rsplit('.', 1)[0]:
            sentence_entities['origin'], sentence_entities['destination'] = sample_path()
            hypothesis_entities['origin'], hypothesis_entities['destination'] = sample_path()
    else:
        sentence_entities['group'] = sample_group()
        hypothesis_entities['group'] = sample_group()
        while sentence_entities['group'] != hypothesis_entities['group']:
            sentence_entities['group'] = sample_group()
            hypothesis_entities['group'] = sample_group()

    return sentence_entities, hypothesis_entities


def sample_hierarchical_endpoints(sentence_entities, hypothesis_entities):
    """ samples target entities from topology for intent that may contradict each other """

    origin = topology.get_node_tree().id
    stn_destination, hyp_destination = sample_hierarchy()
    sentence_entities['origin'], sentence_entities['destination'] = origin, stn_destination
    hypothesis_entities['origin'], hypothesis_entities['destination'] = origin, hyp_destination

    return sentence_entities, hypothesis_entities


def sample_synonyms_endpoints(sentence_entities, hypothesis_entities):
    """ samples target entities from topology for intent that may contradict each other """

    sentence_entities['group'] = sample_group()
    hypothesis_entities['group'] = sample_synonym(sentence_entities['group'])

    return sentence_entities, hypothesis_entities


def sample_entailing_chaining(sentence_entities, hypothesis_entities):
    """ return chaining commands that do not contradict each other """
    sentence_entities['actions'] = [choice(DATASET_ACTIONS_MBS)] + sentence_entities['actions']
    hypothesis_entities['actions'] = [choice(DATASET_ACTIONS_MBS)] + hypothesis_entities['actions']
    if sentence_entities['actions'][0] == hypothesis_entities['actions'][0]:
        sentence_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, len(DATASET_MIDDLEBOXES)))
        hypothesis_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, len(DATASET_MIDDLEBOXES)))
    else:
        sentence_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, len(DATASET_MIDDLEBOXES)))
        hypothesis_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, len(DATASET_MIDDLEBOXES)))
        while bool(set(sentence_entities['middleboxes']) & set(hypothesis_entities['middleboxes'])):
            sentence_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, len(DATASET_MIDDLEBOXES)))
            hypothesis_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, len(DATASET_MIDDLEBOXES)))

    return sentence_entities, hypothesis_entities


def sample_contradicting_chaining(sentence_entities, hypothesis_entities):
    """ return chaining commands that do not contradict each other """
    sentence_entities['actions'] = ["add"] + sentence_entities['actions']
    hypothesis_entities['actions'] = ["remove"] + hypothesis_entities['actions']
    sentence_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, len(DATASET_MIDDLEBOXES)))
    hypothesis_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, len(DATASET_MIDDLEBOXES)))
    while not bool(set(sentence_entities['middleboxes']) & set(hypothesis_entities['middleboxes'])):
        sentence_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, len(DATASET_MIDDLEBOXES)))
        hypothesis_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, len(DATASET_MIDDLEBOXES)))

    return sentence_entities, hypothesis_entities


def sample_entailing_rules(sentence_entities, hypothesis_entities):
    """ return chaining commands that do not contradict each other """
    if randint(0, 10) % 2 == 0:
        sentence_entities['actions'] = [choice(DATASET_ACTIONS_ACL)] + sentence_entities['actions']
        hypothesis_entities['actions'] = [choice(DATASET_ACTIONS_ACL)] + hypothesis_entities['actions']

        # allow - allow, block - block , any targets
        sentence_entities['targets'] = [dict(y) for y in set({tuple(x.items()) for x in [sample_target() for _ in range(1, 3)]})]
        hypothesis_entities['targets'] = [dict(y) for y in set({tuple(x.items()) for x in [sample_target() for _ in range(1, 3)]})]
        while (sentence_entities['actions'] != hypothesis_entities['actions'] and
               any(any(target_match(stn_target, hyp_target, 'allow', 'block') for stn_target in sentence_entities['targets']) for hyp_target in hypothesis_entities['targets'])):
            sentence_entities['targets'] = [dict(y) for y in set({tuple(x.items()) for x in [sample_target() for _ in range(1, 3)]})]
            hypothesis_entities['targets'] = [dict(y) for y in set({tuple(x.items()) for x in [sample_target() for _ in range(1, 3)]})]

    return sentence_entities, hypothesis_entities


def sample_contradicting_rules(sentence_entities, hypothesis_entities):
    """ return chaining commands that do not contradict each other """
    # allow - block, but different targets
    sentence_entities['actions'] = ['allow'] + sentence_entities['actions']
    hypothesis_entities['actions'] = ['block'] + hypothesis_entities['actions']
    sentence_entities['targets'] = [dict(y) for y in set({tuple(x.items()) for x in [sample_target() for _ in range(1, 3)]})]
    hypothesis_entities['targets'] = [dict(y) for y in set({tuple(x.items()) for x in [sample_target() for _ in range(1, 3)]})]
    while not any(any(target_match(stn_target, hyp_target, 'allow', 'block') for stn_target in sentence_entities['targets']) for hyp_target in hypothesis_entities['targets']):
        sentence_entities['targets'] = [dict(y) for y in set({tuple(x.items()) for x in [sample_target() for _ in range(1, 3)]})]
        hypothesis_entities['targets'] = [dict(y) for y in set({tuple(x.items()) for x in [sample_target() for _ in range(1, 3)]})]

    return sentence_entities, hypothesis_entities


def sample_entailing_timeranges(sentence_entities, hypothesis_entities):
    """ returns non contradicting timestamps """
    sentence_entities['start'], sentence_entities['end'] = sample_time_range(8, -5)
    hypothesis_entities['start'], hypothesis_entities['end'] = sample_time_range(2, 1)
    while timerange_overlap(sentence_entities, hypothesis_entities):
        sentence_entities['start'], sentence_entities['end'] = sample_time_range(8, -5)
        hypothesis_entities['start'], hypothesis_entities['end'] = sample_time_range(2, 1)

    return sentence_entities, hypothesis_entities


def sample_contradicting_timeranges(sentence_entities, hypothesis_entities):
    """ returns  contradicting timestamps """
    sentence_entities['start'], sentence_entities['end'] = sample_time_range(6, 1)
    hypothesis_entities['start'], hypothesis_entities['end'] = sample_time_range(6, 1)
    while not timerange_overlap(sentence_entities, hypothesis_entities):
        sentence_entities['start'], sentence_entities['end'] = sample_time_range(6, 1)
        hypothesis_entities['start'], hypothesis_entities['end'] = sample_time_range(6, 1)
    return sentence_entities, hypothesis_entities


def sample_entailing_qos(sentence_entities, hypothesis_entities, stn_action=None, hyp_action=None):
    """ samples qos metric, constraint and values that entail given a chosen path """
    if ('origin' not in sentence_entities or 'destination' not in sentence_entities) and 'group' not in sentence_entities:
        raise ValueError("origin and destination or group in sentence intent must be provided")

    if ('origin' not in hypothesis_entities or 'destination' not in hypothesis_entities) and 'group' not in hypothesis_entities:
        raise ValueError("origin and destination or group in hypothesis intent must be provided")

    sentence_entities['actions'] = [choice(DATASET_ACTIONS_QOS) if not stn_action else stn_action] + sentence_entities['actions']
    hypothesis_entities['actions'] = [choice(DATASET_ACTIONS_QOS) if not hyp_action else stn_action] + hypothesis_entities['actions']

    sentence_entities['qos'] = [sample_qos()]
    hypothesis_entities['qos'] = [sample_qos()]

    while not qos_path_embedding(sentence_entities, hypothesis_entities):
        sentence_entities['actions'] = [choice(DATASET_ACTIONS_QOS) if not stn_action else stn_action] + sentence_entities['actions']
        hypothesis_entities['actions'] = [choice(DATASET_ACTIONS_QOS) if not hyp_action else stn_action] + hypothesis_entities['actions']

        sentence_entities['qos'] = [sample_qos()]
        hypothesis_entities['qos'] = [sample_qos()]

    return sentence_entities, hypothesis_entities


def sample_contradicting_qos(sentence_entities, hypothesis_entities, stn_action=None, hyp_action=None):
    """ samples qos metric, constraint and values that contradict given a chosen path """
    if ('origin' not in sentence_entities or 'destination' not in sentence_entities) and 'group' not in sentence_entities:
        raise ValueError("origin and destination or group in sentence intent must be provided")

    if ('origin' not in hypothesis_entities or 'destination' not in hypothesis_entities) and 'group' not in hypothesis_entities:
        raise ValueError("origin and destination or group in hypothesis intent must be provided")

    sentence_entities['actions'] = [choice(DATASET_ACTIONS_QOS) if not stn_action else stn_action] + sentence_entities['actions']
    hypothesis_entities['actions'] = [choice(DATASET_ACTIONS_QOS) if not hyp_action else stn_action] + hypothesis_entities['actions']

    sentence_entities['qos'] = [sample_qos()]
    hypothesis_entities['qos'] = [sample_qos()]

    while qos_path_embedding(sentence_entities, hypothesis_entities):
        sentence_entities['actions'] = [choice(DATASET_ACTIONS_QOS) if not stn_action else stn_action] + sentence_entities['actions']
        hypothesis_entities['actions'] = [choice(DATASET_ACTIONS_QOS) if not hyp_action else stn_action] + hypothesis_entities['actions']

        sentence_entities['qos'] = [sample_qos()]
        hypothesis_entities['qos'] = [sample_qos()]

    return sentence_entities, hypothesis_entities
