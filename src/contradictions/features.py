"""
    Module to extract contradiction features

    1 Coreference
    2 Negation
    3 Time
    4 Synonyms
    5 Hierarchy
    6 QoS
    7 Path
    8 Similarity (origin, destination, services, groups, traffic and middleboxes)
"""


from datetime import datetime

import re
import spacy

from nltk.corpus import wordnet

from utils import config
from manager import topology

nlp = spacy.load('en_core_web_sm')


def coreference(sentence, hypothesis):
    """ Checks if two intents are coreferent """
    stn_origin, stn_destination = None, None
    hyp_origin, hyp_destination = None, None
    from_pattern = re.compile(r".* from (endpoint|group)\(\'(.*?)\'\).*")
    to_pattern = re.compile(r".* to (endpoint|group)\(\'(.*?)\'\).*")
    group_pattern = re.compile(r".* for (endpoint|group)\(\'(.*?)\'\).*")

    if 'from' in sentence and 'to' in sentence:
        result = from_pattern.search(sentence)
        stn_origin = result.group(2)
        result = to_pattern.search(sentence)
        stn_destination = result.group(2)
    elif 'for' in sentence:
        result = group_pattern.search(sentence)
        group = result.group(2)
        group_key = group if group in config.DATASET_SYNONYMS else next(
            (key for (key, synonyms) in config.DATASET_SYNONYMS.items() if group in synonyms), group)
        stn_destination = topology.get_group_ip(group_key)
        stn_origin = topology.get_node_tree().id

    if 'from' in hypothesis and 'to' in hypothesis:
        result = from_pattern.search(hypothesis)
        hyp_origin = result.group(2)
        result = to_pattern.search(hypothesis)
        hyp_destination = result.group(2)
    elif 'for' in hypothesis:
        result = group_pattern.search(hypothesis)
        group = result.group(2)
        group_key = group if group in config.DATASET_SYNONYMS else next(
            (key for (key, synonyms) in config.DATASET_SYNONYMS.items() if group in synonyms), group)
        hyp_destination = topology.get_group_ip(group_key)
        hyp_origin = topology.get_node_tree().id

    # print "PATHS", (stn_origin, stn_destination), (hyp_origin, hyp_destination)
    common_path = topology.get_common_path((stn_origin, stn_destination), (hyp_origin, hyp_destination))
    coref = 1 if common_path[0] != common_path[1] else 0

    return coref


def negation(sentence, hypothesis):
    """ Inspects the presence of negation in sentence and hypothesis """
    negation_score = 0
    for (act, neg) in config.NILE_ACTIONS_NEGATION.items():
        if (act in sentence and neg in hypothesis) or (neg in sentence and act in hypothesis):
            negation_score += 1

    # print "NEGATION SCORE", negation_score
    return negation_score


def time(sentence, hypothesis):
    """ Inspects time ranges of sentence and hypothesis """
    sentence_range = (0, 0)
    start_pattern = re.compile(r".* start timestamp\(\'(.*?)\'\) .*")
    end_pattern = re.compile(r".* end timestamp\(\'(.*?)\'\).*")

    if "start" in sentence and "end" in sentence:
        result = start_pattern.search(sentence)
        time_start = result.group(1)
        result = end_pattern.search(sentence)
        time_end = result.group(1)
        sentence_range = (datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S.%f"), datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S.%f"))

    hypothesis_range = (0, 0)
    if "start" in hypothesis and "end" in hypothesis:
        result = start_pattern.search(hypothesis)
        time_start = result.group(1)
        result = end_pattern.search(hypothesis)
        time_end = result.group(1)
        hypothesis_range = (datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S.%f"), datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S.%f"))

    overlap = 0
    if sentence_range != (0, 0) and hypothesis_range != (0, 0):
        latest_start = max(sentence_range[0], hypothesis_range[0])
        earliest_end = min(sentence_range[1], hypothesis_range[1])
        delta = ((earliest_end - latest_start).total_seconds() / 3600) + 1
        overlap = max(0, delta)

    return overlap


