
import os, sys
import json
from collections import OrderedDict

import canvas

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

class canvasOptions:
    def __init__(self):
        self._optionsDict = None

        self._optionsFile = self._defaultOptionsFile()
        self.optionsLoad()

    def setToNewDict(self, newDict : dict):
        self._optionsDict = newDict
    
    def getDict(self):
        return self._optionsDict
    
    def setOption(self, key1, key2, value):
        if not key1 in self._optionsDict.keys():
            logger.error(f'Did not find key1 in options "{key1}"')
            return

        if not key2 in self._optionsDict[key1].keys():
            logger.error(f'Did not find key2 in options "{key2}"')
            return

        try:
            self._optionsDict[key1][key2] = value
        except (IndexError) as e:
            logger.error(f'Did not find key2 in options "{key2}"')
            return

    def getOption(self, key1, key2=None):
        if not key1 in self._optionsDict.keys():
            logger.error(f'Did not find key1 in options "{key1}"')
            return
        
        # return entire dictionary of options 'key1'
        if key2 is None:
            return self._optionsDict[key1]
        
        try:
            return self._optionsDict[key1][key2]
        except (IndexError) as e:
            logger.error(f'Did not find key2 in options "{key2}"')
            return
        
    def optionsVersion(self):
        return self.getOption('version', 'version')

    def _optionsDefault(self):
        """Hard coded default options.
        """
        
        self._optionsDict = {}  # OrderedDict()

        self._optionsDict['motor'] = {}  # OrderedDict()

        _motorList = [motor for motor in dir(canvas.motor) if not (motor.endswith('__') or motor=='bMotor')]
        self._optionsDict['motor']['motorNameList'] = _motorList
        
        self._optionsDict['motor']['motorName'] = 'fakeMotor' #'fakeMotor' #'mp285' #'bPrior' # the name of the class derived from bMotor
        self._optionsDict['motor']['portList'] = [f'COM{x+1}' for x in range(20)]
        self._optionsDict['motor']['port'] = 'COM4'
        #self._optionsDict['motor']['isReal'] = False

        # on olympus, camera is 1920 x 1200
        self._optionsDict['video'] = {}  #OrderedDict()
        self._optionsDict['video']['saveAtInterval'] = False
        self._optionsDict['video']['saveIntervalSeconds'] = 2
        #self._optionsDict['video']['oneimage'] = 'bCamera/oneimage.tif'
        self._optionsDict['video']['left'] = 100
        self._optionsDict['video']['top'] = 100
        self._optionsDict['video']['width'] = 1920  #640 #1280 # set this to actual video pixels
        self._optionsDict['video']['height'] = 1080  #480 #720
        self._optionsDict['video']['umWidth'] = 455.2 #693
        self._optionsDict['video']['umHeight'] = 256.05  #341.4 #433
        self._optionsDict['video']['scaleMult'] = 1.0 # as user resizes window
        self._optionsDict['video']['motorStepFraction'] = 0.15 # for motor moves
        self._optionsDict['video']['flipHorizontal'] = True # for motor moves
        self._optionsDict['video']['flipVertical'] = False # for motor moves

        self._optionsDict['Scope'] = {}  # OrderedDict()
        self._optionsDict['Scope']['zoomOneWidthHeight'] = 509.116882454314
        self._optionsDict['Scope']['motorStepFraction'] = 0.15 # for motor moves
        self._optionsDict['Scope']['useWatchFolder'] = False # Olympus needs this

        self._optionsDict['Canvas'] = {}  #OrderedDict()
        # self._optionsDict['Canvas']['left'] = 100
        # self._optionsDict['Canvas']['top'] = 100
        # self._optionsDict['Canvas']['width'] = 640
        # self._optionsDict['Canvas']['height'] = 480
        self._optionsDict['Canvas']['wheelZoom'] = 1.1
        self._optionsDict['Canvas']['maxProjectChannel'] = 1 #
        
        self._optionsDict['Canvas']['savePath'] = ''
        self._optionsDict['Canvas']['recentSavePath'] = []
        # if sys.platform.startswith('win'):
        #     self._optionsDict['Canvas']['savePath'] = 'c:/Users/LindenLab/Desktop/cudmore/data'
        # else:
        #     self._optionsDict['Canvas']['savePath'] = '/Users/cudmore/data/canvas'

        self._optionsDict['version'] = {}  # OrderedDict()
        self._optionsDict['version']['version'] = 0.2


    def optionsLoad(self, userOptions : str = None):
        if userOptions is not None:
            # load from user specified file
            '''
            optionsFolder = os.path.join(canvas.canvasUtil._getBundledDir(), 'config')
            fname = QtWidgets.QFileDialog.getOpenFileName(caption='xxx load options file', directory=optionsFolder, filter="Options Files (*.json)")
            fname = fname[0]
            #dialog.setNameFilter("*.cpp *.cc *.C *.cxx *.c++");
            logger.info(f'Loading user specified file:{fname}')
            if os.path.isfile(fname):
                with open(fname) as f:
                    self._optionsDict = json.load(f, object_pairs_hook=OrderedDict)
                self.optionsFile = fname
            '''
        else:
            if not os.path.isfile(self._optionsFile):
                self._optionsFile = self._defaultOptionsFile()
                logger.info(f'creating defaults options')
                self._optionsDefault()
                self.optionsSave()
            else:
                logger.info(f'loading: {self._optionsFile}')
                with open(self._optionsFile) as f:
                    self._optionsDict = json.load(f, object_pairs_hook=OrderedDict)
                # check if it is old
                loadedVersion = self._optionsDict['version']['version']
                if self.optionsVersion() > loadedVersion:
                    logger.warning('  optionsLoad() loaded older options file, making new one')
                    logger.warning(f'  loadedVersion:{loadedVersion}')
                    logger.warning(f'  self.optionsVersion() is {self.optionsVersion()}')
                    self._optionsDefault()

    def optionsSave(self):
        logger.info(f'saving to:{self._optionsFile}')
        # abb ubuntu
        tmpPath, tmpFile = os.path.split(self._optionsFile)
        if not os.path.isdir(tmpPath):
            logger.info(f'  making:{tmpPath}')
            os.mkdir(tmpPath)
        with open(self._optionsFile, 'w') as outfile:
            json.dump(self._optionsDict, outfile, indent=4, sort_keys=False)

    def setSavePath(self, savePath):
        """Set the path where all canvas will be saved and loaded.
        """
        if not os.path.isdir(savePath):
            logger.warning(f'got bad save path:{savePath}')
        else:
            logger.info(f'Save path is now: {savePath}')
            self._optionsDict['Canvas']['savePath'] = savePath
            self.optionsSave()

    def _defaultOptionsFile(self):
        # bundledDir = canvas.canvasUtil._getBundledDir()
        # optionsFilePath = os.path.join(bundledDir, 'scopeOptions', 'scopeConfig.json')
        scopeOptionsFolder = canvas.canvasUtil._getScopeOptionsFolder()
        optionsFilePath = os.path.join(scopeOptionsFolder, 'scopeConfig.json')
        return optionsFilePath

