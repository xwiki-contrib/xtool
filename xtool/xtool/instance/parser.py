from parser import Parser


class InstanceParser(Parser):
    """
    Parser for instance-related actions.
    """

    """
    See Parsers#addActions()
    """
    @staticmethod
    def addActions(subParsers, topLevel=False):
        # Start by adding actions that are top-level (incidentally, the most used)
        # Create action
        createParser = subParsers.add_parser('create', aliases=['c'], help='create a new instance')
        createParser.add_argument('instance_name', help='the name of the instance to create')
        createParser.add_argument('version', help='the XWiki version to use in the instance')

        # Start action
        startParser = subParsers.add_parser('start', aliases=['s'], help='start an instance')
        startParser.add_argument(
            'entity_name',
            nargs='?',
            default=None,
            help='the name of the instance or version (if --temp) to start'
        )
        startParser.add_argument('-d', '--debug', action='store_true', help='toggle debug mode')
        startParser.add_argument(
            '-p', '--port',
            help='specify a port on which the instance should be started'
        )
        startParser.add_argument(
            '-t', '--temp',
            action='store_true',
            help=('start a temporary instance: xtool will create a random instance name with '
                  'the given version and start it. The instance will be removed automatically after being killed.')
        )

        if not topLevel:
            # Upgrade action
            upgradeParser = subParsers.add_parser(
                'upgrade',
                aliases=['u'],
                help='upgrade an existing instance to a newer version'
            )
            upgradeParser.add_argument('instance_name', help='the name of the instance to upgrade')
            upgradeParser.add_argument('version', help='the version to which the instance should be upgraded')

            # Edit action
            editParser = subParsers.add_parser(
                'edit',
                aliases=['e'],
                help=('edit a file in the given instance, by default, xtool will search or the file in the WEB-INF '
                      'folder of the instance')
            )
            editParser.add_argument('instance_name', help='the name of the instance to use')
            editParser.add_argument('file', help=('the name of the file to edit, for example : `xwiki.cfg` '
                                                  'or `hibernate.xml`'))

            # Copy action
            copyParser = subParsers.add_parser('copy', aliases=['c'], help='copy an instance')
            copyParser.add_argument('instance_name', help='the name of the instance to copy')
            copyParser.add_argument('new_instance_name', help='the new name of the instance')
