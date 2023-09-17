import filecmp
import logging
import shutil

from os.path import basename
from packaging import version

from utils import random_chars


class UpgradeManager:
    logger = logging.getLogger('UpgradeManager')

    def __init__(self, configManager, versionManager, instanceManager):
        self.configManager = configManager
        self.versionManager = versionManager
        self.instanceManager = instanceManager

    def __copyAndCompareFiles(self, originalFilePath, newFilePath, keepconf):
        configFileName = basename(newFilePath)
        if filecmp.cmp(originalFilePath, newFilePath, shallow=False):
            self.logger.info('Configuration file [{}] do not need to be updated'.format(configFileName))
        else:
            self.logger.info('Configuration file [{}] needs to be updated'.format(configFileName))

            if keepconf:
                # Copy the old file in the same dir as the old one, with a suffix
                suffixedFilePath = '{}.new'.format(newFilePath)
                shutil.copyfile(newFilePath, suffixedFilePath)
                shutil.copyfile(originalFilePath, newFilePath)
                self.logger.info('Created copy of the original file in [{}]'.format(suffixedFilePath))
            else:
                # Copy the old file in the same dir as the old one, with a suffix
                suffixedFilePath = '{}.orig'.format(newFilePath)
                shutil.copyfile(originalFilePath, suffixedFilePath)
                self.logger.info('Stored the new version of the file in [{}]'.format(suffixedFilePath))

    def upgrade(self, instanceName, newVersion, force, keepconf):
        # Get the instance
        matchingInstances = [i for i in self.configManager.instances() if i['name'] == instanceName]

        # Make sure that:
        # - the instance exists
        # - the version was properly downloaded
        # - the version that we are going to is greater than the current instance version
        if len(matchingInstances) == 1:

            currentVersion = matchingInstances[0]['version']
            if force or version.parse(currentVersion) < version.parse(newVersion):
                # Download the version if it is not already in the local repository
                self.versionManager.ensureVersion(newVersion)

                if self.versionManager.hasVersion(newVersion):
                    if "SNAPSHOT" not in currentVersion and "SNAPSHOT" in newVersion:
                        self.logger.info("Note: when upgrading to a SNAPSHOT version, you might need to uncomment this in xwiki.properties:")
                        self.logger.info("---")
                        self.logger.info("extension.repositories = maven-xwiki-snapshot:maven:https://nexus.xwiki.org/nexus/content/groups/public-snapshots")
                        self.logger.info("---")

                    self.logger.info('Starting to upgrade instance [{}] from version [{}] to version [{}] ...'
                                     .format(instanceName, currentVersion, newVersion))
                    # Actually start the upgrade
                    # Create a random suffixed instance name
                    tempInstanceName = '{}-{}'.format(instanceName, random_chars(4))
                    self.instanceManager.copy(instanceName, tempInstanceName)
                    tempInstancePath = self.instanceManager.getInstancePath(tempInstanceName)

                    # Remove the old instance folder, replace it with a pristine version
                    self.instanceManager.remove(instanceName)
                    self.instanceManager.create(instanceName, newVersion)
                    instancePath = self.instanceManager.getInstancePath(instanceName)

                    # Copy configuration files, if needed, warn the user that there are some conflicts
                    # For now, we do not handle conflict resolution
                    # TODO: Refactor
                    self.__copyAndCompareFiles(
                        '{}/webapps/xwiki/WEB-INF/xwiki.cfg'.format(tempInstancePath),
                        '{}/webapps/xwiki/WEB-INF/xwiki.cfg'.format(instancePath),
                        keepconf)
                    self.__copyAndCompareFiles(
                        '{}/webapps/xwiki/WEB-INF/xwiki.properties'.format(tempInstancePath),
                        '{}/webapps/xwiki/WEB-INF/xwiki.properties'.format(instancePath),
                        keepconf)
                    self.__copyAndCompareFiles(
                        '{}/webapps/xwiki/WEB-INF/hibernate.cfg.xml'.format(tempInstancePath),
                        '{}/webapps/xwiki/WEB-INF/hibernate.cfg.xml'.format(instancePath),
                        keepconf)

                    # Copy the perm dir
                    shutil.rmtree('{}/data'.format(instancePath))
                    shutil.copytree('{}/data'.format(tempInstancePath), '{}/data'.format(instancePath))

                    # Remove the temporary instance
                    self.instanceManager.remove(tempInstanceName)
                else:
                    self.logger.error(
                        'Not upgrading instance [{}] as version [{}] could not be found in local repository'
                        .format(instanceName, newVersion))
            elif "SNAPSHOT" in newVersion:
                self.logger.error(
                    'Not upgrading instance [{}] to snapshot version [{}]. Please use --force to force this upgrade.'
                    .format(instanceName, newVersion))
            else:
                self.logger.error(
                    'Not upgrading instance [{}] as version [{}] is lower than the version currently used ([{}])'
                    .format(instanceName, newVersion, currentVersion))
        else:
            self.logger.error('The instance name [{}] is invalid'.format(instanceName))
