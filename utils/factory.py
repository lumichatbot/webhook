""" Conflicts intent factories """

from random import randint

from nile import builder
from utils.sampler import (
    sample_entailing_qos,
    sample_conflicting_qos,
    sample_synonyms_endpoints,
    sample_entailing_endpoints,
    sample_conflicting_endpoints,
    sample_hierarchical_endpoints,
    sample_entailing_chaining,
    sample_conflicting_chaining,
    sample_entailing_rules,
    sample_conflicting_rules,
    sample_entailing_timeranges,
    sample_conflicting_timeranges)


def make_sfc_intent(return_entities=False):
    """ Creates a Nile intent with chaining"""
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, _ = sample_entailing_endpoints(sentence_entities, hypothesis_entities)
    sentence_entities, _ = sample_conflicting_chaining(sentence_entities, hypothesis_entities)

    if return_entities:
        return sentence_entities

    intent = {
        'type': 'sfc',
        'nile': builder.build(sentence_entities),
    }
    return intent


def make_qos_intent(return_entities=False):
    """ Creates a Nile intent with qos"""
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, _ = sample_entailing_endpoints(sentence_entities, hypothesis_entities)
    sentence_entities, _ = sample_entailing_qos(
        sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')

    if return_entities:
        return sentence_entities

    intent = {
        'type': 'qos',
        'nile': builder.build(sentence_entities),
    }
    return intent


def make_acl_intent(return_entities=False):
    """ Creates a Nile intent with acl"""
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, _ = sample_entailing_endpoints(sentence_entities, hypothesis_entities)
    sentence_entities, _ = sample_conflicting_rules(sentence_entities, hypothesis_entities)

    if return_entities:
        return sentence_entities

    intent = {
        'type': 'acl',
        'nile': builder.build(sentence_entities),
    }
    return intent


def make_temporal_intent(return_entities=False):
    """ Creates a Nile intent with time"""
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, _ = sample_entailing_endpoints(sentence_entities, hypothesis_entities)
    sentence_entities, _ = sample_entailing_timeranges(sentence_entities, hypothesis_entities)

    if return_entities:
        return sentence_entities

    intent = {
        'type': 'temporal',
        'nile': builder.build(sentence_entities),
    }
    return intent


def make_mixed_intent():
    """ Creates a Nile intent with mixed intents"""
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, _ = sample_entailing_endpoints(sentence_entities, hypothesis_entities)
    option = randint(0, 7)
    if option == 0:
        sentence_entities, _ = sample_entailing_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, _ = sample_entailing_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, _ = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    if option == 3:
        sentence_entities, _ = sample_entailing_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, _ = sample_entailing_rules(sentence_entities, hypothesis_entities)
    elif option == 4:
        sentence_entities, _ = sample_entailing_rules(sentence_entities, hypothesis_entities)
        sentence_entities, _ = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    elif option == 5:
        sentence_entities, _ = sample_entailing_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, _ = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    else:
        sentence_entities, _ = sample_entailing_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, _ = sample_entailing_rules(sentence_entities, hypothesis_entities)
        sentence_entities, _ = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')

    intent = {
        'type': 'mixed',
        'nile': builder.build(sentence_entities),
    }
    return intent


def make_path_entailment():
    """ Creates two Nile intents that entail each other due to non coference"""
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }

    option = randint(0, 2)
    if option == 0:
        sentence_entities = make_sfc_intent(True)
        hypothesis_entities = make_acl_intent(True)
    elif option == 1:
        sentence_entities = make_qos_intent(True)
        hypothesis_entities = make_acl_intent(True)
    elif option == 2:
        sentence_entities = make_qos_intent(True)
        hypothesis_entities = make_sfc_intent(True)

    entailment = {
        'type': 'path',
        'sentence': builder.build(sentence_entities),
        'hypothesis': builder.build(hypothesis_entities),
        'conflict': 0
    }
    return entailment


