""" plotter utils """
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from sklearn.metrics import auc, roc_curve
from sklearn.model_selection import StratifiedKFold


def plot_pie_chart(labels, sizes, filename=None):
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.sans-serif'] = 'Roboto-Light'
    # print(fm.findSystemFonts(fontpaths=None, fontext='ttf'))

    # prop = fm.FontProperties(fname=f.name)

    colors = ["#dcedff", "#94b0da", "#8f91a2", "#505a5b", "#343f3e"]
    # colors = ["#343f3e", "#505a5b",  "#8f91a2", "#94b0da", "#dcedff"]
    fig1, ax1 = plt.subplots()
    patches, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                                        startangle=90, colors=colors, pctdistance=0.8)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.setp(texts, size='medium')
    plt.setp(autotexts, size="medium")

    if filename:
        plt.savefig(filename)
        plt.close()
    else:
        plt.show()


def precision_recall_curve(dataset_size, rates):
    """ plots precision recall curve of model """
    plt.figure()
    plt.title("Precision Recall Curve for {} dataset".format(dataset_size))
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.grid()

    for (mtype, precision, recall) in rates:
        plt.plot(recall, precision, lw=2, label='Precision-recall for model {0}'''.format(mtype))

    return plt


def plot_roc_curve(dataset_size, model_type, model, data, targets):
    """ plots roc curve for each model in rates list """
    # Classification and ROC analysis
    plt.figure()
    # Run classifier with cross-validation and plot ROC curves
    cross_val = StratifiedKFold(n_splits=10, shuffle=True)

    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)

    for i, (train, test) in enumerate(cross_val.split(data, targets)):
        model.train([data[j] for j in train], [targets[j] for j in train], dataset_size)
        probabilities = model.predict_proba([data[j] for j in test])
        # Compute ROC curve and area the curve
        fpr, tpr, _ = roc_curve([targets[j] for j in test], probabilities[:, 1])
        mean_tpr += np.interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc))

    plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')

    mean_tpr /= 10
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    plt.plot(mean_fpr, mean_tpr, 'k--', label='Mean ROC (area = %0.2f)' % mean_auc, lw=2)

    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) for {} with dataset {}'.format(model_type, dataset_size))
    plt.legend(loc="lower right")

    return plt


def learning_curve(train_sizes, train_scores, test_scores):
    """ plots learning curve of model """

    plt.rcParams.update({'text.color': "#343f3e",
                         'axes.labelcolor': "#343f3e"})
    plt.figure()
    plt.minorticks_on()
    plt.grid(b=True, axis='y', which='major', color="#343f3e")
    plt.grid(b=True, axis='y', which='minor', color="#343f3e", alpha=0.2)
    #plt.title("Learning Curve for {} and {} dataset".format(model_type, dataset_size))
    plt.xlabel("Training samples")
    plt.ylabel("MSE", color="#343f3e")
    train_scores_mean = -np.mean(train_scores, axis=1)
    #train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = -np.mean(test_scores, axis=1)
    #test_scores_std = np.std(test_scores, axis=1)
    plt.grid()

    # plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
    #                  train_scores_mean + train_scores_std, alpha=0.1,
    #                  color="r")
    # plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
    #                  test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', dashes=[6, 2], color="#505a5b", label="Training")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="#94b0da", label="Cross-validation")

    plt.legend(loc="best")
    return plt
