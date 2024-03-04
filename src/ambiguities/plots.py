""" Evaluation of Ambiguities module """

import csv
import scipy
import numpy as np

import matplotlib.pyplot as plt

from matplotlib import rcParams


FONT_NAME = "Roboto"
FONT_WEIGHT = "light"

rcParams["font.family"] = "serif"
rcParams["font.serif"] = [FONT_NAME]
rcParams["font.weight"] = FONT_WEIGHT


from ..utils import config


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2.0, n - 1)
    return m, h


def plot_training_time_results():
    """Plots training time results"""
    print("PLOTTING TRAINING TIME")

    svm_results = []
    log_results = []
    forest_results = []
    with open(
        config.TRAINING_RESULTS_PATH.format("time", "campi"), "r", encoding="UTF-8"
    ) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        next(csv_reader)
        for row in csv_reader:
            if row[2] == "svm":
                svm_results.append(
                    {
                        "iteration": row[0],
                        "model": row[2],
                        "training_time": float(row[3]),
                    }
                )
            elif row[2] == "log":
                log_results.append(
                    {
                        "iteration": row[0],
                        "model": row[2],
                        "training_time": float(row[3]),
                    }
                )
            elif row[2] == "forest":
                forest_results.append(
                    {
                        "iteration": row[0],
                        "model": row[2],
                        "training_time": float(row[3]),
                    }
                )

    svm_mean, svm_error = mean_confidence_interval(
        [result["training_time"] for result in svm_results]
    )
    log_mean, log_error = mean_confidence_interval(
        [result["training_time"] for result in log_results]
    )
    forest_mean, forest_error = mean_confidence_interval(
        [result["training_time"] for result in forest_results]
    )
    results_agg = {
        "svm": {
            "mean": svm_mean,
            "error": svm_error,
        },
        "log": {
            "mean": log_mean,
            "error": log_error,
        },
        "forest": {
            "mean": forest_mean,
            "error": forest_error,
        },
    }

    print("RESULTS AGG", results_agg)

    plt.figure(figsize=(4, 1.5))  # width:4, height:1.5
    width = 0.4
    fig, ax = plt.subplots()
    # locs = np.arange(len(results_agg.items()))  # the label locations
    colors = [
        "#396ab1",
        "#da7c30",
        "#3e9651",
        "#c8c5c3",
        "#524a47",
        "#edeef0",
    ]

    ax.bar(
        results_agg.keys(),
        [res["mean"] for res in results_agg.values()],
        width,
        color=colors[0],
        # label=label,
        yerr=[res["error"] for res in results_agg.values()],
    )

    fig.tight_layout()
    plt.savefig(config.TRAINING_PLOTS_PATH.format("time"))
    plt.close()


