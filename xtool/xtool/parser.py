class Parser:
    """
    Generic class for defining a parser.
    """

    def __init__(self, configManager, versionManager, instanceManager,
                 snapshotManager, upgradeManager, execEnvironment):
        self.configManager = configManager
        self.versionManager = versionManager
        self.instanceManager = instanceManager
        self.snapshotManager = snapshotManager
        self.upgradeManager = upgradeManager
        self.execEnvironment = execEnvironment

    """
    @param subParsers : the sub parses to which the actions should be attached
    @param topLevel : specifies if the given subParsers is attached to the top level parser.
    """
    @staticmethod
    def addActions(subParsers, topLevel=False):
        raise NotImplementedError("Please implement this method")

    """
    @param args : the arguments to handle
    @param action : the action specified by the user
    """
    @staticmethod
    def handleArgs(args, action):
        raise NotImplementedError("Please implement this method")
