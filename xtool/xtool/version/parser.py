from parser import Parser


class VersionParser(Parser):
    """
    Parser for versions-related actions.
    """

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
            pass