def plot_deploy_time_results():
    """Plots prediction time results"""
    print("PLOTTING DEPLOY TIME")

    svm_results = []
    log_results = []
    forest_results = []
    intents = {}
    intent_id = 0

    with open(
        config.DEPLOY_RESULTS_PATH.format("time", "campi"),
        "r",
        encoding="UTF-8",
    ) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")

        for row in csv_reader:
            # iteration,model,dataset,sentence university,sentence text,sentence nile,n ambiguities,deploy time
            if row[0] == "iteration":
                # Skip header
                continue

            iteration = row[0]
            model = row[1]
            dataset = row[2]
            sentence_university = row[3]
            sentence_text = row[4]
            sentence_nile = row[5]
            n_ambiguities = row[6]
            deploy_time = row[7]

            if sentence_text not in intents:
                intents[sentence_text] = intent_id
                intent_id += 1

            res = {
                "iteration": iteration,
                "model": model,
                "dataset": dataset,
                "sentence_university": sentence_university,
                "sentence_text": sentence_text,
                "sentence_nile": sentence_nile,
                "n_ambiguities": n_ambiguities,
                "deploy_time": deploy_time,
                "intent_number": intents[sentence_text],
            }

            if model == "svm":
                svm_results.append(res)
            elif model == "log":
                log_results.append(res)
            elif model == "forest":
                forest_results.append(res)

    deploy_time_by_intent = {
        "svm": [],
        "log": [],
        "forest": [],
    }

    num_intents = len(intents)
    # print("SVM", svm_results)
    for model in ["svm", "log", "forest"]:
        for intent in range(0, num_intents):
            # filter just intents using 10000 dataset
            intent_res = [
                float(res["deploy_time"])
                for res in eval(f"{model}_results")
                if res["intent_number"] == intent
                and res["dataset"] == "10000"
                and float(res["deploy_time"]) < 10  # filter outliers
            ]
            intent_mean, intent_error = mean_confidence_interval(intent_res)
            deploy_time_by_intent[model].append((intent_mean, intent_error))

    fig, ax = plt.subplots()
    fig.set_size_inches(4, 2)
    # locs = np.arange(len(results_agg.items()))  # the label locations
    colors = [
        "#396ab1",
        "#da7c30",
        "#3e9651",
        "#c8c5c3",
        "#524a47",
        "#edeef0",
    ]

    # ax.plot(
    #     range(1, num_intents + 1),
    #     [res[0] for res in deploy_time_by_intent["svm"]],
    #     color=colors[0],
    #     label="SVM",
    # )
    # ax.fill_between(
    #     range(1, num_intents + 1),
    #     [res[0] - res[1] for res in deploy_time_by_intent["svm"]],
    #     [res[0] + res[1] for res in deploy_time_by_intent["svm"]],
    #     color=colors[0],
    #     alpha=0.3,
    # )

    # ax.plot(
    #     range(1, num_intents + 1),
    #     [res[0] for res in deploy_time_by_intent["log"]],
    #     color=colors[1],
    #     label="Log. Reg.",
    # )
    # ax.fill_between(
    #     range(1, num_intents + 1),
    #     [res[0] - res[1] for res in deploy_time_by_intent["log"]],
    #     [res[0] + res[1] for res in deploy_time_by_intent["log"]],
    #     color=colors[1],
    #     alpha=0.3,
    # )

    ax.plot(
        range(1, num_intents + 1),
        [res[0] for res in deploy_time_by_intent["forest"]],
        color=colors[2],
        label="Rand. Forest",
    )
    ax.fill_between(
        range(1, num_intents + 1),
        [res[0] - res[1] for res in deploy_time_by_intent["forest"]],
        [res[0] + res[1] for res in deploy_time_by_intent["forest"]],
        color=colors[2],
        alpha=0.3,
    )

    # ticks every 5 intents
    ax.set_xticks(range(0, num_intents + 1, 5))
    ax.set_xticklabels(range(0, num_intents + 1, 5))
    ax.legend()

    ax.set_xlabel("Intent number")
    ax.set_ylabel("Prediction time (s)")

    fig.tight_layout()
    plt.savefig(config.DEPLOY_PLOTS_PATH.format("time"))
    plt.close()


