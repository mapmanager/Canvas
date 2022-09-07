# Author: Robert Cudmore
# Date: 20190424

"""
Load converted headers with bStackHeader._loadHeaderFromConverted(scopeFIlePath)

Converted header .txt file is in json format and looks like this

{
    "path": "/Users/cudmore/box/data/testoir/20190514_0001.oir",
    "date": "2019-05-14",
    "time": "15:43:24.544-07:00",
    "olympusFileVersion": "2.1.2.3",
    "olympusProgramVersion": "2.3.1.163",
    "laserWavelength": "920.0",
    "laserPercent": "7.7",
    "pmtGain1": "1.0",
    "pmtOffset1": "0",
    "pmtVoltage1": "557",
    "pmtGain2": "1.0",
    "pmtOffset2": "0",
    "pmtVoltage2": "569",
    "pmtGain3": "1.0",
    "pmtOffset3": "0",
    "pmtVoltage3": "557",
    "scanner": "Galvano",
    "zoom": "2.0",
    "bitDepth": 16,
    "numChannels": 1,
    "stackType": "TSeries",
    "xPixels": 218,
    "yPixels": 148,
    "numImages": 200,
    "numFrames": 200,
    "xVoxel": 0.497184455521791,
    "yVoxel": 0.497184455521791,
    "zVoxel": 1.0,
    "umWidth": 73.58329941722508,
    "umHeight": 108.38621130375044,
    "frameSpeed": "307.19",
    "lineSpeed": "1.39",
    "pixelSpeed": "0.002",
    "xMotor": null,
    "yMotor": null,
    "zMotor": null
}
"""

import os, sys, json
import time
from collections import OrderedDict
from pprint import pprint
from canvas import canvasUtil

import tifffile

import bioformats

import xml
import xml.dom.minidom # to pretty print

import canvas

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

