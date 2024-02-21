"""
    Module to extract ambiguities features

    1 Path
    2 Negation
    3 Time
    4 Synonyms
    5 Hierarchy (endpoints, traffics)
    6 QoS
    7 Similarity (endpoints, services, groups, traffic, protocol and middleboxes, bandwidths, quotas)
"""

from datetime import datetime

import re
import nltk
import spacy

from nltk.corpus import wordnet

from ..utils import config, topology

# nltk.download("wordnet")
nlp = spacy.load("en_core_web_md")


def negation(sentence, hypothesis):
    """Inspects the presence of negation in sentence and hypothesis"""
    negation_score = 0
    for act, neg in config.NILE_ACTIONS_NEGATION.items():
        if (act in sentence and neg in hypothesis) or (
            neg in sentence and act in hypothesis
        ):
            negation_score += 1

    # print "NEGATION SCORE", negation_score
    return negation_score


def time(sentence, hypothesis):
    """Inspects time ranges of sentence and hypothesis"""
    sentence_range = (0, 0)
    start_pattern = re.compile(r".* start hour\(\'(.*?)\'\) .*")
    end_pattern = re.compile(r".* end hour\(\'(.*?)\'\).*")

    if "start hour" in sentence and "end hour" in sentence:
        result = start_pattern.search(sentence)
        time_start = result.group(1) if result else ""
        result = end_pattern.search(sentence)
        time_end = result.group(1) if result else ""
        if time_start and time_end:
            sentence_range = (
                datetime.strptime(time_start, "%H:%M"),
                datetime.strptime(time_end, "%H:%M"),
            )
        # sentence_range = (datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S.%f"), datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S.%f"))

    hypothesis_range = (0, 0)
    if "start hour" in hypothesis and "end hour" in hypothesis:
        result = start_pattern.search(hypothesis)
        time_start = result.group(1) if result else ""
        result = end_pattern.search(hypothesis)
        time_end = result.group(1) if result else ""
        if time_start and time_end:
            hypothesis_range = (
                datetime.strptime(time_start, "%H:%M"),
                datetime.strptime(time_end, "%H:%M"),
            )
        # hypothesis_range = (datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S.%f"), datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S.%f"))

    overlap = 0
    if sentence_range != (0, 0) and hypothesis_range != (0, 0):
        latest_start = max(sentence_range[0], hypothesis_range[0])
        earliest_end = min(sentence_range[1], hypothesis_range[1])
        delta = ((earliest_end - latest_start).total_seconds() / 60) + 1
        overlap = max(0, delta)
    elif sentence_range != (0, 0) and hypothesis_range == (0, 0):
        delta = ((sentence_range[1] - sentence_range[0]).total_seconds() / 60) + 1
        overlap = max(0, delta)
    elif sentence_range == (0, 0) and hypothesis_range != (0, 0):
        delta = ((hypothesis_range[1] - hypothesis_range[0]).total_seconds() / 60) + 1
        overlap = max(0, delta)
    else:
        overlap = 1440.0

    return overlap


def synonyms(sentence, hypothesis):
    """Calculates synonyms of sentence and hypothesis"""

    endpoint_pattern = re.compile(r"\w*endpoint\(\'(.*?)\'\)\w*")
    group_pattern = re.compile(r"\w*group\(\'(.*?)\'\)\w*")
    service_pattern = re.compile(r"\w*service\(\'(.*?)\'\)\w*")
    traffic_pattern = re.compile(r"\w*traffic\(\'(.*?)\'\)\w*")

    stn_endpoints, stn_groups, stn_services, stn_traffics = ([], [], [], [])
    if "endpoint" in sentence:
        stn_endpoints = re.findall(endpoint_pattern, sentence)

    if "group" in sentence:
        stn_groups = re.findall(group_pattern, sentence)

    if "service" in sentence:
        stn_services = re.findall(service_pattern, sentence)

    if "traffic" in sentence:
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

            for key, synonyms in config.DATASET_SYNONYMS.items():
                synonyms_list = [key] + synonyms
                if entity in synonyms_list:
                    for synonym in synonyms:
                        if synonym in hypothesis and synonym not in syns:
                            syns.append(synonym)

    return len(syns)