def plot_training_usage_results():
    """Plots training time results"""
    print("PLOTTING TRAINING RESOURCE USAGE")

    svm_results = []
    log_results = []
    forest_results = []
    with open(
        config.TRAINING_RESULTS_PATH.format("usage", "campi"),
        "r",
        encoding="UTF-8",
    ) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        next(csv_reader)
        for row in csv_reader:
            # iteration,dataset,model,training time,cpu usage,memory usage,proc cpu usage,proc memory usage
            iteration = row[0]
            dataset = row[1]
            model = row[2]
            training_time = row[3]
            cpu_usage = row[4]
            memory_usage = row[5]
            proc_cpu_usage = row[6]
            proc_memory_usage = row[7]

            results = {
                "iteration": iteration,
                "dataset": dataset,
                "model": model,
                "training_time": training_time,
                "cpu_usage": np.mean([float(val) for val in cpu_usage.split(";")]),
                "memory_usage": np.mean(
                    [float(val) for val in memory_usage.split(";")]
                ),
                "proc_cpu_usage": np.mean(
                    [float(val) for val in proc_cpu_usage.split(";")]
                ),
                "proc_memory_usage": np.mean(
                    [float(val) for val in proc_memory_usage.split(";")]
                ),
            }

            if model == "svm":
                svm_results.append(results)
            elif model == "log":
                log_results.append(results)
            elif model == "forest":
                forest_results.append(results)

    svm_cpu_mean, svm_cpu_error = mean_confidence_interval(
        [result["cpu_usage"] for result in svm_results]
    )
    svm_memory_mean, svm_memory_error = mean_confidence_interval(
        [result["memory_usage"] for result in svm_results]
    )
    svm_proc_cpu_mean, svm_proc_cpu_error = mean_confidence_interval(
        [result["proc_cpu_usage"] for result in svm_results]
    )
    svm_proc_memory_mean, svm_proc_memory_error = mean_confidence_interval(
        [result["proc_memory_usage"] for result in svm_results]
    )

    log_cpu_mean, log_cpu_error = mean_confidence_interval(
        [result["cpu_usage"] for result in log_results]
    )
    log_memory_mean, log_memory_error = mean_confidence_interval(
        [result["memory_usage"] for result in log_results]
    )
    log_proc_cpu_mean, log_proc_cpu_error = mean_confidence_interval(
        [result["proc_cpu_usage"] for result in log_results]
    )
    log_proc_memory_mean, log_proc_memory_error = mean_confidence_interval(
        [result["proc_memory_usage"] for result in log_results]
    )

    forest_cpu_mean, forest_cpu_error = mean_confidence_interval(
        [result["cpu_usage"] for result in forest_results]
    )
    forest_memory_mean, forest_memory_error = mean_confidence_interval(
        [result["memory_usage"] for result in forest_results]
    )
    forest_proc_cpu_mean, forest_proc_cpu_error = mean_confidence_interval(
        [result["proc_cpu_usage"] for result in forest_results]
    )
    forest_proc_memory_mean, forest_proc_memory_error = mean_confidence_interval(
        [result["proc_memory_usage"] for result in forest_results]
    )

    results_agg_mean = {
        "SVM": {
            "cpu": svm_cpu_mean,
            "memory": svm_memory_mean,
            "proc_cpu": svm_proc_cpu_mean,
            "proc_memory": svm_proc_memory_mean,
        },
        "Log. Reg.": {
            "cpu": log_cpu_mean,
            "memory": log_memory_mean,
            "proc_cpu": log_proc_cpu_mean,
            "proc_memory": log_proc_memory_mean,
        },
        "Rand. Forest": {
            "cpu": forest_cpu_mean,
            "memory": forest_memory_mean,
            "proc_cpu": forest_proc_cpu_mean,
            "proc_memory": forest_proc_memory_mean,
        },
    }

    results_agg_error = {
        "SVM": {
            "cpu": svm_cpu_error,
            "memory": svm_memory_error,
            "proc_cpu": svm_proc_cpu_error,
            "proc_memory": svm_proc_memory_error,
        },
        "Log. Reg.": {
            "cpu": log_cpu_error,
            "memory": log_memory_error,
            "proc_cpu": log_proc_cpu_error,
            "proc_memory": log_proc_memory_error,
        },
        "Rand. Forest": {
            "cpu": forest_cpu_error,
            "memory": forest_memory_error,
            "proc_cpu": forest_proc_cpu_error,
            "proc_memory": forest_proc_memory_error,
        },
    }

    print("RESULTS AGG", results_agg_mean, results_agg_error)

    width = 0.15
    fig, ax = plt.subplots()
    fig.set_size_inches(4, 2)
    # locs = np.arange(len(results_agg.items()))  # the label locations
    colors = [
        "#396ab1",
        "#da7c30",
        "#3e9651",
        "#c8c5c3",
        "#524a47",
        "#edeef0",
    ]
    ind = np.arange(len(results_agg_mean.keys()))

    num_bars = len(results_agg_mean.keys())
    position = ind + (width * (1 - num_bars) / 2) + 0 * width
    labels = {
        "cpu": "CPU",
        "memory": "Memory",
        "proc_cpu": "Proc. CPU",
        "proc_memory": "Proc. Memory",
    }

    for i, key in enumerate(["cpu", "memory", "proc_cpu", "proc_memory"]):
        position = ind + (width * (1 - num_bars) / 2) + i * width
        ax.bar(
            position,
            [res[key] for res in results_agg_mean.values()],
            width,
            color=colors[i],
            label=labels[key],
            yerr=[res[key] for res in results_agg_error.values()],
        )
        position = ind + (width * (1 - num_bars) / 2) + 1 * width

    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(results_agg_mean.keys())
    ax.legend()
    ax.set_xlabel("Model")
    ax.set_ylabel("Resource usage (%)")

    fig.tight_layout()
    plt.savefig(config.TRAINING_PLOTS_PATH.format("usage"))
    plt.close()


