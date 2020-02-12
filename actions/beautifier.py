""" Response beautifier for Google Actions """

from copy import deepcopy

import re

from utils import config


def beautify_intent(intent):
    """ Beautify Nile intent """
    beautified = deepcopy(intent)
    # regex_op = r"('[^'\\]*(?:\\.[^'\\]*)*')|\b{0}\b"
    regex_op = r"('[^'\\]*(?:\\.[^'\\]*)*')|\b{0}\b"
    for word in config.NILE_OPERATIONS:
        beautified = re.sub(regex_op.format(word),
                            lambda m: "<font color=`blue`>{}</font>".format(m.group(1)) if m.group(1)
                            else "  <br>&nbsp;&nbsp;&nbsp;&nbsp;<b>{}</b> ".format(word), beautified)
    return beautified


def beautify(intent, words_to_highlight):
    """ Beautify Nile intent """
    beautified = deepcopy(intent)
    regex = r"('[^'\\]*(?:\\.[^'\\]*)*')|\b{0}\b"
    for word in words_to_highlight:
        beautified = re.sub(regex.format(word), lambda m: m.group(
            1) if m.group(1) else " <b>{}</b> ".format(word), beautified)
    return beautified
