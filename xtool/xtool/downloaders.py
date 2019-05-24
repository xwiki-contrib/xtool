import hashlib
import logging
from packaging import version as Version
import urllib.error
import urllib.request

from .configuration import ConfigManager

# Handles the download of an XWiki version
class VersionDownloader:
    logger = logging.getLogger('VersionDownloader')

    def __init__(self, versionManager, configManager):
        self.configManager = configManager
        self.versionManager = versionManager

    # Return the MD5 sum of the downloaded archive
    def __computeArchiveChecksum(self, archivePath):
        with open(archivePath, 'rb') as archive:
            digest = hashlib.md5()
            while True:
                data = archive.read(8192)
                if not data: # In case we're at the end of the file
                    break
                digest.update(data)
            return digest.hexdigest()

    def __generateDownloadLink(self, version, extension):
        if (Version.parse(version) >= self.versionManager.migrationVersion):
            baseURL = ('http://maven.xwiki.org/{}/org/xwiki/platform/xwiki-platform-distribution-flavor-jetty-hsqldb/'
            '{}/xwiki-platform-distribution-flavor-jetty-hsqldb-{}.{}')
        else:
            baseURL = ('http://maven.xwiki.org/{}/org/xwiki/enterprise/xwiki-enterprise-jetty-hsqldb/{}/'
            'xwiki-enterprise-jetty-hsqldb-{}.{}')
        # Make a distinction between SNAPSHOTS and releases
        category = 'snapshots' if version.endswith('-SNAPSHOT') else 'releases'

        return baseURL.format(category, version, version, extension)

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
                archivePath = self.versionManager.getArchivePath(version)
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

class SnapshotVersionDownloader(VersionDownloader):
    pass
