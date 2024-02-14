""" Evaluation of Ambiguities module """

import os
import csv
import time
import psutil
import numpy as np


from threading import Thread
from sklearn import metrics
from sklearn.model_selection import train_test_split

from .features import get_features
from .model import ClassificationModel

from ..utils import dataset, plotter, config, metrics


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def analyze_campus_policies_by_uni(model_size):
    """runs tests with the trained Random Forest model, with each pair of intents in the campi dataset by university"""
    print("MODEL TEST USING CAMPI BY UNI")

    campi_by_uni_dset = dataset.read("ambiguities", "campi", "uni")
    results = []
    summary = {"tp": 0, "tn": 0, "fp": 0, "fn": 0, "precision": 0, "recall": 0, "f1": 0}
    summary_by_type = {
        "qos": {
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
        },
        "negation": {
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
        },
        "path": {
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
        },
        "time": {
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
        },
        "synonym": {
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
        },
        "hierarchy": {
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
        },
    }

    model = ClassificationModel("forest")
    if model.load(model_size):
        for case in campi_by_uni_dset:
            features_vector = get_features(
                case["sentence"]["nile"], case["hypothesis"]["nile"]
            )
            prediction = model.predict([features_vector])[0]
            if prediction == case["amibiguity"]:
                summary["tp" if prediction == 1 else "tn"] += 1
                summary_by_type[case["type"]]["tp" if prediction == 1 else "tn"] += 1
            else:
                print(case["sentence"]["nile"], case["hypothesis"]["nile"])
                summary["fp" if prediction == 1 else "fn"] += 1
                summary_by_type[case["type"]]["fp" if prediction == 1 else "fn"] += 1

            print(features_vector, prediction, case["amibiguity"])
            results.append(
                (
                    case["university"],
                    case["sentence"]["text"],
                    case["hypothesis"]["text"],
                    case["sentence"]["nile"],
                    case["hypothesis"]["nile"],
                    case["type"],
                    case["amibiguity"],
                    features_vector,
                    prediction,
                )
            )

        with open(
            config.AMBIGUITIES_RESULTS_PATH.format("campi", "uni"),
            "w",
            encoding="UTF-8",
        ) as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=",")
            csv_writer.writerow(
                [
                    "university",
                    "sentence text",
                    "hypothesis text",
                    "sentence nile",
                    "hypothesis nile",
                    "type",
                    "amibiguity",
                    "features",
                    "prediction",
                ]
            )
            for (
                uni,
                stn_text,
                hyp_text,
                stn_nile,
                hyp_nile,
                type,
                amibiguity,
                features,
                prediction,
            ) in results:
                csv_writer.writerow(
                    [
                        uni,
                        stn_text,
                        hyp_text,
                        stn_nile,
                        hyp_nile,
                        type,
                        amibiguity,
                        features,
                        prediction,
                    ]
                )

        summary["precision"] = metrics.precision(summary["tp"], summary["fp"])
        summary["recall"] = metrics.recall(summary["tp"], summary["fn"])
        summary["f1"] = metrics.f1_score(summary["precision"], summary["recall"])

        with open(
            config.AMBIGUITIES_RESULTS_PATH.format("campi", "uni_summary"),
            "w",
            encoding="UTF-8",
        ) as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=",")
            csv_writer.writerow(
                ["type", "tp", "tn", "fp", "fn", "precision", "recall", "f1"]
            )
            for type, result in summary_by_type.items():
                result["precision"] = metrics.precision(result["tp"], result["fp"])
                result["recall"] = metrics.recall(result["tp"], result["fn"])
                result["f1"] = metrics.f1_score(result["precision"], result["recall"])

                csv_writer.writerow(
                    [
                        type,
                        result["tp"],
                        result["tn"],
                        result["fp"],
                        result["fn"],
                        result["precision"],
                        result["recall"],
                        result["f1"],
                    ]
                )

            csv_writer.writerow(
                [
                    "total",
                    summary["tp"],
                    summary["tn"],
                    summary["fp"],
                    summary["fn"],
                    summary["precision"],
                    summary["recall"],
                    summary["f1"],
                ]
            )
        print(summary)
    else:
        print("Problem loading model")


