# Robert Cudmore
# 20190420

import os, sys
from collections import OrderedDict
import glob
import numpy as np
import skimage

import tifffile

try:
    import bioformats
except (ImportError) as e:
    bioformats = None

import canvas

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

class canvasStack:
    """
    Manages a 3D image stack or time-series movie of images

    Image data is in self.stack
    """
    #def __init__(self, path='', folderPath='', loadImages=True, loadTracing=True):
    def __init__(self, path='', loadImages=True):
        """
        Args:
            path: full path to file or folder with .tif files
            loadImages: If True then load raw image data, otherwise just the header
        """
        if path and not os.path.isfile(path):
            logger.error(f'Did not find file path: {path}')
            raise ValueError('  raising ValueError: bStack() file not found: ' + path)

        self.path = path # path to file

        # create and load header
        if os.path.isfile(path):
            self.header = canvas.canvasStackHeader(path)
        elif os.path.isdir(path):
            # todo: put into function
            fileList = glob.glob(path + '/*.tif')
            if not fileList:
                fileList = glob.glob(path + '/*.tiff')
            numFiles = len(fileList)
            if numFiles < 1:
                logger.error(f'Did not find any .tif files in folder path: {path}')
                return
            fileList = sorted(fileList)
            firstFile = os.path.join(path, fileList[0])
            self.header = canvas.canvasStackHeader(firstFile)
            logger.info(f'loaded {numFiles} from folder: {path}')
        else:
            logger.error(f'Expecting a file or folder path, got: {path}')

        self._maxNumChannels = 3 # leave this for now
        # pixel data, each channel is element in list
        # *4 because we have (raw, mask, edt, skel) for each stack#
        self._stackList = [None for tmp in range(self._maxNumChannels * 4)]
        self._maxList = [None for tmp in range(self._maxNumChannels * 4)]

        #
        # load image data
        if loadImages:
            self.loadStack2() # loads data into self._stackList
            for _channel in range(self.numChannels):
                self._makeMax(_channel)

    def print(self):
        self.printHeader()
        for idx, stack in enumerate(self._stackList):
            if stack is None:
                pass
            else:
                logger.info(f' raw data channel:{idx} shape is:{stack.shape}')

    def printHeader(self):
        self.header.print()

    def _getSavePath(self):
        """
        return full path to filename without extension
        """
        path, filename = os.path.split(self.path)
        savePath = os.path.join(path, os.path.splitext(filename)[0])
        return savePath

    @property
    def maxNumChannels(self):
        return self._maxNumChannels

    @property
    def fileName(self):
        # abb canvas
        # return self._fileName
        return os.path.split(self.path)[1]

    def getFileName(self):
        # abb canvas
        # return self._fileName
        return os.path.split(self.path)[1]

    @property
    def numChannels(self):
        return self.header.numChannels

    @property
    def numSlices(self):
        # see also numImages
        return self.header.numImages

    @property
    def numImages(self):
        # see also numSLices
        return self.header.numImages

    @property
    def pixelsPerLine(self):
        return self.header.pixelsPerLine

    @property
    def linesPerFrame(self):
        return self.header.linesPerFrame

    @property
    def xVoxel(self):
        return self.header.xVoxel

    @property
    def yVoxel(self):
        return self.header.yVoxel

    @property
    def zVoxel(self):
        return self.header.zVoxel

    @property
    def bitDepth(self):
        return self.header.bitDepth

    def old_getHeaderVal2(self, key):
        """
        key(s) are ALWAYS lower case
        """
        lowerKey = key.lower()
        if key in self.header.header.keys():
            return self.header.header[key]
        elif lowerKey in self.header.header.keys():
            return self.header.header[lowerKey]
        else:
            print('error: bStack.getHeaderVal() did not find key "' + key + '" in self.header.header. Available keys are:', self.header.header.keys())
            return None

    def getHeaderVal(self, key):
        key = key.lower()
        try:
            return self.header[key]
        except (KeyError) as e:
            logger.error(f'Did not find key "{key}" in stack header')
            return None

    def getPixel(self, channel, sliceNum, x, y):
        """
        channel is 1 based !!!!

        channel: (1,2,3, ... 5,6,7)
        """
        #print('bStack.getPixel()', channel, sliceNum, x, y)

        theRet = np.nan

        # channel can be 'RGB'
        if not isinstance(channel, int):
            return theRet

        channelIdx = channel - 1

        if self._stackList[channelIdx] is None:
            #print('getPixel() returning np.nan'
            theRet = np.nan
        else:
            nDim = len(self._stackList[channelIdx].shape)
            if nDim == 2:
                m = self._stackList[channelIdx].shape[0]
                n = self._stackList[channelIdx].shape[1]
            elif nDim == 3:
                m = self._stackList[channelIdx].shape[1]
                n = self._stackList[channelIdx].shape[2]
            else:
                logger.error(f'Got bad dimensions: {self._stackList[channelIdx].shape}')
            if x<0 or x>m-1 or y<0 or y>n-1:
                theRet = np.nan
            else:
                if nDim == 2:
                    theRet = self._stackList[channelIdx][x,y]
                elif nDim == 3:
                    theRet = self._stackList[channelIdx][sliceNum,x,y]
                else:
                    pass
                    # never get here
                    #print('bStack.getPixel() got bad dimensions:', self._stackList[channelIdx].shape)

        #
        return theRet

    def getStack(self, channel:int=1):
        """
        Get the stack data for one channel.

        Args:
            channel: 1 based

        Returns:
            np.ndarray or None
        """
        # leftover from bImPy
        # if not stackType in ['raw', 'mask', 'skel', 'video']:
        #     print('  error: bStack.getStack() expeting type in [raw, mask, skel], got:', type)
        #     return None

        if channel > self.numChannels:
            logger.error(f'Max number of channels is {self.header.numChannels}, got {channel}')
            return
        channelIdx =  channel - 1
        theRet = self._stackList[channelIdx]
        return theRet

    def getImage2(self, channel=1, sliceNum=None):
        """
        new with each channel in list self._stackList

        channel: (1,2,3,...) maps to channel-1
                    (5,6,7,...) maps to self._maskList
        """
        #print('  getImage2() channel:', channel, 'sliceNum:', sliceNum)

        channelIdx = channel - 1

        numStack = len(self._stackList)
        if channelIdx > numStack-1:
            print('ERROR: bStack.getImage2() out of bounds. Asked for channel:', channel, 'channelIdx:', channelIdx, 'but length of _stackList[] is', numStack)
            # print all stack shape
            for i in range(numStack):
                tmpStack = self._stackList[i]
                if tmpStack is None:
                    print('  ', i, 'None')
                else:
                    print('  ', i, tmpStack.shape, tmpStack.dtype)

            return None

        if self._stackList[channelIdx] is None:
            #print('   error: 0 bStack.getImage2() got None _stackList for channel:', channel, 'sliceNum:', sliceNum)
            return None
        elif len(self._stackList[channelIdx].shape)==2:
            # single plane image
            return self._stackList[channelIdx]
        elif len(self._stackList[channelIdx].shape)==3:
            return self._stackList[channelIdx][sliceNum,:,:]
        else:
            #print('   error: 1 bStack.getImage2() got bad _stackList shape for channel:', channel, 'sliceNum:', sliceNum)
            return None

    def old_getImage_ContrastEnhanced(self, display_min, display_max, channel=1, sliceNum=None, useMaxProject=False) :
        """
        sliceNum: pass None to use self.currentImage
        """
        #lut = np.arange(2**16, dtype='uint16')
        lut = np.arange(2**self.bitDepth, dtype='uint8')
        lut = self.old_display0(lut, display_min, display_max) # get a copy of the image
        if useMaxProject:
            # need to specify channel !!!!!!
            #print('self.maxProjectImage.shape:', self.maxProjectImage.shape, 'max:', np.max(self.maxProjectImage))
            #maxProject = self.loadMax(channel=channel)
            #maxProject = self.loadMax()  # load all channels
            maxProject = self._maxList[channel-1]
            if maxProject is not None:
                return np.take(lut, maxProject)
            else:
                logger.warning('Did not get max project for channel:{channel}')
                return None
        else:
            return np.take(lut, self.getImage2(channel=channel, sliceNum=sliceNum))

    def old_display0(self, image, display_min, display_max): # copied from Bi Rico
        # Here I set copy=True in order to ensure the original image is not
        # modified. If you don't mind modifying the original image, you can
        # set copy=False or skip this step.
        image = np.array(image, dtype=np.uint8, copy=True)
        image.clip(display_min, display_max, out=image)
        image -= display_min
        np.floor_divide(image, (display_max - display_min + 1) / (2**self.bitDepth), out=image, casting='unsafe')
        #np.floor_divide(image, (display_max - display_min + 1) / 256,
        #                out=image, casting='unsafe')
        #return image.astype(np.uint8)
        return image

    def hasChannelLoaded(self, channel):
        """
        channel: 1,2,3,...
        """
        channelIdx = channel - 1
        #print('bStack.hasChannelLoaded()')
        #print('  channel:', channel)
        '''
        for idx, stack in enumerate(self._stackList):
            if stack is None:
                print('  stack', idx, 'None')
            else:
                print('  stack', idx, stack.shape)
        '''
        # 20200924 was this
        #channel -= 1
        theRet = self._stackList[channelIdx] is not None
        return theRet

    def getSlidingZ2(self, channel, sliceNumber, upSlices, downSlices, func=np.max):
        """
        leaving thisStack (ch1, ch2, ch3, rgb) so we can implement rgb later

        channel: 1 based
        func: From (max, mean, ...)
        """

        channelIdx = channel - 1

        if self._stackList[channelIdx] is None:
            return None

        if self.numImages>1:
            startSlice = sliceNumber - upSlices
            if startSlice < 0:
                startSlice = 0
            stopSlice = sliceNumber + downSlices
            if stopSlice > self.numImages - 1:
                stopSlice = self.numImages - 1

            #print('    getSlidingZ2() startSlice:', startSlice, 'stopSlice:', stopSlice)

            img = self._stackList[channelIdx][startSlice:stopSlice, :, :] #.copy()

            #print('bStack.getSlidingZ2() channelIdx', channelIdx, 'startSlice:', startSlice, 'xstopSlic:', stopSlice)
            #print('  img:', img.shape)

            #img = np.max(img, axis=0)
            img = func(img, axis=0)

        else:
            logger.warning('  Did not take sliding z !!!')
            # single image stack
            img = self._stackList[0][sliceNumber,:,:].copy()

        return img


    #
    # Loading
    #
    def loadHeader(self):
        if self.header is None:
            if os.path.isfile(self.path):
                self.header = canvas.canvasStackHeader(self.path)
            else:
                print('bStack.loadHeader() did not find self.path:', self.path)

    def getMaxFile(self, channel):
        """
        get full path to max file
        """
        maxSavePath, fileName = os.path.split(self.path)
        baseFileName = os.path.splitext(fileName)[0]
        maxSavePath = os.path.join(maxSavePath, 'max')
        maxFileName = 'max_' + baseFileName + '_ch' + str(channel) + '.tif'
        maxFilePath = os.path.join(maxSavePath, maxFileName)
        return maxFilePath

    # abb canvas
    def loadMax(self):
        """
        todo: this needs to use self.numChannel !!!

        assumes:
            1) self.saveMax
            2) self.numChannels is well formed
        """
        nMax = len(self._maxList)
        for idx in range(nMax):
            channelNumber = idx + 1
            maxFilePath = self.getMaxFile(channelNumber)
            if os.path.isfile(maxFilePath):
                logger.info(f'  loading channel:{channelNumber} maxFilePath:{maxFilePath}')
                maxData = tifffile.imread(maxFilePath)
                self._maxList[idx] = maxData
            else:
                #print('  warning: bStack.loadMax() did not find max file:', maxFilePath)
                pass

    def saveMax(self):
        """
        assumes self._makeMax()
        """
        maxSavePath, tmpFileName = os.path.split(self.path)
        maxSavePath = os.path.join(maxSavePath, 'max')
        logger.info(f'  maxSavePath:{maxSavePath}')
        if not os.path.isdir(maxSavePath):
            os.mkdir(maxSavePath)

        nMax = len(self._maxList)
        for idx in range(nMax):
            maxData = self._maxList[idx]
            if maxData is None:
                continue
            channel = idx + 1
            maxFilePath = self.getMaxFile(channel)
            logger.info(f'  saving idx {idx} maxFilePath:{maxFilePath}')
            tifffile.imsave(maxFilePath, maxData)

    def getMax(self, channel=1):
        """
        Args:
            channel: 1 based
        """
        channel -= 1
        theRet = self._maxList[channel]
        return theRet

    def _makeMax(self, channelIdx):
        """Make max projection for one channel.
        
        Args:
            channelIdx: 0 based
        """
        theMax = None
        stackData = self._stackList[channelIdx]
        if stackData is None:
            logger.warning(f'Returning None for channelIdx:{channelIdx}')
            pass
        else:
            nDim = len(stackData.shape)
            if nDim == 2:
                theMax = stackData
            elif nDim == 3:
                theMax = np.max(stackData, axis=0)
            else:
                logger.warning(f'Got bad dimensions for channelIdx:{channelIdx} nDim:{nDim}')

        self._maxList[channelIdx] = theMax

    def dataIsLoaded(self):
        """True if at least one channel is loaded.
        """
        for i in range(self.numChannels):
            if self._stackList[i] is not None:
                return True
        return False

    def loadStack2(self):
        """
        Load raw stack data.
        """
        if not os.path.exists(self.path):
            logger.error(f'Did not find file path: {self.path}')
            return

        basename, _fileExt = os.path.splitext(self.path)

        if os.path.isdir(self.path):
            self._loadFromFolder()
        elif _fileExt == '.oir':
            self._loadBioFormats_Oir() # oir file (can have multiple channels)
        else:
            try:
                stackData = tifffile.imread(self.path)
            except (tifffile.TiffFileError) as e:
                logger.error(f'\nEXCEPTION e: {e}')
            else:
                # if ScanImage and numChannels>1 ... deinterleave
                logger.info(f'  self.header.stackType:{self.header.stackType}')
                if self.header.numChannels > 1:
                    numChannels = self.header.numChannels
                    
                    stackDataList = self._deinterleave(stackData, numChannels)
                    for _channelIdx in range(self.numChannels):
                        self._stackList[_channelIdx] = stackDataList[_channelIdx]
                else:
                    self._stackList[0] = stackData
                    self._makeMax(0)
                #
                return True

        # load (_ch1, _ch2), this is for backward compatibility with
        # MapManager Igor

        #TODO: I can't just replace str _ch1/_ch2,
        # only replace if it is at end of filename !!!
        
        '''
        basename = basename.replace('_ch1', '')
        basename = basename.replace('_ch2', '')

        path_ch1 = basename + '_ch1.tif'
        if os.path.exists(path_ch1):
            logger.info(f'  path_ch1: {path_ch1}')
            stackData = tifffile.imread(path_ch1)
            self._stackList[0] = stackData
            self._makeMax(0)
        # 2
        path_ch2 = basename + '_ch2.tif'
        if os.path.exists(path_ch2):
            logger.info(f'  path_ch2: {path_ch2}')
            stackData = tifffile.imread(path_ch2)
            self._stackList[1] = stackData
            self._makeMax(1)
        '''

    def _deinterleave(self, stackData : np.ndarray, numChannels : int):
        """Deinterleave raw stack data into a number of channels.

        Args:
            stackData:  CXY
            numChannels:
        """
        if stackData.shape[0] % numChannels != 0:
            logger.error('  num rows in stack data must be divisible by numChannels')

        channelDataList = [None] * numChannels
        for channelIdx in range(numChannels):
            start = channelIdx
            stop = stackData.shape[0]
            step = numChannels

            sliceRange = range(start, stop, step)
            numImagesPerChannel = len(sliceRange)
            self.header['numImages'] = numImagesPerChannel

            #self._stackList[channelIdx] = stackData[sliceRange, :, :]
            channelDataList[channelIdx] = stackData[sliceRange, :, :]

        return channelDataList

    def _loadFromFolder(self):
        """
        load a stack from a folder of .tif files
        """
        stackData = tifffile.imread(self.path + '/*.tif')
        numChannels = stackData.shape[1] # assuming [slices][channels][x][y]
        numSlices = stackData.shape[0] # assuming [slices][channels][x][y]
        self.header['numImages'] = numSlices
        logger.info(f'stackData:{stackData.shape}')
        for channel in range(numChannels):
            self._stackList[channel] = stackData[:, channel, :, :]
            self._makeMax(channel)

    def _loadBioFormats_Oir(self):
        """Load raw data from .oir using bioformats.
        
        Requires javabridge.
        """
        #linesPerFrame = self.linesPerFrame
        #pixelsPerLine = self.pixelsPerLine
        #slices = self.numImages

        # get channel from oir header
        # channels = self.numChannels
        numChannels = self.header.numChannels
        numImages = self.header.numImages

        logger.info(f'  numChannels: {numChannels} numImages:{numImages}')
        #logger.info(f'  linesPerFrame:{linesPerFrame} pixelsPerLine:{pixelsPerLine}')

        with bioformats.ImageReader(self.path) as reader:

            # _coreMetadataList = reader.getCoreMetadataList()
            # print(_coreMetadataList)
            # _seriesMetadata = reader.getSeriesMetadata()

            for channelIdx in range(numChannels):
                c = channelIdx
                numImagesLoaded = 0
                for imageIdx in range(numImages):
                    if self.header.stackType == 'ZStack':
                        z = imageIdx
                        t = 0
                    elif self.header.stackType == 'TSeries':
                        z = 0
                        t = imageIdx
                    else:
                        logger.error(f'  Did not get valid header stackType: {self.header.stackType}')
                        z = 0
                        t = imageIdx

                    image = reader.read(c=c, t=t, z=z, rescale=False) # returns numpy.ndarray

                    loaded_shape = image.shape # we are loading single image, this will be something like (512,512)
                    loaded_dtype = image.dtype
                    newShape = (numImages, loaded_shape[0], loaded_shape[1])

                    if imageIdx == 0:
                        self._stackList[channelIdx] = np.zeros(newShape, dtype=loaded_dtype)
                    self._stackList[channelIdx][imageIdx,:,:] = image

                    numImagesLoaded += 1

                #
                # abb canvas, this is redundant
                self.header.assignToShape2(self._stackList[channelIdx])

        #
        #self.header.assignToShape(self.stack)

        return True

