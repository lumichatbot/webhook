""" Evaluation of Conflicts module """

import csv
import time
import numpy as np

from sklearn import metrics
from sklearn.model_selection import train_test_split

from features import get_features
from model import ClassificationModel

from utils import dataset, plotter, config, metrics


def analyze_campus_policies_by_uni(model_size):
    """ runs tests with the trained Random Forest model, with each pair of intents in the campi dataset by university"""
    print("MODEL TEST USING CAMPI BY UNI")

    campi_by_uni_dset = dataset.read('conflicts', 'campi', 'uni')
    results = []
    summary = {
        'tp': 0,
        'tn': 0,
        'fp': 0,
        'fn': 0,
        'precision': 0,
        'recall': 0,
        'f1': 0
    }
    summary_by_type = {
        'qos': {
            'tp': 0,
            'tn': 0,
            'fp': 0,
            'fn': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0
        },
        'negation': {
            'tp': 0,
            'tn': 0,
            'fp': 0,
            'fn': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0
        },
        'path': {
            'tp': 0,
            'tn': 0,
            'fp': 0,
            'fn': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0
        },
        'time': {
            'tp': 0,
            'tn': 0,
            'fp': 0,
            'fn': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0
        },
        'synonym': {
            'tp': 0,
            'tn': 0,
            'fp': 0,
            'fn': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0
        },
        'hierarchy': {
            'tp': 0,
            'tn': 0,
            'fp': 0,
            'fn': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0
        }
    }

    model = ClassificationModel('forest')
    if model.load(model_size):
        for case in campi_by_uni_dset:
            features_vector = get_features(case['sentence']['nile'], case['hypothesis']['nile'])
            prediction = model.predict([features_vector])[0]
            if prediction == case['conflict']:
                summary['tp' if prediction == 1 else 'tn'] += 1
                summary_by_type[case['type']]['tp' if prediction == 1 else 'tn'] += 1
            else:
                print(case['sentence']['nile'], case['hypothesis']['nile'])
                summary['fp' if prediction == 1 else 'fn'] += 1
                summary_by_type[case['type']]['fp' if prediction == 1 else 'fn'] += 1

            print(features_vector, prediction, case['conflict'])
            results.append((case['university'],
                            case['sentence']['text'], case['hypothesis']['text'],
                            case['sentence']['nile'], case['hypothesis']['nile'],
                            case['type'], case['conflict'], features_vector, prediction))

        with open(config.CONFLICTS_RESULTS_PATH.format('campi', 'uni'), 'w') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(['university', 'sentence text', 'hypothesis text',
                                 'sentence nile', 'hypothesis nile',
                                 'type', 'conflict', 'features', 'prediction'])
            for (uni, stn_text, hyp_text, stn_nile, hyp_nile, type, conflict, features, prediction) in results:
                csv_writer.writerow([uni, stn_text, hyp_text, stn_nile, hyp_nile,
                                     type, conflict, features, prediction])

        summary['precision'] = metrics.precision(summary['tp'], summary['fp'])
        summary['recall'] = metrics.recall(summary['tp'], summary['fn'])
        summary['f1'] = metrics.f1_score(summary['precision'], summary['recall'])

        with open(config.CONFLICTS_RESULTS_PATH.format('campi', 'uni_summary'), 'w') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(['type', 'tp', 'tn', 'fp', 'fn', 'precision', 'recall', 'f1'])
            for type, result in summary_by_type.items():
                result['precision'] = metrics.precision(result['tp'], result['fp'])
                result['recall'] = metrics.recall(result['tp'], result['fn'])
                result['f1'] = metrics.f1_score(result['precision'], result['recall'])

                csv_writer.writerow([type, result['tp'], result['tn'],
                                     result['fp'], result['fn'],
                                     result['precision'], result['recall'], result['f1']])

            csv_writer.writerow(['total', summary['tp'], summary['tn'],
                                 summary['fp'], summary['fn'],
                                 summary['precision'], summary['recall'], summary['f1']])
        print(summary)
    else:
        print("Problem loading model")


