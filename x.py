#!/usr/bin/env python3
import argparse
import logging

from configuration import ConfigManager
from instances import InstanceManager
from versions import VersionManager
from utils import initRootLogger

rootParser = argparse.ArgumentParser(description='Provide a set of tools to manage local XWiki installations')
rootParser.add_argument('--verbose', '-v', action='count', default=0, help='enable verbose logs')
rootParser.add_argument('--debug', '-d', action='store_true', help='If an XWiki instance is to be started, start it in debug mode')
rootParser.add_argument('action', help='the action to perform')
rootParser.add_argument('parameters', default=[], nargs='+', help='the action parameters')
args = rootParser.parse_args()

initRootLogger(args.verbose)
logger = logging.getLogger('Main')

cm = ConfigManager()
vm = VersionManager(cm)
im = InstanceManager(cm, vm)

logger.debug('Arguments : {}'.format(args))
logger.debug('Action : {}'.format(args.action))
logger.debug('Parameters : {}'.format(args.parameters))
if ('list'.startswith(args.action)):
    if ('versions'.startswith(args.parameters[0])):
      print(cm.versions())
    elif ('instances'.startswith(args.parameters[0])):
      print(cm.instances())
elif ('download'.startswith(args.action)):
    if (len(args.parameters) == 0):
        logger.error('No version provided')
    else:
        for version in args.parameters:
            vm.download(version)
elif ('create'.startswith(args.action)):
    if (len(args.parameters) < 2):
        logger.error('You should provide the instance name and the instance version.')
    else:
        im.create(args.parameters[0], args.parameters[1])
elif ('start'.startswith(args.action)):
    if (len(args.parameters) == 0):
        logger.error('No instance provided')
    else:
        im.start(args.parameters[0], args.debug)
elif ('remove'.startswith(args.action)):
    if (len(args.parameters) == 0):
        logger.error('You should provide the instance name.')
    else:
        im.remove(args.parameters[0])
