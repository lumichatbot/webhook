""" Evaluation of Ambiguities module """

import csv
import numpy as np

from ..utils import plotter, config


def plot_training_time_results():
    """Plots training time results"""
    print("PLOTTING TRAINING TIME")

    models_results = []
    with open(
        config.TRAINING_TIME_RESULTS_PATH.format("campi"), "r", encoding="UTF-8"
    ) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        next(csv_reader)
        for row in csv_reader:
            models_results.append(
                {
                    "dataset": row[0],  # "dataset_size": row[0],
                    "model": row[1],
                    "training_time": float(row[2]),
                    "cpu_usage": [float(x) for x in row[3].split(";")],
                    "memory_usage": [float(x) for x in row[4].split(";")],
                    "proc_cpu_usage": [float(x) for x in row[5].split(";")],
                    "proc_memory_usage": [float(x) for x in row[6].split(";")],
                }
            )

    plotter.plot_bars(
        [100, 1000, 5000, 10000],
        [
            [
                np.mean(
                    [
                        result["training_time"]
                        for result in models_results
                        if result["model"] == model
                    ]
                )
                for model in ["svm", "log", "forest"]
            ],
            [
                np.mean(
                    [
                        result["training_time"]
                        for result in models_results
                        if result["model"] == model
                    ]
                )
                for model in ["svm", "log", "forest"]
            ],
            [
                np.mean(
                    [
                        result["training_time"]
                        for result in models_results
                        if result["model"] == model
                    ]
                )
                for model in ["svm", "log", "forest"]
            ],
        ],
        labels=["svm", "log", "forest"],
        title="Training time",
        xlabel="Dataset size",
        ylabel="Time (s)",
        size=(4, 1.5),
        path="../res/plot/training_time.pdf",
    )

    # plotter.plot_lines(
    #     [100, 1000, 5000, 10000],
    #     [
    #         [
    #             np.mean(
    #                 [
    #                     np.mean(result["cpu_usage"])
    #                     for result in models_results
    #                     if result["model"] == model
    #                 ]
    #             )
    #             for model in ["svm", "log", "forest"]
    #         ],
    #         [
    #             np.mean(
    #                 [
    #                     np.mean(result["memory_usage"])
    #                     for result in models_results
    #                     if result["model"] == model
    #                 ]
    #             )
    #             for model in ["svm", "log", "forest"]
    #         ],
    #         [
    #             np.mean(
    #                 [
    #                     np.mean(result["proc_cpu_usage"])
    #                     for result in models_results
    #                     if result["model"] == model
    #                 ]
    #             )
    #             for model in ["svm", "log", "forest"]
    #         ],
    #         [
    #             np.mean(
    #                 [
    #                     np.mean(result["proc_memory_usage"])
    #                     for result in models_results
    #                     if result["model"] == model
    #                 ]
    #             )
    #             for model in ["svm", "log", "forest"]
    #         ],
    #     ],
    #     labels=["svm", "log", "forest"],
    #     title="Training time",
    #     xlabel="Dataset size",
    #     ylabel="Time (s)",
    #     size=(4, 1.5),
    #     path="../res/plot/cpu_mem_usage.pdf",
    # )


if __name__ == "__main__":
    plot_training_time_results()