def synonyms(sentence, hypothesis):
    """ Calculates synonyms of sentence and hypothesis """

    endpoint_pattern = re.compile(r".* endpoint\(\'(.*?)\'\).*")
    group_pattern = re.compile(r".* group\(\'(.*?)\'\).*")
    service_pattern = re.compile(r".* service\(\'(.*?)\'\).*")
    traffic_pattern = re.compile(r".* traffic\(\'(.*?)\'\).*")

    stn_endpoints, stn_groups, stn_services, stn_traffics = ([], [], [], [])
    if 'endpoint' in sentence:
        stn_endpoints = re.findall(endpoint_pattern, sentence)

    if 'group' in sentence:
        stn_groups = re.findall(group_pattern, sentence)

    if 'service' in sentence:
        stn_services = re.findall(service_pattern, sentence)

    if 'service' in sentence:
        stn_traffics = re.findall(traffic_pattern, sentence)

    syns = []
    stn_entities = [stn_endpoints, stn_groups, stn_services, stn_traffics]
    for stn_list in stn_entities:
        for entity in stn_list:
            for syn in wordnet.synsets(entity):
                for lemma in syn.lemmas():
                    synonym = lemma.name()
                    if synonym in hypothesis and synonym not in syns:
                        syns.append(synonym)

    return len(syns)