def qos(sentence, hypothesis):
    """Inspects qos of sentence and hypothesis"""
    from_pattern = re.compile(r".* from (endpoint|group)\(\'(.*?)\'\).*")
    to_pattern = re.compile(r".* to (endpoint|group)\(\'(.*?)\'\).*")
    group_pattern = re.compile(r".*(endpoint|group)\(\'(.*?)\'\).*")
    quota_pattern = re.compile(r"\w*quota\((.*?)\)\w*")
    bandwidth_pattern = re.compile(r"\w*bandwidth\((.*?)\).*")

    # print("sentence", sentence)
    # print("hypothesis", hypothesis)

    if "from" in sentence and "to" in sentence:
        result = from_pattern.search(sentence)
        stn_origin = topology.get_ip_by_handle(result.group(2) if result else "")
        result = to_pattern.search(sentence)
        stn_destination = topology.get_ip_by_handle(result.group(2) if result else "")
    elif "for" in sentence:
        if "group" in sentence or "endpoint" in sentence:
            result = group_pattern.search(sentence)
            group = result.group(2) if result else ""
            group_key = (
                group
                if group in config.DATASET_SYNONYMS
                else next(
                    (
                        key
                        for (key, synonyms) in config.DATASET_SYNONYMS.items()
                        if group in synonyms
                    ),
                    group,
                )
            )
            stn_destination = topology.get_ip_by_handle(group_key)
            stn_origin = topology.get_node_tree().id
        else:
            stn_destination = topology.get_ip_by_handle("gateway")
            stn_origin = topology.get_node_tree().id

    if "from" in hypothesis and "to" in hypothesis:
        result = from_pattern.search(hypothesis)
        hyp_origin = topology.get_ip_by_handle(result.group(2) if result else "")
        result = to_pattern.search(hypothesis)
        hyp_destination = topology.get_ip_by_handle(result.group(2) if result else "")
    elif "for" in hypothesis:
        if "group" in hypothesis or "endpoint" in hypothesis:
            result = group_pattern.search(hypothesis)
            group = result.group(2) if result else ""
            group_key = (
                group
                if group in config.DATASET_SYNONYMS
                else next(
                    (
                        key
                        for (key, synonyms) in config.DATASET_SYNONYMS.items()
                        if group in synonyms
                    ),
                    group,
                )
            )
            hyp_destination = topology.get_ip_by_handle(group_key)
            hyp_origin = topology.get_node_tree().id
        else:
            hyp_destination = topology.get_ip_by_handle("gateway")
            hyp_origin = topology.get_node_tree().id

    sentence_path = (stn_origin, stn_destination)
    hypothesis_path = (hyp_origin, hyp_destination)

    sentence_action = " unset " if " unset " in sentence else " set "
    hypothesis_action = " unset " if " unset " in sentence else " set "

    sentence_qos = []
    hypothesis_qos = []
    if "bandwidth" in sentence:
        results = re.findall(bandwidth_pattern, sentence)
        for bandwidth in results:
            qos = {
                "name": "bandwidth",
                "constraint": (
                    bandwidth.split(",")[0].replace("'", "") if bandwidth else ""
                ),
                "value": (
                    int(bandwidth.split(",")[1].replace("'", "")) if bandwidth else ""
                ),
                "unit": bandwidth.split(",")[2].replace("'", "") if bandwidth else "",
            }
            sentence_qos.append(qos)

    if "quota" in sentence:
        results = re.findall(quota_pattern, sentence)
        for quota in results:
            qos = {
                "name": "quota",
                "constraint": quota.split(",")[0].replace("'", "") if quota else "",
                "value": int(quota.split(",")[1].replace("'", "")) if quota else "",
                "unit": quota.split(",")[2].replace("'", "") if quota else "",
            }
            sentence_qos.append(qos)

    if "bandwidth" in hypothesis:
        results = re.findall(bandwidth_pattern, hypothesis)
        for bandwidth in results:
            qos = {
                "name": "bandwidth",
                "constraint": (
                    bandwidth.split(",")[0].replace("'", "") if bandwidth else ""
                ),
                "value": (
                    int(bandwidth.split(",")[1].replace("'", "")) if bandwidth else ""
                ),
                "unit": bandwidth.split(",")[2].replace("'", "") if bandwidth else "",
            }
            hypothesis_qos.append(qos)

    if "quota" in hypothesis:
        results = re.findall(quota_pattern, hypothesis)
        for quota in results:
            qos = {
                "name": "quota",
                "constraint": quota.split(",")[0].replace("'", "") if quota else "",
                "value": int(quota.split(",")[1].replace("'", "")) if quota else "",
                "unit": quota.split(",")[2].replace("'", "") if quota else "",
            }
            hypothesis_qos.append(qos)

    if not sentence_qos or not hypothesis_qos:
        return 1

    can_embed = 1
    for stn_qos in sentence_qos:
        for hyp_qos in hypothesis_qos:
            if sentence_action == "set" and hypothesis_action == "set":
                if stn_qos["name"] == "bandwidth" and hyp_qos["name"] == "bandwidth":
                    # check individually
                    if not topology.is_bandwidth_available(
                        sentence_path[0],
                        sentence_path[1],
                        stn_qos["value"],
                        stn_qos["constraint"],
                    ):
                        can_embed *= 0
                    elif not topology.is_bandwidth_available(
                        hypothesis_path[0],
                        hypothesis_path[1],
                        hyp_qos["value"],
                        hyp_qos["constraint"],
                    ):
                        can_embed *= 0
                    # check combined
                    elif stn_qos["constraint"] == hyp_qos["constraint"]:
                        common_path_src, common_path_tgt = topology.get_common_path(
                            sentence_path, hypothesis_path
                        )
                        if not common_path_src or not common_path_tgt:
                            can_embed *= 1

                        can_embed *= (
                            1
                            if topology.is_bandwidth_available(
                                common_path_src,
                                common_path_tgt,
                                stn_qos["value"] + hyp_qos["value"],
                                hyp_qos["constraint"],
                            )
                            else 0
                        )
                    else:
                        can_embed *= (
                            1
                            if (
                                (
                                    stn_qos["constraint"] == "min"
                                    and stn_qos["value"] < hyp_qos["value"]
                                )
                                or (
                                    stn_qos["constraint"] == "max"
                                    and stn_qos["value"] > hyp_qos["value"]
                                )
                            )
                            else 0
                        )
                elif stn_qos["name"] == "quota" and hyp_qos["name"] == "quota":
                    if stn_qos["constraint"] == "any" or hyp_qos["constraint"] == "any":
                        can_embed *= (
                            1
                            if stn_qos["value"] == hyp_qos["value"]
                            and stn_qos["unit"] == hyp_qos["unit"]
                            else 0
                        )
                    elif stn_qos["constraint"] == hyp_qos["constraint"]:
                        can_embed *= (
                            1
                            if stn_qos["value"] == hyp_qos["value"]
                            and stn_qos["unit"] == hyp_qos["unit"]
                            else 0
                        )
                    else:
                        can_embed *= 1
                else:
                    can_embed *= 1
            elif sentence_action == "unset" and hypothesis_action == "unset":
                can_embed *= 1
            else:
                if stn_qos["name"] == hyp_qos["name"]:
                    can_embed *= 0
                else:
                    can_embed *= 1

    return can_embed