def analyze_campus_policies(model_size):
    """ runs tests with the trained Random Forest model, with each pair of intents in the campi dataset """
    print("MODEL TEST USING CAMPI ALL")

    campi_by_uni_dset = dataset.read('conflicts', 'campi', 'all')
    results = []
    summary = {
        'tp': 0,
        'tn': 0,
        'fp': 0,
        'fn': 0,
        'precision': 0,
        'recall': 0,
        'f1': 0
    }
    summary_by_type = {
        'qos': {
            'tp': 0,
            'tn': 0,
            'fp': 0,
            'fn': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0
        },
        'negation': {
            'tp': 0,
            'tn': 0,
            'fp': 0,
            'fn': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0
        },
        'path': {
            'tp': 0,
            'tn': 0,
            'fp': 0,
            'fn': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0
        },
        'time': {
            'tp': 0,
            'tn': 0,
            'fp': 0,
            'fn': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0
        },
        'synonym': {
            'tp': 0,
            'tn': 0,
            'fp': 0,
            'fn': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0
        },
        'hierarchy': {
            'tp': 0,
            'tn': 0,
            'fp': 0,
            'fn': 0,
            'precision': 0,
            'recall': 0,
            'f1': 0
        }
    }

    model = ClassificationModel('forest')
    if model.load(model_size):
        for case in campi_by_uni_dset:
            features_vector = get_features(case['sentence']['nile'], case['hypothesis']['nile'])
            prediction = model.predict([features_vector])[0]
            if prediction == case['conflict']:
                summary['tp' if prediction == 1 else 'tn'] += 1
                summary_by_type[case['type']]['tp' if prediction == 1 else 'tn'] += 1
            else:
                print(case['sentence']['nile'], case['hypothesis']['nile'])
                summary['fp' if prediction == 1 else 'fn'] += 1
                summary_by_type[case['type']]['fp' if prediction == 1 else 'fn'] += 1

            print(features_vector, prediction, case['conflict'])
            results.append((case['sentence']['university'], case['hypothesis']['university'],
                            case['sentence']['text'], case['hypothesis']['text'],
                            case['sentence']['nile'], case['hypothesis']['nile'],
                            case['type'], case['conflict'], features_vector, prediction))

        with open(config.CONFLICTS_RESULTS_PATH.format('campi', 'all'), 'w') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(['sentence university', 'hypothesis university',
                                 'sentence text', 'hypothesis text',
                                 'sentence nile', 'hypothesis nile',
                                 'type', 'conflict', 'features', 'prediction'])
            for (stn_uni, hyp_uni, stn_text, hyp_text, stn_nile, hyp_nile, type, conflict, features, prediction) in results:
                csv_writer.writerow([stn_uni, hyp_uni, stn_text, hyp_text, stn_nile, hyp_nile,
                                     type, conflict, features, prediction])

        summary['precision'] = metrics.precision(summary['tp'], summary['fp'])
        summary['recall'] = metrics.recall(summary['tp'], summary['fn'])
        summary['f1'] = metrics.f1_score(summary['precision'], summary['recall'])

        with open(config.CONFLICTS_RESULTS_PATH.format('campi', 'all_summary'), 'w') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')
            csv_writer.writerow(['type', 'tp', 'tn', 'fp', 'fn', 'precision', 'recall', 'f1'])
            for type, result in summary_by_type.items():
                result['precision'] = metrics.precision(result['tp'], result['fp'])
                result['recall'] = metrics.recall(result['tp'], result['fn'])
                result['f1'] = metrics.f1_score(result['precision'], result['recall'])

                csv_writer.writerow([type, result['tp'], result['tn'],
                                     result['fp'], result['fn'],
                                     result['precision'], result['recall'], result['f1']])

            csv_writer.writerow(['total', summary['tp'], summary['tn'],
                                 summary['fp'], summary['fn'],
                                 summary['precision'], summary['recall'], summary['f1']])

        print(summary)
    else:
        print("Problem loading model")


