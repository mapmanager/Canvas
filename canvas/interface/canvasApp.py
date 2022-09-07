# Author: Robert Cudmore
# Date: 20190630

import os, sys, traceback
#import copy # to do deepcopy of (dict, OrderedDict)
from collections import OrderedDict
from datetime import datetime
from pprint import pprint

from PyQt5 import QtCore, QtWidgets, QtGui

import qdarkstyle

import canvas.interface
import canvas.canvasOptions
import canvas.canvasUtil

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

class canvasApp(QtWidgets.QMainWindow):
    """
    One main 'window' for the canvas appication.
        - One instance of video (canvas.bCamera.myVideoWidget)
        - One instance of motor (canvas.bMotor)
        - Keep a list of canvas (canvasWidget) in canvasDict.
    """

    __version__ = 0.2
    
    #def __init__(self, loadIgorCanvas=None, path=None, parent=None):
    def __init__(self, parent=None):
        """
        loadIgorCanvas: path to folder of converted Igor canvas
        path: path to json file of a saved Python canvas
        parent = QtWidgets.QApplication
        """
        super().__init__()

        logger.info(f'')

        # create directories in <user>/Documents and add to python path
        firstTimeRunning = canvas.canvasUtil._addUserPath()
        if firstTimeRunning:
            logger.info('We created <user>/Documents/Canvas and need to restart')
            # tell user to restart
            canvas.interface.canvasDialog.okDialog('First time running canvas ... please quit and restart')

        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

        # size of singleton 'QApplication' window on MS Windows
        w = 500
        h = 200
        self.resize(w, h)

        self.myApp = parent # to use activeWindow() or focusWidget()

        # load default options
        self._canvasOption = canvas.canvasOptions.canvasOptions()

        # todo: do this after user modifies options, so they can set motor on fly
        motorName = self._canvasOption.getOption('motor', 'motorName')
        port = self._canvasOption.getOption('motor', 'port')
        self.assignMotor(motorName, port)

        # dictionary of canvasWidget
        # each key is file name with no extension
        self.canvasDict = OrderedDict()

        self.myMenu = canvas.interface.bMenu(self)

        # camera Thread
        self.camera = None #bCamera.myVideoWidget()
        self.showingCamera = False

    @property
    def options(self):
        return self._canvasOption

    def myQuit(self):
        if self.camera is not None:
            self.camera.stopVideoThread()
        self.myApp.quit()
        
    def closeEvent(self, event):
        # added this on windows, what does it do on mac? There is no main window?
        logger.info('')

        # close canvas windows
        for k in self.canvasDict.keys():
            self.canvasDict[k].close()

        # tell the app to quit?
        self.myApp.quit()  # will shut down video window
        event.accept()

    def toggleVideo(self):
        self.showingCamera = not self.showingCamera
        if self.showingCamera:
            if self.camera is None:
                videoOptions = self.options.getOption('video')  # a dict
                self.camera = canvas.interface.camera.myVideoWidget(self, videoOptions)
                self.camera.videoWindowSignal.connect(self.slot_VideoChanged)
                self.camera.startVideoThread()
            self.camera.show()
        else:
            if self.camera is not None:
                self.camera.hide()

    def slot_VideoChanged(self, videoDict):
        event = videoDict['event']
        if event == 'Close Window':
            # actual video window is already closed (thread is still running)
            self.showingCamera = False
        elif event == 'Resize Window':
            # save the scaleMult (never change w/h)
            scaleMult = videoDict['scaleMult']
            #self._optionsDict['video']['scaleMult'] = scaleMult
            self.options.setOption('video', 'scaleMult', scaleMult)
        elif event == 'Move Window':
            # save the (t,l)
            # self._optionsDict['video']['left'] = videoDict['left']
            # self._optionsDict['video']['top'] = videoDict['top']
            self.options.setOption('video', 'left', videoDict['left'])
            self.options.setOption('video', 'top', videoDict['top'])

    def getCurentImage(self):
        if self.camera is not None:
            return self.camera.getCurentImage()
        else:
            return None

    def assignMotor(self, motorName, motorPort):
        """
        Create a motor controller from a class name

        Parameters:
            useMotor: False for off scope analysis
            motorName: A string corresponding to a derived class of bMotor. File is in bimpy/bMotor folder
        """
        # we will import user defined motor class using a string
        # see: https://stackoverflow.com/questions/4821104/dynamic-instantiation-from-string-name-of-a-class-in-dynamically-imported-module
        # on sutter this is x/y/x !!!

        class_ = getattr(canvas.motor, motorName) # class_ is a module

        #print('class_:', class_)
        #class_ = getattr(class_, motorName) # class_ is a class
        self.xyzMotor = class_(motorPort)

    def mousePressEvent(self, event):
        logger.info('===')
        super().mousePressEvent(event)
        #event.setAccepted(False)

    '''
    def keyPressEvent(self, event):
        print('myApp.keyPressEvent() event:', event)
        bLogger.info(f'event:{event}')
        # todo: abb hopkins, why is this here?
        self.myGraphicsView.keyPressEvent(event)
    '''

    def bringCanvasToFront(self, fileNameNoExtension):
        """Bring a canvas window to the front.
        """
        logger.info(f'fileNameNoExtension:{fileNameNoExtension}')
        for canvas in self.canvasDict.keys():
            if canvas == fileNameNoExtension:
                self.canvasDict[canvas].activateWindow()
                self.canvasDict[canvas].raise_() # raise is a keyword and can't be used
                break

    def activateCanvas(self, path):
        # handled by 'about to show'
        # self.myMenu.buildCanvasMenu(self.canvasDict)
        pass

    def closeCanvas(self, path):
        fileNameNoExt = os.path.split(path)[1]
        fileNameNoExt = os.path.splitext(fileNameNoExt)[0]

        removed = self.canvasDict.pop(fileNameNoExt, None)
        
        # now handled in bMenu when user clicks menu
        '''
        if removed is None:
            logger.warning(f'Did not remove:{fileNameNoExt}')
        else:
            self.myMenu.buildCanvasMenu(self.canvasDict)
        '''

    def newCanvas(self, shortName=''):
        """
        new canvas(s) are always saved in options['Canvas']['savePath']
            options['Canvas']['savePath']/<date>_<name>
        """

        # path where we will save on new
        savePath = self.options.getOption('Canvas', 'savePath')

        if not savePath:
            # user needs to specify with menu 'xxx:yyy'
            text = f'Save path does not exist.'
            informativeText = 'Specify a save path with menu xxx:yyy'
            tmp = canvas.interface.okDialog(text, informativeText=informativeText)
            return

        if shortName=='':
            # if our savePath is bogus then abort
            if not os.path.isdir(savePath):
                # savepath from options is bogus
                logger.error(f'path does not exist savePath:{savePath}')
                logger.error('  Please specify a valid folder in main interface with menu "Options - Set Data Path ..."')

                msgBox = QtWidgets.QMessageBox()
                msgBox.setWindowTitle('Save Path Not Found')
                msgBox.setText('Did not find data path folder:\n  ' + savePath)
                msgBox.setInformativeText('Please specify a valid folder in main interface with menu "Options - Set Data Path ..."')
                retval = msgBox.exec_()
                return

            # ask user for the name of the canvas
            text, ok = QtWidgets.QInputDialog.getText(self,
                            'New Canvas', 'Enter a new canvas name (no spaces):')
            text = text.replace(' ', '')
            if ok:
                shortName = str(text)

        if shortName == '':
            return

        dateStr = datetime.today().strftime('%Y%m%d')

        #datePath = os.path.join(savePath, dateStr)

        folderName = dateStr + '_' + shortName
        folderPath = os.path.join(savePath, folderName)

        videoFolderPath = os.path.join(folderPath, folderName + '_video')

        fileName = dateStr + '_' + shortName + '_canvas.txt'
        filePath = os.path.join(folderPath, fileName)

        if os.path.isfile(filePath):
            logger.warning(f'  file already exists: {filePath}')

            text = f'Canvas "{shortName}" Already Exists'
            informativeText = 'Please choose a different name'
            tmp = canvas.interface.okDialog(text, informativeText=informativeText)
            '''
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)

            msg.setText(f'Canvas "{shortName}" Already Exists')
            msg.setInformativeText("Please choose a different name")
            msg.setWindowTitle("Canvas Already Exists")
            msg.setDetailedText(f'Existing path is:\n {filePath}')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            #msg.buttonClicked.connect(msgbtn)

            retval = msg.exec_()
            '''
        else:
            logger.info(f'  making new canvas: {filePath}')
            # todo: defer these until we actually save !!!
            '''
            if not os.path.isdir(datePath):
                os.mkdir(datePath)
            '''
            if not os.path.isdir(folderPath):
                logger.info(f'  making new folder: {folderPath}')
                os.mkdir(folderPath)

            # made when we actually acquire a video
            #if not os.path.isdir(videoFolderPath):
            #    os.mkdir(videoFolderPath)

            # finally, make the canvas
            newCanvasWidget = canvas.interface.canvasWidget(filePath, self, isNew=True)

            # TODO: organize turning all motor functions on/off
            newCanvasWidget.signalMoveTo.connect(self.slot_motorMoveTo)

            # add to list
            fileNameNoExt, ext = os.path.splitext(fileName)
            self.canvasDict[fileNameNoExt] = newCanvasWidget

            # update menus
            #self.myMenu.buildCanvasMenu(self.canvasDict)

    def activeWindow(self):
        """
        Get frontmost window.
        
        We are most interested in `canvas.interface.canvasWidget`.
        """
        return self.myApp.activeWindow()
    
    def save(self):
        """
        Save the canvas
        """

        # need to get the active canvas window
        #activeWindow = self.myApp.activeWindow()
        activeWindow = self.activeWindow()

        logger.info(f'activeWindow:{activeWindow}')

        #if focusWidget is not None:
        if activeWindow is not None:
            if isinstance(activeWindow, canvas.interface.canvasWidget):
                activeWindow.saveCanvas()
            else:
                logger.warning('  front window is not a canvasWidget')
        else:
            pass
        '''
        self.canvas.save()
        self.optionsSave()
        '''

    def load(self, filePath='', askUser=False):
        """
        Load a canvas
        """
        if askUser:
            dataFolder = self.options.getOption('Canvas', 'savePath')
            if not os.path.isdir(dataFolder):
                dataFolder = ''
            filePath = QtWidgets.QFileDialog.getOpenFileName(caption='Load a _canvas.txt file',
                            directory=dataFolder, filter="Canvas Files (*.json)")
            filePath = filePath[0] # filePath is a tuple
            logger.info(f'Loading user specified file: {filePath}')

        if os.path.isfile(filePath):
            # load
            loadedCanvasWidget = canvas.interface.canvasWidget(filePath, self, isNew=False) #bCanvas(filePath=filePath)

            # TODO: organize turning all motor functions on/off
            # we generally do not want any motor face on load (for analysis)
            loadedCanvasWidget.signalMoveTo.connect(self.slot_motorMoveTo)

            # keep track of loaded canvas widget
            basename = os.path.split(filePath)[1]
            basename = os.path.splitext(basename)[0]
            self.canvasDict[basename] = loadedCanvasWidget

            # now handled in bMenu when user clicks menu
            #self.myMenu.buildCanvasMenu(self.canvasDict)

        else:
            logger.warning(f'Did not find file:{filePath}')
            return

    def slot_motorMoveTo(self, moveDict : dict):
        logger.info(moveDict)
        xMotorPos = moveDict['xMotorPos']
        yMotorPos = moveDict['yMotorPos']
        
        thePos = self.xyzMotor.moveto(x=xMotorPos, y=yMotorPos) # the pos is (x,y)

        # update interface
        #self.qqq.readMotorPosition()

    def slot_UpdateOptions(self, optionsDict :dict):
        """Update all options.
        
        Used when user hits 'ok' in options dialog, see canvas.interface.bOptionsDialog.
        """
        logger.info('')

        # grab existing and compare to new to find changes
        oldMotorName = self.options.getOption('motor', 'motorName')
        oldPort = self.options.getOption('motor', 'port')

        # make sure motor name is in list
        #self._optionsDict['motor']['motorNameList']

        # update
        #self._optionsDict = copy.deepcopy(optionsDict)
        self.options.setToNewDict(optionsDict)
        self.options.optionsSave()

        # update options in camera thread
        if self.camera is not None:
            self.camera.setVideoOptions(self.options.getOption('video'))

        # update the motore
        # todo: check if it has changed
        # todo: do this after user modifies options, so they can set motor on fly
        newMotorName = self.options.getOption('motor', 'motorName') # = 'bPrior'
        newPort = self.options.getOption('motor', 'port')
        if oldMotorName != newMotorName or oldPort != newPort:
            logger.info(f'Assigning new motor:{newMotorName} {newPort}')
            self.assignMotor(newMotorName, newPort)