def hierarchy_targets(sentence, hypothesis):
    """Calculates hierachy of sentence and hypothesis"""
    stn_origin, stn_destination = None, None
    hyp_origin, hyp_destination = None, None
    from_pattern = re.compile(r".* from (endpoint|group)\(\'(.*?)\'\).*")
    to_pattern = re.compile(r".* to (endpoint|group)\(\'(.*?)\'\).*")
    group_pattern = re.compile(r".*(endpoint|group)\(\'(.*?)\'\).*")

    if "from" in sentence and "to" in sentence:
        result = from_pattern.search(sentence)
        stn_origin = result.group(2) if result else ""
        result = to_pattern.search(sentence)
        stn_destination = result.group(2) if result else ""
    elif "for" in sentence:
        if "group" in sentence or "endpoint" in sentence:
            result = group_pattern.search(sentence)
            group = result.group(2) if result else ""
            group_key = (
                group
                if group in config.DATASET_SYNONYMS
                else next(
                    (
                        key
                        for (key, synonyms) in config.DATASET_SYNONYMS.items()
                        if group in synonyms
                    ),
                    group,
                )
            )
            stn_destination = group_key
            stn_origin = "gateway"
        else:
            stn_destination = "gateway"
            stn_origin = "gateway"

    if "from" in hypothesis and "to" in hypothesis:
        result = from_pattern.search(hypothesis)
        hyp_origin = result.group(2) if result else ""
        result = to_pattern.search(hypothesis)
        hyp_destination = result.group(2) if result else ""
    elif "for" in hypothesis:
        if "group" in hypothesis or "endpoint" in hypothesis:
            result = group_pattern.search(hypothesis)
            group = result.group(2) if result else ""
            group_key = (
                group
                if group in config.DATASET_SYNONYMS
                else next(
                    (
                        key
                        for (key, synonyms) in config.DATASET_SYNONYMS.items()
                        if group in synonyms
                    ),
                    group,
                )
            )
            hyp_destination = group_key
            hyp_origin = "gateway"
        else:
            hyp_destination = "gateway"
            hyp_origin = "gateway"

    descendent = False
    if stn_origin and stn_destination and hyp_origin and hyp_destination:
        # descendent = topology.is_descendent(stn_origin, hyp_origin) or descendent
        descendent = (
            topology.is_descendent(stn_destination, hyp_destination) or descendent
        )
        # descendent = topology.is_descendent(hyp_origin, stn_origin) or descendent
        descendent = (
            topology.is_descendent(hyp_destination, stn_destination) or descendent
        )

    return 1 if descendent else 0


