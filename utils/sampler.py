""" Dataset generator sampler """


from random import sample, randint, randrange, choice

from datetime import datetime, timedelta

from .topology import *
from .config import (DATASET_ACTIONS_MBS,
                     DATASET_ACTIONS_ACL,
                     DATASET_ACTIONS_QOS,
                     DATASET_GROUPS,
                     DATASET_SYNONYMS,
                     DATASET_MIDDLEBOXES,
                     DATASET_SERVICES,
                     DATASET_TRAFFIC,
                     DATASET_PROTOCOLS,
                     DATASET_QOS_METRICS,
                     DATASET_BW_CONSTRAINTS,
                     DATASET_QUOTA_CONSTRAINTS,
                     DATASET_SERVICE_ASSOCIATIONS,
                     DATASET_TRAFFIC_ASSOCIATIONS)


def timerange_overlap(sentence_entities, hypothesis_entities):
    """ checks if two time ranges overlap """
    stn_start = datetime.strptime(sentence_entities['start'], "%H:%M")
    stn_end = datetime.strptime(sentence_entities['end'], "%H:%M")

    if "start" in hypothesis_entities and "end" in hypothesis_entities:
        hyp_start = datetime.strptime(hypothesis_entities['start'], "%H:%M")
        hyp_end = datetime.strptime(hypothesis_entities['end'], "%H:%M")

        return stn_start <= hyp_end and stn_end >= hyp_start
    else:
        return True


def target_match(sentence_target, hypothesis_target, sentece_action, hypothesis_action):
    """ given two targets, return True if they match and False if not """

    # direct matching
    if 'traffics' in sentence_target and 'traffics' in hypothesis_target and sentence_target['traffics'] == hypothesis_target['traffics']:
        return True

    if 'services' in sentence_target and 'services' in hypothesis_target and sentence_target['services'] == hypothesis_target['services']:
        return True

    if 'protocols' in sentence_target and 'protocols' in hypothesis_target and sentence_target['protocols'] == hypothesis_target['protocols']:
        return True

    # hierarchy
    if 'traffics' in sentence_target:
        if 'services' in hypothesis_target:
            return next((True for x in DATASET_TRAFFIC_ASSOCIATIONS[sentence_target['traffics']]['services'] if x == hypothesis_target['services']), False)

        if 'protocols' in hypothesis_target:
            return next((True for x in DATASET_TRAFFIC_ASSOCIATIONS[sentence_target['traffics']]['protocols'] if x == hypothesis_target['protocols']), False)
    elif 'services' in sentence_target:
        if 'protocols' in hypothesis_target:
            return next((True for x in DATASET_SERVICE_ASSOCIATIONS[sentence_target['services']]['protocols'] if x == hypothesis_target['protocols']), False)
        if 'traffics' in hypothesis_target:
            return next((True for x in DATASET_SERVICE_ASSOCIATIONS[sentence_target['services']]['traffics'] if x == hypothesis_target['traffics']), False)
    elif 'protocols' in sentence_target:
        if 'services' in hypothesis_target:
            return next((True for x in DATASET_SERVICE_ASSOCIATIONS[hypothesis_target['services']]['protocols'] if x == sentence_target['protocols']), False)
        if 'traffics' in hypothesis_target:
            return next((True for x in DATASET_TRAFFIC_ASSOCIATIONS[hypothesis_target['traffics']]['protocols'] if x == sentence_target['protocols']), False)

    return False


def is_bandwidth_available(source, target, bandwidth, constraint):
    """ checks if given bandwidth is available in given path """
    path_capacity = get_path_capacity(source, target)
    return path_capacity >= bandwidth if constraint == 'min' else bandwidth >= path_capacity


def fetch_group_path(group):
    """ given a group, finds the path in the Network that corresponds to it """
    # check synonym
    group_key = group if group in DATASET_SYNONYMS else next(
        (key for (key, synonyms) in DATASET_SYNONYMS.items() if group in synonyms), group)

    return get_node_tree().id, get_ip_by_handle(group_key)


