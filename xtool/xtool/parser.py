class Parser:
    """
    Generic class for defining a parser.
    """

    """
    @param subParsers : the sub parses to which the actions should be attached
    @param topLevel : specifies if the given subParsers is attached to the top level parser.
    """
    @staticmethod
    def addActions(subParsers, topLevel=False):
        raise NotImplementedError("Please implement this method")