def old_main():
    """
    debugging
    """

    path = '/Users/cudmore/data/canvas/20200911/20200911_aaa/xy512z1zoom5bi_00001_00010.tif'
    path = '/Users/cudmore/data/canvas/20200913/20200913_aaa/xy512z1zoom5bi_00001_00009.tif'

    # test oir
    if 1:
        print('--- bstack __main__ is instantiating stack')
        path = 'C:/Users/Administrator/Desktop/Sites/canvas/20200311__0001.oir'
        myStack = bStack(path)

    # test canvas video
    if 0:
        path = '/Users/cudmore/data/canvas/20200921_xxx/20200921_xxx_video/v20200921_xxx_000.tif'
        myStack = bStack(path)
        myStack.print()

    # test scanimage folder
    if 0:
        folderPath = '/Users/cudmore/data/linden-images/512by512by1zoom5'
        myStack = bStack(folderPath)
        myStack.print()
        bitDepth = myStack.getHeaderVal('bitDepth')
        print('bitDepth:', bitDepth)

    if 0:
        myStack = bStack(path, loadImages=False)

        myStack.print()
        #myStack.printHeader()

        myStack.loadStack2()

        maxFile = myStack.getMaxFile(1)
        print('maxFile:', maxFile)

        #myStack.saveMax()

        myStack.loadMax()

        theMax = myStack.getMax(1)
        print('theMax:', theMax)

    if 0:
        try:
            myStack = bStack(path)

            myStack.print()
            myStack.printHeader()

        finally:
            pass

    print('bstack __main__ finished')

def test_load_scanimage():
    
    # patrick, one channel time series
    path = '/Users/cudmore/data/patrick/GCaMP Time Series 2.tiff'

    cs = canvasStack(path)
    print(cs)

    data = cs.getStack(channel=1)
    print('data.shape:', data.shape)
    _min = np.min(data)
    _max = np.max(data)
    print('  _min:', _min)
    print('  _max:', _max)
    
def test_load_oir():
    import canvas.canvasJavaBridge

    _startedJavaBridge = canvas.canvasJavaBridge._startJavaBridge()

    path = '/Users/cudmore/data/example-oir/20190416__0001.oir'
    cs = canvasStack(path)
    print(cs)

    if _startedJavaBridge:
        canvas.canvasJavaBridge._stopJavaBridge()

if __name__ == '__main__':
    #test_load_scanimage()
    
    test_load_oir()

    #old_main()