def qos_path_embedding(sentence_entities, hypothesis_entities, sentence_action, hypothesis_action, conflicting_endpoints):
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
                common_path_src, common_path_tgt = get_common_path(sentence_path, hypothesis_path)
                if not common_path_src or not common_path_tgt:
                    return True
                return is_bandwidth_available(common_path_src, common_path_tgt, sentence_qos['value'] + hypothesis_qos['value'], hypothesis_qos['constraint'])
            else:
                if conflicting_endpoints:
                    return ((sentence_qos['constraint'] == 'min' and sentence_qos['value'] < hypothesis_qos['value'])
                            or (sentence_qos['constraint'] == 'max' and sentence_qos['value'] > hypothesis_qos['value']))
                else:
                    return True
        elif sentence_qos['name'] == 'quota' and hypothesis_qos['name'] == 'quota':
            if conflicting_endpoints:
                if sentence_qos['constraint'] == 'any' or hypothesis_qos['constraint'] == 'any':
                    return sentence_qos['value'] == hypothesis_qos['value']
                elif sentence_qos['constraint'] == hypothesis_qos['constraint']:
                    return sentence_qos['value'] == hypothesis_qos['value']
                else:
                    return True
            else:
                return True
        else:
            return True
    elif sentence_action != hypothesis_action:
        if sentence_qos['name'] == hypothesis_qos['name']:
            return conflicting_endpoints
        return True
    return True


def sample_path():
    """ sample origin and destination from topology """

    node_tree = get_node_tree()
    core_switches = node_tree.children
    aggr_switches = choice(core_switches).children
    edge_switches = choice(aggr_switches).children
    hosts = choice(edge_switches).children

    origin = node_tree.id

    num_nodes = randint(1, 5)
    if num_nodes == 1:
        destination = origin
    elif num_nodes == 2:
        destination = choice(core_switches).id
    elif num_nodes == 3:
        destination = choice(aggr_switches).id
    elif num_nodes == 4:
        destination = choice(edge_switches).id
    else:
        destination = choice(hosts).id

    return origin, destination


def sample_hierarchy():
    """ sample origin and destination from topology """
    node_tree = get_node_tree()
    core_switches = node_tree.children
    aggr_switches = choice(core_switches).children
    edge_switches = choice(aggr_switches).children
    hosts = choice(edge_switches).children

    child = choice(hosts)
    parent = child.parent

    return parent.id, child.id


def sample_targets():
    """ sample target from contants """
    stn_target, hyp_target = {}, {}
    target_types = randint(1, 6)
    if target_types == 1:
        stn_target = {
            "services": choice(DATASET_SERVICES)
        }
        hyp_target = {
            "services": choice(DATASET_SERVICES)
        }
    elif target_types == 2:
        stn_target = {
            "traffics": choice(DATASET_TRAFFIC)
        }
        hyp_target = {
            "traffics": choice(DATASET_TRAFFIC)
        }
    elif target_types == 3:
        stn_target = {
            "protocols": choice(DATASET_PROTOCOLS)
        }
        hyp_target = {
            "protocols": choice(DATASET_PROTOCOLS)
        }
    elif target_types == 4:
        stn_target = {
            "services": choice(DATASET_SERVICES)
        }
        hyp_target = {
            "traffics": choice(DATASET_TRAFFIC)
        }
    elif target_types == 5:
        stn_target = {
            "services": choice(DATASET_SERVICES)
        }
        hyp_target = {
            "protocols": choice(DATASET_PROTOCOLS)
        }
    elif target_types == 6:
        stn_target = {
            "traffics": choice(DATASET_TRAFFIC)
        }
        hyp_target = {
            "protocols": choice(DATASET_PROTOCOLS)
        }
    else:
        stn_target = {
            "services": choice(DATASET_SERVICES)
        }
        hyp_target = {
            "services": choice(DATASET_SERVICES)
        }

    return stn_target, hyp_target


def sample_group():
    """ sample group from topology """
    group = choice(DATASET_GROUPS)

    while group == 'network':
        group = choice(DATASET_GROUPS)

    return group


def sample_synonym(group):
    """ given a group, sample a synonym """
    return choice(DATASET_SYNONYMS[group])