def analyze_campus_policies(model_size):
    """runs tests with the trained Random Forest model, with each pair of intents in the campi dataset"""
    print("MODEL TEST USING CAMPI ALL")

    campi_by_uni_dset = dataset.read("ambiguities", "campi", "all")
    results = []
    summary = {"tp": 0, "tn": 0, "fp": 0, "fn": 0, "precision": 0, "recall": 0, "f1": 0}
    summary_by_type = {
        "qos": {
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
        },
        "negation": {
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
        },
        "path": {
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
        },
        "time": {
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
        },
        "synonym": {
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
        },
        "hierarchy": {
            "tp": 0,
            "tn": 0,
            "fp": 0,
            "fn": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
        },
    }

    model = ClassificationModel("forest")
    if model.load(model_size):
        for case in campi_by_uni_dset:
            start_time = time.time()
            features_vector = get_features(
                case["sentence"]["nile"], case["hypothesis"]["nile"]
            )
            prediction = model.predict([features_vector])[0]
            prediction_time = time.time() - start_time
            if prediction == case["amibiguity"]:
                summary["tp" if prediction == 1 else "tn"] += 1
                summary_by_type[case["type"]]["tp" if prediction == 1 else "tn"] += 1
            else:
                print(case["sentence"]["nile"], case["hypothesis"]["nile"])
                summary["fp" if prediction == 1 else "fn"] += 1
                summary_by_type[case["type"]]["fp" if prediction == 1 else "fn"] += 1

            print(features_vector, prediction, case["amibiguity"])
            results.append(
                (
                    case["sentence"]["university"],
                    case["hypothesis"]["university"],
                    case["sentence"]["text"],
                    case["hypothesis"]["text"],
                    case["sentence"]["nile"],
                    case["hypothesis"]["nile"],
                    case["type"],
                    case["amibiguity"],
                    features_vector,
                    prediction,
                    prediction_time,
                )
            )

        with open(
            config.AMBIGUITIES_RESULTS_PATH.format("campi", "all"),
            "w",
            encoding="UTF-8",
        ) as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=",")
            csv_writer.writerow(
                [
                    "sentence university",
                    "hypothesis university",
                    "sentence text",
                    "hypothesis text",
                    "sentence nile",
                    "hypothesis nile",
                    "type",
                    "amibiguity",
                    "features",
                    "prediction",
                    "prediction time",
                ]
            )
            for (
                stn_uni,
                hyp_uni,
                stn_text,
                hyp_text,
                stn_nile,
                hyp_nile,
                type,
                amibiguity,
                features,
                prediction,
                prediction_time,
            ) in results:
                csv_writer.writerow(
                    [
                        stn_uni,
                        hyp_uni,
                        stn_text,
                        hyp_text,
                        stn_nile,
                        hyp_nile,
                        type,
                        amibiguity,
                        features,
                        prediction,
                        prediction_time,
                    ]
                )

        summary["precision"] = metrics.precision(summary["tp"], summary["fp"])
        summary["recall"] = metrics.recall(summary["tp"], summary["fn"])
        summary["f1"] = metrics.f1_score(summary["precision"], summary["recall"])

        with open(
            config.AMBIGUITIES_RESULTS_PATH.format("campi", "all_summary"),
            "w",
            encoding="UTF-8",
        ) as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=",")
            csv_writer.writerow(
                ["type", "tp", "tn", "fp", "fn", "precision", "recall", "f1"]
            )
            for type, result in summary_by_type.items():
                result["precision"] = metrics.precision(result["tp"], result["fp"])
                result["recall"] = metrics.recall(result["tp"], result["fn"])
                result["f1"] = metrics.f1_score(result["precision"], result["recall"])

                csv_writer.writerow(
                    [
                        type,
                        result["tp"],
                        result["tn"],
                        result["fp"],
                        result["fn"],
                        result["precision"],
                        result["recall"],
                        result["f1"],
                    ]
                )

            csv_writer.writerow(
                [
                    "total",
                    summary["tp"],
                    summary["tn"],
                    summary["fp"],
                    summary["fn"],
                    summary["precision"],
                    summary["recall"],
                    summary["f1"],
                ]
            )

        print(summary)
    else:
        print("Problem loading model")


