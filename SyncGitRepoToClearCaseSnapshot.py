import os
import sys
import subprocess
import shutil

#the base of your ClearCase snapshots. You'll be presented with an option of which branch to sync NO ENDING FORWARD SLASH
dirCC = 'C:/ccsnapshot'
#the git repository path WITH ENDING FORWARD SLASH
dirGIT = 'C:/gitrepos/my_repo_dir/'
#filter snapshots you want to list by what their folder name starts with 
snapFilter = 'username_prefix'
#path under snapshot/vob that gets to the matching folders of the GIT repo 
pathInSnapToMatchGitRepo = '/my_project'

def mkdirTree(dest):
    try:
        elementToAddDir = os.path.dirname(dest)
        print elementToAddDir
        if not os.path.exists(elementToAddDir):
            mkdirTree(elementToAddDir)
            os.makedirs(elementToAddDir)
            command = 'cleartool mkelem -c \"Add element from GIT-Sync\" ' + elementToAddDir
            print command
            outputResult = subprocess.check_output(command)
        else:
            command = 'cleartool describe -short ' + elementToAddDir
            outputResult = subprocess.check_output(command)
            checkedOut = outputResult[-12:]
            if not checkedOut.startswith('CHECKEDOUT'):
                command = 'cleartool checkout -c \"Add element from GIT-Sync\" ' + elementToAddDir
                print command
                outputResult = subprocess.check_output(command)            
            
    # eg. src and dest are the same file
    except shutil.Error as e:
        print('Error: %s' % e)
    # eg. source or destination doesn't exist
    except IOError as e:
        print('Error: %s - %s' % (e.strerror, src))

def copyFile(src, dest):
    try:
        elementToAddDir = os.path.dirname(dest)
        if not os.path.exists(elementToAddDir):
            os.makedirs(elementToAddDir)
        shutil.copy(src, dest)
    # eg. src and dest are the same file
    except shutil.Error as e:
        print('Error: %s' % e)
    # eg. source or destination doesn't exist
    except IOError as e:
        print('Error: %s - %s' % (e.strerror, src))

dirList = os.listdir(dirCC);

snapsList = []

for entry in dirList:
    if len(snapFilter) > 0:
        if entry.startswith(snapFilter):
            snapsList.append(entry)
    else:
        snapsList.append(entry)        

for i in range(0, len(snapsList)):
    print "%d - %s \n" % (i+1, snapsList[i])

selectedSnapIndex = raw_input("What snapshot do you want to sync: ")
selectedSnapIndex = int(selectedSnapIndex)-1

dirCC = dirCC + '/' + snapsList[selectedSnapIndex] + pathInSnapToMatchGitRepo

print 'Sync -> '
print '    ' + dirGIT
print '    ' + dirCC

#we now have the 2 directories to sync... ask GIT what has changed and apply changes.
fromTag = raw_input("Enter Commit or TAG to compare (Can be a TAG, Commit, range see git diff --help for options): ")

diffResult = subprocess.check_output('git diff --name-status ' + fromTag)

#Some elements don't makes sense to sync, add ignored elements to this list.
elementsToIgnore = []
elementsToIgnore.append('.gitignore')
elementsToIgnore.append('.idea/worspace.xml')

for line in diffResult.split('\n'):
    if len(line) > 0:
        lineSplit = line.split('\t')
        action = lineSplit[0]
        element = lineSplit[1]
        if not element in elementsToIgnore:
            srcElement = dirGIT + element
            dstElement = dirCC + '/' + element
            if action == 'A':
                mkdirTree(dstElement)
                shutil.copy(srcElement, dstElement)
                command = 'cleartool mkelem -c \"Add element from GIT-Sync\" ' + dstElement
                print command
                outputResult = subprocess.check_output(command)

            elif action == 'M':
                command = 'cleartool checkout -unreserved -c \"GIT-Sync [' + fromTag + ']\" ' + dstElement
                print command
                outputResult = subprocess.check_output(command)
                copyFile(srcElement, dstElement)                

            elif action == 'D':
                if os.path.exists(dstElement):
                    elementToAddDir = os.path.dirname(dstElement)
                    command = 'cleartool describe -short ' + elementToAddDir
                    outputResult = subprocess.check_output(command)
                    checkedOut = outputResult[-12:]
                    if not checkedOut.startswith('CHECKEDOUT'):
                        command = 'cleartool checkout -c \"Remove element from GIT-Sync\" ' + elementToAddDir
                        print command
                        outputResult = subprocess.check_output(command)            
                    command = 'cleartool rmname -c \"Remove element from GIT-Sync\" ' + dstElement
                    print command
                    outputResult = subprocess.check_output(command)

            else:
                print 'UNKNOW ACTION ENCOUNTERED %s %s' % (action, element)
print ''
print ''
print 'GIT to ClearCase sync completed'
print ''
print 'Check your ClearCase branch and complete check-ins if all looks good.'