def sample_time_range(delta_start, delta_end):
    """ sample a start and end timestamps """
    start_hour = randint(8, 12) + delta_start
    end_hour = randint(13, 18) + delta_end
    while start_hour >= end_hour:
        start_hour = randint(8, 12) + delta_start
        end_hour = randint(13, 18) + delta_end

    start = "{:02d}:{:02d}".format(start_hour, randrange(0, 50, 10))
    end = "{:02d}:{:02d}".format(end_hour, randrange(0, 50, 10))
    return start, end


def sample_qos():
    """ sample a qos metric, constraint and value """
    qos_metric = choice(DATASET_QOS_METRICS)
    qos = {
        'name': qos_metric[0],
        'unit': qos_metric[1],
        'constraint': choice(DATASET_BW_CONSTRAINTS) if qos_metric[0] == 'bandwidth' else choice(DATASET_QUOTA_CONSTRAINTS),
        'value': randrange(10, 100, 10) if qos_metric[0] == 'bandwidth' else randrange(1, 10, 1)
    }
    return qos


def sample_endpoints(sentence_entities):
    option = randint(0, 2)
    if option == 1:
        sentence_entities['origin'], sentence_entities['destination'] = sample_path()
    else:
        sentence_entities['group'] = sample_group()


def sample_entailing_endpoints(sentence_entities, hypothesis_entities, mixed=False, groups=False):
    """ samples target entities from topology for intent that cannot contradict each other """
    option = randint(0, 3)
    if (option == 0 or mixed) and not groups:
        sentence_entities['origin'], sentence_entities['destination'] = sample_path()
        group = sample_group()
        hypothesis_entities['group'] = group
        group_key = group if group in DATASET_SYNONYMS else next(
            (key for (key, synonyms) in DATASET_SYNONYMS.items() if group in synonyms), group)
        group_destination = get_ip_by_handle(group_key)
        group_origin = get_node_tree().id

        common_path = get_common_path_list(
            (sentence_entities['origin'], sentence_entities['destination']),
            (group_origin, group_destination))
        descendent = is_descendent(sentence_entities['destination'], group_destination) or is_descendent(
            group_destination, sentence_entities['destination'])
        while len(common_path) > 2 or (sentence_entities['destination'] == group_destination) or descendent:
            sentence_entities['origin'], sentence_entities['destination'] = sample_path()
            group = sample_group()
            hypothesis_entities['group'] = group
            group_key = group if group in DATASET_SYNONYMS else next(
                (key for (key, synonyms) in DATASET_SYNONYMS.items() if group in synonyms), group)
            group_destination = get_ip_by_handle(group_key)
            group_origin = get_node_tree().id
            common_path = get_common_path_list(
                (sentence_entities['origin'], sentence_entities['destination']),
                (group_origin, group_destination))
            descendent = is_descendent(sentence_entities['destination'], group_destination) or is_descendent(
                group_destination, sentence_entities['destination'])

    elif option == 1 and not groups:
        sentence_entities['origin'], sentence_entities['destination'] = sample_path()
        hypothesis_entities['origin'], hypothesis_entities['destination'] = sample_path()
        common_path = get_common_path_list(
            (sentence_entities['origin'], sentence_entities['destination']),
            (hypothesis_entities['origin'], hypothesis_entities['destination']))
        descendent = is_descendent(sentence_entities['destination'], hypothesis_entities['destination']) or is_descendent(
            hypothesis_entities['destination'], sentence_entities['destination'])
        while len(common_path) > 2 or (sentence_entities['destination'] == hypothesis_entities['destination']) or descendent:
            sentence_entities['origin'], sentence_entities['destination'] = sample_path()
            hypothesis_entities['origin'], hypothesis_entities['destination'] = sample_path()
            common_path = get_common_path_list(
                (sentence_entities['origin'], sentence_entities['destination']),
                (hypothesis_entities['origin'], hypothesis_entities['destination']))
    else:
        sentence_entities['group'] = sample_group()
        hypothesis_entities['group'] = sample_group()
        descendent = is_descendent(sentence_entities['group'], hypothesis_entities['group']) or is_descendent(
            hypothesis_entities['group'], sentence_entities['group'])
        while sentence_entities['group'] == hypothesis_entities['group'] or descendent:
            sentence_entities['group'] = sample_group()
            hypothesis_entities['group'] = sample_group()

    return sentence_entities, hypothesis_entities