def measure_cpu_memory_usage():
    """measures cpu and memory usage"""
    print("MEASURE CPU MEMORY USAGE")
    global running

    running = True

    cpu_results = []
    proc_cpu_results = []
    memory_results = []
    proc_memory_results = []
    process = psutil.Process(os.getpid())

    while running:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        proc_cpu_usage = process.cpu_percent(interval=1)
        proc_mem_usage = process.memory_percent()

        cpu_results.append(cpu_usage)
        memory_results.append(memory_usage)
        proc_cpu_results.append(proc_cpu_usage)
        proc_memory_results.append(proc_mem_usage)

    return cpu_results, memory_results, proc_cpu_results, proc_memory_results


def train(dataset_size, model_type):
    """opens fit dataset and trains SVM/LogReg/Forest model with it, then tests it"""
    print("MODEL TRAIN", dataset_size, model_type)

    stats = {
        "training_time": 0,
        "cpu_usage": [],
        "memory_usage": [],
    }

    dset = dataset.read("ambiguities", dataset_size)
    targets = []
    feature_vector = []
    for case in dset["content"]:
        targets.append(case["amibiguity"])
        features = get_features(case["sentence"], case["hypothesis"])
        feature_vector.append(features)

    # with open(f"{config.ROOT}/res/training.csv", "w", encoding="UTF-8") as csvfile:
    # csv_writer = csv.writer(csvfile, delimiter=",")
    # csv_writer.writerow(["sentence", "hypothesis", "features", "amibiguity"])
    #     for case in data:
    #         features = get_features(case["sentence"], case["hypothesis"])
    #         feature_vector.append(features)
    #     print(feature_vector[idx], targets[idx])
    #     csv_writer.writerow(
    #     [case["sentence"], case["hypothesis"], features, targets[idx]]
    #     )

    global running

    running = True

    model = ClassificationModel(model_type)
    t = ThreadWithReturnValue(target=measure_cpu_memory_usage)
    t.start()
    train_start = time.time()

    model.train(feature_vector, targets, dataset_size)

    running = False
    (cpu_results, mem_results, proc_cpu_results, proc_mem_results) = t.join()
    stats["training_time"] = time.time() - train_start
    stats["cpu_usage"] = cpu_results
    stats["memory_usage"] = mem_results
    stats["proc_cpu_usage"] = proc_cpu_results
    stats["proc_memory_usage"] = proc_mem_results

    model.save(dataset_size)

    return stats


def test(dataset_size, model_type):
    """opens fit dataset and trains SVM/LogReg/Forest model with it, then tests it"""
    print("MODEL TEST", dataset_size, model_type)

    dset = dataset.read("ambiguities", dataset_size)
    data, targets = [], []
    for case in dset["content"]:
        data.append(case)
        targets.append(case["amibiguity"])

    fit_data, test_data = [], []
    fit_cases, test_cases, fit_target, test_target = train_test_split(
        data, targets, test_size=0.25, shuffle=True, random_state=0
    )

    for idx, fit_case in enumerate(fit_cases):
        fit_data.append(get_features(fit_case["sentence"], fit_case["hypothesis"]))
        print(fit_data[idx], fit_target[idx])

    for test_case in test_cases:
        test_data.append(get_features(test_case["sentence"], test_case["hypothesis"]))

    model = ClassificationModel(model_type)
    start_time = time.time()
    model.train(fit_data, fit_target, dataset_size)
    elapsed_time = time.time() - start_time
    test_results = model.test(test_data)

    with open(
        config.AMBIGUITIES_RESULTS_PATH.format(dataset_size, model_type),
        "w",
        encoding="UTF-8",
    ) as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",")
        csv_writer.writerow(
            ["hypothesis", "sentence", "type", "amibiguity", "features", "prediction"]
        )
        for test_case, result, features in zip(test_cases, test_results, test_data):
            csv_writer.writerow(
                [
                    test_case["hypothesis"],
                    test_case["sentence"],
                    test_case["type"],
                    test_case["amibiguity"],
                    features,
                    result,
                ]
            )

    precision = metrics.precision_score(test_target, test_results)
    recall = metrics.recall_score(test_target, test_results)
    f1_score = metrics.f1_score(test_target, test_results)

    print("FIT TIME", elapsed_time)
    print("PRECISION", precision)
    print("RECALL", recall)
    print("F1 SCORE", f1_score)
    model.save(dataset_size)