def hierarchy_traffics(sentence, hypothesis):
    # hierarchy
    service_pattern = re.compile(r"\w*service\(\'(.*?)\'\)\w*")
    traffic_pattern = re.compile(r"\w*traffic\(\'(.*?)\'\)\w*")
    protocol_pattern = re.compile(r"\w*protocol\(\'(.*?)\'\)\w*")

    stn_services, stn_traffics, stn_protocols = [], [], []
    hyp_services, hyp_traffics, hyp_protocols = [], [], []

    if "service" in sentence:
        stn_services = re.findall(service_pattern, sentence)

    if "traffic" in sentence:
        stn_traffics = re.findall(traffic_pattern, sentence)

    if "protocol" in sentence:
        stn_protocols = re.findall(protocol_pattern, sentence)

    if "service" in hypothesis:
        hyp_services = re.findall(service_pattern, hypothesis)

    if "traffic" in hypothesis:
        hyp_traffics = re.findall(traffic_pattern, hypothesis)

    if "protocol" in hypothesis:
        hyp_protocols = re.findall(protocol_pattern, hypothesis)

    ancestor, descendent = False, False
    for traffic in stn_traffics:
        for service in hyp_services:
            # higher level, no problem
            ancestor = ancestor or next(
                (
                    True
                    for x in config.DATASET_TRAFFIC_ASSOCIATIONS[traffic]["services"]
                    if x == service
                ),
                False,
            )

        for protocol in hyp_protocols:
            descendent = descendent or next(
                (
                    True
                    for x in config.DATASET_TRAFFIC_ASSOCIATIONS[traffic]["protocols"]
                    if x == protocol
                ),
                False,
            )

    for service in stn_services:
        for protocol in hyp_protocols:
            descendent = descendent or next(
                (
                    True
                    for x in config.DATASET_SERVICE_ASSOCIATIONS[service]["protocols"]
                    if x == protocol
                ),
                False,
            )

        for traffic in hyp_traffics:
            descendent = descendent or next(
                (
                    True
                    for x in config.DATASET_SERVICE_ASSOCIATIONS[service]["traffics"]
                    if x == traffic
                ),
                False,
            )

    for protocol in stn_protocols:
        for service in hyp_services:
            # higher level, no problem
            ancestor = ancestor or next(
                (
                    True
                    for x in config.DATASET_SERVICE_ASSOCIATIONS[service]["protocols"]
                    if x == protocol
                ),
                False,
            )

        for traffic in hyp_traffics:
            ancestor = ancestor or next(
                (
                    True
                    for x in config.DATASET_TRAFFIC_ASSOCIATIONS[traffic]["protocols"]
                    if x == protocol
                ),
                False,
            )

    return 1 if ancestor or descendent else 0


