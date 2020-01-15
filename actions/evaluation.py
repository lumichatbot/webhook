""" Information extraction evaluation """

import time
import csv

from random import sample, shuffle
from math import ceil

from api import Dialogflow
from utils import dataset, config

INTENT_ID = '64cdfdeb-18dd-4c76-be0a-4b55021ad1eb'

END_TRAINING = None


def recall(result):
    """ calculates recall for given intent result """
    return (float(result['tp']) / (result['tp'] + result['fn'])) if (result['tp'] + result['fn']) != 0 else 0.


def precision(result):
    """ calculates precision for given intent result """
    return (float(result['tp']) / (result['tp'] + result['fp'])) if (result['tp'] + result['fp']) != 0 else 0.


def f1_score(result):
    """ calculates f1 score for given intent result """
    denominator = precision(result) + recall(result)
    return (2 * ((precision(result) * recall(result)) / denominator)) if denominator > 0. else 0.


def training_callback(operation):
    """ callback indicating the training is done """
    global END_TRAINING
    while not operation.done():
        print("Training")
    print('Training ended.')
    END_TRAINING = time.time()


def feedback():
    """ opens alpha dataset, splits 75-25 percent for train-test, then opens campi dataset to use as feedback """
    print("FEEDBACK ",)
    global END_TRAINING

    diag = Dialogflow()
    alpha_data = dataset.read('extraction', 'alpha')['intents']
    campi_data = dataset.read('extraction', 'campi')['intents']

    alpha_intents = []
    for case in alpha_data:
        intent = []
        for part in case['parts']:
            if 'entity_type' in part and not 'alias' in part:
                part['alias'] = part['entity_type'][1:]
            intent.append(part)
        alpha_intents.append(intent)

    campi_intents = []
    for case in campi_data:
        intent = []
        for part in case['parts']:
            if 'entity_type' in part and not 'alias' in part:
                part['alias'] = part['entity_type'][1:]
            intent.append(part)
        campi_intents.append(intent)

    print("DATASET CASES ALPHA #", len(alpha_intents))
    print("DATASET CASES CAMPI #", len(campi_intents))

    diag.update_intent(INTENT_ID, alpha_intents, False)
    training_begin = diag.train_agent(training_callback)

    time_elapsed = None
    while True:
        if END_TRAINING:
            time_elapsed = (END_TRAINING - training_begin)
            print("Training time: ", time_elapsed)
            break
        time.sleep(60)

    print("Testing...")

    results = []
    shuffle(campi_intents)
    for idx, feedback_case in enumerate(campi_intents):
        print("intent", idx)
        result = diag.detect_intent_texts([feedback_case])[0]
        rec = recall(result)
        prec = precision(result)
        f1_sc = f1_score(result)
        print(result['text'])
        print('recall: ', rec)
        print('precision: ', prec)
        print('f1_score: ', f1_sc)
        results.append((idx, result['text'], result['recognized_entities'], result['tp'],
                        result['tn'], result['fp'], result['fn'], rec, prec, f1_sc))

        if result['fp'] != 0 or result['fn'] != 0:
            alpha_intents.append(feedback_case)
            print("DATASET CASES ALPHA #", len(alpha_intents))

            diag.update_intent(INTENT_ID, alpha_intents, False)
            END_TRAINING = None
            training_begin = diag.train_agent(training_callback)

            time_elapsed = None
            while True:
                if END_TRAINING:
                    time_elapsed = (END_TRAINING - training_begin)
                    print("Training time: ", time_elapsed)
                    break

    with open(config.EXTRACTION_RESULTS_PATH.format('feedback'), 'wb') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(["feedback_round", "text", "recognized_entities", "training_time",
                             "tp", "tn", "fp", "fn", "recall", "precision", "f1_score"])
        for (idx, intent, rec_entities, tp, tn, fp, fn, rec, prec, f1_sc) in results:
            csv_writer.writerow([idx, intent, rec_entities, time_elapsed, tp, tn, fp, fn, rec, prec, f1_sc])


def train(dtype):
    """ opens specific dataset and trains agent with it """
    print("DATASET ", dtype)
    data = dataset.read('extraction', dtype)['intents']
    intents = []
    for case in data:
        intent = []
        for part in case['parts']:
            if 'entity_type' in part and not 'alias' in part:
                part['alias'] = part['entity_type'][1:]
            intent.append(part)
        intents.append(intent)

    print("DATASET CASES #", len(intents))

    diag = Dialogflow()
    diag.update_intent(INTENT_ID, intents, False)
    training_begin = diag.train_agent(training_callback)


def run(dtype):
    """ opens specific dataset, splits 75-25 percent for train-test and runs extraction """
    print("DATASET ", dtype)
    global END_TRAINING
    data = dataset.read('extraction', dtype)['intents']
    intents = []
    for case in data:
        intent = []
        for part in case['parts']:
            if 'entity_type' in part and not 'alias' in part:
                part['alias'] = part['entity_type'][1:]
            intent.append(part)
        intents.append(intent)

    print("DATASET CASES #", len(intents))

    n_samples = int(ceil(len(intents) * 0.75))
    training = sample(intents, n_samples)
    validation = sample(intents, len(intents) - n_samples)

    diag = Dialogflow()
    diag.update_intent(INTENT_ID, training, False)
    training_begin = diag.train_agent(training_callback)

    time_elapsed = None
    while True:
        if END_TRAINING:
            time_elapsed = (END_TRAINING - training_begin)
            print("Training time: ", time_elapsed)
            break
        # time.sleep(50)

    print("Testing...")

    results = diag.detect_intent_texts(validation)
    with open(config.EXTRACTION_RESULTS_PATH.format(dtype), 'wb') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(["text", "recognized_entities", "training_time", "recall", "precision", "f1_score"])
        for result in results:
            rec = recall(result)
            prec = precision(result)
            f1_sc = f1_score(result)
            print(result['text'])
            print('recall: ', rec)
            print('precision: ', prec)
            print('f1_score: ', f1_sc)
            csv_writer.writerow([result['text'], result['recognized_entities'], time_elapsed, rec, prec, f1_sc])


if __name__ == '__main__':
    train('alpha')
    # run('alpha')
    # run('campi')
    # run('both')
    # feedback()
