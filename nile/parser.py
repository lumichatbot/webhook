""" Nile parser module """
import re


def parse(nile):
    """ Parses a Nile intent from text and return dictionary with intent operation targets """
    from_pattern = re.compile(r".*from (.*) .*")
    to_pattern = re.compile(r".*to (.*) .*")
    group_pattern = re.compile(r".*for (.*) .*")
    set_unset_pattern = re.compile(r".*(set|unset) (.*) .*")
    allow_block_pattern = re.compile(r".*(allow|block) (.*) .*")
    add_remove_pattern = re.compile(r".*(add|remove) (.*) .*")
    op_targets = {}

    return op_targets