def qos(sentence, hypothesis):
    """ Inspects qos of sentence and hypothesis """
    from_pattern = re.compile(r".* from (endpoint|group)\(\'(.*?)\'\).*")
    to_pattern = re.compile(r".* to (endpoint|group)\(\'(.*?)\'\).*")
    group_pattern = re.compile(r".* for (endpoint|group)\(\'(.*?)\'\).*")
    quota_pattern = re.compile(r".* quota\((.*?)\).*")
    bandwidth_pattern = re.compile(r".* bandwidth\((.*?)\).*")

    print "sentence", sentence
    print "hypothesis", hypothesis

    if 'from' in sentence and 'to' in sentence:
        result = from_pattern.search(sentence)
        stn_origin = result.group(2)
        result = to_pattern.search(sentence)
        stn_destination = result.group(2)
    elif 'for' in sentence:
        result = group_pattern.search(sentence)
        group = result.group(2)
        group_key = group if group in config.DATASET_SYNONYMS else next(
            (key for (key, synonyms) in config.DATASET_SYNONYMS.items() if group in synonyms), group)
        stn_destination = topology.get_group_ip(group_key)
        stn_origin = topology.get_node_tree().id

    if 'from' in hypothesis and 'to' in hypothesis:
        result = from_pattern.search(hypothesis)
        hyp_origin = result.group(2)
        result = to_pattern.search(hypothesis)
        hyp_destination = result.group(2)
    elif 'for' in hypothesis:
        result = group_pattern.search(hypothesis)
        group = result.group(2)
        group_key = group if group in config.DATASET_SYNONYMS else next(
            (key for (key, synonyms) in config.DATASET_SYNONYMS.items() if group in synonyms), group)
        hyp_destination = topology.get_group_ip(group_key)
        hyp_origin = topology.get_node_tree().id

    sentence_path = (stn_origin, stn_destination)
    hypothesis_path = (hyp_origin, hyp_destination)

    sentence_action = 'set' if 'set' in sentence else 'unset'
    hypothesis_action = 'set' if 'set' in sentence else 'unset'

    sentence_qos = None
    hypothesis_qos = None
    if 'bandwidth' in sentence:
        result = bandwidth_pattern.search(sentence)
        bandwidth = result.group(1)
        sentence_qos = {
            'name': 'bandwidth',
            'constraint': bandwidth.split(',')[0].replace("'", ""),
            'value': bandwidth.split(',')[1].replace("'", ""),
            'unit': bandwidth.split(',')[2].replace("'", "")
        }
    elif 'quota' in sentence:
        result = quota_pattern.search(sentence)
        bandwidth = result.group(1)
        sentence_qos = {
            'name': 'quota',
            'constraint': '',
            'value': bandwidth.split(',')[0].replace("'", ""),
            'unit': bandwidth.split(',')[1].replace("'", "")
        }

    if 'bandwidth' in hypothesis:
        result = bandwidth_pattern.search(hypothesis)
        bandwidth = result.group(1)
        hypothesis_qos = {
            'name': 'bandwidth',
            'constraint': bandwidth.split(',')[0],
            'value': bandwidth.split(',')[1],
            'unit': bandwidth.split(',')[2]
        }
    elif 'quota' in hypothesis:
        result = quota_pattern.search(hypothesis)
        bandwidth = result.group(1)
        hypothesis_qos = {
            'name': 'quota',
            'constraint': '',
            'value': bandwidth.split(',')[0],
            'unit': bandwidth.split(',')[1]
        }

    if not sentence_qos or not hypothesis_qos:
        return 1

    if sentence_action == 'set' and hypothesis_action == 'set':
        if sentence_qos['name'] == 'bandwidth' and hypothesis_qos['name'] == 'bandwidth':
            # check individually
            if not topology.is_bandwidth_available(sentence_path[0], sentence_path[1], sentence_qos['value'], sentence_qos['constraint']):
                return 0

            if not topology.is_bandwidth_available(hypothesis_path[0], hypothesis_path[1], hypothesis_qos['value'], hypothesis_qos['constraint']):
                return 0

            # check combined
            if sentence_qos['constraint'] == hypothesis_qos['constraint']:
                common_path_src, common_path_tgt = topology.get_common_path(sentence_path, hypothesis_path)
                if not common_path_src or not common_path_tgt:
                    return 1
                return 1 if topology.is_bandwidth_available(common_path_src, common_path_tgt, sentence_qos['value'] + hypothesis_qos['value'], hypothesis_qos['constraint']) else 0

            return 1 if ((sentence_qos['constraint'] == 'min' and sentence_qos['value'] < hypothesis_qos['value']) or
                         (sentence_qos['constraint'] == 'max' and sentence_qos['value'] > hypothesis_qos['value'])) else 0
        elif sentence_qos['name'] == 'quota' and hypothesis_qos['name'] == 'quota':
            return 1 if sentence_qos['value'] == hypothesis_qos['value'] else 0
        else:
            return 1
    elif (sentence_action == 'set' and hypothesis_action) == 'unset' or (sentence_action == 'unset' and hypothesis_action == 'set'):
        if ((sentence_qos['name'] == 'bandwidth' and hypothesis_qos['name'] == 'bandwidth')
                or (sentence_qos['name'] == 'quota' and hypothesis_qos['name'] == 'quota')):
            return 1 if stn_destination != hyp_destination else 0
        return 1

    return 1


