#!/usr/bin/env python3

import logging

from configuration import ConfigManager
from execution import ExecEnvironment
from instance.manager import InstanceManager
from snapshot.manager import SnapshotManager
from instance.upgrade import UpgradeManager
from version.manager import VersionManager

from utils import init_logger
from utils import parse_args

args = parse_args()
init_logger(args.verbose)
logger = logging.getLogger('Main')

cm = ConfigManager()
vm = VersionManager(cm)
im = InstanceManager(cm, vm)
sm = SnapshotManager(cm, vm, im)
um = UpgradeManager(cm, vm, im)
ex = ExecEnvironment()

logger.debug('Arguments : {}'.format(args))
if (args.action == 'list'):
    if (args.action == 'versions'):
        vm.list()
    elif (args.action == 'instances'):
        im.list()
    elif (args.action == 'snapshots'):
        sm.list()
elif (args.action == 'download'):
    vm.download(args.version)
elif (args.action == 'config'):
    if args.set is not None:
        cm.set(args.property_name, args.set)
        cm.persist()
    else:
        print(cm.get(args.property_name))
elif (args.action == 'copy'):
    im.copy(args.instance_name, args.new_instance_name)
elif (args.action == 'create'):
    im.create(args.instance_name, args.version)
elif (args.action == 'edit'):
    im.edit(args.instance_name, args.file)
elif (args.action == 'snapshot'):
    if (args.action == 'create'):
        sm.create(args.entity_name)
    if (args.action == 'restore'):
        sm.restore(args.entity_name, args.overwrite)
elif (args.action == 'start'):
    # Check if we have an explicit instance name, else, use the environment
    if args.entity_name:
        im.start(args.entity_name, args.port, args.debug, args.temp)
    elif ex.getInferredInstanceName():
        im.start(ex.getInferredInstanceName(), args.port, args.debug)
    else:
        logger.error('Unable to determine the name of the instance to start.')
elif (args.action == 'remove'):
    im.remove(args.instance_name)
elif (args.action == 'upgrade'):
    um.upgrade(args.instance_name, args.version)
