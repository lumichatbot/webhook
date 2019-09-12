""" Response beautifier for Google Actions """

from copy import deepcopy

import re

from nile import config


def beautify_intent(intent):
    """ Beautify Nile intent """
    beautified = deepcopy(intent)
    regex = r"('[^'\\]*(?:\\.[^'\\]*)*')|\b{0}\b"
    for word in config.NILE_OPERATIONS:
        beautified = re.sub(regex.format(word), lambda m: m.group(1) if m.group(1) else "  \n&nbsp;&nbsp;&nbsp;&nbsp;**{}** ".format(word), beautified)
    return beautified


def beautify(intent, words_to_highlight):
    """ Beautify Nile intent """
    beautified = deepcopy(intent)
    regex = r"('[^'\\]*(?:\\.[^'\\]*)*')|\b{0}\b"
    for word in words_to_highlight:
        beautified = re.sub(regex.format(word), lambda m: m.group(1) if m.group(1) else " **{}** ".format(word), beautified)
    return beautified