def sample_conflicting_endpoints(sentence_entities, hypothesis_entities, mixed=False, groups=False):
    """ samples target entities from topology for intent that may contradict each other """
    option = randint(0, 3)
    if (option == 0 or mixed) and not groups:
        sentence_entities['origin'], sentence_entities['destination'] = sample_path()
        group = sample_group()
        hypothesis_entities['group'] = group
        group_key = group if group in DATASET_SYNONYMS else next(
            (key for (key, synonyms) in DATASET_SYNONYMS.items() if group in synonyms), group)
        group_destination = get_ip_by_handle(group_key)
        group_origin = get_node_tree().id

        common_path = get_common_path_list(
            (sentence_entities['origin'], sentence_entities['destination']),
            (group_origin, group_destination))
        while len(common_path) <= 2 and (sentence_entities['destination'] != group_destination):
            sentence_entities['origin'], sentence_entities['destination'] = sample_path()
            group = sample_group()
            hypothesis_entities['group'] = group
            group_key = group if group in DATASET_SYNONYMS else next(
                (key for (key, synonyms) in DATASET_SYNONYMS.items() if group in synonyms), group)
            group_destination = get_ip_by_handle(group_key)
            group_origin = get_node_tree().id
            common_path = get_common_path_list(
                (sentence_entities['origin'], sentence_entities['destination']),
                (group_origin, group_destination))

    elif option == 1 and not groups:
        sentence_entities['origin'], sentence_entities['destination'] = sample_path()
        hypothesis_entities['origin'], hypothesis_entities['destination'] = sample_path()
        common_path = get_common_path_list(
            (sentence_entities['origin'], sentence_entities['destination']),
            (hypothesis_entities['origin'], hypothesis_entities['destination']))
        while len(common_path) <= 2 and (sentence_entities['destination'] != hypothesis_entities['destination']):
            sentence_entities['origin'], sentence_entities['destination'] = sample_path()
            hypothesis_entities['origin'], hypothesis_entities['destination'] = sample_path()
            common_path = get_common_path_list(
                (sentence_entities['origin'], sentence_entities['destination']),
                (hypothesis_entities['origin'], hypothesis_entities['destination']))
    else:
        sentence_entities['group'] = sample_group()
        hypothesis_entities['group'] = sample_group()
        while sentence_entities['group'] != hypothesis_entities['group']:
            sentence_entities['group'] = sample_group()
            hypothesis_entities['group'] = sample_group()

    return sentence_entities, hypothesis_entities


def sample_hierarchical_endpoints(sentence_entities, hypothesis_entities):
    """ samples target entities from topology for intent that may contradict each other """

    origin = get_node_tree().id
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
    sentence_entities['operations'] = [choice(DATASET_ACTIONS_MBS)] + sentence_entities['operations']
    hypothesis_entities['operations'] = [choice(DATASET_ACTIONS_MBS)] + hypothesis_entities['operations']
    if sentence_entities['operations'][0] == hypothesis_entities['operations'][0]:
        sentence_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, 3))
        hypothesis_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, 3))
    else:
        sentence_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, 3))
        hypothesis_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, 3))
        while bool(set(sentence_entities['middleboxes']) & set(hypothesis_entities['middleboxes'])):
            sentence_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, 3))
            hypothesis_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, 3))

    return sentence_entities, hypothesis_entities


def sample_conflicting_chaining(sentence_entities, hypothesis_entities):
    """ return chaining commands that do not contradict each other """
    sentence_entities['operations'] = ["add"] + sentence_entities['operations']
    hypothesis_entities['operations'] = ["remove"] + hypothesis_entities['operations']
    sentence_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, 3))
    hypothesis_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, 3))
    while not bool(set(sentence_entities['middleboxes']) & set(hypothesis_entities['middleboxes'])):
        sentence_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, 3))
        hypothesis_entities['middleboxes'] = sample(DATASET_MIDDLEBOXES, randint(1, 3))

    return sentence_entities, hypothesis_entities


