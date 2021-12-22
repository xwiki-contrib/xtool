import logging

from parser import Parser


class VersionParser(Parser):
    """
    Parser for versions-related actions.
    """

    logger = logging.getLogger('VersionParser')

    """
    See Parsers#addActions()
    """
    @staticmethod
    def addActions(subParsers, topLevel=False):
        # Start by adding actions that are top-level (incidentally, the most used)
        # Download action
        downloadParser = subParsers.add_parser('download', aliases=['d'], help='download a new version')
        downloadParser.add_argument('version', help='the XWiki version to download')

        if not topLevel:
            # Remove action
            removeParser = subParsers.add_parser('remove', aliases=['r'], help='remove a version')
            removeParser.add_argument('version', help='the XWiki version to remove')
            # Prune action
            subParsers.add_parser('prune', aliases=['p'], help='remove any version that is not used by an instance')

    """
    See Parsers#handleArgs()
    """
    def handleArgs(self, args, action):
        if action in ['download', 'd']:
            self.versionManager.download(args.version)
        elif action in ['remove', 'r']:
            self.versionManager.remove(args.version)
        elif action in ['prune', 'p']:
            self.versionManager.prune()
