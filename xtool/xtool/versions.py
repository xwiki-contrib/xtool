import logging
from packaging import version as Version

from environment import Environment

from downloaders import VersionDownloader
from downloaders import SnapshotVersionDownloader


class VersionManager:
    logger = logging.getLogger('VersionManager')
    # version from which we started to use platform instead of enterprise
    migrationVersion = Version.parse("9.5")

    def __init__(self, configManager):
        self.configManager = configManager

    def list(self):
        rowFormat = '{}'
        print(rowFormat.format('Version'))
        for version in self.configManager.versions():
            print(rowFormat.format(version))

    def getArchiveBaseName(self, version):
        if version.endswith('-SNAPSHOT') or Version.parse(version) >= self.migrationVersion:
            return 'xwiki-platform-distribution-flavor-jetty-hsqldb-{}'.format(version)
        else:
            return 'xwiki-enterprise-jetty-hsqldb-{}'.format(version)

    # Generate the file name used for a given version
    def getArchiveName(self, version):
        return '{}.zip'.format(self.getArchiveBaseName(version))

    # Generate the file path used for a given version
    def getArchivePath(self, version):
        return '{}/{}'.format(Environment.dataDir, self.getArchiveName(version))

    def ensureVersion(self, version):
        if not self.hasVersion(version):
            self.logger.info('Version {} not in the local repository ; downloading it ...'.format(version))
            self.download(version)

    def hasVersion(self, version):
        return version in self.configManager.versions()

    def download(self, version):
        # First, check that we have a version already registered
        self.logger.debug('Downloading version : {}'.format(version))
        self.logger.debug('Downloaded versions : {}'.format(self.configManager.versions()))
        if version in self.configManager.versions():
            self.logger.info('The version {} is already downloaded, skipping.'.format(self.version))
        else:
            if (version.endswith('-SNAPSHOT')):
                downloadSuccessful = SnapshotVersionDownloader(version, self).download()
            else:
                # Use the standard version downloader
                downloadSuccessful = VersionDownloader(version, self).download()

            if downloadSuccessful:
                # Mark the instance as present in the instance repository
                self.configManager.versions().append(self.version)
                self.configManager.persist()
                self.logger.info('Version {} successfully downloaded!'.format(self.version))