def sample_entailing_rules(sentence_entities, hypothesis_entities):
    """ return chaining commands that do not contradict each other """
    # allow - allow, block - block , any targets
    sentence_op = choice(DATASET_ACTIONS_ACL)
    hypothesis_op = choice(DATASET_ACTIONS_ACL)

    raw_sentence_targets = []
    raw_hypothesis_targets = []
    for (stn_target, hyp_target) in [sample_targets() for _ in range(1, 3)]:
        raw_sentence_targets.append(stn_target)
        raw_hypothesis_targets.append(hyp_target)
    # remove possible duplicates
    sentence_targets = [dict(y) for y in set({tuple(x.items()) for x in raw_sentence_targets})]
    hypothesis_targets = [dict(y) for y in set({tuple(x.items()) for x in raw_hypothesis_targets})]

    while (sentence_op != hypothesis_op and
           any(any(target_match(stn_target, hyp_target, sentence_op, hypothesis_op)
                   for stn_target in sentence_targets)
               for hyp_target in hypothesis_targets)):

        sentence_op = choice(DATASET_ACTIONS_ACL)
        hypothesis_op = choice(DATASET_ACTIONS_ACL)

        raw_sentence_targets = []
        raw_hypothesis_targets = []
        for (stn_target, hyp_target) in [sample_targets() for _ in range(1, 3)]:
            raw_sentence_targets.append(stn_target)
            raw_hypothesis_targets.append(hyp_target)
        # remove possible duplicates
        sentence_targets = [dict(y) for y in set({tuple(x.items()) for x in raw_sentence_targets})]
        hypothesis_targets = [dict(y) for y in set({tuple(x.items()) for x in raw_hypothesis_targets})]

    for target in sentence_targets:
        for type in target:
            if type not in sentence_entities:
                sentence_entities[type] = []
            sentence_entities[type].append(target[type])

    for target in hypothesis_targets:
        for type in target:
            if type not in hypothesis_entities:
                hypothesis_entities[type] = []
            hypothesis_entities[type].append(target[type])

    sentence_entities['operations'] = [sentence_op] + sentence_entities['operations']
    hypothesis_entities['operations'] = [hypothesis_op] + hypothesis_entities['operations']

    return sentence_entities, hypothesis_entities


def sample_conflicting_rules(sentence_entities, hypothesis_entities):
    """ return chaining commands that do not contradict each other """
    # allow - block, but different targets
    sentence_entities['operations'] = ['allow'] + sentence_entities['operations']
    hypothesis_entities['operations'] = ['block'] + hypothesis_entities['operations']

    raw_sentence_targets = []
    raw_hypothesis_targets = []
    for (stn_target, hyp_target) in [sample_targets() for _ in range(1, 3)]:
        raw_sentence_targets.append(stn_target)
        raw_hypothesis_targets.append(hyp_target)
    # remove possible duplicates
    sentence_targets = [dict(y) for y in set({tuple(x.items()) for x in raw_sentence_targets})]
    hypothesis_targets = [dict(y) for y in set({tuple(x.items()) for x in raw_hypothesis_targets})]

    while not any(any(target_match(stn_target, hyp_target, 'allow', 'block')
                      for stn_target in sentence_targets)
                  for hyp_target in hypothesis_targets):
        raw_sentence_targets = []
        raw_hypothesis_targets = []
        for (stn_target, hyp_target) in [sample_targets() for _ in range(1, 3)]:
            raw_sentence_targets.append(stn_target)
            raw_hypothesis_targets.append(hyp_target)
        # remove possible duplicates
        sentence_targets = [dict(y) for y in set({tuple(x.items()) for x in raw_sentence_targets})]
        hypothesis_targets = [dict(y) for y in set({tuple(x.items()) for x in raw_hypothesis_targets})]

    for target in sentence_targets:
        for type in target:
            if type not in sentence_entities:
                sentence_entities[type] = []
            sentence_entities[type].append(target[type])

    for target in hypothesis_targets:
        for type in target:
            if type not in hypothesis_entities:
                hypothesis_entities[type] = []
            hypothesis_entities[type].append(target[type])

    return sentence_entities, hypothesis_entities