def path_similarity(sentence, hypothesis):
    """counts the number of same nodes in intent paths"""
    stn_origin, stn_destination = None, None
    hyp_origin, hyp_destination = None, None
    from_pattern = re.compile(r".* from (endpoint|group)\(\'(.*?)\'\).*")
    to_pattern = re.compile(r".* to (endpoint|group)\(\'(.*?)\'\).*")
    group_pattern = re.compile(r".*(endpoint|group)\(\'(.*?)\'\).*")

    if "from" in sentence and "to" in sentence:
        result = from_pattern.search(sentence)
        stn_origin = topology.get_ip_by_handle(result.group(2) if result else "")
        result = to_pattern.search(sentence)
        stn_destination = topology.get_ip_by_handle(result.group(2) if result else "")
    elif "for" in sentence:
        if "group" in sentence or "endpoint" in sentence:
            result = group_pattern.search(sentence)
            group = result.group(2) if result else ""
            group_key = (
                group
                if group in config.DATASET_SYNONYMS
                else next(
                    (
                        key
                        for (key, synonyms) in config.DATASET_SYNONYMS.items()
                        if group in synonyms
                    ),
                    group,
                )
            )
            stn_destination = topology.get_ip_by_handle(group_key)
            stn_origin = topology.get_node_tree().id
        else:
            stn_destination = topology.get_ip_by_handle("gateway")
            stn_origin = topology.get_node_tree().id

    if "from" in hypothesis and "to" in hypothesis:
        result = from_pattern.search(hypothesis)
        hyp_origin = topology.get_ip_by_handle(result.group(2) if result else "")
        result = to_pattern.search(hypothesis)
        hyp_destination = topology.get_ip_by_handle(result.group(2) if result else "")
    elif "for" in hypothesis:
        if "group" in hypothesis or "endpoint" in hypothesis:
            result = group_pattern.search(hypothesis)
            group = result.group(2) if result else ""
            group_key = (
                group
                if group in config.DATASET_SYNONYMS
                else next(
                    (
                        key
                        for (key, synonyms) in config.DATASET_SYNONYMS.items()
                        if group in synonyms
                    ),
                    group,
                )
            )
            hyp_destination = topology.get_ip_by_handle(group_key)
            hyp_origin = topology.get_node_tree().id
        else:
            hyp_destination = topology.get_ip_by_handle("gateway")
            hyp_origin = topology.get_node_tree().id

    # print("SENTENCE", sentence)
    # print("HYPHOTESIS", hypothesis)
    # print("PATHS", (stn_origin, stn_destination), (hyp_origin, hyp_destination))
    common_path = []
    if stn_origin and stn_destination and hyp_origin and hyp_destination:
        common_path = topology.get_common_path_list(
            (stn_origin, stn_destination), (hyp_origin, hyp_destination)
        )

    return len(common_path)


def endpoints(sentence, hypothesis):
    """similarity of targets vectors"""
    endpoint_pattern = re.compile(r"\w*endpoint\(\'(.*?)\'\)\w*")

    stn_endpoints = []
    hyp_endpoints = []

    if "endpoint" in sentence:
        stn_endpoints = re.findall(endpoint_pattern, sentence)

    if "endpoint" in hypothesis:
        hyp_endpoints = re.findall(endpoint_pattern, hypothesis)

    sim = 0
    for i in stn_endpoints:
        endpoint = nlp(i)
        for j in hyp_endpoints:
            sim += endpoint.similarity(
                nlp(j)
            )  # 1 if i == j else 0  # endpoint.similarity(nlp(j))
    return sim


def num_endpoints(sentence, hypothesis):
    """similarity of targets vectors"""
    endpoint_pattern = re.compile(r"\w*endpoint\(\'(.*?)\'\)\w*")

    stn_endpoints = []
    hyp_endpoints = []

    if "endpoint" in sentence:
        stn_endpoints = re.findall(endpoint_pattern, sentence)

    if "endpoint" in hypothesis:
        hyp_endpoints = re.findall(endpoint_pattern, hypothesis)

    return len(stn_endpoints) + len(hyp_endpoints)


def services(sentence, hypothesis):
    """similarity of targets vectors"""
    service_pattern = re.compile(r"\w*service\(\'(.*?)\'\)\w*")

    stn_services = []
    hyp_services = []

    if "service" in sentence:
        stn_services = re.findall(service_pattern, sentence)

    if "service" in hypothesis:
        hyp_services = re.findall(service_pattern, hypothesis)

    sim = 0
    for i in stn_services:
        srv = nlp(i)
        for j in hyp_services:
            sim += srv.similarity(
                nlp(j)
            )  # 1 if i == j else 0  # srv.similarity(nlp(j))

    return sim