def validate(dataset_size, model_type):
    """runs cross validation in classification model"""
    print("MODEL VALIDATION", dataset_size, model_type)

    dset = dataset.read("ambiguities", dataset_size)
    data, targets = [], []
    for case in dset["content"]:
        data.append(get_features(case["sentence"], case["hypothesis"]))
        targets.append(case["amibiguity"])

    print("DATASET LOADED")

    model = ClassificationModel(model_type)
    scores = model.cross_validate(data, targets)
    print("scores", scores)

    print("MEAN FIT TIME", np.mean(scores["fit_time"]))
    print("MEAN VALIDATION TIME", np.mean(scores["score_time"]))
    print("MEAN PRECISION", np.mean(scores["test_precision_macro"]))
    print("MEAN RECALL", np.mean(scores["test_recall_macro"]))
    print("MEAN F1 SCORE", np.mean(scores["test_f1_macro"]))
    return (
        scores["fit_time"],
        scores["score_time"],
        scores["test_precision_macro"],
        scores["test_recall_macro"],
        scores["test_f1_macro"],
    )


def learning_curve(dataset_size, model_type):
    """runs cross validation to plot learning curve"""
    print("LEARNING CURVE", dataset_size, model_type)

    dset = dataset.read("ambiguities", dataset_size)
    data, targets = [], []
    for case in dset["content"]:
        data.append(get_features(case["sentence"], case["hypothesis"]))
        targets.append(case["amibiguity"])

    model = ClassificationModel(model_type)
    train_sizes, train_scores, test_scores = model.learning_curve(data, targets)
    with open(
        config.LEARNING_CURVE_PATH.format(dataset_size, model_type),
        "w",
        encoding="UTF-8",
    ) as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",")
        csv_writer.writerow(
            ["model", "dataset_size", "train_size", "train_mse", "test_mse"]
        )
        for train_size, train_score, test_score in zip(
            train_sizes, train_scores, test_scores
        ):
            csv_writer.writerow(
                [
                    model_type,
                    dataset_size,
                    train_size,
                    ";".join(np.char.mod("%f", train_score)),
                    ";".join(np.char.mod("%f", test_score)),
                ]
            )

    plot = plotter.learning_curve(train_sizes, train_scores, test_scores)
    plot.savefig("../res/plot/learning_{}_{}.pdf".format(dataset_size, model_type))


def roc_curve(dataset_size):
    """runs cross validation to plot precision recall curve"""
    print("ROC CURVE", dataset_size)

    dset = dataset.read("ambiguities", dataset_size)
    data, targets = [], []
    for case in dset["content"]:
        data.append(get_features(case["sentence"], case["hypothesis"]))
        targets.append(case["amibiguity"])

    for mtype in ["svm", "log", "forest"]:
        model = ClassificationModel(mtype)
        plot = plotter.plot_roc_curve(dataset_size, mtype, model, data, targets)
        plot.savefig(
            "../res/plot/roc_{}_{}.pdf".format(dataset_size, mtype), bbox_inches="tight"
        )


def run():
    """runs tests with each model"""
    with open(
        config.AMBIGUITIES_RESULTS_PATH.format("summary", "0"), "w", encoding="UTF-8"
    ) as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",")
        csv_writer.writerow(
            [
                "dataset",
                "model",
                "k-fold",
                "fit time",
                "validation time",
                "precision",
                "recall",
                "f1",
            ]
        )
        for dataset_size in config.DATASET_SIZES:
            # roc_curve(dataset_size)
            for mtype in ["svm", "log", "forest"]:
                if dataset_size == 10000 and mtype != "forest":
                    continue

                # test(dataset_size, mtype)
                # learning_curve(dataset_size, mtype)
                print("DATASET VALIDATION", dataset_size, mtype)
                (
                    training_times,
                    score_times,
                    precisions,
                    recalls,
                    f1_scores,
                ) = validate(dataset_size, mtype)
                for k, (
                    training_time,
                    score_time,
                    precision,
                    recall,
                    f1_score,
                ) in enumerate(
                    zip(training_times, score_times, precisions, recalls, f1_scores)
                ):
                    csv_writer.writerow(
                        [
                            dataset_size,
                            mtype,
                            k + 1,
                            training_time,
                            score_time,
                            precision,
                            recall,
                            f1_score,
                        ]
                    )