def plot_deploy_usage_results():
    """Plots prediction time results"""
    print("PLOTTING DEPLOY RESOURCE USAGE")

    svm_results = []
    log_results = []
    forest_results = []
    with open(
        config.DEPLOY_RESULTS_PATH.format("usage", "campi"),
        "r",
        encoding="UTF-8",
    ) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        next(csv_reader)
        for row in csv_reader:
            # iteration,model,dataset,sentence university,sentence text,sentence nile,n ambiguities,deploy time,cpu usage,memory usage,proc cpu usage,proc memory usage

            # print(row)
            iteration = row[0]
            model = row[1]
            dataset = row[2]
            sentence_university = row[3]
            sentence_text = row[4]
            sentence_nile = row[5]
            n_ambiguities = row[6]
            deploy_time = row[7]
            cpu_usage = row[8] if row[8] else 0
            memory_usage = row[9] if row[9] else 0
            proc_cpu_usage = row[10] if row[10] else 0
            proc_memory_usage = row[11] if row[11] else 0

            results = {
                "iteration": iteration,
                "model": model,
                "dataset": dataset,
                "sentence_university": sentence_university,
                "sentence_text": sentence_text,
                "sentence_nile": sentence_nile,
                "n_ambiguities": n_ambiguities,
                "deploy_time": deploy_time,
                "cpu_usage": float(cpu_usage),
                "memory_usage": float(memory_usage),
                "proc_cpu_usage": float(proc_cpu_usage),
                "proc_memory_usage": float(proc_memory_usage),
            }

            if model == "svm":
                svm_results.append(results)
            elif model == "log":
                log_results.append(results)
            elif model == "forest":
                forest_results.append(results)

    svm_cpu_mean, svm_cpu_error = mean_confidence_interval(
        [result["cpu_usage"] for result in svm_results if result["dataset"] == "10000"]
    )
    svm_memory_mean, svm_memory_error = mean_confidence_interval(
        [
            result["memory_usage"]
            for result in svm_results
            if result["dataset"] == "10000"
        ]
    )
    svm_proc_cpu_mean, svm_proc_cpu_error = mean_confidence_interval(
        [
            result["proc_cpu_usage"]
            for result in svm_results
            if result["dataset"] == "10000"
        ]
    )
    svm_proc_memory_mean, svm_proc_memory_error = mean_confidence_interval(
        [
            result["proc_memory_usage"]
            for result in svm_results
            if result["dataset"] == "10000"
        ]
    )

    log_cpu_mean, log_cpu_error = mean_confidence_interval(
        [result["cpu_usage"] for result in log_results if result["dataset"] == "10000"]
    )
    log_memory_mean, log_memory_error = mean_confidence_interval(
        [
            result["memory_usage"]
            for result in log_results
            if result["dataset"] == "10000"
        ]
    )
    log_proc_cpu_mean, log_proc_cpu_error = mean_confidence_interval(
        [
            result["proc_cpu_usage"]
            for result in log_results
            if result["dataset"] == "10000"
        ]
    )
    log_proc_memory_mean, log_proc_memory_error = mean_confidence_interval(
        [
            result["proc_memory_usage"]
            for result in log_results
            if result["dataset"] == "10000"
        ]
    )

    forest_cpu_mean, forest_cpu_error = mean_confidence_interval(
        [
            result["cpu_usage"]
            for result in forest_results
            if result["dataset"] == "10000"
        ]
    )
    forest_memory_mean, forest_memory_error = mean_confidence_interval(
        [
            result["memory_usage"]
            for result in forest_results
            if result["dataset"] == "10000"
        ]
    )
    forest_proc_cpu_mean, forest_proc_cpu_error = mean_confidence_interval(
        [
            result["proc_cpu_usage"]
            for result in forest_results
            if result["dataset"] == "10000"
        ]
    )
    forest_proc_memory_mean, forest_proc_memory_error = mean_confidence_interval(
        [
            result["proc_memory_usage"]
            for result in forest_results
            if result["dataset"] == "10000"
        ]
    )

    results_agg_mean = {
        "SVM": {
            "cpu": svm_cpu_mean,
            "memory": svm_memory_mean,
            "proc_cpu": svm_proc_cpu_mean,
            "proc_memory": svm_proc_memory_mean,
        },
        "Log. Reg.": {
            "cpu": log_cpu_mean,
            "memory": log_memory_mean,
            "proc_cpu": log_proc_cpu_mean,
            "proc_memory": log_proc_memory_mean,
        },
        "Rand. Forest": {
            "cpu": forest_cpu_mean,
            "memory": forest_memory_mean,
            "proc_cpu": forest_proc_cpu_mean,
            "proc_memory": forest_proc_memory_mean,
        },
    }

    results_agg_error = {
        "SVM": {
            "cpu": svm_cpu_error,
            "memory": svm_memory_error,
            "proc_cpu": svm_proc_cpu_error,
            "proc_memory": svm_proc_memory_error,
        },
        "Log. Reg.": {
            "cpu": log_cpu_error,
            "memory": log_memory_error,
            "proc_cpu": log_proc_cpu_error,
            "proc_memory": log_proc_memory_error,
        },
        "Rand. Forest": {
            "cpu": forest_cpu_error,
            "memory": forest_memory_error,
            "proc_cpu": forest_proc_cpu_error,
            "proc_memory": forest_proc_memory_error,
        },
    }

    print("RESULTS AGG", results_agg_mean, results_agg_error)

    width = 0.15
    fig, ax = plt.subplots()
    fig.set_size_inches(4, 2)
    # locs = np.arange(len(results_agg.items()))  # the label locations
    colors = [
        "#396ab1",
        "#da7c30",
        "#3e9651",
        "#c8c5c3",
        "#524a47",
        "#edeef0",
    ]
    ind = np.arange(len(results_agg_mean.keys()))

    num_bars = len(results_agg_mean.keys())
    position = ind + (width * (1 - num_bars) / 2) + 0 * width
    labels = {
        "cpu": "CPU",
        "memory": "Memory",
        "proc_cpu": "Proc. CPU",
        "proc_memory": "Proc. Memory",
    }

    for i, key in enumerate(["cpu", "memory", "proc_cpu", "proc_memory"]):
        position = ind + (width * (1 - num_bars) / 2) + i * width
        ax.bar(
            position,
            [res[key] for res in results_agg_mean.values()],
            width,
            color=colors[i],
            label=labels[key],
            yerr=[res[key] for res in results_agg_error.values()],
        )
        position = ind + (width * (1 - num_bars) / 2) + 1 * width

    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(results_agg_mean.keys())
    ax.legend()
    ax.set_xlabel("Model")
    ax.set_ylabel("Resource usage (%)")

    fig.tight_layout()
    plt.savefig(config.DEPLOY_PLOTS_PATH.format("usage"))
    plt.close()


if __name__ == "__main__":
    # plot_training_time_results()
    # plot_deploy_time_results()
    plot_training_usage_results()
    # plot_deploy_usage_results()
