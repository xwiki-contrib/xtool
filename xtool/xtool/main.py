#!/usr/bin/env python3

import logging

from configuration import ConfigManager
from execution import ExecEnvironment
from instances import InstanceManager
from versions import VersionManager

from utils import init_logger
from utils import parse_args

args = parse_args()
init_logger(args.verbose)
logger = logging.getLogger('Main')

cm = ConfigManager()
vm = VersionManager(cm)
im = InstanceManager(cm, vm)
ex = ExecEnvironment()

logger.debug('Arguments : {}'.format(args))
if ('list'.startswith(args.action)):
    if ('versions'.startswith(args.entity)):
        vm.list()
    elif ('instances'.startswith(args.entity)):
        im.list()
elif ('download'.startswith(args.action)):
    vm.download(args.version)
elif ('config'.startswith(args.action)):
    if args.set is not None:
        cm.set(args.property_name, args.set)
        cm.persist()
    else:
        print(cm.get(args.property_name))
elif ('create'.startswith(args.action)):
    im.create(args.instance_name, args.version)
elif ('edit'.startswith(args.action)):
    im.edit(args.instance_name, args.file)
elif ('start'.startswith(args.action)):
    # Check if we have an explicit instance name, else, use the environment
    if args.entity_name:
        im.start(args.entity_name, args.debug, args.temp)
    elif ex.getInferredInstanceName():
        im.start(ex.getInferredInstanceName(), args.debug)
    else:
        logger.error('Unable to determine the name of the instance to start.')
elif ('remove'.startswith(args.action)):
    im.remove(args.instance_name)
