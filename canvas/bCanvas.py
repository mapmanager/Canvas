# Author: Robert Cudmore
# Date: 20190703

import os, sys, time, json, glob
from datetime import datetime
from collections import OrderedDict
import enum
from pprint import pprint

#import numpy as np
import pandas as pd

import canvas

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

class canvasStackType(enum.Enum):
    scanning = 'scanning'
    video = 'video'

class bCanvas:
    """
    A visuospatial canvas that brings together different light paths of a scope. USually video and laser-scanning confocal or two-photon.
    """
    
    __version__ = 0.1
    
    def __init__(self, filePath=None):
        """
        filePath: path to _canvas.txt file to load a canvas

        todo:
            don't rely on canvas app?
            add logFileObject so we can ask it for motor positions
        """

        self._filePath = None #filePath # todo: not used
        self._folderPath = None

        if filePath is not None:
            self._filePath = filePath
            self._folderPath, tmpFilename = os.path.split(filePath)

        # TODO: this is really interface, e.g. Qt, put it somewhere else?
        self._windowPosition = {}
        #self._options['version'] = self.__version__
        self._windowPosition['left'] = 700  # size of the canvas window
        self._windowPosition['top'] = 200
        self._windowPosition['width'] = 640
        self._windowPosition['height'] = 480
        
        # list of canvas.canvasStack
        # new
        self._fileDictList = {}  # dict of _defaultFileDict()
        # old
        # self._videoFileList = []  # aquired video
        # self._scopeFileList = []  # images off the scope

        '''
        now = datetime.now()
        dateStr = now.strftime('%Y-%m-%d')
        timeStr = now.strftime('%H:%M:%S.%f')
        seconds = now.timestamp()
        '''

        self._creationDate = None
        self._creationTime = None
        self._creationSeconds = None

        if filePath is not None and os.path.isfile(filePath):
            # load existing txt file (json)
            self.load(filePath)
        else:
            # save txt file (json) when creating a new canvas
            now = datetime.now()
            dateStr = now.strftime('%Y-%m-%d')
            timeStr = now.strftime('%H:%M:%S.%f')
            seconds = now.timestamp()

            self._creationDate = dateStr
            self._creationTime = timeStr
            self._creationSeconds = seconds

            self.save()

    def stackListToDf(self):
        """Return a DataFrame of all canvasStack header(s), one stack per row.
        """
        
        #df = pd.DataFrame()
        df = None

        for k,v in self._fileDictList.items():
            stackFileName = k
            canvasStack = v['canvasStack']

            stackHeader = canvasStack.header.header
            stackHeader = dict(stackHeader)

            # print('===', stackFileName)
            # pprint(stackHeader)

            #oneDf = pd.DataFrame.from_dict(stackHeader, orient='index')
            oneDf = pd.DataFrame.from_dict([stackHeader], orient='columns')
            if df is None:
                df = oneDf
            else:
                df = pd.concat([df, oneDf])
        
        return df

    @property
    def numVideoFiles(self):
        count = 0

    def getVersion(self):
        return self.__version__
    
    def setItemVisible(self, filename, isVisible):
        self._fileDictList[filename]['isVisible'] = isVisible

    def setContrast(self, fileNameList, minContrast, maxContrast):
        """Set the contrast for each item in list of filename.
        """
        logger.info(f'minContrast:{minContrast}, maxContrast:{maxContrast}')
        for filename in fileNameList:
            logger.info(f'  setting contrast for {filename}')
            self._fileDictList[filename]['minContrast'] = minContrast
            self._fileDictList[filename]['maxContrast'] = maxContrast


    def getStackDict(self, filename : str) -> dict:
        """Get one stack dict from filename.
        """
        try:
            return self._fileDictList[filename]
        except (KeyError) as e:
            logger.error(f'Did not find {filename} in list of stacks')
            return

    def getFileDictList(self) -> dict:
        return self._fileDictList

    def old_findStackByName(self, filename : str) -> canvas.canvasStack:
        """Find a stack by name.
        
        Return:
            canvas.canvasStack
        """
        return self.findStackByName2(filename)
        
        # video files
        theFile = None
        for file in self._videoFileList:
            if file.getFileName() == filename:
                theFile = file
                break

        # scope files
        if theFile is None:
            for file in self._scopeFileList:
                if file.getFileName() == filename:
                    theFile = file
                    break
        return theFile

    def numFiles(self):
        return len(self._fileDictList.keys())

    def numVideoFiles(self):
        """Get number of video files.
        
        Used to increment filename when acquiring new video.
        """
        count = 0
        for _file, stackDict in self._fileDictList.items():
            if stackDict['stackType'] == canvasStackType.video.value:
                count += 1
        return count

    def newVideoStack(self, imageData, videoHeader : dict):
        """
        Create a new video stack from data and header.
        
        Args:
            imageData: numpy image
            videoHeader: dict with (motor, um widht/height, date/time)

        Return:
            newVideoStack: canvas.canvasStack
            newVideoDict: canvas file dict
        """
        logger.info(f'imageData:{imageData.shape} videoHeader:{videoHeader}')

        # make _video folder if necc
        if not os.path.isdir(self.videoFolderPath):
            os.mkdir(self.videoFolderPath)

        # construct file path/name
        numVideoFiles = self.numVideoFiles()  #len(self.videoFileList)
        fileNumStr = str(numVideoFiles).zfill(3)
        saveVideoFile = 'v' + self.enclosingFolder + '_' + fileNumStr + '.tif'
        saveVideoPath = os.path.join(self.videoFolderPath, saveVideoFile)

        print('2222 SAVING with videoHeader')
        print('  ', imageData.shape)
        pprint(videoHeader)

        # save stack
        canvas.canvasStackUtil.imsave(saveVideoPath, imageData, tifHeader=videoHeader)

        # load as bStack
        newVideoStack = canvas.canvasStack(saveVideoPath, loadImages=True)

        print('2222 LOADED')
        pprint(newVideoStack.header.print())

        # append to list
        newVideoDict = self.appendStack(newVideoStack, canvasStackType.video)

        # save canvas file
        self.save()

        return newVideoStack, newVideoDict

    def _defaultFileDict(self):
        """Each entry in _fileDictList is this dict
        """
        theDict = {
            'canvasStack': None,  # actual canvas.canvasStack object
            'date': None,
            'time': None,
            'seconds': None,
            'xMotor': None,
            'yMotor': None,
            'zMotor': None,
            'umWidth': None,
            'umHeight': None,
            # canvas specific (not in stack header)
            'stackType': '',  # (canvasStackType.scope, canvasStackType.video
            'relPath': None,
            'isVisible': True,
            'minContrast': None,
            'maxContrast': None,
        }
        return theDict

    def appendStack(self, newStack : canvas.canvasStack,
                        stackType: canvasStackType) -> dict:
        """Append a new stack to the canvas.

        Args:
            newStack:
            canvasStackType: in ('scanning', 'video')
        """
        fileName = newStack.getFileName()
        if stackType == canvasStackType.video:
            relPath = 'video'  #os.path.join('video', fileName)
        else:
            relPath = ''  # fileName

        fileDict = self._defaultFileDict()
        fileDict['canvasStack'] = newStack  # canvas.canvasStack object
        fileDict['date'] = newStack.header['date']
        fileDict['time'] = newStack.header['time']
        fileDict['seconds'] = newStack.header['seconds']
        fileDict['xMotor'] = newStack.header['xMotor']
        fileDict['yMotor'] = newStack.header['yMotor']
        fileDict['zMotor'] = newStack.header['zMotor']
        fileDict['umWidth'] = newStack.header['umWidth']
        fileDict['umHeight'] = newStack.header['umHeight']
        #
        fileDict['stackType'] = stackType.value  # in (2p, video)
        fileDict['relPath'] = relPath
        fileDict['isVisible'] = True
        fileDict['minContrast'] = 0
        fileDict['maxContrast'] = 2**newStack.header['bitDepth'] - 1
        
        # TODO: check if it exists
        self._fileDictList[fileName] = fileDict

        # logger.info(f'{fileName} dict is now')
        # pprint(self._fileDictList)

        return fileDict

    def old_appendVideo(self, newVideoStack):
        """
        Append a video stack to the canvas list of video stacks.
        
        Args:
            newVideoStack: canvas.canvasStack
        
        Notes:        
            Used when user acquires a new image from video
            See: canvasWidget.grabImage()
        """
        # old
        self._videoFileList.append(newVideoStack)

    def importNewScopeFiles(self, watchDict : dict = None) -> list:
        """
        import new scope files from canvas folder.
        
        Look through files in our hard-drive folder and look for new files.
        A new file is one that is not already in self.scopeFileList

        watchDict: dictionary mapping file name to x/y/z motor position
                    passed when we are on Olympus

        Return list of files/folders we imported
        """
        #newStackList = [] # build a list of new files
        newStackDictList = []

        listDir = os.listdir(self._folderPath)
        theseFileExtensions = ['.tif', '.tiff', '.oir']

        logger.info('')
        logger.info(f'  Looking for "{theseFileExtensions}" files in folder:{self._folderPath}')

        for potentialNewFile in listDir:
            tmpFile, fileExt = os.path.splitext(potentialNewFile)

            # adding option to load from folder of .tif
            folderPath = ''
            potentialFolder = os.path.join(self._folderPath, tmpFile)
            if os.path.isdir(potentialFolder):
                # todo: make this more precise like <canvas>_video
                videoFolderPath = self.videoFolderPath # todo: stop using properties !!!
                tmpVideoFolderPath, videoFolderName = os.path.split(videoFolderPath)

                if tmpFile == videoFolderName:
                    # don't load _video folder
                    continue
                if tmpFile == 'max':
                    # don't load max folder
                    continue

                # load from folder of tif
                fileList = glob.glob(potentialFolder + '/*.tif')
                fileList = sorted(fileList)
                if len(fileList) == 0:
                    logger.info('  did not find any "{theseFileExtensions}" files in folder:{potentialFolder}')
                    continue
                #folderPath = potentialFolder
                #potentialNewFile = fileList[0]
                logger.info('  loading potentialNewFile:{potentialNewFile}')
            # was this
            elif not fileExt in theseFileExtensions:
                continue
            #if not potentialNewFile.endswith(thisFileExtension):
            #    continue
            logger.info(f'  considering file:{potentialNewFile}')
            # check if file is in self.scopeFileList
            
            # old
            # isInList = False
            # for loadedScopeFile in self.scopeFileList:
            #     if loadedScopeFile.getFileName() == potentialNewFile:
            #         logger.info('  already in self.scopeFileList, potentialNewFile:{potentialNewFile}')
            #         isInList = True
            #         break
            
            # new
            isInList = potentialNewFile in self._fileDictList.keys()

            if not isInList:
                # found a file that is not in scopeFileList
                # we need to find it in bLogFilePosition
                #print('   New file:', potentialNewFile, 'find it in bLogFilePosition')
                newFilePath = os.path.join(self._folderPath, potentialNewFile)

                # load stack with images and save max
                newScopeStack = canvas.canvasStack(newFilePath, loadImages=True)
                newScopeStack.saveMax()

                # append to header
                # todo: on windows use os.path.getctime(path_to_file)
                # see: https://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
                cTime = os.path.getctime(newFilePath)
                dateStr = time.strftime('%Y%m%d', time.localtime(cTime))
                timeStr = time.strftime('%H:%M:%S', time.localtime(cTime))
                newScopeStack.header['date'] = dateStr #time.strftime('%Y%m%d')
                newScopeStack.header['time'] = timeStr #datetime.now().strftime("%H:%M:%S.%f")[:-4]
                newScopeStack.header['seconds'] = cTime #time.time()

                # get motor position from watchDict
                #     updated from thread each time a new file appears
                #     used on systems (like Olympus that do not save motor position into image file)
                if watchDict is not None:
                    # zPos is ignored on olympus (it is controlled by olympus software)
                    xPos, yPos, zPos = self.getFilePositon(watchDict, potentialNewFile)
                    if xPos is not None and yPos is not None:
                        logger.info(f'  Got from watch dict xPos:{xPos} yPos:{yPos}')
                        newScopeStack.header['xMotor'] = xPos
                        newScopeStack.header['yMotor'] = yPos
                    else:
                        logger.error(f'  Did not find file in watchDict:{potentialNewFile}')
                        newScopeStack.header['xMotor'] = None
                        newScopeStack.header['yMotor'] = None

                # append to return list of new stacks
                #newStackList.append(newScopeStack)

                # old
                #self._scopeFileList.append(newScopeStack)
                # new
                oneStackDict = self.appendStack(newScopeStack, canvasStackType.scanning)
        
                newStackDictList.append(oneStackDict)

        logger.info(f'  found {len(newStackDictList)} new scope (scanning) files')

        # TODO: save here, do not save from canvasWidget (interface)
        if len(newStackDictList) > 0:
            self.save()

        return newStackDictList

    # this parallels bLogFilePosition() but just uses a dictionary
    def getFilePositon(self, logDict, fileName):
        if fileName in logDict.keys():
            logger.info(f'{fileName} from dict {logDict[fileName]}')
            xPos = logDict[fileName]['xPos']
            yPos = logDict[fileName]['yPos']
            zPos = logDict[fileName]['zPos']
            return xPos, yPos, zPos
        else:
            return None, None, None

    @property
    def old_videoFileList(self):
        return self._videoFileList

    @property
    def old_scopeFileList(self):
        return self._scopeFileList

    @property
    def enclosingFolder(self):
        """ Name of the enclosing folder"""
        if self._folderPath is None:
            #print('error: @property enclosingFolder got None self._folderPath')
            return None
        else:
            return os.path.basename(os.path.normpath(self._folderPath))

    @property
    def videoFolderPath(self):
        if self._folderPath is None:
            #print('error: @property videoFolderPath got None self._folderPath')
            return None
        else:
            #return os.path.join(self._folderPath, self.enclosingFolder + '_video')
            return os.path.join(self._folderPath, 'video')

    def getWindowPosition(self):
        return self._windowPosition

    def setWindowPosition(self, key, value):
        try:
            self._windowPosition[key] = value
        except (KeyError) as e:
            logger.error(f'Filed to set window option key:{key} to value:{value}')

    def old_getOption(self, name):
        return self._options[name]
    
    def old_setOption(self, key, value):
        self._options[key] = value

    def _saveFileDict(self, stack : canvas.canvasStack) -> dict:
        """
        Generate a dict to save both (video/scope) files to json

        stack: pointer to stack
        """
        header = stack.header
        fileDict = OrderedDict()
        # todo: make sure path get filled in in header !!!
        fileName = stack.fileName
        fileDict['filename'] = fileName

        #fileDict['folderPath'] = stack.folderPath # to open stack from folder of .tif

        fileDict['date'] = header['date']
        fileDict['time'] = header['time']
        fileDict['seconds'] = header['seconds']

        fileDict['stackType'] = header.stackType
        fileDict['bitDepth'] = header.bitDepth  # TODO: not neccessary
        fileDict['pixelsPerLine'] = header.pixelsPerLine
        fileDict['linesPerFrame'] = header.linesPerFrame
        fileDict['numImages'] = header.numImages
        fileDict['umWidth'] = header.umWidth
        fileDict['umHeight'] = header.umHeight
        fileDict['xMotor'] = header.xMotor
        fileDict['yMotor'] = header.yMotor

        # canvas specific
        # is it visible in the canvas? Checkbox next to filname in canvas.
        fileDict['canvasFileType'] = ''  # (scope, video)
        fileDict['canvasIsVisible'] = True
        # contrast setting in canvas
        fileDict['canvasMinContrast'] = 0
        fileDict['canvasMaxContrast'] = 2**header.bitDepth

        return fileDict

    
    def saveAsCsv(self):
        if self.numFiles() > 0:
            saveFilePath = os.path.join(self._folderPath, self.enclosingFolder + '_canvas.csv')
            logger.info(f'Saving stack headers to {saveFilePath}')
            df = self.stackListToDf()
            df.to_csv(saveFilePath)

    def save(self):
        saveFilePath = os.path.join(self._folderPath, self.enclosingFolder + '_canvas.json')

        logger.info(f'Saving {self.numFiles()} files to {saveFilePath}')

        saveDict = OrderedDict() # the dictionary we will save

        # make a canvas options header
        saveDict['canvasVersion'] = self.getVersion()

        saveDict['creationDate'] = self._creationDate
        saveDict['creationTime'] = self._creationTime
        saveDict['creationSeconds'] = self._creationSeconds
        
        saveDict['windowPosition'] = self._windowPosition

        saveDict['files'] = OrderedDict()
        
        for filename, fileDict in self._fileDictList.items():
            saveDict['files'][filename] = OrderedDict()
            # print('tttttt saving file dict')
            # pprint(fileDict)
            for k,v in fileDict.items():
                if k == 'canvasStack':
                    # don't save the canvasStack object (in memory)
                    continue
                else:
                    saveDict['files'][filename][k] = v

        with open(saveFilePath, 'w') as outfile:
            json.dump(saveDict, outfile, indent=4)

        #
        self.saveAsCsv()

    def load(self, thisFile):
        """Load canvas from json file.
        """
        logger.info(f'{thisFile}')
        
        currentVersion = self.getVersion()

        self._filePath = thisFile
        self._folderPath, tmpFilename = os.path.split(self._filePath)
        with open(self._filePath) as f:
            data = json.load(f)

        for key, item in data.items():
            #print(key,item)
            if key == 'canvasVersion':
                loadedVersion = item
                if loadedVersion < currentVersion:
                    logger.warning(f'\nloaded version {loadedVersion} is older than current version {currentVersion}')

            elif key == 'creationDate':
                self._creationDate = item
            elif key == 'creationTime':
                self._creationTime = item
            elif key == 'creationSeconds':
                self._creationSeconds = item

            elif key == 'windowPosition':
                #logger.info(f'  windowPosition key:{key} item:{item}')
                self._options = item

            elif key=='files':
                for fileName, fileDict in item.items():
                    # fileDict is what we store in _defaultFileDict
                    _canvasStackType = fileDict['stackType']  # (2p, video)
                    relPath = fileDict['relPath']  # (2p, video)
    
                    stackFilePath = os.path.join(self._folderPath, relPath, fileName)
                    logger.info(f'  stackFilePath:{stackFilePath}')
                    
                    # load from disk
                    if _canvasStackType == canvasStackType.video.value:
                        loadImages = True
                        loadMax = False
                    elif _canvasStackType == canvasStackType.scanning.value:
                        loadImages = False
                        loadMax = True
                    else:
                        logger.error(f'did not understand canvasStackType:{_canvasStackType}')
                        loadImages = False
                        loadMax = False

                    # load the stack    
                    oneStack = canvas.canvasStack(stackFilePath, loadImages=loadImages)
                    if loadMax:
                        oneStack.loadMax()

                    # filedict should parallel _defaultFileDict
                    fileDict['canvasStack'] = oneStack

                    # could use ???
                    #self.appendStack(oneStack, canvasStackType)
                    self._fileDictList[fileName] = fileDict

def old_main():
    try:
        from bJavaBridge import bJavaBridge
        myJavaBridge = bJavaBridge()
        myJavaBridge.start()

        folderPath = '/Users/cudmore/box/data/nathan/canvas/20190429_tst2'
        bc = bCanvas(folderPath=folderPath)
        #print(bc._optionsDict)

        bc.old_buildFromScratch()

        for videoFile in bc.videoFileList:
            print(videoFile._header)

        bc.save()

        '''
        tmpPath = '/Users/cudmore/Dropbox/data/20190429/20190429_tst2/20190429_tst2_0012.oir'
        from bStackHeader import bStackHeader
        tmpHeader = bStackHeader(tmpPath)
        tmpHeader.prettyPrint()
        '''

    finally:
        myJavaBridge.stop()

def test_canvas():
    path = '/Users/cudmore/data/canvas/20220823_a100/20220823_a100_canvas.json'
    c = bCanvas(path)

    df = c.stackListToDf()
    print('stackListToDf returned')
    print(df)

    '''
    newStackDictList = c.importNewScopeFiles()
    for newStack in newStackDictList:
        pprint(newStack)
    '''

if __name__ == '__main__':
    test_canvas()