def sample_entailing_timeranges(sentence_entities, hypothesis_entities):
    """ returns non conflicting timestamps """
    sentence_entities['start'], sentence_entities['end'] = sample_time_range(-6, -4)
    hypothesis_entities['start'], hypothesis_entities['end'] = sample_time_range(6, 0)
    while timerange_overlap(sentence_entities, hypothesis_entities):
        sentence_entities['start'], sentence_entities['end'] = sample_time_range(-6, -4)
        hypothesis_entities['start'], hypothesis_entities['end'] = sample_time_range(6, 0)

    return sentence_entities, hypothesis_entities


def sample_conflicting_timeranges(sentence_entities, hypothesis_entities):
    """ returns  conflicting timestamps """
    sentence_entities['start'], sentence_entities['end'] = sample_time_range(0, 1)
    if randint(0, 2) % 2 == 0:
        hypothesis_entities['start'], hypothesis_entities['end'] = sample_time_range(0, 1)
    while not timerange_overlap(sentence_entities, hypothesis_entities):
        sentence_entities['start'], sentence_entities['end'] = sample_time_range(0, 1)
        if randint(0, 2) % 2 == 0:
            hypothesis_entities['start'], hypothesis_entities['end'] = sample_time_range(0, 1)
        else:
            hypothesis_entities.pop('start', None)
            hypothesis_entities.pop('end', None)
    return sentence_entities, hypothesis_entities


def sample_entailing_qos(sentence_entities, hypothesis_entities, stn_action=None, hyp_action=None):
    """ samples qos metric, constraint and values that entail given a chosen path """
    if ('origin' not in sentence_entities or 'destination' not in sentence_entities) and 'group' not in sentence_entities:
        raise ValueError("origin and destination or group in sentence intent must be provided")

    if ('origin' not in hypothesis_entities or 'destination' not in hypothesis_entities) and 'group' not in hypothesis_entities:
        raise ValueError("origin and destination or group in hypothesis intent must be provided")

    sentence_op = choice(DATASET_ACTIONS_QOS) if not stn_action else stn_action
    hypothesis_op = choice(DATASET_ACTIONS_QOS) if not hyp_action else stn_action

    sentence_entities['qos'] = [sample_qos()]
    hypothesis_entities['qos'] = [sample_qos()]

    while not qos_path_embedding(sentence_entities, hypothesis_entities, sentence_op, hypothesis_op,  conflicting_endpoints=False):
        sentence_op = choice(DATASET_ACTIONS_QOS) if not stn_action else stn_action
        hypothesis_op = choice(DATASET_ACTIONS_QOS) if not hyp_action else stn_action

        sentence_entities['qos'] = [sample_qos()]
        hypothesis_entities['qos'] = [sample_qos()]

    sentence_entities['operations'] = [sentence_op] + sentence_entities['operations']
    hypothesis_entities['operations'] = [hypothesis_op] + hypothesis_entities['operations']

    return sentence_entities, hypothesis_entities


def sample_conflicting_qos(sentence_entities, hypothesis_entities, stn_action=None, hyp_action=None):
    """ samples qos metric, constraint and values that contradict given a chosen path """
    if ('origin' not in sentence_entities or 'destination' not in sentence_entities) and 'group' not in sentence_entities:
        raise ValueError("origin and destination or group in sentence intent must be provided")

    if ('origin' not in hypothesis_entities or 'destination' not in hypothesis_entities) and 'group' not in hypothesis_entities:
        raise ValueError("origin and destination or group in hypothesis intent must be provided")

    sentence_op = choice(DATASET_ACTIONS_QOS) if not stn_action else stn_action
    hypothesis_op = choice(DATASET_ACTIONS_QOS) if not hyp_action else stn_action

    sentence_entities['qos'] = [sample_qos()]
    hypothesis_entities['qos'] = [sample_qos()]

    while qos_path_embedding(sentence_entities, hypothesis_entities, sentence_op, hypothesis_op, conflicting_endpoints=True):
        sentence_op = choice(DATASET_ACTIONS_QOS) if not stn_action else stn_action
        hypothesis_op = choice(DATASET_ACTIONS_QOS) if not hyp_action else stn_action

        sentence_entities['qos'] = [sample_qos()]
        hypothesis_entities['qos'] = [sample_qos()]

    sentence_entities['operations'] = [sentence_op] + sentence_entities['operations']
    hypothesis_entities['operations'] = [hypothesis_op] + hypothesis_entities['operations']

    return sentence_entities, hypothesis_entities