def main(canvasPath : str = None):
    """Main entry point to run the canvas interface.

    Args:
        canvasPath: full path to existing canvas (for debugging).
    """
    import canvas.canvasJavaBridge
    
    try:
        logger.info(f'Starting canvasPath:{canvasPath}')
        
        # print all package info
        _versionDict = canvas.canvasUtil.getVersionInfo()
        for k,v in _versionDict.items():
            logger.info(f'  {k}:{v}')

        _javaBridgeStarted = canvas.canvasJavaBridge._startJavaBridge()

        app = QtWidgets.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)

        # set the icon of the application
        # tmpPath = os.path.dirname(os.path.abspath(__file__))
        # iconsFolderPath = os.path.join(tmpPath, 'icons')
        # iconPath = os.path.join(iconsFolderPath, 'canvas-color-64.png')
        iconPath = canvas.canvasUtil._getIcon('miro-canvas-64.png')
        logger.info(f'  iconPath:{iconPath}')
        appIcon = QtGui.QIcon(iconPath)

        app.setWindowIcon(appIcon)

        myCanvasApp = canvasApp(parent=app)

        # todo: could also use platform.system() which returns 'Windows'
        if sys.platform.startswith('win') or sys.platform.startswith('linux'):
            # linden windows machine isreporting 'win32'
            myCanvasApp.show()
        
        # load an existing canvas (for debugging)
        if canvasPath is not None and os.path.isfile(canvasPath):
            myCanvasApp.load(canvasPath)

        sys.exit(app.exec_())

    except Exception as e:
        logger.error('\nEXCEPTION: canvasApp.main()')
        logger.error(traceback.format_exc())
    finally:
        canvas.canvasJavaBridge._stopJavaBridge()

    logger.info('canvasApp.main() last line .. bye bye')


if __name__ == '__main__':
    """
    call main() with or without javabridge
    """

    okGo = True
    # if len(sys.argv) > 1:
    #     if sys.argv[1] == 'javabridge':
    #         withJavaBridge = True
    #     else:
    #         okGo = False
    #         logger.error(f'Did not understand command line:{sys.argv[1]}')

    if okGo:
        canvasPath = '/Users/cudmore/data/canvas/20220809_tstlinen1/20220809_tstlinen1_canvas.txt'
        canvasPath = '/Users/cudmore/data/canvas/20220823_a100/20220823_a100_canvas.json'
        main(canvasPath=canvasPath)