class canvasStackHeader:
    """Stack header is created from header in raw image file (tif, oir).
    
    Underlying representation is a dictionary.
    """
    def __init__(self, path=''):

        logger.info(f'path:{path}')

        self.header = canvasStackHeader.getDefaultHeader(path)  # creates self.header dict
        
        # TODO: add (Nikon, Bruker, etc)
        if path.endswith('.oir'):
            self._readOirHeader()
        else:
            # load (generic tif, scanimage)
            self.loadHeader()

    def getDefaultHeader(path=None):
        """Initialize default stack header.
        
        - All keys must be lower-case, saving/loading using tiffile forces all keys to lower().
        - All stacks wil have the same header.
        - Some stacks will add keys to the header (e.g. ScanImage version).
        """
        header = {}  # OrderedDict()

        header['path'] = path # full path to the file
        header['filename'] = os.path.split(path)[1] if path is not None else None
        header['date'] = ''
        header['time'] = ''
        #header['seconds'] = ''

        header['stacktype'] = None
        header['numchannels'] = None
        header['bitdepth'] = None

        header['xpixels'] = None
        header['ypixels'] = None
        header['numimages'] = None
        header['numframes'] = None
        #
        header['xvoxel'] = 1 # um/pixel
        header['yvoxel'] = 1
        header['zvoxel'] = 1

        header['umwidth'] = None  # xPixels * xVoxel
        header['umheight'] = None  # yPixels * yVoxel

        header['xmotor'] = None
        header['ymotor'] = None
        header['zmotor'] = None

        header['zoom'] = None # optical zoom of objective

        # abb removed 20200915 working on canvas in Baltimore
        # maybe tiff headers should be dynamic based on file type?
        # with some key elements ['xVoxel', 'yVoxel', 'xMotor', 'yMotor', ...]
        '''
        self.header['laserWavelength'] = None #
        self.header['laserPercent'] = None #

        # 1
        self.header['pmtGain1'] = None #
        self.header['pmtOffset1'] = None #
        self.header['pmtVoltage1'] = None #
        # 2
        self.header['pmtGain2'] = None #
        self.header['pmtOffset2'] = None #
        self.header['pmtVoltage2'] = None #
        # 3
        self.header['pmtGain3'] = None #
        self.header['pmtOffset3'] = None #
        self.header['pmtVoltage3'] = None #

        self.header['scanner'] = None

        self.header['frameSpeed'] = None #
        self.header['lineSpeed'] = None # time of each line scan (ms)
        self.header['pixelSpeed'] = None #

        self.header['olympusFileVersion'] = '' # Of the Olympus software
        self.header['olympusProgramVersion'] = '' # Of the Olympus software
        '''

        return header
        
    def __getitem__(self, key):
        """Get key from header disctionary.
        
        Usage:
            linesPerFrame = stackHeader['linesPerFrame']
        """
        key = key.lower()
        try:
            return self.header[key]
        except (KeyError) as e:
            logger.error(f'Did not find key "{key}" in header.')

    def __setitem__(self, key, value):
        """Set key in header dictionary.

        Usage:
            stackHeader['linesPerFrame'] = 512
        """
        key = key.lower()
        try:
            self.header[key] = value
        except (KeyError) as e:
            logger.error(f'Did not find key "{key}" in header.')

    def __getattr__(self, key):
        """Get class attribute from header dictionary.
        
        Usage:
            linesPerFrame = stackHeader.linesPerFrame
        """
        #logger.info(f'key:{key}')
        key = key.lower()
        try:                                                                    
            return self.header[key]                                                    
        except (KeyError) as e:                                                        
            logger.error(f'Did not find attr "{key}" in header.')

    def keys(self):
        """Get keys in the header.
        """
        return self.header.keys()

    def print(self):
        """Print all key:value pairs in the header.
        """
        logger.info(f'  {self.path}')
        for k,v in self.header.items():
            logger.info(f'  {k}: {v}')
        
    '''
    def getHeaderFromDict(self, igorImportDict):
        """
        Used to import video from Igor canvas
        theDict: created in bCanvas.importIgorCanvas()
        """
        fullFileName = os.path.basename(self.path)
        baseFileName, extension = os.path.splitext(fullFileName)
        if baseFileName in igorImportDict.keys():
            self._header = igorImportDict[baseFileName] # may fail
        else:
            print('bStack.getHeaderFromDict() did not find imported header information for file:', self.path)
    '''

    # def old_importVideoHeaderFromIgor(self, igorImportDict):
    #     print('importVideoHeaderFromIgor()')
    #     fullFileName = os.path.basename(self.path)
    #     baseFileName, extension = os.path.splitext(fullFileName)
    #     if baseFileName in igorImportDict.keys():
    #         self.header = igorImportDict[baseFileName].header # may fail
    #         print('   self.header:', self.header)
    #     else:
    #         print('bStackHeader.importVideoHeaderFromIgor() did not find imported header information for file:', self.path)

    def loadHeader(self):
        """Load header from underlying image file (tif, oir, etc).
        """
        
        #logger.info(f'{self.path}')

        self.header = canvasStackHeader.getDefaultHeader(self.path)  # we need to keep path 

        # make sure this works, if not, then bail
        try:
            with tifffile.TiffFile(self.path) as tif:
                pass
        except(tifffile.TiffFileError) as e:
            logger.error('\n\n EXCEPTION is: {e}')
            logger.error(f'  {self.path} \n\n')
            return

        with tifffile.TiffFile(self.path) as tif:
            isScanImage = tif.is_scanimage

            xVoxel = 1
            yVoxel = 1
            zVoxel = 1
            numChannels = 1

            try:
                tag = tif.pages[0].tags['XResolution']
                if tag.value[0]>0 and tag.value[1]>0:
                    # xTag_value_1 = tag.value[1] # debug
                    # xTag_value_0 = tag.value[0]
                    xVoxel = tag.value[1] / tag.value[0]
                    if isScanImage:
                        _orig_xVoxel = xVoxel
                        xVoxel *= 1e4
                        #logger.info(f'  scaling ScanImage xVoxel:{_orig_xVoxel} to {xVoxel}')
                else:
                    logger.error('  got bad XResolution value?')
            except (KeyError) as e:
                logger.warning('  did not find XResolution')

            try:
                tag = tif.pages[0].tags['YResolution']
                if tag.value[0]>0 and tag.value[1]>0:
                    # yTag_value_1 = tag.value[1] # debug
                    # yTag_value_0 = tag.value[0]
                    yVoxel = tag.value[1] / tag.value[0]
                    if isScanImage:
                        _orig_yVoxel = yVoxel
                        yVoxel *= 1e4
                        #logger.info(f'  scaling ScanImage yVoxel:{_orig_yVoxel} to {yVoxel}')
                else:
                    logger.error('  got bad YResolution value?')
            except (KeyError) as e:
                logger.warning('  did not find YResolution')

            imagej_metadata = tif.imagej_metadata            
            # print('=== loadheader() imagej_metadata:')
            # pprint(imagej_metadata)
            if imagej_metadata is not None:
                try:
                    zVoxel = imagej_metadata['spacing']
                except (KeyError) as e:
                    zVoxel = 1
                    logger.error("  Did not find key imagej_metadata['spacing']")

            '''
            tag = tif.pages[0].tags['ResolutionUnit']
            print('ResolutionUnit:', tag.value)
            '''

            numImages = len(tif.pages)

            tag = tif.pages[0].tags['ImageWidth']
            xPixels = tag.value  # swapped
            tag = tif.pages[0].tags['ImageLength']
            yPixels = tag.value  # swapped

        self['stackType'] = 'Tiff'

        self['xPixels'] = xPixels
        self['yPixels'] = yPixels
        self['numChannels'] = numChannels
        self['numImages'] = numImages
        self['numFrames'] = None
        #
        #logger.info(f'  got xVoxel:{xVoxel} yVoxel:{yVoxel}')
        self['xVoxel'] = xVoxel # um/pixel
        self['yVoxel'] = yVoxel
        self['zVoxel'] = zVoxel
        
        if imagej_metadata is not None:
            for k,v in imagej_metadata.items():
                self[k] = v

        # assign meaningfull um width/height
        # acquired video should alread have this
        #logger.info(f"self['umWidth'] is {self['umWidth']}")
        #logger.info(f"self['umHeight'] is {self['umHeight']}")
        if self['umWidth'] is None:
            if xPixels is not None and xVoxel is not None:
                self['umWidth'] = xPixels * xVoxel
            else:
                self['umWidth'] = None

        if self['umHeight'] is None:
            if yPixels is not None and yVoxel is not None:
                self['umHeight'] = yPixels * yVoxel
            else:
                self['umHeight'] = None

        if isScanImage:
            # sets numChannels
            self._loadScanImageHeader()

        #logger.info('=== loaded header is')
        #self.print()

    def _loadScanImageHeader(self):
        logger.info('')
        with tifffile.TiffFile(self.path) as f:
            isScanImage = f.is_scanimage
            if not isScanImage:
                logger.error(f'  is not a ScanImage file: {self.path}')
            else:
                self['stackType'] = 'ScanImage'
                
                scanimage_metadata = f.scanimage_metadata
                # print('  scanimage_metadata:')
                # pprint(scanimage_metadata)

                if not scanimage_metadata:
                    logger.error(f'  tif file had is_scanimage but scanimage_metadata is empty dict')
                    return
                
                k2 = 'SI.VERSION_MAJOR'
                VERSION_MAJOR = scanimage_metadata['FrameData'][k2]
                #logger.info(f'  SI.VERSION_MAJOR:{VERSION_MAJOR}')
                self['si_VERSION_MAJOR'] = VERSION_MAJOR

                k2 = 'SI.VERSION_MINOR'
                VERSION_MINOR = scanimage_metadata['FrameData'][k2]
                #logger.info(f'  SI.VERSION_MINOR:{VERSION_MINOR}')
                self['si_VERSION_MINOR'] = VERSION_MINOR

                k2 = 'SI.hChannels.channelSave' # like [[1], [2]]
                channelSave = scanimage_metadata['FrameData'][k2]
                #logger.info(f'  SI.hChannels.channelSave: {type(channelSave)} {channelSave}')
                # jhu patrick
                if isinstance(channelSave, int):
                    numChannels = 1
                else:
                    numChannels = len(channelSave)
                self['numChannels'] = numChannels

                '''
                k2 = 'SI.hStackManager.numSlices'
                numSlices = scanimage_metadata['FrameData'][k2]
                self['numImages'] = numChannels
                '''

                k2 = 'SI.hChannels.channelAdcResolution'
                # a list of bit depth per channel
                bitDepth = scanimage_metadata['FrameData'][k2]
                bitDepth = bitDepth[0] # assuming all channels the same
                #logger.info(f'  SI.hChannels.channelAdcResolution:{bitDepth}')
                #logger.warning('   forcing bit depth to 11')
                bitDepth = 11
                self['bitDepth'] = bitDepth

                #k2 = 'SI.hRoiManager.linesPerFrame'
                #linesPerFrame = scanimage_metadata['FrameData'][k2]

                #k2 = 'SI.hRoiManager.pixelsPerLine'
                #pixelsPerLine = scanimage_metadata['FrameData'][k2]

                k2 = 'SI.hRoiManager.scanZoomFactor'
                zoom = scanimage_metadata['FrameData'][k2]
                #logger.info(f'  zoom: {k2}')
                self['zoom'] = zoom

                # SI.hMotors.motorPosition: [-186541, -180967, -651565]
                if VERSION_MAJOR==2021 and VERSION_MINOR==1:
                    k2 = 'SI.hMotors.axesPosition'
                else:
                    k2 = 'SI.hMotors.motorPosition'
                motorPosition = scanimage_metadata['FrameData'][k2]
                #logger.info(f'  {k2}:{motorPosition}')
                self['xMotor'] = motorPosition[0]
                self['yMotor'] = motorPosition[1]
                self['zMotor'] = motorPosition[2]

    def old_loadHeaderFromConverted(self, convertedStackHeaderPath):
        """Load header from coverted header .txt file"""

        #print('bStackHeader._loadHeaderFromConverted() convertedStackHeaderPath:', convertedStackHeaderPath)
        # clear our existing header
        self._initHeader()

        with open(convertedStackHeaderPath, 'r') as f:
            self.header = json.load(f)

        '''
        print('bStackHeader._loadHeaderFromConverted() is loading header information from .txt file:', convertedStackHeaderPath)
        with open(convertedStackHeaderPath, 'r') as file:
            lines = file.readlines()
        # remove whitespace characters like `\n` at the end of each line
        lines = [x.strip() for x in lines]

        # clear our existing header
        self.initHeader()

        # parse what we just read
        for line in lines:
            lhs, rhs = line.split('=')
            self.header[lhs] = rhs

        ######
        ## FIX THIS
        ######
        #print('bStackHeader._loadHeaderFromConverted() *** TODO *** add umWidth and umHeight to original conversion !!!!!')
        #print('   also need to figure out str versus int versus float !!!!')
        # todo: add this to original python/fiji scripts that convert header
        # add (umWidth, umHeight)
        # x
        #if 'umWidth' not in self.header.keys():
        if 1:
            xPixels = int(self.header['xPixels'])
            xVoxel = float(self.header['xVoxel'])
            umWidth = xPixels * xVoxel
            self.header['umWidth'] = umWidth
        # y
        #if 'umHeight' not in self.header.keys():
        if 1:
            yPixels = int(self.header['yPixels'])
            yVoxel = float(self.header['yVoxel'])
            umHeight = yPixels * yVoxel
            self.header['umHeight'] = umHeight
        '''

    def old_prettyPrint(self):
        print('   file:', os.path.split(self.path)[1],
            'stackType:', self.stackType, ',', 'bitDepth:', self.bitDepth,
            'channels:', self.numChannels, ',',
            'images:', self.numImages, ',',
            'x/y pixels:', self.pixelsPerLine, '/', self.linesPerFrame, ',',
            'x/y um/pixel:', self.xVoxel, '/', self.yVoxel,
            'umWidth:', self.umWidth, 'umHeight:', self.umHeight,
            )

    def getMetaData(self):
        """Get all header items as text in a single line"""
        ijmetadataStr = ''
        for k, v in self.header.items():
            ijmetadataStr += k + '=' + str(v) + '\n'
        return ijmetadataStr

    def saveHeader(self, headerSavePath):
        """ Save the header as a .txt file to the path.
        """
        # todo: check that the path exists
        with open(headerSavePath, 'w') as fp:
            json.dump(self.header, fp, indent=4)

    def old_assignToShape(self, stack):
        """shape is (channels, slices, x, y)"""
        #print('=== === bStackHeader.assignToShape()')
        shape = stack.shape
        if len(shape)==3:
            # single plane image
            self.header['numChannels'] = shape[0]
            self.header['numImages'] = 1
            self.header['xPixels'] = shape[1]
            self.header['yPixels'] = shape[2]
        elif len(shape)==4:
            # 3d image volume
            self.header['numChannels'] = shape[0]
            self.header['numImages'] = shape[1]
            self.header['xPixels'] = shape[2]
            self.header['yPixels'] = shape[3]
        else:
            print('   error: bStackHeader.assignToShape() got bad shape:', shape)
        #print('self.header:', self.header)
        #bitDepth = self.header['bitDepth']
        bitDepth = self.bitDepth # this will trigger warning if not already assigned
        #if bitDepth is not None:
        if type(self.bitDepth) != 'NoneType':
            #print('bStackHeader.assignToShape() bitDepth is already', self.bitDepth, type(self.bitDepth))
            pass
        else:
            dtype = stack.dtype
            if dtype == 'uint8':
                bitDepth = 8
            else:
                bitDepth = 16
            self.header['bitDepth'] = bitDepth

    def assignToShape2(self, stack):
        """Used when opening Olympus oir.
        
        shape is (channels, slices, x, y)
        """
        logger.info(f'{stack.shape}')
        
        shape = stack.shape
        if len(shape)==2:
            # single plane image
            #self['numChannels'] = shape[0]
            self['numImages'] = 1
            self['xPixels'] = shape[0]
            self['yPixels'] = shape[1]
        elif len(shape)==3:
            # 3d image volume
            #self['numChannels'] = shape[0]
            self['numImages'] = shape[0]
            self['xPixels'] = shape[1]
            self['yPixels'] = shape[2]
        else:
            logger.error('  Got bad shape: {shape}')

        bitDepth = self.bitDepth # this will trigger warning if not already assigned
        if type(self.bitDepth) != 'NoneType':
            # already assigned
            pass
        else:
            dtype = stack.dtype
            if dtype == 'uint8':
                bitDepth = 8
            else:
                bitDepth = 16
            self['bitDepth'] = bitDepth

    def readOirHeader_baltimore(self):
        import javabridge
        from pprint import pprint

        _startSec = time.time()
        
        _startedJavaBridge = canvas.canvasJavaBridge._startJavaBridge()

        print(f'1 elapsed {round(time.time()-_startSec,3)}')

        # abb baltimore, trying to speed things up
        with bioformats.ImageReader(self.path) as reader:

            print(f'2 elapsed {round(time.time()-_startSec,3)}')

            print('reader:', type(reader))
            print('reader.rdr:', type(reader.rdr))

            #print('xxx:', reader.rdr.getMetadataValue('PhysicalSizeX'))

            # reader.rdr is
            # {'o': <Java object at 0x-558de1c8>}
            # print('vars(reader.rdr)):', vars(reader.rdr))
            
            # _coreMetadataList = javabridge.jutil.jdictionary_to_string_dictionary(reader.rdr.getCoreMetadataList())
            # print('_coreMetadataList:')
            # pprint(_coreMetadataList)

            # no work
            _myReaderHeader = {
                'sizeC': reader.rdr.getSizeC(),
                'sizeT': reader.rdr.getSizeT(),
                'sizeX': reader.rdr.getSizeX(),
                'sizeY': reader.rdr.getSizeY(),
                'sizeZ': reader.rdr.getSizeZ(),
                'imageCount': reader.rdr.getImageCount(),
                #'bitsPerPixel': reader.rdr.getBitsPerPixel(),
                'dimensionOrder': reader.rdr.getDimensionOrder(),
                'isInterleaved': reader.rdr.isInterleaved(),
            }
            pprint(_myReaderHeader)

            _getSeriesMetadata = reader.rdr.getSeriesMetadata()
            print('_getSeriesMetadata:', _getSeriesMetadata)
            _seriesMetadata = javabridge.jutil.jdictionary_to_string_dictionary(_getSeriesMetadata)
            # print('_seriesMetadata:')
            # pprint(_seriesMetadata)
            
            # this does return but _globalMetadata is too complex to parse
            '''
            _getGlobalMetadata = reader.rdr.getGlobalMetadata()
            print('_getGlobalMetadata:', _getGlobalMetadata)
            _globalMetadata = javabridge.jutil.jdictionary_to_string_dictionary(_getGlobalMetadata)
            print('_globalMetadata:')
            pprint(_globalMetadata)
            '''

            _getCoreMetadataList = reader.rdr.getCoreMetadataList()
            print('_getCoreMetadataList:', _getCoreMetadataList)
            _coreMetadataList = javabridge.jutil.jdictionary_to_string_dictionary(_getCoreMetadataList)
            print('_coreMetadataList:')
            pprint(_coreMetadataList)

            #print('series_count:', reader.series_count)
            
            #_seriesMetadata = reader.getSeriesMetadata()
            #print('_seriesMetadata:', _seriesMetadata)

        if _startedJavaBridge:
                _stoppedJavaBridge = canvas.canvasJavaBridge._stopJavaBridge()

    def _readOirHeader(self):
        """
        Read header information from xml. This is not pretty.
        """
        logger.info(f'path:{self.path}')

        def _qn(namespace, tag_name):
            '''
            xml helper. Return the qualified name for a given namespace and tag name
            This is the ElementTree representation of a qualified name
            '''
            return "{%s}%s" % (namespace, tag_name)

        try:
            _startSec = time.time()

            # get_omexml_metadata takes about 4 seconds !!!
            # metaData is str, len(metaDate) = 182126
            metaData = bioformats.get_omexml_metadata(path=self.path)

            # omeXml is <class 'bioformats.omexml.OMEXML'>
            omeXml = bioformats.OMEXML(metaData)

            # leave this here, will extract ome-xml as pretty printed string
            #print('omeXml:', omeXml.prettyprintxml())
            '''
            pretty_xml = xml.dom.minidom.parseString(str(omeXml))
            print(pretty_xml.toprettyxml())
            sys.exit()
            '''

            # this does not work, always gives us time as late in the PM?
            '''
            dateTime = omeXml.image().AcquisitionDate
            print('dateTime:', dateTime)
            date, time = dateTime.split('T')
            self.header['date'] = date
            self.header['time'] = time
            '''

            #_laserWavelength = omeXml.instrument().laser.WaveLength

            instrumentObject = omeXml.instrument()
            #print('instrumentObject:', instrumentObject)
            
            laserElement = instrumentObject.node.find(_qn(instrumentObject.ns['ome'], "Laser")) # laserElement is a 'xml.etree.ElementTree.Element'
            #print('    laserElement:',type(laserElement))
            if laserElement is not None:
                self['laserWavelength'] = laserElement.get("Wavelength")

            # todo: how do i get info from detector 1 and 2 ???
            '''
            self['pmt1_gain'] = omeXml.instrument().Detector.node.get("Gain") #
            self['pmt1_offset'] = omeXml.instrument().Detector.node.get("Offset") #
            self['pmt1_voltage'] = omeXml.instrument().Detector.node.get("Voltage") #
            '''

            # XYCZT
            _dimensionOrder = omeXml.image().Pixels.DimensionOrder
            self['dimensionOrder'] = _dimensionOrder

            # error
            # _significantBits = omeXml.image().Pixels.SignificantBits
            #self['bitDepth'] = _significantBits


            numChannels = omeXml.image().Pixels.channel_count
            self['numChannels'] = numChannels

            self['xPixels'] = omeXml.image().Pixels.SizeX # pixels
            self['yPixels'] = omeXml.image().Pixels.SizeY # pixels

            # todo: this is NOT working
            #self['numImages'] = omeXml.image_count

            self['numImages'] = omeXml.image().Pixels.SizeZ # number of images
            self['numFrames'] = omeXml.image().Pixels.SizeT # number of images

            if self['numImages'] > 1:
                #print('--------- tmp setting -------- self["stackType"] = "ZStack"')
                self['stackType'] = 'ZStack' #'ZStack'
            elif self['numImages'] == 1 and self['numFrames'] > 1:
                # swap numFrames into numImages
                self['numImages'] = self['numFrames']
                #print('--------- tmp setting -------- self["stackType"] = "TSeries"')
                self['stackType'] = 'TSeries'
            elif self['numImages'] == 1:
                self['stackType'] = 'OneImage'
            else:
                logger.error(f"stackType is UNKNOWN numImages:{self['numImages']}, numFrames:{self['numFrames']}")
                self['stackType'] = 'UNKNOWN'

            self['xVoxel'] = omeXml.image().Pixels.PhysicalSizeX # um/pixel
            self['yVoxel'] = omeXml.image().Pixels.PhysicalSizeY
            self['zVoxel'] = omeXml.image().Pixels.PhysicalSizeZ

            self['umWidth'] = self['xPixels'] * self['xVoxel']
            self['umHeight'] = self['yPixels'] * self['yVoxel']

            root = xml.etree.ElementTree.fromstring(str(omeXml))

            i=0
            pixelSpeed2, pixelSpeed3 = None, None
            lineSpeed2, lineSpeed3 = None, None
            frameSpeed2, frameSpeed3 = None, None
            for child in root:
                if child.tag.endswith('StructuredAnnotations'):
                    for grandchild in child:
                        for greatgrandchild in grandchild:
                            for greatgreatgrandchild in greatgrandchild:
                                i+=1
                                
                                # many are prepended with file name
                                finalKey = greatgreatgrandchild[0].text
                                
                                finalValue = greatgreatgrandchild[1].text

                                #print(f'  finalKey: "{finalKey}": {finalValue}')

                                # 20190617
                                """
                                <ome:OriginalMetadata>
                                    <ome:Key>20190613__0028.oir method sequentialType #1</ome:Key>
                                    <ome:Value>Line</ome:Value>
                                </ome:OriginalMetadata>
                                """
                                # removed 20191029, was not working
                                """
                                if 'method sequentialType' in finalKey:
                                    print(finalKey)
                                    print('   ', finalValue)
                                    print('--------- tmp setting -------- self.header["stackType"] = ', finalValue)
                                    self.header['stackType'] = finalValue
                                """

                                # 20190617, very specific for our scope
                                """
                                <ome:OriginalMetadata>
                                    <ome:Key>- Laser Chameleon Vision II transmissivity</ome:Key>
                                    <ome:Value>[9.3]</ome:Value>
                                </ome:OriginalMetadata>
                                """
                                if '- Laser Chameleon Vision II transmissivity' in finalKey:
                                    finalValue = finalValue.strip('[')
                                    finalValue = finalValue.strip(']')
                                    self['laserPercent'] = finalValue

                                if 'general creationDateTime' in finalKey:
                                    theDate, theTime = finalValue.split('T')
                                    self['date'] = theDate
                                    self['time'] = theTime

                                #if 'fileInfomation version #1' in finalKey:
                                if 'fileInfomation version' in finalKey:
                                    self['olympusFileVersion'] = finalValue
                                #if 'system systemVersion #1' in finalKey:
                                if 'system systemVersion' in finalKey:
                                   self['olympusProgramVersion'] = finalValue

                                if 'area zoom' in finalKey:
                                    self['zoom'] = finalValue
                                if 'configuration scannerType' in finalKey:
                                    self['scanner'] = finalValue # in ('Resonant', 'Galvano')
                                
                                # see _significantBits
                                if 'imageDefinition bitCounts' in finalKey:
                                    self['bitDepth'] = int(finalValue)

                                # channel 1
                                if 'pmt gain #1' in finalKey:
                                    self['pmtGain1'] = finalValue
                                if 'pmt offset #1' in finalKey:
                                    self['pmtOffset1'] = finalValue
                                if 'pmt voltage #1' in finalKey:
                                    self['pmtVoltage1'] = finalValue
                                # channel 2
                                if 'pmt gain #2' in finalKey:
                                    self['pmtGain2'] = finalValue
                                if 'pmt offset #2' in finalKey:
                                    self['pmtOffset2'] = finalValue
                                if 'pmt voltage #2' in finalKey:
                                    self['pmtVoltage2'] = finalValue
                                # channel 3
                                if 'pmt gain #3' in finalKey:
                                    self['pmtGain3'] = finalValue
                                if 'pmt offset #3' in finalKey:
                                    self['pmtOffset3'] = finalValue
                                if 'pmt voltage #3' in finalKey:
                                    self['pmtVoltage3'] = finalValue

                                # use #2 for Galvano, and #3 for Resonant
                                # specific to Santana scope (configurations may be different)
                                if 'speedInformation pixelSpeed #2' in finalKey:
                                    pixelSpeed2 = finalValue
                                if 'speedInformation pixelSpeed #3' in finalKey:
                                    pixelSpeed3 = finalValue
                                if 'speedInformation lineSpeed #2' in finalKey:
                                    lineSpeed2 = finalValue
                                if 'speedInformation lineSpeed #3' in finalKey:
                                    lineSpeed3 = finalValue
                                if 'speedInformation frameSpeed #2' in finalKey:
                                    frameSpeed2 = finalValue
                                if 'speedInformation frameSpeed #3' in finalKey:
                                    frameSpeed3 = finalValue

            if self['scanner'] == 'Galvano':
                self['pixelSpeed'] = pixelSpeed2
                self['lineSpeed'] = lineSpeed2
                self['frameSpeed'] = frameSpeed2
            elif self['scanner'] == 'Resonant':
                self['pixelSpeed'] = pixelSpeed3
                self['lineSpeed'] = lineSpeed3
                self['frameSpeed'] = frameSpeed3
            else:
                self['pixelSpeed'] = None
                self['lineSpeed'] = None
                self['frameSpeed'] = None

            _stopSec = time.time()
            logger.info(f'  took {round(_stopSec-_startSec,3)}')

        except Exception as e:
            logger.error(f'EXCEPTION: {e}')
            raise
        finally:
            pass

if __name__ == '__main__':
    #print('tifffile.__version__', tifffile.__version__)

    path = '/Users/cudmore/data/canvas/20200911/20200911_aaa/xy512z1zoom5bi_00001_00010.tif'
    path = '/Users/cudmore/data/canvas/20200914/20200914_ssslllaaa/20200914_ssslllaaa_video/v20200914_ssslllaaa_000.tif'
    
    path = '/Users/cudmore/data/canvas/20220808_work2/040418_026.tif'
    
    path = '/Users/cudmore/data/linden-sutter/1024by1024by1zoom3/xy1024z1zoom3bi_00001_00001.tif'

    path = '/Users/cudmore/data/example-oir/20190416__0001.oir'

    _startedJavaBridge = canvas.canvasJavaBridge._startJavaBridge()

    try:
        sh = canvasStackHeader(path=path)
        sh.print()

        #testSpeed()

    finally:
        logger.info('stop javabridge')
        canvas.canvasJavaBridge._stopJavaBridge()