def num_services(sentence, hypothesis):
    """similarity of targets vectors"""
    service_pattern = re.compile(r"\w*service\(\'(.*?)\'\)\w*")

    stn_services = []
    hyp_services = []

    if "service" in sentence:
        stn_services = re.findall(service_pattern, sentence)

    if "service" in hypothesis:
        hyp_services = re.findall(service_pattern, hypothesis)

    return len(stn_services) + len(hyp_services)


def middleboxes(sentence, hypothesis):
    """similarity of targets vectors"""
    middlebox_pattern = re.compile(r"\w*middlebox\(\'(.*?)\'\)\w*")

    stn_mbs = []
    hyp_mbs = []

    if "middlebox" in sentence:
        stn_mbs = re.findall(middlebox_pattern, sentence)

    if "middlebox" in hypothesis:
        hyp_mbs = re.findall(middlebox_pattern, hypothesis)

    sim = 0
    for i in stn_mbs:
        mb = nlp(i)
        for j in hyp_mbs:
            sim += mb.similarity(nlp(j))  # 1 if i == j else 0  # mb.similarity(nlp(j))

    return sim


def num_middleboxes(sentence, hypothesis):
    """similarity of targets vectors"""
    middlebox_pattern = re.compile(r"\w*middlebox\(\'(.*?)\'\)\w*")

    stn_mbs = []
    hyp_mbs = []

    if "middlebox" in sentence:
        stn_mbs = re.findall(middlebox_pattern, sentence)

    if "middlebox" in hypothesis:
        hyp_mbs = re.findall(middlebox_pattern, hypothesis)

    return len(stn_mbs) + len(hyp_mbs)


def traffics(sentence, hypothesis):
    """similarity of targets vectors"""
    traffic_pattern = re.compile(r"\w*traffic\(\'(.*?)\'\)\w*")

    stn_traffic = []
    hyp_traffic = []

    if "traffic" in sentence:
        stn_traffic = re.findall(traffic_pattern, sentence)

    if "traffic" in hypothesis:
        hyp_traffic = re.findall(traffic_pattern, hypothesis)

    sim = 0
    for i in stn_traffic:
        trf = nlp(i)
        for j in hyp_traffic:
            sim += trf.similarity(
                nlp(j)
            )  # 1 if i == j else 0  # trf.similarity(nlp(j))

    return sim


def num_traffics(sentence, hypothesis):
    """similarity of targets vectors"""
    traffic_pattern = re.compile(r"\w*traffic\(\'(.*?)\'\)\w*")

    stn_traffic = []
    hyp_traffic = []

    if "traffic" in sentence:
        stn_traffic = re.findall(traffic_pattern, sentence)

    if "traffic" in hypothesis:
        hyp_traffic = re.findall(traffic_pattern, hypothesis)

    return len(stn_traffic) + len(hyp_traffic)


def protocols(sentence, hypothesis):
    """similarity of targets vectors"""
    protocol_pattern = re.compile(r"\w*protocol\(\'(.*?)\'\)\w*")

    stn_traffic = []
    hyp_traffic = []

    if "protocol" in sentence:
        stn_traffic = re.findall(protocol_pattern, sentence)

    if "protocol" in hypothesis:
        hyp_traffic = re.findall(protocol_pattern, hypothesis)

    sim = 0
    for i in stn_traffic:
        ptr = nlp(i)
        for j in hyp_traffic:
            sim += ptr.similarity(
                nlp(j)
            )  # 1 if i == j else 0  # ptr.similarity(nlp(j))

    return sim


def num_protocols(sentence, hypothesis):
    """similarity of targets vectors"""
    protocol_pattern = re.compile(r"\w*protocol\(\'(.*?)\'\)\w*")

    stn_traffic = []
    hyp_traffic = []

    if "protocol" in sentence:
        stn_traffic = re.findall(protocol_pattern, sentence)

    if "protocol" in hypothesis:
        hyp_traffic = re.findall(protocol_pattern, hypothesis)

    return len(stn_traffic) + len(hyp_traffic)


