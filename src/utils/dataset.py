""" Contradiction dataset generator """

import json
from random import randint

from config import EXTRACTION_DATASET_PATH, CONTRADICTIONS_DATASET_PATH, COMPILATION_DATASET_PATH, DATASET_SIZES
from factory import CONTRADICTION_FACTORY, ENTAILMENT_FACTORY, NILE_FACTORY


def make_entailment():
    """ Creates two Nile intents that entail (do not contradict) each other """
    return ENTAILMENT_FACTORY[randint(0, len(ENTAILMENT_FACTORY) - 1)]()


def make_contradiction():
    """ Creates two Nile intents that contradict each other """
    return CONTRADICTION_FACTORY[randint(0, len(CONTRADICTION_FACTORY) - 1)]()


def write_compilation():
    """ Creates dataset of contradicting Nile intents """
    dataset = []
    for i in range(30):
        for nile_fact in NILE_FACTORY:
            print "DATASET ENTRY #{}".format(i)
            value = nile_fact()
            dataset.append(value)

    with open(COMPILATION_DATASET_PATH, 'w') as dataset_file:
        json.dump(dataset, dataset_file, indent=4, sort_keys=True)


def write(dataset_size):
    """ Creates dataset of contradicting Nile intents """
    dataset = {
        "summary": {
            "contradiction": {
                "count": 0,
                "byType": {
                    "qos": 0,
                    "time": 0,
                    "synonym": 0,
                    "hierarchical": 0,
                    "domain": 0,
                    "negation": 0
                }
            },
            "entailment": {
                "count": 0,
                "byType": {
                    "qos": 0,
                    "time": 0,
                    "synonym": 0,
                    "hierarchical": 0,
                    "domain": 0,
                    "negation": 0,
                    "non_coreferent": 0
                }
            }
        },
        "content": []
    }

    for i in range(dataset_size):
        print "DATASET ENTRY #{}".format(i)
        value = make_contradiction() if randint(0, 100) % 2 == 0 else make_entailment()
        value_class = "contradiction" if value['contradiction'] else "entailment"
        dataset['summary'][value_class]['count'] += 1
        dataset['summary'][value_class]['byType'][value['type']] += 1
        dataset['content'].append(value)

    with open(CONTRADICTIONS_DATASET_PATH.format(dataset_size), 'w') as dataset_file:
        json.dump(dataset, dataset_file, indent=4, sort_keys=True)


def read(dtype, dname):
    """ opens dataset file of given type and returns dict """
    dataset = {}
    if dtype == 'contradictions':
        with open(CONTRADICTIONS_DATASET_PATH.format(dname), 'r') as dataset_file:
            dataset = json.load(dataset_file)
    elif dtype == 'extraction':
        with open(EXTRACTION_DATASET_PATH.format(dname), 'r') as dataset_file:
            dataset = json.load(dataset_file)
    elif dtype == 'compilation':
        with open(COMPILATION_DATASET_PATH, 'r') as dataset_file:
            dataset = json.load(dataset_file)

    return dataset


if __name__ == "__main__":
    # for d_size in DATASET_SIZES:
    #     write(d_size)
    # write(10000)
    write_compilation()