def train(dataset_size, model_type):
    """ opens fit dataset and trains SVM/LogReg/Forest model with it, then tests it"""
    print("MODEL TRAIN", dataset_size, model_type)

    dset = dataset.read('conflicts', dataset_size)
    data, targets = [], []
    for case in dset['content']:
        data.append(case)
        targets.append(case['conflict'])

    feature_vector = []
    with open('../res/training.csv', 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['sentence', 'hypothesis', 'features', 'conflict'])

        for idx, case in enumerate(data):
            features = get_features(case['sentence'], case['hypothesis'])
            feature_vector.append(features)
            # print(feature_vector[idx], targets[idx])
            csv_writer.writerow([case['sentence'], case['hypothesis'], features, targets[idx]])

    model = ClassificationModel(model_type)
    model.train(feature_vector, targets, dataset_size)
    model.save(dataset_size)


def test(dataset_size, model_type):
    """ opens fit dataset and trains SVM/LogReg/Forest model with it, then tests it"""
    print("MODEL TEST", dataset_size, model_type)

    dset = dataset.read('conflicts', dataset_size)
    data, targets = [], []
    for case in dset['content']:
        data.append(case)
        targets.append(case['conflict'])

    fit_data, test_data = [], []
    fit_cases, test_cases, fit_target, test_target = train_test_split(
        data, targets, test_size=0.25, shuffle=True, random_state=0)

    for idx, fit_case in enumerate(fit_cases):
        fit_data.append(get_features(fit_case['sentence'], fit_case['hypothesis']))
        print(fit_data[idx], fit_target[idx])

    for test_case in test_cases:
        test_data.append(get_features(test_case['sentence'], test_case['hypothesis']))

    model = ClassificationModel(model_type)
    start_time = time.time()
    model.train(fit_data, fit_target, dataset_size)
    elapsed_time = time.time() - start_time
    test_results = model.test(test_data)

    with open(config.CONFLICTS_RESULTS_PATH.format(dataset_size, model_type), 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['hypothesis', 'sentence', 'type', 'conflict', 'features', 'prediction'])
        for (test_case, result, features) in zip(test_cases, test_results, test_data):
            csv_writer.writerow([test_case['hypothesis'], test_case['sentence'],
                                 test_case['type'], test_case['conflict'], features, result])

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

    dset = dataset.read('conflicts', dataset_size)
    data, targets = [], []
    for case in dset['content']:
        data.append(get_features(case['sentence'], case['hypothesis']))
        targets.append(case['conflict'])

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

    dset = dataset.read('conflicts', dataset_size)
    data, targets = [], []
    for case in dset['content']:
        data.append(get_features(case['sentence'], case['hypothesis']))
        targets.append(case['conflict'])

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

    dset = dataset.read('conflicts', dataset_size)
    data, targets = [], []
    for case in dset['content']:
        data.append(get_features(case['sentence'], case['hypothesis']))
        targets.append(case['conflict'])

    for mtype in ['svm', 'log', 'forest']:
        model = ClassificationModel(mtype)
        plot = plotter.plot_roc_curve(dataset_size, mtype, model, data, targets)
        plot.savefig("../res/plot/roc_{}_{}.pdf".format(dataset_size, mtype), bbox_inches='tight')


def run():
    """ runs tests with each model """
    with open(config.CONFLICTS_RESULTS_PATH.format('summary', '0'), 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['dataset', 'model', 'k-fold', 'fit time', 'validation time', 'precision', 'recall', 'f1'])
        for dataset_size in config.DATASET_SIZES:
            # roc_curve(dataset_size)
            for mtype in ['svm', 'log', 'forest']:
                if dataset_size == 10000 and mtype != 'forest':
                    continue

                # test(dataset_size, mtype)
                # learning_curve(dataset_size, mtype)
                print("DATASET VALIDATION", dataset_size, mtype)
                (training_times, score_times, precisions, recalls, f1_scores) = validate(dataset_size, mtype)
                for k, (training_time, score_time, precision, recall, f1_score) in enumerate(zip(training_times, score_times, precisions, recalls, f1_scores)):
                    csv_writer.writerow([dataset_size, mtype, k + 1, training_time,
                                         score_time, precision, recall, f1_score])


if __name__ == "__main__":
    run()
    # test(100, 'forest')
    # train(1000, 'forest')
    # analyze_campus_policies_by_uni(10000)
    # analyze_campus_policies(10000)
