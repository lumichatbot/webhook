""" Contradiction dataset generator """

import json
import csv
from random import randint

from utils.config import EXTRACTION_DATASET_PATH, CONFLICTS_DATASET_PATH, COMPILATION_DATASET_PATH, CONFLICTS_CAMPI_DATASET_PATH,  DATASET_SIZES
from utils.factory import CONFLICTS_FACTORY, ENTAILMENT_FACTORY, NILE_FACTORY


def make_entailment():
    """ Creates two Nile intents that entail (do not contradict) each other """
    return ENTAILMENT_FACTORY[randint(0, len(ENTAILMENT_FACTORY) - 1)]()


def make_contradiction():
    """ Creates two Nile intents that contradict each other """
    return CONFLICTS_FACTORY[randint(0, len(CONFLICTS_FACTORY) - 1)]()


def write_compilation():
    """ Creates dataset of contradicting Nile intents """
    dataset = []
    for i in range(30):
        for nile_fact in NILE_FACTORY:
            print("DATASET ENTRY #{}".format(i))
            value = nile_fact()
            dataset.append(value)

    with open(COMPILATION_DATASET_PATH, "w") as dataset_file:
        json.dump(dataset, dataset_file, indent=4, sort_keys=True)


def write(dataset_size):
    """ Creates dataset of contradicting Nile intents """
    dataset = {
        "summary": {
            "contradiction": {
                "count": 0,
                "byType": {
                    "path": 0,
                    "qos": 0,
                    "time": 0,
                    "synonym": 0,
                    "hierarchical": 0,
                    "negation": 0
                }
            },
            "entailment": {
                "count": 0,
                "byType": {
                    "path": 0,
                    "qos": 0,
                    "time": 0,
                    "synonym": 0,
                    "hierarchical": 0,
                    "negation": 0
                }
            }
        },
        "content": []
    }

    for i in range(dataset_size):
        print("DATASET ENTRY #{}".format(i))
        value = make_contradiction() if i % 2 == 0 else make_entailment()
        value_class = "contradiction" if value["contradiction"] else "entailment"
        dataset["summary"][value_class]["count"] += 1
        dataset["summary"][value_class]["byType"][value["type"]] += 1
        dataset["content"].append(value)

    with open(CONFLICTS_DATASET_PATH.format(dataset_size), "w") as dataset_file:
        json.dump(dataset, dataset_file, indent=4, sort_keys=True)


def read(dtype, dname, dsuffix=None):
    """ opens dataset file of given type and returns dict """
    dataset = {}
    if dtype == "conflicts":
        if dsuffix:
            with open(CONFLICTS_CAMPI_DATASET_PATH.format(dname, dsuffix), "r") as dataset_file:
                dataset = json.load(dataset_file)
        else:
            with open(CONFLICTS_DATASET_PATH.format(dname), "r") as dataset_file:
                dataset = json.load(dataset_file)
    elif dtype == "extraction":
        with open(EXTRACTION_DATASET_PATH.format(dname), "r") as dataset_file:
            dataset = json.load(dataset_file)
    elif dtype == "compilation":
        with open(COMPILATION_DATASET_PATH, "r") as dataset_file:
            dataset = json.load(dataset_file)

    return dataset


def convert():
    """ Method to convert Dialogflow files into dataset format """

    df_intents = []
    dataset = {
        "intents": []
    }
    with open("../res/build_usersays_en.json", "r") as df_intents_file:
        df_intents = json.load(df_intents_file)

        for intent in df_intents:
            entry = {
                "text": "",
                "parts": []
            }
            text = ""
            for data in intent["data"]:
                text += data["text"]
                part_of_speech = {
                    "text": data["text"],
                }
                if "meta" in data:
                    part_of_speech["entity_type"] = data["meta"]

                if "alias" in data:
                    part_of_speech["alias"] = data["alias"]

                entry["parts"].append(part_of_speech)
            entry["text"] = text
            dataset["intents"].append(entry)

    with open(EXTRACTION_DATASET_PATH.format("converted"), "w") as dataset_file:
        json.dump(dataset, dataset_file, indent=4, sort_keys=True)


