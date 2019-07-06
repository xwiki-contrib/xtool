import hashlib
import logging
from packaging import version as Version
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from configuration import ConfigManager

# Handles the download of an XWiki version
class VersionDownloader:
    logger = logging.getLogger('VersionDownloader')

    # version : the version that needs to be downloaded
    # versionManager : the version manager
    # configManager : the configuration manager
    def __init__(self, version, versionManager, configManager, category='releases'):
        self.version = version

        self.configManager = configManager
        self.versionManager = versionManager
        self.versionCategory = category

    # Return the MD5 sum of a file
    def __computeChecksum(self, path):
        with open(path, 'rb') as f:
            digest = hashlib.md5()
            while True:
                data = f.read(8192)
                if not data: # In case we're at the end of the file
                    break
                digest.update(data)
            return digest.hexdigest()

    def _generateFolderLink(self):
        if self.version.endswith('-SNAPSHOT') or Version.parse(self.version) >= self.versionManager.migrationVersion:
            baseURL = 'http://maven.xwiki.org/{}/org/xwiki/platform/xwiki-platform-distribution-flavor-jetty-hsqldb/{}'
        else:
            baseURL = 'http://maven.xwiki.org/{}/org/xwiki/enterprise/xwiki-enterprise-jetty-hsqldb/{}'

        return baseURL.format(self.versionCategory, self.version)

    def _generateRemoteFileName(self, version, extension):
        if self.version.endswith('-SNAPSHOT') or Version.parse(self.version) >= self.versionManager.migrationVersion:
            downloadURL = 'xwiki-platform-distribution-flavor-jetty-hsqldb-{}.{}'
        else:
            downloadURL = 'xwiki-enterprise-jetty-hsqldb-{}.{}'

        return downloadURL.format(version, extension)

    def _generateDownloadLink(self, extension):
        return '{}/{}'.format(self._generateFolderLink(), self._generateRemoteFileName(self.version, extension))

    # Will safely download a file and check its MD5 sum before returning
    def __safeDownloadFile(self, fileURL, md5FileURL, destinationPath):
        try:
            # Test if we don't get a 404 error or something similar
            self.logger.debug('Testing url [{}]'.format(md5FileURL))
            md5Sum = urllib.request.urlopen(md5FileURL).read().decode('utf-8')

            # Actually download the archive
            self.logger.info('Downloading file [{}] ...'.format(fileURL))
            downloadedFile = urllib.request.urlretrieve(fileURL, destinationPath)
            fileMD5Sum = self.__computeChecksum(destinationPath)

            # Verify the control sum of the downloaded file
            self.logger.debug('Checking file integrity ...')
            self.logger.debug('EXPECTED : {}'.format(md5Sum))
            self.logger.debug('ACTUAL   : {}'.format(fileMD5Sum))
            if fileMD5Sum != md5Sum:
                # If it's actually the case, delete the download files and quit
                os.remove(destinationPath)
                raise IOError('The control sum of the downloaded file is invalid. Aborting.')
            return
        except urllib.error.HTTPError as e:
            self.logger.debug('Gotten error {}'.format(e))
            self.logger.error('The URL [{}] is either unaccesible or unavailable'.format(md5FileURL))
            raise e

    def download(self):
        # First, check that we have a version already registered
        self.logger.debug('Downloading version : {}'.format(self.version))
        self.logger.debug('Downloaded versions : {}'.format(self.configManager.versions()))
        if self.version in self.configManager.versions():
            self.logger.info('The version {} is already downloaded, skipping.'.format(self.version))
        else:
            zipDownloadURL = self._generateDownloadLink('zip')
            md5DownloadURL = self._generateDownloadLink('zip.md5')
            archivePath = self.versionManager.getArchivePath(self.version)

            try:
                self.__safeDownloadFile(zipDownloadURL, md5DownloadURL, archivePath)

                # Mark the instance as present in the instance repository
                self.configManager.versions().append(self.version)
                self.configManager.persist()

                self.logger.info('Version {} successfully downloaded!'.format(self.version))
            except urllib.error.HTTPError as e:
                self.logger.warning('Skipping version {}'.format(self.version))

# On the contrary to standard RC or release versions, there can be multiple artifacts for a given snapshot,
# we need to determine the file name of the last snapshot that we will download based on the maven metadata.
class SnapshotVersionDownloader(VersionDownloader):
    logger = logging.getLogger('SnapshotVersionDownloader')

    def __init__(self, version, versionManager, configManager):
        super().__init__(version, versionManager, configManager, category='snapshots')
        self.__getSnapshotVersionValue()

    def __getSnapshotVersionValue(self):
        self.logger.debug('Fetching the maven-metadata.xml file from the SNAPSHOT version ...')
        mavenMetadataURL = '{}/maven-metadata.xml'.format(self._generateFolderLink())

        try:
            mavenMetadata = urllib.request.urlopen(mavenMetadataURL).read().decode('utf-8')
            metadataRoot = ET.fromstring(mavenMetadata)

            self.snapshotVersion = (
                metadataRoot.find('./versioning/snapshotVersions/snapshotVersion[extension=\'zip\']/value').text)
        except urllib.error.HTTPError as e:
            self.logger.error('Failed to fetch maven-metadata.xml file for XWiki [{}]'.format(self.version))
            self.logger.debug('Error : [{}]'.format(e))

    def _generateDownloadLink(self, extension):
        return '{}/{}'.format(self._generateFolderLink(), self._generateRemoteFileName(self.snapshotVersion, extension))
