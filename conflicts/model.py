""" Classification Model """
import os
import numpy as np
import traceback

from joblib import dump, load
from sklearn.svm import SVC, LinearSVC
from sklearn.metrics import roc_curve, precision_recall_curve
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate, cross_val_predict, learning_curve
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_selection import SelectFromModel

from utils import config


class ClassificationModel(object):
    """ Model wrapper """

    def __init__(self, model_type):
        print('[INFO] Creating model...')

        self.model_type = model_type

        if model_type == 'svm':
            clf = SVC(kernel='linear', verbose=3)
        elif model_type == 'forest':
            clf = RandomForestClassifier(verbose=3)
        else:
            clf = LogisticRegression(verbose=3, random_state=0, solver='lbfgs', multi_class='multinomial')

        self.model = make_pipeline(RobustScaler(), SelectFromModel(LinearSVC(penalty="l1", dual=False)), clf)

    def train(self, features, targets, dataset_size):
        """ trains the model with given features and expected targets """
        print("BEGGINING TRAINING")
        if not self.load(dataset_size):
            self.model.fit(features, targets)

        if self.model_type == 'svm' or self.model_type == 'log':
            print("FEATURES", self.model_type, self.model.steps[2][1].coef_)
        else:
            print("FEATURES forest", self.model.steps[2][1].feature_importances_)

    def test(self, features):
        """ tests the model with given features and expected targets """
        print("BEGGINING TESTING")
        predicted_targets = self.model.predict(features)

        return predicted_targets

    def predict_proba(self, features):
        """ predict probability for each class """
        return self.model.predict_proba(features)

    def cross_validate(self, features, targets):
        """ Cross validates the model """
        scoring = ['precision_macro', 'recall_macro', 'f1_macro']
        scores = cross_validate(self.model, features, targets, scoring=scoring, cv=10, return_train_score=False)
        return scores

    def learning_curve(self, features, targets):
        """ Cross validates the model """
        train_sizes, train_scores, test_scores = learning_curve(
            self.model, features, targets, shuffle=True, cv=10, scoring='neg_mean_squared_error')
        return train_sizes, train_scores, test_scores

    def predict(self, features):
        """ given an array of input features, predicts if case is a conflict or not """
        return self.model.predict(features)

    def load(self, dataset_size):
        """ Loads model weights, if they exist """
        model_path = config.MODEL_WEIGHTS_PATH.format(self.model_type, dataset_size)
        print("Model path", model_path)
        if os.path.isfile(model_path):
            try:
                self.model = load(model_path)
                return True
            except:
                traceback.print_exc()
                return False
        return False

    def save(self, dataset_size):
        """ saves model weights """
        return dump(self.model, config.MODEL_WEIGHTS_PATH.format(self.model_type, dataset_size))