def write_conflicts_campi():
    """ pairs intents in the campi dataset """
    dset = read('extraction', 'campi')
    intents = []
    for itnt in dset['intents']:
        intents.append((itnt['university'], itnt['text'], itnt['nile']))

    dset_by_uni = read('conflicts', 'campi', 'uni')
    conflicts_by_uni = {}
    for contradiction in dset_by_uni:
        if contradiction['university'] not in conflicts_by_uni:
            conflicts_by_uni[contradiction['university']] = []
        conflicts_by_uni[contradiction['university']].append(contradiction)

    dataset = []
    for i in range(len(intents)):
        (uni_stn, text_stn, sentence) = intents[i]
        for j in range(i + 1, len(intents)):
            (uni_hyp, text_hyp, hypothesis) = intents[j]
            if sentence != hypothesis:
                case = {}
                if uni_stn == uni_hyp:
                    # get case already labeled from other dataset
                    for entry in conflicts_by_uni[uni_stn]:
                        if ((entry['sentence']['text'] == text_stn and entry['hypothesis']['text'] == text_hyp) or
                                (entry['sentence']['text'] == text_hyp and entry['hypothesis']['text'] == text_stn)):
                            case = {
                                "sentence": {
                                    "university": uni_stn,
                                    "text": text_stn,
                                    "nile": sentence,
                                },
                                "hypothesis": {
                                    "university": uni_hyp,
                                    "text": text_hyp,
                                    "nile": hypothesis
                                },
                                "contradiction": entry["contradiction"],
                                "type": entry["type"],
                                "imported": True
                            }

                    if not case:
                        print("SOMETHING IS WRONG.")
                else:
                    case = {
                        "sentence": {
                            "university": uni_stn,
                            "text": text_stn,
                            "nile": sentence,
                        },
                        "hypothesis": {
                            "university": uni_hyp,
                            "text": text_hyp,
                            "nile": hypothesis
                        },
                        "contradiction": 0,
                        "type": "path"
                    }
                dataset.append(case)

    with open(CONFLICTS_CAMPI_DATASET_PATH.format('campi', 'all'), 'w') as dataset_file:
        json.dump(dataset, dataset_file, indent=4, sort_keys=True)


def write_conflicts_campi_by_uni():
    """ pairs intents in the campi dataset """
    dset = read('extraction', 'campi')

    intents = {}
    for case in dset['intents']:
        if case['university'] not in intents:
            intents[case['university']] = []
        intents[case['university']].append((case['university'], case['text'], case['nile']))

    dataset = []
    for (uni, intents) in intents.items():
        print(uni, len(intents))
        for i in range(len(intents)):
            (uni_stn, text_stn, sentence) = intents[i]
            for j in range(i + 1, len(intents)):
                (uni_hyp, text_hyp, hypothesis) = intents[j]
                if sentence != hypothesis:
                    case = {
                        "university": uni_stn,
                        "sentence": {
                            "text": text_stn,
                            "nile": sentence,
                        },
                        "hypothesis": {
                            "text": text_hyp,
                            "nile": hypothesis
                        },
                        "contradiction": 0,
                        "type": "path"
                    }
                    dataset.append(case)

    with open(CONFLICTS_CAMPI_DATASET_PATH.format('campi', 'uni'), 'w') as dataset_file:
        json.dump(dataset, dataset_file, indent=4, sort_keys=True)


if __name__ == "__main__":
    convert()
    # for d_size in DATASET_SIZES:
    #     write(d_size)
    # write(100)
    # write(1000)
    # write(2500)
    # write(5000)
    # write(10000)

    # write_conflicts_campi_by_uni()
    # write_conflicts_campi()

    # write_compilation()
