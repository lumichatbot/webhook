""" Information extraction evaluation """

import time
import csv

from scipy.stats import sem, t
from scipy import mean

from random import sample, shuffle
from math import ceil, floor

from api import Dialogflow
from utils import dataset, config, metrics

INTENT_ID = '64cdfdeb-18dd-4c76-be0a-4b55021ad1eb'

END_TRAINING = None


def training_callback(operation):
    """ callback indicating the training is done """
    global END_TRAINING
    while not operation.done():
        print("Training")
    print('Training ended.')
    END_TRAINING = time.time()


def feedback():
    """ opens alpha dataset, splits 75-25 percent for train-feedback """
    print("FEEDBACK")
    global END_TRAINING

    diag = Dialogflow()
    all_data = dataset.read('extraction', 'both')['intents']

    all_intents = []
    for case in all_data:
        intent = []
        for part in case['parts']:
            intent.append(part)
        all_intents.append(intent)

    num_repeats = 1

    with open(config.EXTRACTION_RESULTS_PATH.format('feedback', 'single'), 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(["repeat", "feedback_round", "text", "recognized_entities",
                             "expected_entities", "tp", "fp", "fn", "recall", "precision", "f1_score"])

        for repeat in range(num_repeats):
            n_samples = int(floor(len(all_intents) * 0.25))
            training = sample(all_intents, n_samples)
            feedback = sample(all_intents, len(all_intents) - n_samples)

            print("DATASET CASES TRAIN #", len(training))
            print("DATASET CASES FEEDBACK #", len(feedback))

            diag.update_intent(INTENT_ID, training, False)
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
            shuffle(feedback)
            for idx, feedback_case in enumerate(feedback):
                print("intent", idx)
                result = diag.detect_intent_texts([feedback_case])[0]
                rec = metrics.recall(result['tp'], result['fn'])
                prec = metrics.precision(result['tp'], result['fp'])
                f1_sc = metrics.f1_score(prec, rec)
                print(result['text'])
                print('recall: ', rec)
                print('precision: ', prec)
                print('f1_score: ', f1_sc)

                csv_writer.writerow([repeat, idx, result['text'],
                                     result['recognized_entities'], result['expected_entities'],
                                     result['tp'], result['fp'], result['fn'], rec, prec, f1_sc])

                if result['fp'] != 0 or result['fn'] != 0:
                    training.append(feedback_case)
                    print("DATASET CASES TRAIN #", len(training))

                    diag.update_intent(INTENT_ID, training, False)
                    END_TRAINING = None
                    training_begin = diag.train_agent(training_callback)

                    time_elapsed = None
                    while True:
                        if END_TRAINING:
                            time_elapsed = (END_TRAINING - training_begin)
                            print("Training time: ", time_elapsed)
                            break
                        time.sleep(60)

            csv_writer.writerow(["DATASET CASES TRAIN #", len(training)])


def mean_feedback():
    """ Opens all executions file and calculates mean preicions and recall """
    mean_precision = {}
    mean_recall = {}
    confidence_interval = {}

    num_repeats = 30
    confidence = 0.95
    with open(config.EXTRACTION_RESULTS_PATH.format('feedback', 'all'), 'r') as csvfile:
        all_feedback = csv.reader(csvfile, delimiter=',')
        for row in all_feedback:
            try:
                repeat = int(row[0])
                idx = int(row[1])
                if idx not in mean_precision:
                    mean_precision[idx] = []
                    mean_recall[idx] = []

                rec = float(row[8])
                prec = float(row[9])
                mean_precision[idx].append(prec)
                mean_recall[idx].append(rec)
            except:
                print(row)

    with open(config.EXTRACTION_RESULTS_PATH.format('feedback', 'mean'), 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(["idx", "mean_precision", "prec_ci_start", "prec_ci_end",
                                    "mean_recall", "rec_ci_start", "rec_ci_end"])

        for idx in range(len(mean_precision)):
            prec_mean = mean(mean_precision[idx])
            prec_std_err = sem(mean_precision[idx])
            prec_h = prec_std_err * t.ppf((1 + confidence) / 2, num_repeats - 1)

            rec_mean = mean(mean_recall[idx])
            rec_std_err = sem(mean_recall[idx])
            rec_h = rec_std_err * t.ppf((1 + confidence) / 2, num_repeats - 1)

            csv_writer.writerow([idx, prec_mean, prec_mean - prec_h, min(prec_mean + prec_h, 1.0),
                                 rec_mean, rec_mean - rec_h, min(rec_mean + rec_h, 1.0)])

        print("MEAN PREC", mean_precision.values())
        print("MEAN REC", mean_recall.values())


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
            intent.append(part)
        intents.append(intent)

    print("DATASET CASES #", len(intents))

    highest_precision = 0
    highest_recall = 0
    highest_f1 = 0
    highest_try = 0
    num_tries = 0

    while num_tries < 30:
        num_tries += 1
        END_TRAINING = None

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
        with open(config.EXTRACTION_RESULTS_PATH.format(dtype, num_tries), 'w') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(["text", "recognized_entities", "expected_entities",
                                 "training_time", "recall", "precision", "f1_score"])

            mean_precision = 0
            mean_recall = 0
            num_entries = len(results)

            for result in results:
                rec = metrics.recall(result['tp'], result['fn'])
                prec = metrics.precision(result['tp'], result['fp'])
                f1_sc = metrics.f1_score(prec, rec)

                mean_precision += prec
                mean_recall += rec
                print(result['text'])
                print('recall: ', rec)
                print('precision: ', prec)
                print('f1_score: ', f1_sc)
                csv_writer.writerow([result['text'], result['recognized_entities'],
                                     result['expected_entities'], time_elapsed, rec, prec, f1_sc])

            mean_precision /= num_entries
            mean_recall /= num_entries
            mean_f1 = metrics.f1_score(mean_precision, mean_recall)
            csv_writer.writerow(["Mean Precision", mean_precision])
            csv_writer.writerow(["Mean Recall", mean_recall])
            csv_writer.writerow(["Mean F1", mean_f1])

            print("Mean Precision", mean_precision)
            print("Mean Recall", mean_recall)
            print("Mean F1", mean_f1)

            if mean_f1 > highest_f1:
                highest_f1 = mean_f1
                highest_precision = mean_precision
                highest_recall = mean_recall
                highest_try = num_tries

    print("Highest Precision", highest_precision)
    print("Highest Recall", highest_recall)
    print("Highest F1", highest_f1)
    print("Highest Try", highest_try)


if __name__ == '__main__':
    # run('alpha')
    # run('campi')
    # run('both')
    feedback()
    # mean_feedback()
