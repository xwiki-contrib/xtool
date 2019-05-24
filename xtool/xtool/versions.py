import hashlib
import logging
from packaging import version as Version
from pathlib import Path
import urllib.error
import urllib.request

from .configuration import ConfigManager
from .configuration import Environment

class VersionManager:
    logger = logging.getLogger('VersionManager')

    def __init__(self, configManager):
        self.configManager = configManager
        # version from which we started to use platform
        self.migrationVersion = Version.parse("9.5")

    def __generateDownloadLink(self, version, extension):
        if (Version.parse(version) >= self.migrationVersion):
            baseURL = ('http://maven.xwiki.org/{}/org/xwiki/platform/xwiki-platform-distribution-flavor-jetty-hsqldb/'
            '{}/xwiki-platform-distribution-flavor-jetty-hsqldb-{}.{}')
        else:
            baseURL = ('http://maven.xwiki.org/{}/org/xwiki/enterprise/xwiki-enterprise-jetty-hsqldb/{}/'
            'xwiki-enterprise-jetty-hsqldb-{}.{}')
        # Make a distinction between SNAPSHOTS and releases
        category = 'snapshots' if version.endswith('-SNAPSHOT') else 'releases'

        return baseURL.format(category, version, version, extension)

    # Return the MD5 sum of the given archive
    def __computeArchiveChecksum(self, archivePath):
        with open(archivePath, 'rb') as archive:
            digest = hashlib.md5()
            while True:
                data = archive.read(8192)
                if not data: # In case we're at the end of the file
                    break
                digest.update(data)
            return digest.hexdigest()

    def getArchiveBaseName(self, version):
        if (Version.parse(version) >= self.migrationVersion):
            return 'xwiki-platform-distribution-flavor-jetty-hsqldb-{}'.format(version)
        else:
            return 'xwiki-enterprise-jetty-hsqldb-{}'.format(version)

    # Generate the file name used for a given version
    def getArchiveName(self, version):
        return '{}.zip'.format(self.getArchiveBaseName(version))

    # Generate the file path used for a given version
    def getArchivePath(self, version):
        return '{}/{}'.format(Environment.dataDir, self.getArchiveName(version))

    # Download the given version
    def download(self, version):
        # First, check that we have a version already registered
        self.logger.debug('Downloading version : {}'.format(version))
        self.logger.debug('Downloaded versions : {}'.format(self.configManager.versions()))
        if version in self.configManager.versions():
            self.logger.info('The version {} is already downloaded, skipping.'.format(version))
        else:
            zipDownloadURL = self.__generateDownloadLink(version, 'zip')
            md5DownloadURL = self.__generateDownloadLink(version, 'zip.md5')

            try:
                # Test if we don't get a 404 error or something similar
                self.logger.debug('Testing url [{}]'.format(md5DownloadURL))
                md5Sum = urllib.request.urlopen(md5DownloadURL).read().decode('utf-8')

                # Actually download the archive
                self.logger.info('Downloading XWiki {} archive ...'.format(version))
                archivePath = self.getArchivePath(version)
                archive = urllib.request.urlretrieve(zipDownloadURL, archivePath)
                archiveMD5Sum = self.__computeArchiveChecksum(archivePath)

                # Verify the control sum of the downloaded file
                self.logger.debug('Checking archive integrity ...')
                self.logger.debug('EXPECTED : {}'.format(md5Sum))
                self.logger.debug('ACTUAL   : {}'.format(archiveMD5Sum))
                if archiveMD5Sum != md5Sum:
                    # If it's actually the case, delete the download files and quit
                    os.remove(archivePath)
                    raise IOError('The control sum of the downloaded file is invalid. Aborting.')

                # Mark the instance as present in the instance repository
                self.configManager.versions().append(version)
                self.configManager.persist()

                self.logger.info('Version {} successfully downloaded!'.format(version))
            except urllib.error.HTTPError as e:
                self.logger.debug('Gotten error {}'.format(e))
                self.logger.error('The url [{}] is either unaccessible or unavailable'.format(md5DownloadURL))
                self.logger.warning('Skipping version {}'.format(version))
