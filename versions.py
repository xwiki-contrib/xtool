import logging
import urllib.error
import urllib.request

from configuration import ConfigManager
from configuration import Environment

class VersionManager:
    logger = logging.getLogger('VersionManager')

    def __init__(self, configManager):
        self.configManager = configManager

    def __generateDownloadLink(self, version, extension):
        baseURL = ('http://maven.xwiki.org/{}/org/xwiki/platform/xwiki-platform-distribution-flavor-jetty-hsqldb/'
        '{}/xwiki-platform-distribution-flavor-jetty-hsqldb-{}.{}')
        # Make a distinction between SNAPSHOTS and releases
        category = 'snapshots' if version.endswith('-SNAPSHOT') else 'releases'

        return baseURL.format(category, version, version, extension)

    def getArchiveBaseName(self, version):
        return 'xwiki-platform-distribution-flavor-jetty-hsqldb-{}'.format(version)

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
                urllib.request.urlopen(md5DownloadURL)

                # Actually download the archive
                self.logger.info('Downloading XWiki {} archive ...'.format(version))
                archive = urllib.request.urlretrieve(zipDownloadURL, self.getArchivePath(version))

                # Mark the instance as present in the instance repository
                self.configManager.versions().append(version)
                self.configManager.persist()

                self.logger.info('Version {} successfully downloaded!'.format(version))
            except urllib.error.HTTPError as e:
                self.logger.debug('Gotten error {}'.format(e))
                self.logger.error('The url [{}] is either unaccessible or unavailable'.format(md5DownloadURL))
                self.logger.warning('Skipping version {}'.format(version))