def hierarchy(sentence, hypothesis):
    """ Calculates hierachy of sentence and hypothesis """
    stn_origin, stn_destination = None, None
    hyp_origin, hyp_destination = None, None
    from_pattern = re.compile(r".* from (endpoint|group)\(\'(.*?)\'\).*")
    to_pattern = re.compile(r".* to (endpoint|group)\(\'(.*?)\'\).*")
    group_pattern = re.compile(r".* for (endpoint|group)\(\'(.*?)\'\).*")

    if 'from' in sentence and 'to' in sentence:
        result = from_pattern.search(sentence)
        stn_origin = result.group(2)
        result = to_pattern.search(sentence)
        stn_destination = result.group(2)
    elif 'for' in sentence:
        result = group_pattern.search(sentence)
        group = result.group(2)
        group_key = group if group in config.DATASET_SYNONYMS else next(
            (key for (key, synonyms) in config.DATASET_SYNONYMS.items() if group in synonyms), group)
        stn_destination = topology.get_group_ip(group_key)
        stn_origin = topology.get_node_tree().id

    if 'from' in hypothesis and 'to' in hypothesis:
        result = from_pattern.search(hypothesis)
        hyp_origin = result.group(2)
        result = to_pattern.search(hypothesis)
        hyp_destination = result.group(2)
    elif 'for' in hypothesis:
        result = group_pattern.search(hypothesis)
        group = result.group(2)
        group_key = group if group in config.DATASET_SYNONYMS else next(
            (key for (key, synonyms) in config.DATASET_SYNONYMS.items() if group in synonyms), group)
        hyp_destination = topology.get_group_ip(group_key)
        hyp_origin = topology.get_node_tree().id

    ancestor = (topology.is_ancestor(stn_origin, hyp_origin) or topology.is_ancestor(stn_destination, hyp_destination))
    descendent = (topology.is_descendent(stn_origin, hyp_origin) or topology.is_descendent(stn_destination, hyp_destination))

    return 1 if ancestor or descendent else 0


def path_similarity(sentence, hypothesis):
    """ counts the number of same nodes in intent paths """
    stn_origin, stn_destination = None, None
    hyp_origin, hyp_destination = None, None
    from_pattern = re.compile(r".* from (endpoint|group)\(\'(.*?)\'\).*")
    to_pattern = re.compile(r".* to (endpoint|group)\(\'(.*?)\'\).*")
    group_pattern = re.compile(r".* for (endpoint|group)\(\'(.*?)\'\).*")

    if 'from' in sentence and 'to' in sentence:
        result = from_pattern.search(sentence)
        stn_origin = result.group(2)
        result = to_pattern.search(sentence)
        stn_destination = result.group(2)
    elif 'for' in sentence:
        result = group_pattern.search(sentence)
        group = result.group(2)
        group_key = group if group in config.DATASET_SYNONYMS else next(
            (key for (key, synonyms) in config.DATASET_SYNONYMS.items() if group in synonyms), group)
        stn_destination = topology.get_group_ip(group_key)
        stn_origin = topology.get_node_tree().id

    if 'from' in hypothesis and 'to' in hypothesis:
        result = from_pattern.search(hypothesis)
        hyp_origin = result.group(2)
        result = to_pattern.search(hypothesis)
        hyp_destination = result.group(2)
    elif 'for' in hypothesis:
        result = group_pattern.search(hypothesis)
        group = result.group(2)
        group_key = group if group in config.DATASET_SYNONYMS else next(
            (key for (key, synonyms) in config.DATASET_SYNONYMS.items() if group in synonyms), group)
        hyp_destination = topology.get_group_ip(group_key)
        hyp_origin = topology.get_node_tree().id

    # print "PATHS", (stn_origin, stn_destination), (hyp_origin, hyp_destination)
    common_path = topology.get_common_path_list((stn_origin, stn_destination), (hyp_origin, hyp_destination))

    return len(common_path)


def origin(sentence, hypothesis):
    """ similarity of targets vectors """
    stn_origin = ""
    hyp_origin = ""

    from_pattern = re.compile(r".* endpoint\(\'(.*?)\'\).*")

    if 'endpoint' in sentence:
        result = from_pattern.search(sentence)
        stn_origin = result.group(1)

    if 'endpoint' in hypothesis:
        result = from_pattern.search(hypothesis)
        hyp_origin = result.group(1)

    stn_origin_doc = nlp(stn_origin if isinstance(stn_origin, unicode) else unicode(stn_origin, 'utf-8'))
    hyp_origin_doc = nlp(hyp_origin if isinstance(hyp_origin, unicode) else unicode(hyp_origin, 'utf-8'))
    sim = stn_origin_doc.similarity(hyp_origin_doc)
    return sim


