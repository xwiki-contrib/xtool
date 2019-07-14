import datetime
import binascii
import filecmp
import logging
import os
import shutil
import tempfile
import zipfile

from configuration import Environment


class SnapshotManager:
    logger = logging.getLogger('Snapshotmanager')

    def __init__(self, configManager, versionManager, instanceManager):
        self.configManager = configManager
        self.versionManager = versionManager
        self.instanceManager = instanceManager

    def list(self):
        pass

    def __makeDirDiff(self, dirDiff, removedElements, relativePath, snapshotPath):
        self.logger.debug('Current diff dirs : [{}] - [{}]'.format(dirDiff.left, dirDiff.right))

        # Handle dirs and files that have been removed from the reference version
        for removedElement in dirDiff.left_only:
            removedElements.append(os.path.join(relativePath, removedElement))

        # Copy in the snapshot the elements that are new or modified in the instance compared to the reference version
        dissimilarElements = dirDiff.right_only + dirDiff.funny_files + dirDiff.diff_files
        self.logger.debug('Dissimilar elements : [{}]'.format(dissimilarElements))
        for element in dissimilarElements:
            self.logger.debug('Considering element [{}]'.format(element))
            elementPath = os.path.join(dirDiff.right, element)
            isDir = os.path.isdir(elementPath)

            if not os.path.exists(snapshotPath):
                os.makedirs(snapshotPath)

            if isDir:
                # In that case, it is a directory that is not present in the reference version
                shutil.copytree(elementPath, os.path.join(snapshotPath, element))
            else:
                shutil.copy(elementPath, snapshotPath)

        # In any case, continue the copy in the subdirs
        for dir in dirDiff.subdirs.keys():
            self.__makeDirDiff(dirDiff.subdirs[dir],
                               removedElements,
                               os.path.join(relativePath, dir),
                               os.path.join(snapshotPath, dir))

    def create(self, instanceName):
        matchingInstances = [i for i in self.configManager.instances() if i['name'] == instanceName]
        if len(matchingInstances) == 1:
            instanceConfig = matchingInstances[0]
            self.versionManager.ensureVersion(instanceConfig['version'])

            with tempfile.TemporaryDirectory(prefix='xtool-') as workdir:
                self.logger.debug('Working in [{}]'.format(workdir))
                # 1. Uncompress a reference version
                referenceVersionPath = os.path.join(workdir,
                                                    self.versionManager.getArchiveBaseName(instanceConfig['version']))
                self.logger.debug('Unzipping reference version in [{}]'.format(referenceVersionPath))
                referenceZip = zipfile.ZipFile(self.versionManager.getArchivePath(instanceConfig['version']), 'r')
                referenceZip.extractall(workdir)
                referenceZip.close()

                snapshotDir = os.path.join(workdir, instanceName)
                os.makedirs(snapshotDir)

                # 2. Do the diff, put all the diffs in a dir
                diff = filecmp.dircmp(referenceVersionPath, self.instanceManager.getInstancePath(instanceName))
                removedElements = []
                self.__makeDirDiff(diff, removedElements, '.', snapshotDir)
                self.logger.debug('Removed elements : [{}]'.format(removedElements))

                # 3. Archive the dir
                snapshotName = '{}-{}'.format(instanceName, binascii.b2a_hex(os.urandom(4)).decode('UTF-8'))
                snapshotFormat = self.configManager.get('snapshot-format') or 'zip'
                snapshotPath = os.path.join(Environment.snapshotsDir, snapshotName)
                self.logger.info('Creating snapshot in [{}]'.format(snapshotPath))
                shutil.make_archive(snapshotPath, snapshotFormat, root_dir=snapshotDir)

                # 4. Save the snapshot information
                self.configManager.snapshots().append({
                    'name': snapshotName,
                    'format': snapshotFormat,
                    'date': datetime.datetime.now().__str__(),
                    'instance-name': instanceName,
                    'version': instanceConfig['version'],
                    'removed-elements': removedElements
                })
                self.configManager.persist()

        else:
            self.logger.error('The instance name [{}] is invalid'.format(instanceName))


    def restore(self, snapshotName):
        pass