def export():
    """Process features and exports dataset"""

    dset = dataset.read("ambiguities", 10000)
    with open(
        config.AMBIGUITIES_RESULTS_PATH.format("export", "0"), "w", encoding="UTF-8"
    ) as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",")
        csv_writer.writerow(
            [
                "path_similarity",
                "qos",
                "time",
                "negation",
                "synonyms",
                "hierarchy_targets",
                "hierarchy_traffics",
                "endpoints",
                "num_endpoints",
                "services",
                "num_services",
                "groups",
                "num_groups",
                "traffics",
                "num_traffics",
                "protocols",
                "num_protocols",
                "middleboxes",
                "num_middleboxes",
                "amibiguity",
            ]
        )

        for case in dset["content"]:
            (
                path_similarity,
                qos,
                time,
                negation,
                synonyms,
                hierarchy_targets,
                hierarchy_traffics,
                endpoints,
                num_endpoints,
                services,
                num_services,
                groups,
                num_groups,
                traffics,
                num_traffics,
                protocols,
                num_protocols,
                middleboxes,
                num_middleboxes,
            ) = get_features(case["sentence"], case["hypothesis"])

            csv_writer.writerow(
                [
                    path_similarity,
                    qos,
                    time,
                    negation,
                    synonyms,
                    hierarchy_targets,
                    hierarchy_traffics,
                    endpoints,
                    num_endpoints,
                    services,
                    num_services,
                    groups,
                    num_groups,
                    traffics,
                    num_traffics,
                    protocols,
                    num_protocols,
                    middleboxes,
                    num_middleboxes,
                    case["amibiguity"],
                ]
            )


def analyze_training_time(dataset_sizes=[100, 1000, 5000, 10000]):
    """
    Runs tests with the each model, for each new intent in the campi dataset,
    to measure training time, cpu and memory usage.
    """
    print("MODEL TRAINING")
    results = []
    for model_type in ["svm", "log", "forest"]:
        print("MODEL TRAIN", model_type)
        for dataset_size in dataset_sizes:
            print("DATASET SIZE", dataset_size)

            print(f"STARTING TESTS FOR MODEL {model_type} SIZE {dataset_size}.")
            stats = train(dataset_size, model_type)
            results.append(
                (
                    model_type,
                    dataset_size,
                    stats["training_time"],
                    ";".join(np.char.mod("%f", stats["cpu_usage"])),
                    ";".join(np.char.mod("%f", stats["memory_usage"])),
                    ";".join(np.char.mod("%f", stats["proc_cpu_usage"])),
                    ";".join(np.char.mod("%f", stats["proc_memory_usage"])),
                )
            )

    print(FINISHED TESTS. WRITING RESULTS TO FILE...")
    with open(
        config.TRAINING_TIME_RESULTS_PATH.format("campi"), "a", encoding="UTF-8"
    ) as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",")
        csv_writer.writerow(
            [
                "dataset",
                "model",
                "training time",
                "cpu usage",
                "memory usage",
                "proc cpu usage",
                "proc memory usage",
            ]
        )

        for (
            dataset_size,
            model_type,
            training_time,
            cpu_usage,
            memory_usage,
            proc_cpu_usage,
            proc_memory_usage,
        ) in results:
            csv_writer.writerow(
                [
                    model_type,
                    dataset_size,
                    training_time,
                    cpu_usage,
                    memory_usage,
                    proc_cpu_usage,
                    proc_memory_usage,
                ]
            )


