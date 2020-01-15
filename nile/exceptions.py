""" Nile syntax error exceptions """


class NileSyntaxError(Exception):
    """ Base class for Nile syntax exceptions """
    pass


class MissingTargetError(NileSyntaxError):
    """
        Exception raised for syntax error when the built intent has no target
        Attributes:
            expression -- input expression in which the error occurred
            message -- explanation of the error
    """

    def __init__(self, message, entities=None):
        self.entities = entities
        self.message = message


class MissingOperationError(NileSyntaxError):
    """
        Exception raised for syntax error when the built intent has no operation
        Attributes:
            entities -- input entities in which the error occurred
            message -- explanation of the error
    """

    def __init__(self, message, entities=None):
        self.entities = entities
        self.message = message


class MissingParameterError(NileSyntaxError):
    """
        Exception raised for syntax error when the built intent is missing some paremeter
        Attributes:
            entities -- input entities in which the error occurred
            message -- explanation of the error
    """

    def __init__(self, message, entities=None):
        self.entities = entities
        self.message = message
