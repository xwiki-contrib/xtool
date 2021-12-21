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
        subParsers.add_parser('prune', aliases=['p'], help='remove unused versions')

    """
    See Parsers#handleArgs()
    """
    def handleArgs(self, args, action):
        if action in ['download', 'd']:
            self.versionManager.download(args.version)
        elif action in ['prune', 'p']:
            self.versionManager.prune()