def groups(sentence, hypothesis):
    """similarity of targets vectors"""
    group_pattern = re.compile(r"\w*group\(\'(.*?)\'\)\w*")
    stn_group = []
    hyp_group = []

    if "group" in sentence:
        stn_group = re.findall(group_pattern, sentence)

    if "group" in hypothesis:
        hyp_group = re.findall(group_pattern, hypothesis)

    sim = 0
    for i in stn_group:
        group = nlp(i)
        for j in hyp_group:
            sim += 1 if i == j else 0  # group.similarity(nlp(j))

    return sim


def num_groups(sentence, hypothesis):
    """similarity of targets vectors"""
    group_pattern = re.compile(r"\w*group\(\'(.*?)\'\)\w*")
    stn_group = []
    hyp_group = []

    if "group" in sentence:
        stn_group = re.findall(group_pattern, sentence)

    if "group" in hypothesis:
        hyp_group = re.findall(group_pattern, hypothesis)

    return len(stn_group) + len(hyp_group)


def bandwidths(sentence, hypothesis):
    """similarity of targets vectors"""
    bandwidth_pattern = re.compile(r"\w*bandwidth\((.*?)\)\w*")

    stn_bandwidth = []
    hyp_bandwidth = []

    if "bandwidth" in sentence:
        stn_bandwidth = re.findall(bandwidth_pattern, sentence)

    if "bandwidth" in hypothesis:
        hyp_bandwidth = re.findall(bandwidth_pattern, hypothesis)

    sim = 0
    for i in stn_bandwidth:
        bw = nlp(i)
        for j in hyp_bandwidth:
            sim += bw.similarity(nlp(j))  # 1 if i == j else 0  # bw.similarity(nlp(j))

    return sim


def num_bandwidths(sentence, hypothesis):
    """similarity of targets vectors"""
    bandwidth_pattern = re.compile(r"\w*bandwidth\((.*?)\)\w*")

    stn_bandwidth = []
    hyp_bandwidth = []

    if "bandwidth" in sentence:
        stn_bandwidth = re.findall(bandwidth_pattern, sentence)

    if "bandwidth" in hypothesis:
        hyp_bandwidth = re.findall(bandwidth_pattern, hypothesis)

    return len(stn_bandwidth) + len(hyp_bandwidth)


def quotas(sentence, hypothesis):
    """similarity of targets vectors"""
    quota_pattern = re.compile(r"\w*quota\((.*?)\)\w*")

    stn_quota = []
    hyp_quota = []

    if "quota" in sentence:
        stn_quota = re.findall(quota_pattern, sentence)

    if "quota" in hypothesis:
        hyp_quota = re.findall(quota_pattern, hypothesis)

    sim = 0
    for i in stn_quota:
        quota = nlp(i)
        for j in hyp_quota:
            sim += quota.similarity(
                nlp(j)
            )  # 1 if i == j else 0  # quota.similarity(nlp(j))

    return sim


def num_quotas(sentence, hypothesis):
    """similarity of targets vectors"""
    quota_pattern = re.compile(r"\w*quota\((.*?)\)\w*")

    stn_quota = []
    hyp_quota = []

    if "quota" in sentence:
        stn_quota = re.findall(quota_pattern, sentence)

    if "quota" in hypothesis:
        hyp_quota = re.findall(quota_pattern, hypothesis)

    return len(stn_quota) + len(hyp_quota)


def get_features(sentence, hypothesis):
    """Return array with conflict features for the given sentence and hypothesis"""
    features = [
        path_similarity(sentence, hypothesis),
        qos(sentence, hypothesis),
        time(sentence, hypothesis),
        negation(sentence, hypothesis),
        synonyms(sentence, hypothesis),
        hierarchy_targets(sentence, hypothesis),
        hierarchy_traffics(sentence, hypothesis),
        endpoints(sentence, hypothesis),
        num_endpoints(sentence, hypothesis),
        services(sentence, hypothesis),
        num_services(sentence, hypothesis),
        groups(sentence, hypothesis),
        num_groups(sentence, hypothesis),
        traffics(sentence, hypothesis),
        num_traffics(sentence, hypothesis),
        protocols(sentence, hypothesis),
        num_protocols(sentence, hypothesis),
        middleboxes(sentence, hypothesis),
        num_middleboxes(sentence, hypothesis),
    ]
    return features