def make_time_entailment():
    """ Creates two Nile intents that entail each other with time constraints"""
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, hypothesis_entities = sample_conflicting_endpoints(sentence_entities, hypothesis_entities)
    option = randint(0, 2)
    if option == 0:
        # middleboxes
        if randint(1, 10) % 2 == 0:
            sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
        else:
            sentence_entities, hypothesis_entities = sample_conflicting_chaining(
                sentence_entities, hypothesis_entities)
    elif option == 1:
        # allow/block
        if randint(1, 10) % 2 == 0:
            sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
        else:
            sentence_entities, hypothesis_entities = sample_conflicting_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        # allow/block
        if randint(1, 10) % 2 == 0:
            sentence_entities, hypothesis_entities = sample_entailing_qos(sentence_entities, hypothesis_entities)
        else:
            sentence_entities, hypothesis_entities = sample_conflicting_qos(sentence_entities, hypothesis_entities)

    # start/end
    sentence_entities, hypothesis_entities = sample_entailing_timeranges(sentence_entities, hypothesis_entities)

    entailment = {
        'type': 'time',
        'sentence': builder.build(sentence_entities),
        'hypothesis': builder.build(hypothesis_entities),
        'conflict': 0
    }
    return entailment


def make_qos_entailment():
    """ Creates two Nile intents that entail each other with qos constraints """
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }

    sentence_entities, hypothesis_entities = sample_conflicting_endpoints(sentence_entities, hypothesis_entities)
    sentence_entities, hypothesis_entities = sample_entailing_qos(sentence_entities, hypothesis_entities)

    entailment = {
        'type': 'qos',
        'sentence': builder.build(sentence_entities),
        'hypothesis': builder.build(hypothesis_entities),
        'conflict': 0
    }
    return entailment


def make_negation_entailment():
    """ Creates two Nile intents that entail each other with negation """

    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, hypothesis_entities = sample_conflicting_endpoints(sentence_entities, hypothesis_entities)

    option = randint(0, 2)
    if option == 0:
        # add/remove
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        # allow/block
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        # set/unset
        sentence_entities, hypothesis_entities = sample_entailing_qos(sentence_entities, hypothesis_entities,
                                                                      stn_action='set', hyp_action='unset')

    if 'allow' in sentence_entities['operations'] or 'block' in sentence_entities['operations']:
        if randint(0, 2) % 2 == 0:
            sentence_entities['operations'].append('add')
            sentence_entities['middleboxes'] = ['firewall']

        if randint(0, 2) % 2 == 0:
            hypothesis_entities['operations'].append('add')
            hypothesis_entities['middleboxes'] = ['firewall']

    entailment = {
        'type': 'negation',
        'sentence': builder.build(sentence_entities),
        'hypothesis': builder.build(hypothesis_entities),
        'conflict': 0
    }
    return entailment


def make_synonym_entailment():
    """ Creates two Nile intents that entail each other with synonyms use """
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, hypothesis_entities = sample_synonyms_endpoints(sentence_entities, hypothesis_entities)
    option = randint(0, 2)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, hypothesis_entities = sample_entailing_qos(sentence_entities, hypothesis_entities,
                                                                      stn_action='set', hyp_action='unset')

    entailment = {
        'type': 'synonym',
        'sentence': builder.build(sentence_entities),
        'hypothesis': builder.build(hypothesis_entities),
        'conflict': 0
    }

    return entailment


def make_hierarchical_entailment():
    """ Creates two Nile intents that entail each other with group hierarchy """
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, hypothesis_entities = sample_hierarchical_endpoints(sentence_entities, hypothesis_entities)

    option = randint(0, 2)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, hypothesis_entities = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')

    entailment = {
        'type': 'hierarchical',
        'sentence': builder.build(sentence_entities),
        'hypothesis': builder.build(hypothesis_entities),
        'conflict': 0
    }
    return entailment


def make_path_conflict():
    """ Creates two Nile intents that contradict each other due to path overlap"""
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }

    sentence_entities, hypothesis_entities = sample_conflicting_endpoints(sentence_entities, hypothesis_entities)

    option = randint(0, 2)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_conflicting_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_conflicting_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, hypothesis_entities = sample_conflicting_qos(sentence_entities, hypothesis_entities,
                                                                        stn_action='set', hyp_action='unset')

    entailment = {
        'type': 'path',
        'sentence': builder.build(sentence_entities),
        'hypothesis': builder.build(hypothesis_entities),
        'conflict': 1
    }
    return entailment


