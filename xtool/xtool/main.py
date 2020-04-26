#!/usr/bin/env python3

import logging

from configuration import ConfigManager
from execution import ExecEnvironment
from instance.manager import InstanceManager
from snapshot.manager import SnapshotManager
from instance.upgrade import UpgradeManager
from version.manager import VersionManager
from version.parser import VersionParser
from instance.parser import InstanceParser
from snapshot.parser import SnapshotParser

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

vp = VersionParser(cm, vm, im, sm, um, ex)
ip = InstanceParser(cm, vm, im, sm, um, ex)
sp = SnapshotParser(cm, vm, im, sm, um, ex)

logger.debug('Arguments : {}'.format(args))
if (args.action in ['list', 'l']):
    if (args.entity == 'versions'):
        vm.list()
    elif (args.entity == 'instances'):
        im.list()
    elif (args.entity == 'snapshots'):
        sm.list()
# Shortcuts for accessing entities actions
elif (args.action in ['download', 'd']):
    vp.handleArgs(args, args.action)
elif (args.action in ['create', 'c', 'start', 's']):
    ip.handleArgs(args, args.action)
elif (args.action in ['snapshot', 'sp']):
    sp.handleArgs(args, args.action)
# Delegation to entity sub parsers
elif (args.action == 'version'):
    vp.handleArgs(args, args.subAction)
elif (args.action == 'instance'):
    ip.handleArgs(args, args.subAction)
elif (args.action == 'snapshot'):
    sp.handleArgs(args, args.subAction)
# Generic methods
elif (args.action == 'remove'):
    im.remove(args.instance_name)
elif (args.action == 'config'):
    if args.set is not None:
        cm.set(args.property_name, args.set)
        cm.persist()
    else:
        print(cm.get(args.property_name))