def analyze_prediction_time(model_sizes=[100, 1000, 5000, 10000]):
    """runs tests with the each model, for each new intent in the campi dataset, to measure prediction time"""
    print("MODEL TEST USING CAMPI DATASET")
    campi_dset = dataset.read("extraction", "campi")["intents"]
    results = []
    deploy_intent_results = []
    deployed_intents = []
    process = psutil.Process(os.getpid())

    for model_type in ["svm", "log", "forest"]:
        print("MODEL TEST", model_type)
        model = ClassificationModel(model_type)
        for model_size in model_sizes:
            print("MODEL SIZE", model_size)
            if not model.load(model_size):
                print("Problem loading model.", model_type, model_size)
                continue

            print(f"STARTING TESTS FOR MODEL {model_type} SIZE {model_size}.")
            for case in campi_dset:
                n_ambiguities = 0
                deploy_intent_start = time.time()
                for intent in deployed_intents:
                    # avoid testing the same intent
                    if intent["nile"] != case["nile"]:
                        cpu_usage = psutil.cpu_percent(interval=1)
                        memory_usage = psutil.virtual_memory().percent
                        proc_cpu_usage = process.cpu_percent(interval=1)
                        proc_mem_usage = process.memory_percent()

                        start_time = time.time()
                        features_vector = get_features(case["nile"], case["nile"])
                        prediction = model.predict([features_vector])[0]
                        prediction_time = time.time() - start_time
                        if prediction == 1:
                            n_ambiguities += 1

                        # print(
                        #     features_vector,
                        #     prediction,
                        #     prediction_time,
                        # )
                        results.append(
                            (
                                model_type,
                                model_size,
                                case["university"],
                                intent["university"],
                                case["text"],
                                intent["text"],
                                case["nile"],
                                intent["nile"],
                                features_vector,
                                prediction,
                                prediction_time,
                                cpu_usage,
                                memory_usage,
                                proc_cpu_usage,
                                proc_mem_usage,
                            )
                        )

                cpu_usage = psutil.cpu_percent(interval=1)
                memory_usage = psutil.virtual_memory().percent
                proc_cpu_usage = process.cpu_percent(interval=1)
                proc_mem_usage = process.memory_percent()

                deploy_time = time.time() - deploy_intent_start
                deployed_intents.append(case)
                deploy_intent_results.append(
                    (
                        model_type,
                        model_size,
                        case["university"],
                        case["text"],
                        case["nile"],
                        n_ambiguities,
                        deploy_time,
                        cpu_usage,
                        memory_usage,
                        proc_cpu_usage,
                        proc_mem_usage,
                    )
                )

        print("FINISHED TESTS. WRITING RESULTS TO FILE...")
        with open(
            config.PREDICTION_TIME_RESULTS_PATH.format("campi", "all"),
            "a",
            encoding="UTF-8",
        ) as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=",")
            csv_writer.writerow(
                [
                    "model",
                    "dataset",
                    "sentence university",
                    "hypothesis university",
                    "sentence text",
                    "hypothesis text",
                    "sentence nile",
                    "hypothesis nile",
                    "features",
                    "prediction",
                    "prediction time",
                    "cpu usage",
                    "memory usage",
                    "proc cpu usage",
                    "proc memory usage",
                ]
            )
            for (
                model_type,
                model_size,
                stn_uni,
                hyp_uni,
                stn_text,
                hyp_text,
                stn_nile,
                hyp_nile,
                features,
                prediction,
                prediction_time,
                cpu_usage,
                memory_usage,
                proc_cpu_usage,
                proc_mem_usage,
            ) in results:
                csv_writer.writerow(
                    [
                        model_type,
                        model_size,
                        stn_uni,
                        hyp_uni,
                        stn_text,
                        hyp_text,
                        stn_nile,
                        hyp_nile,
                        features,
                        prediction,
                        prediction_time,
                        cpu_usage,
                        memory_usage,
                        proc_cpu_usage,
                        proc_mem_usage,
                    ]
                )

        with open(
            config.PREDICTION_TIME_RESULTS_PATH.format("campi", "deploy"),
            "a",
            encoding="UTF-8",
        ) as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=",")
            csv_writer.writerow(
                [
                    "model",
                    "dataset",
                    "sentence university",
                    "sentence text",
                    "sentence nile",
                    "n ambiguities",
                    "deploy time",
                    "cpu usage",
                    "memory usage",
                    "proc cpu usage",
                    "proc memory usage",
                ]
            )
            for (
                model_type,
                model_size,
                stn_uni,
                stn_text,
                stn_nile,
                n_ambiguities,
                deploy_time,
                cpu_usage,
                memory_usage,
                proc_cpu_usage,
                proc_mem_usage,
            ) in deploy_intent_results:
                csv_writer.writerow(
                    [
                        model_type,
                        model_size,
                        stn_uni,
                        stn_text,
                        stn_nile,
                        n_ambiguities,
                        deploy_time,
                        cpu_usage,
                        memory_usage,
                        proc_cpu_usage,
                        proc_mem_usage,
                    ]
                )


if __name__ == "__main__":
    # export()
    # run()
    # test(100, 'forest')
    # train(1000, "forest")
    # train(5000, "forest")
    # train(10000, "forest")
    # train(10000, "svm")
    # train(10000, "log")
    # validate(10000, 'forest')
    # analyze_campus_policies_by_uni(10000)
    # analyze_campus_policies(10000)
    analyze_training_time(dataset_sizes=[100])
    analyze_prediction_time(model_sizes=[100])
