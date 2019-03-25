import logging
import os
import xml.etree.ElementTree

class ExecEnvironment:
    logger = logging.getLogger('ExecEnvironment')

    def __init__(self):
        self.environmentVersion = None
        self.environmentInstanceName = None

        # From the current directory in which the tool is called, try to fetch a POM that describes the
        # XWiki instance needed
        # In order to do so, we need to fetch the top level POM file of the project we're in.
        # Note that this rule is not perfect, however, that's how it's done usually
        # in XWiki projects
        currentPath = os.getcwd();
        previousPath = currentPath;
        pomFound = False
        noMorePomAvailable = False

        while (not noMorePomAvailable and os.path.dirname(currentPath) != currentPath):
            self.logger.debug('Searching for POM in path : [{}]'.format(currentPath))
            if os.path.isfile(os.path.join(currentPath, 'pom.xml')):
                pomFound = True
            elif pomFound:
                # If we have already found a POM previously, it would mean that we
                # have opt out of the project directory
                noMorePomAvailable = True

            if not noMorePomAvailable:
                previousPath = currentPath
                currentPath = os.path.realpath(os.path.join(currentPath, '..'))

        if pomFound:
            self.logger.debug('Found POM file in [{}]'.format(previousPath))
            self.projectPom = os.path.join(previousPath, 'pom.xml')
            self.__parseProjectPom()

    def getInferredVersion(self):
        return self.environmentVersion

    def getInferredInstanceName(self):
        return self.environmentInstanceName

    def __parseProjectPom(self):
        tree = xml.etree.ElementTree.parse(self.projectPom)
        root = tree.getroot()
        self.environmentVersion = tree.find("./{http://maven.apache.org/POM/4.0.0}parent"
                                       "/{http://maven.apache.org/POM/4.0.0}version").text
        self.environmentVersion = self.environmentVersion.split('-')[0]
        self.logger.debug('Inferred version : [{}]'.format(self.environmentVersion))

        self.environmentInstanceName = tree.find("./{http://maven.apache.org/POM/4.0.0}artifactId").text
        self.logger.debug('Inferred instance name : [{}]'.format(self.environmentInstanceName))
