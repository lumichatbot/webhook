""" Contradiction and Entailement intent factories """

from random import randint

from nile import interpreter
from sampler import (
    sample_entailing_qos,
    sample_contradicting_qos,
    sample_synonyms_endpoints,
    sample_entailing_endpoints,
    sample_contradicting_endpoints,
    sample_hierarchical_endpoints,
    sample_entailing_chaining,
    sample_contradicting_chaining,
    sample_entailing_rules,
    sample_contradicting_rules,
    sample_entailing_timeranges,
    sample_contradicting_timeranges)


def make_sfc_intent():
    """ Creates a Nile intent with chaining"""
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, _ = sample_entailing_endpoints(sentence_entities, hypothesis_entities)
    sentence_entities, _ = sample_contradicting_chaining(sentence_entities, hypothesis_entities)

    intent = {
        'type': 'sfc',
        'nile': interpreter.translate(sentence_entities),
    }
    return intent


def make_qos_intent():
    """ Creates a Nile intent with qos"""
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, _ = sample_entailing_endpoints(sentence_entities, hypothesis_entities)
    sentence_entities, _ = sample_entailing_qos(
        sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')

    intent = {
        'type': 'qos',
        'nile': interpreter.translate(sentence_entities),
    }
    return intent


def make_acl_intent():
    """ Creates a Nile intent with acl"""
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, _ = sample_entailing_endpoints(sentence_entities, hypothesis_entities)
    sentence_entities, _ = sample_contradicting_rules(sentence_entities, hypothesis_entities)

    intent = {
        'type': 'acl',
        'nile': interpreter.translate(sentence_entities),
    }
    return intent


def make_temporal_intent():
    """ Creates a Nile intent with time"""
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, _ = sample_entailing_endpoints(sentence_entities, hypothesis_entities)
    sentence_entities, _ = sample_entailing_timeranges(sentence_entities, hypothesis_entities)

    intent = {
        'type': 'temporal',
        'nile': interpreter.translate(sentence_entities),
    }
    return intent


def make_mixed_intent():
    """ Creates a Nile intent with mixed intents"""
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
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
        'nile': interpreter.translate(sentence_entities),
    }
    return intent


def make_non_coreferent_entailment():
    """ Creates two Nile intents that entail each other due to non coference"""
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, hypothesis_entities = sample_entailing_endpoints(sentence_entities, hypothesis_entities)

    if randint(0, 10) % 2 == 0:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)

    if randint(0, 10) % 2 == 0:
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)

    if randint(0, 10) % 2 == 0:
        sentence_entities, hypothesis_entities = sample_entailing_qos(sentence_entities, hypothesis_entities)
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_qos(sentence_entities, hypothesis_entities)

    if randint(0, 10) % 2 == 0:
        sentence_entities, hypothesis_entities = sample_entailing_timeranges(sentence_entities, hypothesis_entities)

    entailment = {
        'type': 'non_coreferent',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 0
    }
    return entailment


def make_time_entailment():
    """ Creates two Nile intents that entail each other with time constraints"""
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, hypothesis_entities = sample_contradicting_endpoints(sentence_entities, hypothesis_entities)
    # middleboxes
    if randint(1, 10) % 2 == 0:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
    # allow/block
    if randint(1, 10) % 2 == 0:
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)

    # start/end
    sentence_entities, hypothesis_entities = sample_entailing_timeranges(sentence_entities, hypothesis_entities)

    entailment = {
        'type': 'time',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 0
    }
    return entailment


def make_qos_entailment():
    """ Creates two Nile intents that entail each other with qos constraints """
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, hypothesis_entities = sample_contradicting_endpoints(sentence_entities, hypothesis_entities)
    sentence_entities, hypothesis_entities = sample_entailing_qos(sentence_entities, hypothesis_entities)

    entailment = {
        'type': 'qos',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 0
    }
    return entailment