def destination(sentence, hypothesis):
    """ similarity of targets vectors """
    stn_destination = ""
    hyp_destination = ""

    from_pattern = re.compile(r".* endpoint\(\'(.*?)\'\).*")

    if 'endpoint' in sentence:
        result = from_pattern.search(sentence)
        stn_destination = result.group(1)

    if 'endpoint' in hypothesis:
        result = from_pattern.search(hypothesis)
        hyp_destination = result.group(1)

    stn_destination_doc = nlp(stn_destination if isinstance(stn_destination, unicode) else unicode(stn_destination, 'utf-8'))
    hyp_destination_doc = nlp(hyp_destination if isinstance(hyp_destination, unicode) else unicode(hyp_destination, 'utf-8'))
    sim = stn_destination_doc.similarity(hyp_destination_doc)
    return sim


def services(sentence, hypothesis):
    """ similarity of targets vectors """
    service_pattern = re.compile(r".* service\(\'(.*?)\'\).*")

    stn_services = []
    hyp_services = []

    if 'service' in sentence:
        stn_services = re.findall(service_pattern, sentence)

    if 'service' in hypothesis:
        hyp_services = re.findall(service_pattern, hypothesis)

    sim = 0
    for i in stn_services:
        srv = nlp(i)
        for j in hyp_services:
            sim += srv.similarity(nlp(j))

    return sim


def middleboxes(sentence, hypothesis):
    """ similarity of targets vectors """
    middlebox_pattern = re.compile(r".* middlebox\(\'(.*?)\'\).*")

    stn_mbs = []
    hyp_mbs = []

    if 'service' in sentence:
        stn_mbs = re.findall(middlebox_pattern, sentence)

    if 'service' in hypothesis:
        hyp_mbs = re.findall(middlebox_pattern, hypothesis)

    sim = 0
    for i in stn_mbs:
        mb = nlp(i)
        for j in hyp_mbs:
            sim += mb.similarity(nlp(j))

    return sim


def traffic(sentence, hypothesis):
    """ similarity of targets vectors """
    traffic_pattern = re.compile(r".* traffic\(\'(.*?)\'\).*")

    stn_traffic = []
    hyp_traffic = []

    if 'traffic' in sentence:
        stn_traffic = re.findall(traffic_pattern, sentence)

    if 'traffic' in hypothesis:
        hyp_traffic = re.findall(traffic_pattern, hypothesis)

    sim = 0
    for i in stn_traffic:
        trf = nlp(i)
        for j in hyp_traffic:
            sim += trf.similarity(nlp(j))

    return sim


def groups(sentence, hypothesis):
    """ similarity of targets vectors """
    group_pattern = re.compile(r".* group\(\'(.*?)\'\).*")
    stn_group = ""
    hyp_group = ""

    if 'group' in sentence:
        result = group_pattern.search(sentence)
        stn_group = result.group(1)

    if 'group' in hypothesis:
        result = group_pattern.search(hypothesis)
        hyp_group = result.group(1)

    stn_group_doc = nlp(stn_group if isinstance(stn_group, unicode) else unicode(stn_group, 'utf-8'))
    hyp_group_doc = nlp(hyp_group if isinstance(hyp_group, unicode) else unicode(hyp_group, 'utf-8'))
    sim = stn_group_doc.similarity(hyp_group_doc)
    return sim


def get_features(sentence, hypothesis):
    """ Return array with contradiction features for the given sentence and hypothesis """
    features = [
        origin(sentence, hypothesis),
        destination(sentence, hypothesis),
        services(sentence, hypothesis),
        groups(sentence, hypothesis),
        traffic(sentence, hypothesis),
        time(sentence, hypothesis),
        middleboxes(sentence, hypothesis),
        qos(sentence, hypothesis),
        negation(sentence, hypothesis),
        coreference(sentence, hypothesis),
        synonyms(sentence, hypothesis),
        hierarchy(sentence, hypothesis),
        path_similarity(sentence, hypothesis),
    ]
    return features
