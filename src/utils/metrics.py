""" metrics for evaluation """


def precision(tp, fp):
    """ calculates precision """
    return (float(tp) / (tp + fp)) if (tp + fp) != 0 else 0.


def recall(tp, fn):
    """ calculates recall  """
    return (float(tp) / (tp + fn)) if (tp + fn) != 0 else 0.


def f1_score(prec, rec):
    """ calculates f1 score """
    denominator = prec + rec
    return (2 * ((prec * rec) / denominator)) if denominator > 0. else 0.