def make_negation_entailment():
    """ Creates two Nile intents that entail each other with negation """

    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, hypothesis_entities = sample_contradicting_endpoints(sentence_entities, hypothesis_entities)
    # middleboxes
    sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
    # allow/block
    sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
    # set/unset
    sentence_entities, hypothesis_entities = sample_entailing_qos(sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')

    entailment = {
        'type': 'negation',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 0
    }
    return entailment


def make_synonym_entailment():
    """ Creates two Nile intents that entail each other with synonyms use """
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, hypothesis_entities = sample_synonyms_endpoints(sentence_entities, hypothesis_entities)
    option = randint(0, 7)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, hypothesis_entities = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    if option == 3:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
    elif option == 4:
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    elif option == 5:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    else:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')

    entailment = {
        'type': 'synonym',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 0
    }

    return entailment


def make_hierarchical_entailment():
    """ Creates two Nile intents that entail each other with group hierarchy """
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, hypothesis_entities = sample_hierarchical_endpoints(sentence_entities, hypothesis_entities)

    option = randint(0, 7)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, hypothesis_entities = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    if option == 3:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
    elif option == 4:
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    elif option == 5:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    else:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_entailing_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')

    entailment = {
        'type': 'hierarchical',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 0
    }
    return entailment


def make_domain_entailment():
    """ Creates two Nile intents that entail each other with domains """
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, hypothesis_entities = sample_entailing_endpoints(sentence_entities, hypothesis_entities, mixed=True)
    option = randint(0, 7)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    if option == 3:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
    elif option == 4:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    elif option == 5:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')

    entailment = {
        'type': 'domain',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 0
    }
    return entailment


def make_time_contradiction():
    """ Creates two Nile intents that contradict each other due to time constraints"""
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, hypothesis_entities = sample_contradicting_endpoints(sentence_entities, hypothesis_entities)
    # middleboxes
    if randint(1, 10) % 2 == 0:
        sentence_entities, hypothesis_entities = sample_entailing_chaining(sentence_entities, hypothesis_entities)
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
    # allow/block
    if randint(1, 10) % 2 == 0:
        sentence_entities, hypothesis_entities = sample_entailing_rules(sentence_entities, hypothesis_entities)
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)

    # qos
    if randint(1, 10) % 2 == 0:
        sentence_entities, hypothesis_entities = sample_entailing_qos(sentence_entities, hypothesis_entities)
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_qos(sentence_entities, hypothesis_entities)

    # start/end
    sentence_entities, hypothesis_entities = sample_contradicting_timeranges(sentence_entities, hypothesis_entities)

    contradiction = {
        'type': 'time',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 1
    }
    return contradiction


def make_qos_contradiction():
    """ Creates two Nile intents that contradict each other due to qos constraints """
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }

    sentence_entities, hypothesis_entities = sample_contradicting_endpoints(sentence_entities, hypothesis_entities)
    sentence_entities, hypothesis_entities = sample_contradicting_qos(sentence_entities, hypothesis_entities)

    contradiction = {
        'type': 'qos',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 1
    }
    return contradiction


def make_negation_contradiction():
    """ Creates two Nile intents that contradict each other due to negation """
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, hypothesis_entities = sample_contradicting_endpoints(sentence_entities, hypothesis_entities)
    option = randint(0, 7)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    if option == 3:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
    elif option == 4:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    elif option == 5:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')

    contradiction = {
        'type': 'negation',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 1
    }
    return contradiction


def make_synonym_contradiction():
    """ Creates two Nile intents that contradict each other due to synonyms use """
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, hypothesis_entities = sample_synonyms_endpoints(sentence_entities, hypothesis_entities)
    option = randint(0, 7)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    if option == 3:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
    elif option == 4:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    elif option == 5:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')

    contradiction = {
        'type': 'synonym',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 1
    }
    return contradiction


def make_hierarchical_contradiction():
    """ Creates two Nile intents that contradict each other due to group hierarchy """
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, hypothesis_entities = sample_hierarchical_endpoints(sentence_entities, hypothesis_entities)
    option = randint(0, 7)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    if option == 3:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
    elif option == 4:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    elif option == 5:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')

    contradiction = {
        'type': 'hierarchical',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 1
    }
    return contradiction


def make_domain_contradiction():
    """ Creates two Nile intents that contradict each other due to domains """
    sentence_entities = {
        "id": "stn",
        "actions": []
    }
    hypothesis_entities = {
        "id": "hyp",
        "actions": []
    }
    sentence_entities, hypothesis_entities = sample_contradicting_endpoints(sentence_entities, hypothesis_entities, mixed=True)
    option = randint(0, 7)
    if option == 0:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
    elif option == 1:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
    elif option == 2:
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    if option == 3:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
    elif option == 4:
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    elif option == 5:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')
    else:
        sentence_entities, hypothesis_entities = sample_contradicting_chaining(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_rules(sentence_entities, hypothesis_entities)
        sentence_entities, hypothesis_entities = sample_contradicting_qos(
            sentence_entities, hypothesis_entities, stn_action='set', hyp_action='unset')

    contradiction = {
        'type': 'domain',
        'sentence': interpreter.translate(sentence_entities),
        'hypothesis': interpreter.translate(hypothesis_entities),
        'contradiction': 1
    }
    return contradiction


ENTAILMENT_FACTORY = [
    make_qos_entailment,
    make_time_entailment,
    make_synonym_entailment,
    make_hierarchical_entailment,
    make_domain_entailment,
    make_negation_entailment,
    make_non_coreferent_entailment
]

CONTRADICTION_FACTORY = [
    make_qos_contradiction,
    make_time_contradiction,
    make_synonym_contradiction,
    make_hierarchical_contradiction,
    make_domain_contradiction,
    make_negation_contradiction
]

NILE_FACTORY = [
    make_sfc_intent,
    make_qos_intent,
    make_temporal_intent,
    make_acl_intent,
    make_mixed_intent,
]
