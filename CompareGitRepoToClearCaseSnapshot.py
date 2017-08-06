import filecmp
import os
import shutil
import subprocess
import sys
import tempfile
import webbrowser

#the base of your ClearCase snapshots. You'll be presented with an option of which branch to sync NO ENDING FORWARD SLASH
dirCC = 'C:/ccsnapshot'
#the git repository path WITH ENDING FORWARD SLASH
dirGIT = 'C:/gitrepos/my_repo_dir/'
#filter snapshots you want to list by what their folder name starts with 
snapFilter = 'username_prefix'
#path under snapshot/vob that gets to the matching folders of the GIT repo 
pathInSnapToMatchGitRepo = '/my_project'

#Some elements don't makes sense to compare, add ignored elements to this list down below.
elementsToIgnore = []

class TraverseTree():

    def __init__(self):
        self.pathFromRepo = ''

    def setDirs(self, source, destination):
        self.source = source
        self.destination = destination

    def compareEntry(self, entryToCompare):
        baseEntry = os.path.join(self.pathFromRepo, entryToCompare)

        srcElement = os.path.normpath(os.path.join(self.source, baseEntry))
        dstElement = os.path.normpath(os.path.join(self.destination, baseEntry))

        if not srcElement in elementsToIgnore:
            if os.path.isfile(srcElement):
                #make sure the file exists on both sides.
                if os.path.isfile(dstElement):
                    compResult = filecmp.cmp(srcElement, dstElement)
                    if not compResult:
                        tempReportFile.write('DIFF FOUND: ' + srcElement + '\n')
                else:
                    tempReportFile.write(' NOT FOUND: ' + dstElement + '\n')

            elif os.path.isdir(srcElement):
                dirNameLen = len(entryToCompare)

                self.pathFromRepo = os.path.join(self.pathFromRepo, entryToCompare)

                dirList = os.listdir(srcElement)

                for entry in dirList:
                    entryPath = os.path.join(baseDirSrc , entry)
                    if not entryPath in elementsToIgnore:
                        self.compareEntry(entry)

                self.pathFromRepo = self.pathFromRepo[:-(dirNameLen+1)]

            else:
                message ='Oops! What the heck is this: %s' % srcElement
                tempReportFile.write(message + '\n')

try:
    dirList = os.listdir(dirCC)

    snapsList = []

    for entry in dirList:
        if len(snapFilter) > 0:
            if entry.startswith(snapFilter):
                snapsList.append(entry)
        else:
            snapsList.append(entry)

    for i in range(0, len(snapsList)):
        print "%d - %s \n" % (i+1, snapsList[i])

    selectedSnapIndex = raw_input("What snapshot do you want to compare: ")
    selectedSnapIndex = int(selectedSnapIndex)-1

    dirCC = dirCC + '/' + snapsList[selectedSnapIndex] + pathInSnapToMatchGitRepo

    print 'What direction do you want this comparison to run in?'
    selectedDirection = raw_input("     [1] GIT -> CC       [2] CC -> GIT  : ")

    #make GIT -> CC default
    baseDirSrc = dirGIT
    baseDirDst = dirCC

    if selectedDirection == '2':
        baseDirSrc = dirCC
        baseDirDst = dirGIT

    #add elements to ignore with full path
    elementsToIgnore.append(os.path.normpath(os.path.join(baseDirSrc , '.git')))
    elementsToIgnore.append(os.path.normpath(os.path.join(baseDirSrc , '.gitignore')))
    elementsToIgnore.append(os.path.normpath(os.path.join(baseDirSrc , 'target')))

    print 'Comparing -> '
    print '    ' + baseDirSrc
    print '    ' + baseDirDst

    home = os.path.expanduser("~")
    tempFilePath = os.path.join(home, 'git-cc-compare.txt')
    print 'Generating ' + tempFilePath
    tempReportFile = file(tempFilePath, 'w')

    tempReportFile.write('Comparing: \n')
    tempReportFile.write('    ' + baseDirSrc + '\n')
    tempReportFile.write('    ' + baseDirDst + '\n\n')

    for ignoredFile in elementsToIgnore:
        tempReportFile.write(' IGNORING: ' + ignoredFile + '\n')

    tempReportFile.write('\n')

    #we now have the 2 directories to compare... traverse GIT's folders comparing with CC
    dirList = os.listdir(baseDirSrc)

    traverseTree = TraverseTree()
    traverseTree.setDirs(baseDirSrc, baseDirDst)

    for entry in dirList:
        entryPath = os.path.join(baseDirSrc , entry)
        traverseTree.compareEntry(entry)

    print ''
    print ''
    print 'GIT to ClearCase comparison completed'

    webbrowser.open(tempFilePath)

finally:
    tempReportFile.close()
