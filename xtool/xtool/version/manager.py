import logging
import os
from packaging import version as Version
import shutil
import zipfile

from environment import Environment

from version.downloaders import VersionDownloader
from version.downloaders import SnapshotVersionDownloader


class VersionManager:
    logger = logging.getLogger('VersionManager')
    # version from which we started to use platform instead of enterprise
    migrationVersion = Version.parse("9.5")

    def __init__(self, configManager):
        self.configManager = configManager
        self.migrateVersions()

    def list(self):
        rowFormat = '{}'
        print(rowFormat.format('Version'))
        for version in self.configManager.versions():
            print(rowFormat.format(version))

    def getVersionBaseName(self, version):
        if version.endswith('-SNAPSHOT') or Version.parse(version) >= self.migrationVersion:
            return 'xwiki-platform-distribution-flavor-jetty-hsqldb-{}'.format(version)
        else:
            return 'xwiki-enterprise-jetty-hsqldb-{}'.format(version)

    # Generate the file name used for a given version
    def getArchiveName(self, version):
        return '{}.zip'.format(self.getVersionBaseName(version))

    # Generate the file path used for a given version
    def getArchivePath(self, version):
        return os.path.abspath('{}/{}'.format(Environment.dataDir, self.getArchiveName(version)))

    def getDirectoryPath(self, version):
        return os.path.abspath('{}/{}'.format(Environment.dataDir, self.getVersionBaseName(version)))

    def ensureVersion(self, version):
        if not self.hasVersion(version):
            self.logger.info('Version {} not in the local repository ; downloading it ...'.format(version))
            self.download(version)

    def removeVersionArchive(self, version):
        if os.path.exists(self.getArchivePath(version)):
            os.remove(self.getArchivePath(version))

    def removeVersionDirectory(self, version):
        if os.path.exists(self.getDirectoryPath(version)):
            shutil.rmtree(self.getDirectoryPath(version))

    def removeVersion(self, version):
        self.removeVersionArchive(version)
        self.removeVersionDirectory(version)
        self.configManager.versions().remove(version)
        self.configManager.persist()

    def extractVersion(self, version):
        self.logger.debug('Unzipping version {} in {}'.format(version, Environment.dataDir))
        zipRef = zipfile.ZipFile(self.getArchivePath(version), 'r')
        zipRef.extractall(Environment.dataDir)
        zipRef.close()

        versionPath = self.getDirectoryPath(version)

        # Mark the execution scripts executable
        os.chmod('{}/start_xwiki.sh'.format(versionPath), 0o755)
        os.chmod('{}/start_xwiki_debug.sh'.format(versionPath), 0o755)
        os.chmod('{}/stop_xwiki.sh'.format(versionPath), 0o755)

    def migrateVersions(self):
        # Check if the versions are stored as zip files, if so, unzip them and remove the zip
        for version in self.configManager.versions():
            if os.path.exists(self.getArchivePath(version)):
                if not os.path.exists(self.getDirectoryPath(version)):
                    self.extractVersion(version)
                self.removeVersionArchive(version)

    def hasVersion(self, version):
        return version in self.configManager.versions()

    def download(self, version):
        # First, check that we have a version already registered
        self.logger.debug('Downloading version : {}'.format(version))
        self.logger.debug('Downloaded versions : {}'.format(self.configManager.versions()))
        if version in self.configManager.versions():
            self.logger.info('The version {} is already downloaded, skipping.'.format(version))
        else:
            if (version.endswith('-SNAPSHOT')):
                downloadSuccessful = SnapshotVersionDownloader(version, self).download()
            else:
                # Use the standard version downloader
                downloadSuccessful = VersionDownloader(version, self).download()

            if downloadSuccessful:
                # Unzip the version
                self.extractVersion(version)
                self.removeVersionArchive(version)

                # Mark the instance as present in the instance repository
                self.configManager.versions().append(version)
                self.configManager.persist()
                self.logger.info('Version {} successfully downloaded!'.format(version))

    def prune(self):
        unusedVersions = self.configManager.versions()[:]

        for instance in self.configManager.instances():
            self.logger.debug('Checking instance [{}]'.format(instance['name']))
            if instance['version'] in unusedVersions:
                unusedVersions.remove(instance['version'])

        for unusedVersion in unusedVersions:
            self.logger.info('Removing unused version [{}]'.format(unusedVersion))
            self.removeVersion(unusedVersion)
