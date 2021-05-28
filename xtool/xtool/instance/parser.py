import logging

from parser import Parser


class InstanceParser(Parser):
    """
    Parser for instance-related actions.
    """

    logger = logging.getLogger('InstanceParser')

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
            copyParser = subParsers.add_parser('copy', aliases=['cp'], help='copy an instance')
            copyParser.add_argument('instance_name', help='the name of the instance to copy')
            copyParser.add_argument('new_instance_name', help='the new name of the instance')

            # Remove action
            removeParser = subParsers.add_parser('remove', aliases=['rm'], help='remove an entity')
            removeParser.add_argument('instance_name', help='the name of the instance to remove')

            # Symlink action
            symlinkParser = subParsers.add_parser('symlink', aliases=['sym'], help=('symlink files in the instance to'
                                                                                    'their equivalent in the version'))
            symlinkParser.add_argument(
                '-i',
                '--instance',
                help='the name of the instance to symlink'
            )
            symlinkParser.add_argument(
                '--all',
                action='store_true',
                help='symlink all instances'
            )

    """
    See Parsers#handleArgs()
    """
    def handleArgs(self, args, action):
        if action in ['create', 'c']:
            self.instanceManager.create(args.instance_name, args.version)
        elif action in ['start', 's']:
            # Check if we have an explicit instance name, else, use the environment
            if args.entity_name:
                self.instanceManager.start(args.entity_name, args.port, args.debug, args.temp)
            elif self.execEnvironment.getInferredInstanceName():
                self.instanceManager.start(
                    self.execEnvironment.getInferredInstanceName(), args.port, args.debug)
            else:
                self.logger.error('Unable to determine the name of the instance to start.')
        elif action in ['upgrade', 'u']:
            self.upgradeManager.upgrade(args.instance_name, args.version)
        elif action in ['edit', 'e']:
            self.instanceManager.edit(args.instance_name, args.file)
        elif action in ['copy', 'cp']:
            self.instanceManager.copy(args.instance_name, args.new_instance_name)
        elif (action in ['remove', 'rm']):
            self.instanceManager.remove(args.instance_name)
        elif (action in ['symlink', 'sym']):
            if args.all:
                for instance in self.configManager.instances():
                    self.instanceManager.symlink(instance['name'])
            elif args.instance is not None:
                self.instanceManager.symlink(args.instance)
            else:
                self.logger.error('Unable to determine the instance to symlink.')
