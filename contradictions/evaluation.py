""" Evaluation of Contradictions module """

import csv
import time
import numpy as np

from sklearn import metrics
from sklearn.model_selection import train_test_split

from features import get_features
from model import ClassificationModel

from utils import dataset, plotter, config


def analyze_campus_policies():
    """ runs tests with the trained Random Forest model, with each pair of intents in the campi dataset """
    print("MODEL TEST USING CAMPI")

    dset = dataset.read('contradictions', 'campi')
    intents = []
    for case in dset['intents']:
        # if case['university'] not in intents:
        #     intents[case['university']] = []
        intents.append((case['university'], case['text'], case['nile']))

    model = ClassificationModel('forest')
    results = []
    if model.load(10000):
        # for (uni, intents) in intents.items():
        for i in range(len(intents)):
            (uni_stn, text_stn, sentence) = intents[i]
            for j in range(i + 1, len(intents)):
                (uni_hyp, text_hyp, hypothesis) = intents[j]
                if sentence != hypothesis:
                    results.append((uni_stn, uni_hyp, text_stn, text_hyp, sentence, hypothesis,
                                    model.predict([get_features(sentence, hypothesis)])))

        with open(config.CONTRADICTIONS_RESULTS_PATH.format('summary', 'campi'), 'w') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(['university stn', 'university hyp', 'text stn',
                                 'text hyp', 'sentence', 'hypothesis', 'prediction'])
            for (uni_stn, uni_hyp, text_stn, text_hyp, sentence, hypothesis, prediction) in results:
                csv_writer.writerow([uni_stn, uni_hyp, text_stn, text_hyp, sentence, hypothesis, prediction[0]])
    else:
        print("Problem loading model")


def test(dataset_size, model_type):
    """ opens fit dataset and trains SVM/LogReg/Forest model with it, then tests it"""
    print("MODEL TEST", dataset_size, model_type)

    dset = dataset.read('contradictions', dataset_size)
    data, targets = [], []
    for case in dset['content']:
        data.append(case)
        targets.append(case['contradiction'])

    fit_data, test_data = [], []
    fit_cases, test_cases, fit_target, test_target = train_test_split(
        data, targets, test_size=0.25, shuffle=True, random_state=0)
    for fit_case in fit_cases:
        fit_data.append(get_features(fit_case['sentence'], fit_case['hypothesis']))

    for test_case in test_cases:
        test_data.append(get_features(test_case['sentence'], test_case['hypothesis']))

    model = ClassificationModel(model_type)
    start_time = time.time()
    model.train(fit_data, fit_target, dataset_size)
    elapsed_time = time.time() - start_time
    test_results = model.test(test_data)

    with open(config.CONTRADICTIONS_RESULTS_PATH.format(dataset_size, model_type), 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['hypothesis', 'sentence', 'type', 'contradiction', 'prediction', 'features'])
        for (test_case, result, features) in zip(test_cases, test_results, test_data):
            csv_writer.writerow([test_case['hypothesis'], test_case['sentence'],
                                 test_case['type'], test_case['contradiction'], result, features])

    precision = metrics.precision_score(test_target, test_results)
    recall = metrics.recall_score(test_target, test_results)
    f1_score = metrics.f1_score(test_target, test_results)

    print("FIT TIME", elapsed_time)
    print("PRECISION", precision)
    print("RECALL", recall)
    print("F1 SCORE", f1_score)
    model.save(dataset_size)


def validate(dataset_size, model_type):
    """ runs cross validation in classification model """
    print("MODEL VALIDATION", dataset_size, model_type)

    dset = dataset.read('contradictions', dataset_size)
    data, targets = [], []
    for case in dset['content']:
        data.append(get_features(case['sentence'], case['hypothesis']))
        targets.append(case['contradiction'])

    model = ClassificationModel(model_type)
    scores = model.cross_validate(data, targets)
    print("scores", scores)

    print("FIT TIME", scores['fit_time'])
    print("VALIDATION TIME", scores['score_time'])
    print("PRECISION", scores['test_precision_macro'])
    print("RECALL", scores['test_recall_macro'])
    print("F1 SCORE", scores['test_f1_macro'])
    return scores['fit_time'], scores['score_time'], scores['test_precision_macro'], scores['test_recall_macro'], scores['test_f1_macro']


def learning_curve(dataset_size, model_type):
    """ runs cross validation to plot learning curve """
    print("LEARNING CURVE", dataset_size, model_type)

    dset = dataset.read('contradictions', dataset_size)
    data, targets = [], []
    for case in dset['content']:
        data.append(get_features(case['sentence'], case['hypothesis']))
        targets.append(case['contradiction'])

    model = ClassificationModel(model_type)
    train_sizes, train_scores, test_scores = model.learning_curve(data, targets)
    with open(config.LEARNING_CURVE_PATH.format(dataset_size, model_type), 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['model', 'dataset_size', 'train_size', 'train_mse', 'test_mse'])
        for (train_size, train_score, test_score) in zip(train_sizes, train_scores, test_scores):
            csv_writer.writerow([model_type, dataset_size, train_size, ','.join(
                np.char.mod('%f', train_score)), ','.join(np.char.mod('%f', test_score))])

    plot = plotter.learning_curve(train_sizes, train_scores, test_scores)
    plot.savefig("../res/plot/learning_{}_{}.pdf".format(dataset_size, model_type))


def roc_curve(dataset_size):
    """ runs cross validation to plot precision recall curve """
    print("ROC CURVE", dataset_size)

    dset = dataset.read('contradictions', dataset_size)
    data, targets = [], []
    for case in dset['content']:
        data.append(get_features(case['sentence'], case['hypothesis']))
        targets.append(case['contradiction'])

    for mtype in ['svm', 'log', 'forest']:
        model = ClassificationModel(mtype)
        plot = plotter.plot_roc_curve(dataset_size, mtype, model, data, targets)
        plot.savefig("../res/plot/roc_{}_{}.pdf".format(dataset_size, mtype), bbox_inches='tight')


def run():
    """ runs tests with each model """
    with open(config.CONTRADICTIONS_RESULTS_PATH.format('summary', '0'), 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['dataset', 'model', 'k-fold', 'fit time', 'validation time', 'precision', 'recall', 'f1'])
        for dataset_size in config.DATASET_SIZES:
            # roc_curve(dataset_size)
            for mtype in ['svm', 'log', 'forest']:
                # test(dataset_size, mtype)
                # learning_curve(dataset_size, mtype)
                print("DATASET VALIDATION", dataset_size, mtype)
                (training_times, score_times, precisions, recalls, f1_scores) = validate(dataset_size, mtype)
                for k, (training_time, score_time, precision, recall, f1_score) in enumerate(zip(training_times, score_times, precisions, recalls, f1_scores)):
                    csv_writer.writerow([dataset_size, mtype, k + 1, training_time,
                                         score_time, precision, recall, f1_score])


if __name__ == "__main__":
    test(10000, 'forest')
    # run()
    # analyze_campus_policies()