def make_time_conflict():
    """ Creates two Nile intents that contradict each other due to time constraints"""
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, hypothesis_entities = sample_conflicting_endpoints(sentence_entities, hypothesis_entities)

    option = randint(0, 2)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_conflicting_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_conflicting_rules(sentence_entities, hypothesis_entities)
    else:
        sentence_entities, hypothesis_entities = sample_conflicting_qos(sentence_entities, hypothesis_entities)

    # start/end
    sentence_entities, hypothesis_entities = sample_conflicting_timeranges(sentence_entities, hypothesis_entities)

    conflict = {
        'type': 'time',
        'sentence': builder.build(sentence_entities),
        'hypothesis': builder.build(hypothesis_entities),
        'conflict': 1
    }
    return conflict


def make_qos_conflict():
    """ Creates two Nile intents that contradict each other due to qos constraints """
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }

    if randint(0, 2) % 2 == 0:
        sentence_entities, hypothesis_entities = sample_conflicting_endpoints(sentence_entities, hypothesis_entities)
    else:
        sentence_entities, hypothesis_entities = sample_hierarchical_endpoints(sentence_entities, hypothesis_entities)

    if randint(0, 2) % 2 == 0:
        sentence_entities, hypothesis_entities = sample_conflicting_qos(sentence_entities, hypothesis_entities)
    else:
        sentence_entities, hypothesis_entities = sample_conflicting_qos(sentence_entities, hypothesis_entities,
                                                                        stn_action='set', hyp_action='unset')

    conflict = {
        'type': 'qos',
        'sentence': builder.build(sentence_entities),
        'hypothesis': builder.build(hypothesis_entities),
        'conflict': 1
    }
    return conflict


def make_negation_conflict():
    """ Creates two Nile intents that contradict each other due to negation """
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, hypothesis_entities = sample_conflicting_endpoints(sentence_entities, hypothesis_entities)
    option = randint(0, 2)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_conflicting_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_conflicting_rules(sentence_entities, hypothesis_entities)
    else:
        sentence_entities, hypothesis_entities = sample_conflicting_qos(sentence_entities, hypothesis_entities,
                                                                        stn_action='set', hyp_action='unset')

    conflict = {
        'type': 'negation',
        'sentence': builder.build(sentence_entities),
        'hypothesis': builder.build(hypothesis_entities),
        'conflict': 1
    }
    return conflict


def make_synonym_conflict():
    """ Creates two Nile intents that contradict each other due to synonyms use """
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, hypothesis_entities = sample_synonyms_endpoints(sentence_entities, hypothesis_entities)
    option = randint(0, 2)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_conflicting_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_conflicting_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, hypothesis_entities = sample_conflicting_qos(sentence_entities, hypothesis_entities,
                                                                        stn_action='set', hyp_action='unset')

    conflict = {
        'type': 'synonym',
        'sentence': builder.build(sentence_entities),
        'hypothesis': builder.build(hypothesis_entities),
        'conflict': 1
    }
    return conflict


def make_hierarchical_conflict():
    """ Creates two Nile intents that contradict each other due to group hierarchy """
    sentence_entities = {
        "id": "stn",
        "operations": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "operations": []
    }
    sentence_entities, hypothesis_entities = sample_hierarchical_endpoints(sentence_entities, hypothesis_entities)
    option = randint(0, 3)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_conflicting_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_conflicting_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, hypothesis_entities = sample_conflicting_qos(sentence_entities, hypothesis_entities,
                                                                        stn_action='set', hyp_action='unset')

    conflict = {
        'type': 'hierarchical',
        'sentence': builder.build(sentence_entities),
        'hypothesis': builder.build(hypothesis_entities),
        'conflict': 1
    }
    return conflict


ENTAILMENT_FACTORY = [
    make_qos_entailment,
    make_time_entailment,
    make_synonym_entailment,
    make_hierarchical_entailment,
    make_negation_entailment,
    make_path_entailment
]

CONFLICTS_FACTORY = [
    make_qos_conflict,
    make_time_conflict,
    make_synonym_conflict,
    make_hierarchical_conflict,
    make_negation_conflict,
    make_path_conflict
]

NILE_FACTORY = [
    make_sfc_intent,
    make_qos_intent,
    make_temporal_intent,
    make_acl_intent,
    make_mixed_intent,
]
