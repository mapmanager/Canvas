# Robert H Cudmore
# 20191224

import os, sys, time, subprocess
from datetime import datetime
from functools import partial
from collections import OrderedDict
from pprint import pprint

from typing import ItemsView, List

import numpy as np

from PyQt5 import QtCore, QtWidgets, QtGui

import canvas
import canvas.interface.bToolbar
import canvas.interface.stackWidget

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

class canvasWidget(QtWidgets.QMainWindow):
    signalMoveTo = QtCore.pyqtSignal(object)  # {filename, x, y}
    
    def __init__(self, filePath, parent=None, isNew=True):
        """
        filePath:
        parent: canvasApp
        """
        super().__init__(parent)
        logger.info(f'filePath:{filePath} isNew:{isNew}')
        self.filePath = filePath
        self.myCanvasApp = parent
        self.isNew = isNew # if False then was loaded

        # if filePath exists then will load,
        #   otherwise will make new and save
        self.myCanvas = canvas.bCanvas(filePath=filePath)

        self.myStackList = {} # a dict of open bStack

        # on olympus we watch for new files to log motor position from Prior controller
        self.myLogFilePositon = None
        useWatchFolder = self.myCanvasApp.options.getOption('Scope', 'useWatchFolder')
        if useWatchFolder:
            folderPath = os.path.dirname(self.filePath)
            self.myLogFilePositon = canvas.bLogFilePosition(folderPath, self.myCanvasApp.xyzMotor)

        self._buildUI()

        if self.isNew: # and self.getOptions()['motor']['useMotor']:
            # always read motor position on new canvas (assumes we are on a scope)
            self.userEvent('read motor position')
        else:
            # we loaded, default to editing (no motor)
            self.myGraphicsView.centerOnCrosshair()

        #
        self.show()

        # has to be done after self.show()
        # center existing video/tiff
        self.myGraphicsView.centerOnCrosshair()

    # def contextMenuEvent(self, event):
    #     logger.info('')

    def bad_dragMoveEvent(self, event):
        logger.info('')
        super().dragMoveEvent(event)
    
    def contextMenuEvent(self, event):
        logger.info('')
        #super().contextMenuEvent(event)

        _parentMenu = super().createPopupMenu()  # QMenu
        
        # list of QAction (one for each toolbar)
        #print('  _parentMenu:', _parentMenu.actions())

        # turn off bottom toolbar
        for action in _parentMenu.actions():
            # action is QtWidgets.QAction
            actionText = action.text()
            print('  ', actionText)
            if actionText == 'Status':
                # bottom status toolbar
                action.setVisible(False)

        # if a stack/file is selected in canvas
        selectedItem = self.myGraphicsView.getSelectedItem()

        # add to _parentMenu
        _parentMenu.addSeparator()
        
        # move front/back
        actionName = 'Move Forward ...'
        _action = QtWidgets.QAction(actionName, self)  # self is required !!!
        _action.setDisabled(selectedItem is None)
        _action.triggered.connect(lambda enabled, name=actionName: self._contextMenuAction(name, enabled))
        _parentMenu.addAction(_action)

        actionName = 'Move Backward ...'
        _action = QtWidgets.QAction(actionName, self)  # self is required !!!
        _action.setDisabled(selectedItem is None)
        _action.triggered.connect(lambda enabled, name=actionName: self._contextMenuAction(name, enabled))
        _parentMenu.addAction(_action)

        _parentMenu.addSeparator()

        # move motor to
        actionName = 'Move To Motor Position ...'
        _action = QtWidgets.QAction(actionName, self)  # self is required !!!
        _action.setDisabled(selectedItem is None)
        _action.triggered.connect(lambda enabled, name=actionName: self._contextMenuAction(name, enabled))
        _parentMenu.addAction(_action)

        action = _parentMenu.exec_(event.globalPos())
        print(action)
        
        # disable bottom toolbar, never allow hiding
        #return _parentMenu

    def _contextMenuAction(self, actionName, enabled):
        logger.info(f'actionName:{actionName} enabled:{enabled}')
        if actionName == 'Move Forward ...':
            self.getGraphicsView().changeOrder('bring to front')
        elif actionName == 'Move Backward ...':
            self.getGraphicsView().changeOrder('send to back')
        elif actionName == 'Move To Motor Position ...':
            self._moveToPosition()
        else:
            logger.warning(f'Case not taken: {actionName}')

    def _moveToPosition(self):
        """Move to position of selected item.
        """
        selectedItem = self.myGraphicsView.getSelectedItem()
        if selectedItem is None:
            return
        _pos = selectedItem.pos()
        xPos = _pos.x()
        yPos = _pos.y()
        moveToDict = {
            'filename': selectedItem.getFileName(),
            'xMotorPos': xPos,
            'yMotorPos': yPos,
        }
        self.signalMoveTo.emit(moveToDict)

        # update red square position
        self.readMotorPosition()

    @property
    def appOptions(self):
        """Get applications options.
        
        Saved and loaded to remember state.
        """
        return self.myCanvasApp.options

    def old_ignore_event(self, event):
        """
        implemented to catch window activate
        """
        if (event.type() == QtCore.QEvent.WindowActivate):
            # window was activated
            logger.info('QtCore.QEvent.WindowActivate')
            self.myCanvasApp.activateCanvas(self.filePath)  # does nothing

        # see self.closeEvent()
        #if (event.type() == QtCore.QEvent.Close):
        #    print('canvasWidget.event() QtCore.QEvent.Close')

        return super().event(event)
            
    def moveEvent(self, event):
        """Inherited method called when user moves window.
        """
        left = self.frameGeometry().left()
        top = self.frameGeometry().top()

        self.myCanvas.setWindowPosition('left', left)
        self.myCanvas.setWindowPosition('top', top)

        super().moveEvent(event)

    def resizeEvent(self, event):
        """Inherited method called when user resizes window.
        """
        width = self.width()
        height = self.height()
        logger.info(f'{width} {height}')

        self.myCanvas.setWindowPosition('width', width)
        self.myCanvas.setWindowPosition('height', height)

        super().resizeEvent(event)

    def closeEvent(self, event):
        """Inherited method called when user closes window.
        """

        # ask user if it is ok
        fileName = os.path.split(self.filePath)[1]
        fileName = os.path.splitext(fileName)[0]
        fileNameStr = f'Canvas name is "{fileName}"'

        close = canvas.interface.okCancelDialog('Do You Want To Close The Canvas?',
                                    informativeText=fileNameStr)

        if close:
            # remove
            self.myCanvasApp.closeCanvas(self.filePath)
            #
            event.accept()
        else:
            event.ignore()

    def saveCanvas(self):
        """Save canvas as one json file
        """
        if self.myCanvas is not None:
            self.myCanvas.save()

    def getCanvas(self):
        return self.myCanvas

    def getGraphicsView(self):
        return self.myGraphicsView

    def getStatusToolbar(self):
        return self.statusToolbarWidget

    def slot_selectFile(self, filename):
        """User click on canvas image will select in file list
        """
        logger.info(f'{filename}')
        self.toolbarWidget.setSelectedItem(filename)

    def openStack(self, filename:str, layer:str, channel:int=1):
        """
        open a stack from the canvas.

        Args:
            filename:
            layer:
            channel: not used
        """
        logger.info(f'{filename} layer:{layer} channel:{channel}')

        # main folder of canvas, holds raw scope data
        canvasPath = self.myCanvas._folderPath

        if layer == 'Video Layer':
            # video is generally in a 'video/' folder
            canvasPath = self.myCanvas.videoFolderPath

        alreadyOpen = False
        if filename == self.myStackList.keys():
            # bring to front
            alreadyOpen = True

        stackPath = os.path.join(canvasPath, filename)

        if alreadyOpen:
            # works for qwidget
            logger.info(f'  Re-opening viewer for stackPath:{stackPath}')
            stack = self.self.myStackList['filename']
            stack.show()
            stack.activateWindow()
            stack.raise_()
        else:
            # if I pass parent=self, all hell break loos (todo: fix this)
            # when i don't pass parent=self then closing the last stack window quits the application?

            """
            we should keep a list of open stack (and function to close them)
            on double-clikc throw loaded data (load if necc) to a viewer
            """
            logger.info(f'  Opening file (from disk) and viewer for stackPath:{stackPath}')

            loadedStackPtr = canvas.interface.stackWidget(path=stackPath)
            loadedStackPtr.show()

            self.myStackList['filename'] = loadedStackPtr

    def grabImage(self):
        """
        Grab video image from a running video thread.

        todo:
            1) grab image
            2) make header with (motor, um size, date/time)
            3) tell backend bCanvas to .newVideoStack(imageData, imageHeader)
            """

        logger.info('=== grabbing image')

        # user specified video with/height (um)
        umWidth = self.myCanvasApp.options.getOption('video', 'umWidth')
        umHeight = self.myCanvasApp.options.getOption('video', 'umHeight')

        logger.info(f'  video options umWidth:{umWidth} umHeight:{umHeight}')

        # grab single image from camera
        imageData = self.myCanvasApp.getCurentImage()
        if imageData is None:
            logger.error('  got empty imageData -->> aborting')
            return

        logger.info(f'  shape:{imageData.shape}')  # (planes, y,x)
        logger.info(f'  dtype:{imageData.dtype}')

        # reduce 3d to 2d
        if len(imageData.shape) == 2:
            pass  # ok
        elif len(imageData.shape) == 3:
            # assume last axis is r/g/b planes
            logger.info(f'  imageData has 3 planes, just using first')
            imageData = imageData[:,:,0]
        yPixels, xPixels = imageData.shape  # (y,x) swapped

        # get the current motor position
        xMotor, yMotor, zMotor = self.readMotorPosition()
        if xMotor is None or yMotor is None: # or zMotor is None:
            logger.error('  Got bad motor position')
            #return False

        if imageData.dtype == np.uint8:
            bitDepth = 8
        elif imageData.dtype == np.uint16:
            bitDepth = 16
        else:
            logger.error(f'  unknown dtype {imageData.dtype}, defaulting to 8 bit')
            bitDepth = 8
        
        # datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        now = datetime.now()
        dateStr = now.strftime('%Y-%m-%d')
        timeStr = now.strftime('%H:%M:%S.%f')
        seconds = now.timestamp()

        imageHeader = {
            'date': dateStr,
            'time': timeStr,
            'seconds': seconds,
            'xmotor': xMotor,
            'ymotor': yMotor,
            'zmotor': zMotor,
            'xpixels': xPixels,
            'ypixels': yPixels,
            'umwidth': umWidth,
            'umheight': umHeight,
            'bitdepth': bitDepth,
            'xvoxel': umWidth / xPixels,
            'yvoxel': umHeight / yPixels,
            'zvoxel': 1,
            #'unit': 'um',
        }

        # create/save/append new stack to backend canvas
        newVideoStack,newVideoDict = self.myCanvas.newVideoStack(imageData, imageHeader)

        if newVideoStack is not None:
            # append to graphics view
            # new
            self.myGraphicsView.appendFile(newVideoDict)
            # old
            # self.myGraphicsView.appendVideo(newVideoStack)
            
            # append to toolbar widget (list of files)
            # new
            self.toolbarWidget.appendFile(newVideoDict)
            # old
            #self.toolbarWidget.appendVideo(newVideoStack)

        return True

    def userEvent(self, event):
        logger.info(f'event:{event}')

        '''
        xStep = yStep = None
        if self.appOptions()['motor']['useMotor']:
            xStep, yStep = self.motorToolbarWidget.getStepSize()
        '''

        if event == 'move stage right':
            # todo: read current x/y move distance
            xStep, yStep = self.motorToolbarWidget.getStepSize()
            thePos = self.myCanvasApp.xyzMotor.move('right', xStep) # the pos is (x,y)
            self.userEvent('read motor position')
        elif event == 'move stage left':
            # todo: read current x/y move distance
            xStep, yStep = self.motorToolbarWidget.getStepSize()
            thePos = self.myCanvasApp.xyzMotor.move('left', xStep) # the pos is (x,y)
            self.userEvent('read motor position')
        elif event == 'move stage front':
            # todo: read current x/y move distance
            xStep, yStep = self.motorToolbarWidget.getStepSize()
            thePos = self.myCanvasApp.xyzMotor.move('front', yStep) # the pos is (x,y)
            self.userEvent('read motor position')
        elif event == 'move stage back':
            # todo: read current x/y move distance
            xStep, yStep = self.motorToolbarWidget.getStepSize()
            thePos = self.myCanvasApp.xyzMotor.move('back', yStep) # the pos is (x,y)
            self.userEvent('read motor position')
        elif event == 'read motor position':
            self.readMotorPosition()
        elif event == 'move motor to selected item':
            # new 20220823
            # need to figure out how to 'move to' position rather than absolute
            pass
            '''
            selectedItem = self.myGraphicsView.getSelectedItem()
            if selectedItem is not None:
                canvasStack = selectedItem.myStack
                xMotor = canvasStack.header['xMotor']
                yMotor = canvasStack.header['yMotor']
            '''

        elif event == 'Canvas Folder':
            path = self.myCanvas._folderPath
            logger.info('  opening folder on hdd:{path}')
            if sys.platform.startswith('darwin'):
                subprocess.Popen(["open", path])
            elif sys.platform.startswith('win'):
                windowsPath = os.path.abspath(path)
                os.startfile(windowsPath)
            else:
                subprocess.Popen(["xdg-open", path])

        elif event == 'Live Video':
            # toggle video on/offset
            self.myCanvasApp.toggleVideo()

        elif event == 'Grab Image':
            self.grabImage()

        elif event =='Import From Scope':
            # todo: build a list of all (.tif and folder)
            # pass this to self.myCanvas.addNEwScopeFile()
            # that will return a list of files actually added
            #
            # option 2: pass importNewScope file
            #    - a dict of log file positions
            #    - try and swap x/y of motor when we display?

            # abb southwest
            useWatchFolder = self.appOptions.getOption('Scope', 'useWatchFolder')
            if useWatchFolder:
                watchDict = self.myLogFilePositon.getPositionDict()
            else:
                watchDict = None

            # old
            # newScopeFileList = self.myCanvas.importNewScopeFiles(watchDict=watchDict)
            # new
            newScopeFileDictList = self.myCanvas.importNewScopeFiles(watchDict=watchDict)

            for newScopeFileDict in newScopeFileDictList:
                # append to view
                # old
                # self.myGraphicsView.appendScopeFile(newScopeFile)
                # new
                self.myGraphicsView.appendFile(newScopeFileDict)

                # append to file list
                # old
                # newScopeFile = newScopeFileDict['canvasStack']
                #self.toolbarWidget.appendScopeFile(newScopeFile)
                # new
                self.toolbarWidget.appendFile(newScopeFileDict)

            # if len(newScopeFileDictList) > 0:
            #     self.saveCanvas()
            #     #self.myCanvas.save()

        elif event == 'print stack info':
            selectedItem = self.myGraphicsView.getSelectedItem()
            if selectedItem is not None:
                selectedItem.myStack.print()

        elif event == 'center canvas on motor position':
            self.getGraphicsView().centerOnCrosshair()

        else:
            logger.warning(f'did not understood:{event}')

    def readMotorPosition(self):
        # update the interface
        x,y,z = self.myCanvasApp.xyzMotor.readPosition()

        # for mp285 swap x/y for diaply
        xDisplay = x
        yDisplay = y
        if self.myCanvasApp.xyzMotor.swapxy:
            tmp = xDisplay
            xDisplay = yDisplay
            yDisplay = tmp

        if xDisplay is not None:
            xDisplay = round(xDisplay,1)
        if yDisplay is not None:
            yDisplay = round(yDisplay,1)

        if xDisplay is None:
            self.motorToolbarWidget.xStagePositionLabel.setStyleSheet("color: red;")
            self.motorToolbarWidget.xStagePositionLabel.repaint()
        else:
            self.motorToolbarWidget.xStagePositionLabel.setStyleSheet("color: white;")
            self.motorToolbarWidget.xStagePositionLabel.setText(str(xDisplay))
            self.motorToolbarWidget.xStagePositionLabel.repaint()
        if yDisplay is None:
            self.motorToolbarWidget.yStagePositionLabel.setStyleSheet("color: red;")
            self.motorToolbarWidget.yStagePositionLabel.repaint()
        else:
            self.motorToolbarWidget.yStagePositionLabel.setStyleSheet("color: white;")
            self.motorToolbarWidget.yStagePositionLabel.setText(str(yDisplay))
            self.motorToolbarWidget.yStagePositionLabel.repaint()

        #self.motorToolbarWidget.setStepSize(x,y)

        # x/y coords are not updating???
        #self.motorToolbarWidget.xStagePositionLabel.update()

        # set red crosshair
        if xDisplay is not None and yDisplay is not None:
            self.myGraphicsView.myCrosshair.setMotorPosition(xDisplay, yDisplay)

        return x,y,z

    @property
    def options(self):
        return self.myCanvasApp.options

    def _buildUI(self):
        self.centralwidget = QtWidgets.QWidget()

        # v Layout for: canvas | one line feedback
        self.myQVBoxLayout = QtWidgets.QVBoxLayout(self.centralwidget)

        self.title = self.filePath
        self.setWindowTitle(self.title)

        _windowPosition = self.myCanvas.getWindowPosition() # dict
        self._left = _windowPosition['left']
        self._top = _windowPosition['top']
        self._width = _windowPosition['width']
        self._height = _windowPosition['height']
        self.setGeometry(self._left, self._top, self._width, self._height)

        self.setMinimumSize(480, 480)

        # main view to hold images
        self.myGraphicsView = myQGraphicsView(self)
        self.myGraphicsView.signalOpenStack.connect(self.openStack)
        self.myGraphicsView.signalSelectFile.connect(self.slot_selectFile)
        self.myGraphicsView.signalToggleVisible.connect(self.slot_setVisible)

        self.myQVBoxLayout.addWidget(self.myGraphicsView)

        # bottom status bar
        self.statusToolbarWidget = canvas.interface.bToolbar.myStatusToolbarWidget(parent=self)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.statusToolbarWidget)

        # here I am linking the toolbar to the graphics view
        # i can't figure out how to use QAction !!!!!!
        self.motorToolbarWidget = canvas.interface.bToolbar.myScopeToolbarWidget(parent=self)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.motorToolbarWidget)

        #useMotor = self.getOptions()['motor']['useMotor']
        if self.isNew:
            pass
        else:
            # hide when we are loading from saved canvas for analysis
            self.motorToolbarWidget.hide()

        # left toolbar to show (display options, contrast slider, file list)
        self.toolbarWidget = canvas.interface.bToolbar.myToolbarWidget(self)
        self.toolbarWidget.signalSetContrast.connect(self.slot_setContrast)
        self.toolbarWidget.signalSelectFile.connect(self.myGraphicsView.slot_selectFile)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbarWidget)

        self.setCentralWidget(self.centralwidget)

    def slot_setContrast(self, fileNameList : List[str], theMin : int, theMax :int):
        self.myCanvas.setContrast(fileNameList, theMin, theMax)

    def slot_setVisible(self, filename, doShow):
        """
        toggle checkbox in list on/off
        """
        self.myCanvas.setItemVisible(filename, doShow)
        self.toolbarWidget.setCheckedState(filename, doShow)

    def toggleMotor(self):
        isVisible = self.motorToolbarWidget.isVisible()
        logger.info(f'isVisible:{isVisible}')
        if isVisible:
            self.motorToolbarWidget.hide()
            self.myGraphicsView.myCrosshair.hide()
        else:
            self.motorToolbarWidget.show()
            self.myGraphicsView.myCrosshair.show()

    def keyPressEvent(self, event):
        logger.info('')

        modifiers = QtWidgets.QApplication.keyboardModifiers()
        isShift = modifiers == QtCore.Qt.ShiftModifier
        isControl = modifiers == QtCore.Qt.ControlModifier

        '''
        if isControl and event.key() == QtCore.Qt.Key_S:
            #event.accept(True)
            print('  ... save canvas ...')
            print('  TODO: reactivate bMenu Save by having canvas window signal app when window takes focus')
        '''

        if event.key() == QtCore.Qt.Key_M:
            self.toggleMotor()

        elif isControl and event.key() == QtCore.Qt.Key_W:
            self.close() # should trigger self.closeEvent()

globalSquare = {
    'pen': QtCore.Qt.SolidLine, # could be QtCore.Qt.DotLine
    'penColor': QtCore.Qt.blue,
    'penWidth': 4,
}
globalSelectionSquare = {
    'pen': QtCore.Qt.SolidLine, # could be QtCore.Qt.DotLine
    'penColor': QtCore.Qt.yellow,
    'penWidth': 7,
}

class myQGraphicsView(QtWidgets.QGraphicsView):
    """
    Main canvas widget to visually display (video, scope) files.
    """

    signalOpenStack = QtCore.pyqtSignal(str, str)  # fileName, layer
    signalSelectFile = QtCore.pyqtSignal(str)  # fileName
    signalToggleVisible = QtCore.pyqtSignal(str, bool)  # filename, doShow

    def __init__(self, myCanvasWidget):
        super().__init__(myCanvasWidget)

        self.myCanvasWidget = myCanvasWidget

        self.myMouse_x = None
        self.myMouse_y = None

        # this works, without, we default to theme
        #self.setBackgroundBrush(QtCore.Qt.darkGray)

        myScene = QtWidgets.QGraphicsScene(self)
        self.setScene(myScene)

        # allow context menu to bubble up to parent
        #self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu);
        #self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu);

        # visually turn off scroll bars
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # these work
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

        #numItems = 0 # used to stack items with item.setZValue()

        # new
        for _file, fileDict in self.myCanvasWidget.getCanvas().getFileDictList().items():
            self.appendFile(fileDict)

        # a cross hair and rectangle (size of zoom)
        #useMotor = self.myCanvasWidget.appOptions()['motor']['useMotor']
        #if useMotor:
        self.myCrosshair = myCrosshairRectItem(self)
        self.myCrosshair.setZValue(10000)
        # 20220806 was this
        #self.scene().addItem(self.myCrosshair)
        
        # read initial position (might cause problems)
        # does not work, not all objects are initialized
        #print('myQGraphicsView.__init__ is asking myCanvasWidget to read initial motor position')
        #self.myCanvasWidget.userEvent('read motor position')
        
        if self.myCanvasWidget.isNew:
            pass
            #self.scene().addItem(self.myCrosshair)
        else:
            pass
            #self.myCrosshair.hide()

        # force update 20220806
        self.scene().update()

    def slot_selectFile(self, filename, doZoom):
        """Respond to file selection.
        
        Usually from file list in tree widget toolbar
        """
        logger.info(f'{filename} doZoom:{doZoom}')

        # clear selected
        #self.scene().clearSelection()

        # visually select image in canvas with yellow square
        self.setSelectedItem(filename)

        # zoom
        if doZoom:
            self.zoomSelectedItem(filename)

        self.scene().update()

    def setContrast_Item(self, item, theMin, theMax):
        """Set contrast of one item.

        Will always be 8-bit
        """
        logger.info(f'')
        
        itemStack = item.myStack
        #itemLayer = item.myLayer

        umWidth = itemStack.getHeaderVal('umWidth')
        umHeight = itemStack.getHeaderVal('umHeight')

        # each scope stack needs to know if it is
        # diplaying a real stack OR just a max project
        if item.myLayer == 'Video Layer':
            useMaxProject = False
        elif item.myLayer == '2P Max Layer':
            # todo: change this in future
            useMaxProject = True

        itemStack = itemStack.old_getImage_ContrastEnhanced(theMin, theMax,
                                        useMaxProject=useMaxProject)

        imageStackHeight, imageStackWidth = itemStack.shape  # (y,x)

        myQImage = QtGui.QImage(itemStack, imageStackWidth, imageStackHeight,
                                QtGui.QImage.Format_Indexed8)
        # myQImage = QtGui.QImage(itemStack, umWidth, umHeight,
        #                         QtGui.QImage.Format_Indexed8)

        #
        # try and set color
        if item.myLayer == '2P Max Layer':
            colors=[]
            for i in range(256):
                colors.append(QtGui.qRgb(i/4,i,i/2))  # green
            myQImage.setColorTable(colors)

        logger.info(f'  imageStackWidth:{imageStackWidth} imageStackHeight:{imageStackHeight}')
        logger.info(f'  scaling to umWidth:{umWidth} umHeight:{umHeight}')

        pixmap = QtGui.QPixmap(myQImage)
        pixmap = pixmap.scaled(umWidth, umHeight,
                        aspectRatioMode=QtCore.Qt.KeepAspectRatio,
                        transformMode=QtCore.Qt.SmoothTransformation,
                        )

        item.setPixmap(pixmap)

    def setCrosshairVisible(self, visible):
        if visible:
            self.scene().addItem(self.myCrosshair)
        else:
            self.scene().removeItem(self.myCrosshair)

    def centerOnCrosshair(self):
        logger.info('')

        # trying to zoom to full view
        borderMult = 1.1

        bounds = self.scene().itemsBoundingRect()

        bounds.setWidth(bounds.width() * borderMult)
        bounds.setHeight(bounds.height() * borderMult)

        #self.ensureVisible ( bounds )
        self.fitInView( bounds, QtCore.Qt.KeepAspectRatio )

        #self.myGraphicsView.myCrosshair.setMotorPosition(xDisplay, yDisplay)

    def zoomSelectedItem(self, fileName):
        #logger.info(f'fileName:{fileName}')
        zoomThisItem = None
        for item in self.scene().items():
            if item._fileName == fileName:
                zoomThisItem = item
        if zoomThisItem is not None:
            '''
            bounds = item.boundingRect() # local to item
            print('  1 type(bounds):', bounds)
            bounds = item.mapToScene(bounds)
            print('  2 type(bounds):', bounds)
            '''
            logger.info(f'{zoomThisItem._fileName}')
            self.fitInView(zoomThisItem, QtCore.Qt.KeepAspectRatio )

    def old_appendScopeFile(self, newScopeFile):
        """
        """

        # what about
        # pixMapItem.setZValue(numItems)

        # todo: on olympus the header will not have x/y motor, we need to look up in our watched folderPath
        # THESE ARE FUCKING STRINGS !!!!!!!!!!!!!!!!!!!!
        path = newScopeFile.path
        fileName = newScopeFile.getFileName()
        xMotor = newScopeFile.header['xMotor']
        yMotor = newScopeFile.header['yMotor']

        # abb 20200912, baltimore
        # IMPORTANT: If we do not know (umwidth, umHeight) WE CANNOT place iimage in canvas !!!
        umWidth = newScopeFile.header['umWidth']
        umHeight = newScopeFile.header['umHeight']
        #

        '''
        print('\n')
        print('canvasWidget.appendScopeFile() path:', path)
        print('  umWidth:', umWidth, 'umHeight:', umHeight)
        print('\n')
        '''

        if xMotor == 'None':
            xMotor = None
        if yMotor == 'None':
            yMotor = None

        #if xMotor is None or yMotor is None:
        #    print('canvasWidget.myQGraphicsView() not inserting scopeFile -->> xMotor or yMotor is None ???')
        #    #continue

        # stackMax can be None
        maxProjectChannel = self.myCanvasWidget.options.getOption('Canvas', 'maxProjectChannel')
        stackMax = newScopeFile.getMax(channel=maxProjectChannel) # stackMax can be None
        if stackMax is None:
            # print('\n\n')
            # print('  myQGraphicsView.appendScopeFile() got stackMax None. path:', path)
            
            imageStackHeight = newScopeFile.header['xPixels']
            imageStackWidth = newScopeFile.header['yPixels']
            
            logger.warning(f'NO MAX, using header imageStackWidth {imageStackWidth} imageStackHeight {imageStackHeight}')
        else:
            imageStackHeight, imageStackWidth = stackMax.shape

        logger.info(f'{path}')
        print('  xMotor:', xMotor, 'yMotor:', yMotor)
        print('  umWidth:', umWidth, 'umHeight:', umHeight)
        print('  imageStackHeight:', imageStackHeight, 'imageStackWidth:', imageStackWidth)

        if stackMax is None:
            logger.warning(f'  No stack max, making zero max image for newScopeFile:{newScopeFile}')
            stackMax = np.zeros((imageStackWidth, imageStackHeight), dtype=np.uint8)
            stackMax_8Bit = stackMax
        else:
            # always map to 8-bit (should work for 8/14/16, etc)
            # numpy 'ptp' is peak to peak (max - min)
            stackMax_8Bit = ((stackMax - stackMax.min()) / (stackMax.ptp() / 255.0)).astype(np.uint8) # map the data range to 0 - 255

        myQImage = QtGui.QImage(stackMax_8Bit, imageStackWidth, imageStackHeight, QtGui.QImage.Format_Indexed8)

        #
        # try and set color
        colors=[]
        for i in range(256): colors.append(QtGui.qRgb(i/4,i,i/2))
        myQImage.setColorTable(colors)

        pixmap = QtGui.QPixmap(myQImage)
        pixmap = pixmap.scaled(umWidth, umHeight, QtCore.Qt.KeepAspectRatio)

        # insert
        #pixMapItem = myQGraphicsPixmapItem(fileName, idx, '2P Max Layer', self, parent=pixmap)
        pixMapItem = myQGraphicsPixmapItem(fileName, '2P Max Layer', newScopeFile, pixMap=pixmap)
        pixMapItem.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        pixMapItem.setToolTip(fileName)
        pixMapItem.setPos(xMotor,yMotor)
        #todo: this is important, self.myScene needs to keep all video BELOW 2p images!!!

        #pixMapItem.setZValue(200)
        numItems = len(self.scene().items())
        pixMapItem.setZValue(1000 + numItems) # do i use this???

        # this also effects bounding rect
        #pixMapItem.setOpacity(0.0) # 0.0 transparent 1.0 opaque

        pixMapItem.setShapeMode(QtWidgets.QGraphicsPixmapItem.BoundingRectShape)
        #print('appendScopeFile() setting pixMapItem.shapeMode():', pixMapItem.shapeMode())

        # add to scene
        self.scene().addItem(pixMapItem)

        #numItems += 1

    # new
    def appendFile(self, fileDict : dict):
        """Append a new file/stack to xxx.
        
        Args:
            fileDict: Dictionary from canvas.bCanvas._defaultFileDict
        """

        # for scanning files
        maxProjectChannel = self.myCanvasWidget.options.getOption('Canvas', 'maxProjectChannel')

        # print('tttt APPEND FILE:')
        # pprint(fileDict)
        
        stackType = fileDict['stackType']  # (scanning, video)
        canvasStack = fileDict['canvasStack']  # stack to insert

        path = canvasStack.path
        fileName = canvasStack.getFileName()

        xMotor = fileDict['xmotor']  # core stack header key -->> lowercase
        yMotor = fileDict['ymotor']
        umWidth = fileDict['umwidth']
        umHeight = fileDict['umheight']

        if xMotor is None or yMotor is None:
            logger.error('got bad xMotor/yMotor')
            logger.error('      -->> ABORTING')
            return
        if umWidth is None or umHeight is None:
            logger.error('got bad umWidth/umHeight')
            logger.error('      -->> ABORTING')
            return

        xMotor = float(xMotor)
        yMotor = float(yMotor)

        _numItems = len(self.scene().items())

        # for video, get actual image from stack
        if stackType == 'video':
            _theLayer = 'Video Layer'
            _zValue = 500 + _numItems
            _videoChannel = 1
            oneImage = canvasStack.getStack(_videoChannel) # ndarray
            imageStackHeight, imageStackWidth = oneImage.shape


        elif stackType == 'scanning':
            _theLayer = '2P Max Layer'
            _zValue = 1000 + _numItems
            # for scanning, get stack max project
            stackMax = canvasStack.getMax(channel=maxProjectChannel) # stackMax can be None
            if stackMax is None:
                imageStackHeight = canvasStack.header['xPixels']
                imageStackWidth = canvasStack.header['yPixels']
                logger.warning(f'NO MAX, using header imageStackWidth {imageStackWidth} imageStackHeight {imageStackHeight}')
            else:
                imageStackHeight, imageStackWidth = stackMax.shape

            if stackMax is None:
                logger.warning(f'  No stack max, making zero max image for newScopeFile:{fileName}')
                stackMax = np.zeros((imageStackWidth, imageStackHeight), dtype=np.uint8)
                oneImage = stackMax
            else:
                # always map to 8-bit (should work for 8/14/16, etc)
                # numpy 'ptp' is peak to peak (max - min)
                oneImage = ((stackMax - stackMax.min()) / (stackMax.ptp() / 255.0)).astype(np.uint8) # map the data range to 0 - 255

        logger.info(f'{path}')
        logger.info(f'  xMotor:{xMotor} yMotor:{yMotor}')
        logger.info(f'  umWidth:{umWidth} umHeight:{umHeight}')
        logger.info(f'  pixelHeight:{imageStackHeight} pixelWidth:{imageStackWidth}')
        logger.info(f'  oneImage:{oneImage.shape} min:{np.min(oneImage)} max:{np.max(oneImage)}')

        #myQImage = QtGui.QImage(oneImage, imageStackWidth, imageStackHeight, QtGui.QImage.Format_Indexed8)
        myQImage = QtGui.QImage(oneImage, umWidth, umHeight, QtGui.QImage.Format_Indexed8)

        if stackType == 'scanning':
            # try and set color
            colors=[]
            for i in range(256): colors.append(QtGui.qRgb(i/4,i,i/2))
            myQImage.setColorTable(colors)

        pixmap = QtGui.QPixmap(myQImage)
        # old
        # pixmap = pixmap.scaled(umWidth, umHeight, QtCore.Qt.KeepAspectRatio)

        # insert
        #pixMapItem = myQGraphicsPixmapItem(fileName, idx, 'Video Layer', self, parent=pixmap)
        pixMapItem = myQGraphicsPixmapItem(fileName, _theLayer, canvasStack, pixMap=pixmap)
        pixMapItem.setPos(xMotor,yMotor)
        #pixMapItem.setSize(umWidth,umHeight)

        #This is important, self.myScene needs to keep all video BELOW 2p images!!!
        pixMapItem.setZValue(_zValue) # do i use this???

        # add to scene
        self.scene().addItem(pixMapItem)

        # TODO: put this into myQGraphicsPixmapItem.__init__()
        self.setContrast_Item(pixMapItem, 0, 255)  # always 8-bit

    # todo: put this in __init__() as a function
    def old_appendVideo(self, newVideoStack):
        # what about
        # pixMapItem.setZValue(numItems)

        path = newVideoStack.path
        fileName = newVideoStack.getFileName()

        xMotor = newVideoStack.getHeaderVal2('xMotor')
        yMotor = newVideoStack.getHeaderVal2('yMotor')
        umWidth = newVideoStack.getHeaderVal2('umWidth')
        umHeight = newVideoStack.getHeaderVal2('umHeight')

        if xMotor is None or yMotor is None:
            logger.error('got bad xMotor/yMotor')
            logger.error('      -->> ABORTING')
            return
        if umWidth is None or umHeight is None:
            logger.error('got bad umWidth/umHeight')
            logger.error('      -->> ABORTING')
            return

        xMotor = float(xMotor)
        yMotor = float(yMotor)

        channel = 1
        videoImage = newVideoStack.getStack(channel) # ndarray
        imageStackHeight, imageStackWidth = videoImage.shape

        logger.info(f'{path}')
        logger.info(f'  xMotor:{xMotor} yMotor:{yMotor}')
        logger.info(f'  umWidth:{umWidth} umHeight:{umHeight}')
        print(f'  pixelHeight:{imageStackHeight} pixelWidth:{imageStackWidth}')

        myQImage = QtGui.QImage(videoImage, imageStackWidth, imageStackHeight, QtGui.QImage.Format_Indexed8)
        #myQImage = QtGui.QImage(videoImage, imageStackWidth, imageStackHeight, QtGui.QImage.Format_RGB32)

        pixmap = QtGui.QPixmap(myQImage)
        pixmap = pixmap.scaled(umWidth, umHeight, QtCore.Qt.KeepAspectRatio)

        # insert
        #pixMapItem = myQGraphicsPixmapItem(fileName, idx, 'Video Layer', self, parent=pixmap)
        pixMapItem = myQGraphicsPixmapItem(fileName, 'Video Layer', newVideoStack, pixmap=pixmap)
        pixMapItem.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        pixMapItem.setToolTip(fileName)
        pixMapItem.setPos(xMotor,yMotor)
        #todo: this is important, self.myScene needs to keep all video BELOW 2p images!!!
        #tmpNumItems = 100
        numItems = len(self.scene().items())
        pixMapItem.setZValue(500 + numItems) # do i use this???

        # add to scene
        self.scene().addItem(pixMapItem)

    def getSelectionFromContext(self, adjustThisLayer : str):
        """Return alist of items based on user selected context (selected, video, 2p).
        
        Each item is type 'canvas.interface.canvasWidget.myQGraphicsPixmapItem'

        Args:
            adjustThisLayer: in ('', '')
        """
        _itemList = []
        
        selectedItem = self.getSelectedItem()

        if adjustThisLayer == 'selected' and selectedItem is not None:
            _itemList.append(selectedItem)
        else:
            for item in self.scene().items():
                if item.myLayer == adjustThisLayer:
                    _itemList.append(item)
        #
        return _itemList

    def getSelectedItem(self):
        """
        Get the currently selected item, return None if no selection
        """
        selectedItems = self.scene().selectedItems()
        if len(selectedItems) > 0:
            return selectedItems[0]
        else:
            return None

    def setSelectedItem(self, fileName):
        """
        Select the item by file name.

        This is usually coming from toolbar file list selection
        """
        logger.info(f'fileName:{fileName}')
        selectThisItem = None
        for item in self.scene().items():
            isSelectable = item.flags() & QtWidgets.QGraphicsItem.ItemIsSelectable
            #item.setSelected(False) # as we iterate, make sure we turn off all selection
            if isSelectable and item._fileName == fileName:
                selectThisItem = item
                break

        if selectThisItem is None:
            logger.info('  selected None')
        else:
            logger.info(f'  selectThisItem:{selectThisItem._fileName}')

        # _sceneRect = self.sceneRect()
        # logger.info(f'  _sceneRect:{_sceneRect}')

        # clear selected
        self.scene().clearSelection()

        #self.scene().setFocusItem(selectThisItem)
        selectThisItem.setSelected(True)

        self.scene().update()

    def hideShowItem(self, fileName, doShow):
        """
        Hide/Show individual items

        todo: if a layer is off then do not hide/show, better yet,
        when layer is off, disable checkboxes in myToolbarWidget
        """
        for item in self.scene().items():
            if item._fileName == fileName:
                # todo: need to ask the self.myCanvas if the layer is on !!!

                #item.setVisible(doShow)
                
                if item.myLayer=='Video Layer':
                    item.setOpacity(1.0 if doShow else 0)
                    item.setVisible(doShow)
                else:
                    item.setOpacity(1.0 if doShow else 0.01)

                # keep track of this for each item so we can keep checked items in myToolbarWidget in sync
                #when user presses checkboxes to toggle layers on/off
                item._isVisible = doShow

    def hideShowLayer(self, thisLayer, isVisible):
        """
        if hide/show thisLayer is '2p max layer' then set opacity of '2p max layer'

        layers:
            Video Layer
            Video Squares Layer
            2P Max Layer
            2P Squares Layer

        """
        logger.info(f'thisLayer:{thisLayer} isVisible:{isVisible}')

        doVideoSquares = False
        if thisLayer == 'Video Squares Layer':
            thisLayer = 'Video Layer'
            doVideoSquares= True

        doTwoPhotonSquares = False
        if thisLayer == '2P Squares Layer':
            thisLayer = '2P Max Layer'
            doTwoPhotonSquares= True

        for item in self.scene().items():
            #print(item._fileName, item.myLayer)
            if item.myLayer == thisLayer:
                # don't show items in this layer that are not visible
                # not visible are files that are checked off in myToolbarWidget
                if isVisible and not item._isVisible:
                    continue
                if thisLayer=='Video Layer':
                    # turn off both image and outline
                    if doVideoSquares:
                        item._drawSquare = isVisible
                    else:
                        item.setOpacity(1.0 if isVisible else 0.01)
                elif thisLayer == '2P Max Layer':
                    # allow show/hide of both (max, square)
                    if doTwoPhotonSquares:
                        item._drawSquare = isVisible
                    else:
                        item.setOpacity(1.0 if isVisible else 0.01)
            else:
                pass
        #
        self.scene().update()

    def mouseDoubleClickEvent(self, event):
        """
        open a stack on a double-click
        """
        selectedItems = self.scene().selectedItems()
        if len(selectedItems) > 0:
            selectedItem = selectedItems[0]
            fileName = selectedItem._fileName
            layer = selectedItem.myLayer

            logger.info(f'fileName:{fileName} layer:{layer}')

            #self.myCanvasWidget.openStack(fileName, layer)
            self.signalOpenStack.emit(fileName, layer)
        else:
            logger.info('No selected items')

    '''
    def mousePressEvent(self, event):
        print('=== myQGraphicsView.mousePressEvent() x:', event.x(), 'y:', event.y())
        scenePoint = self.mapToScene(event.x(), event.y())
        #print('=== myQGraphicsView.mousePressEvent() scene_x:', scenePoint.x(), 'scene_y:', scenePoint.y())
        super().mousePressEvent(event)
        #event.setAccepted(False)
    '''

    '''
    def mousePressEvent(self, event):
        logger.info('')
        super().mousePressEvent(event)

        scenePoint = self.mapToScene(event.x(), event.y())
        #print(type(scenePoint))
        painterPath = QtGui.QPainterPath(scenePoint)
        self.scene().setSelectionArea(painterPath, QtGui.QTransform())
    '''

    def mouseMoveEvent(self, event):
        """Emit signal of mouse position.
        """
        super().mouseMoveEvent(event)

        scenePoint = self.mapToScene(event.x(), event.y())

        item = self.scene().itemAt(scenePoint, QtGui.QTransform())
        if item is not None:
            filename = item._fileName
        else:
            filename = ''

        self.myCanvasWidget.getStatusToolbar().setMousePosition(scenePoint, filename=filename)

        # keep track of mouse position so we zoom to/from mouse
        self.myMouse_x = event.x() #scenePoint.x()
        self.myMouse_y = event.y() #scenePoint.y()

        #self.scene().update()

    def mousePressEvent(self, event):
        """Respond to user mouse press in graphics view.
        
        We are selecting the item in BOTH mouse press and release.
        Mouse release is REQUIRED as the PyQt backend cancels selections.
        """
        
        super().mousePressEvent(event)

        scenePoint = self.mapToScene(event.x(), event.y())
        item = self.scene().itemAt(scenePoint, QtGui.QTransform())

        # clear selected
        self.scene().clearSelection()

        filename = ''
        if item is not None:
            filename = item._fileName
            logger.info(f'selecting file:{filename}')
            item.setSelected(True)
        
        self.signalSelectFile.emit(filename)  # filename can be ('', None)

        self.scene().update()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        scenePoint = self.mapToScene(event.x(), event.y())
        item = self.scene().itemAt(scenePoint, QtGui.QTransform())

        # clear selected
        self.scene().clearSelection()

        if item is not None:
            logger.info(f'selecting file:{item._fileName}')
            item.setSelected(True)
            self.signalSelectFile.emit(item._fileName)
        # else:
        #     self.scene().clearSelection()

        self.scene().update()

    '''
    def mousePressEvent(self, event):
        print('=== myQGraphicsView.mousePressEvent()')
        print('   ', event.pos())
        xyPos = event.pos()
        item = self.itemAt(xyPos)
        print('   mouse selected item:', item)

        #super(QtWidgets.QGraphicsView, self).mousePressEvent(event)
        super().mousePressEvent(event)
    '''

    # I want to drag the scene around when click+drag on an image ?????
    # see:
    # https://stackoverflow.com/questions/55007339/allow-qgraphicsview-to-move-outside-scene
    '''
    def mouseMoveEvent(self, event):
        print('=== myQGraphicsView.mouseMoveEvent()')
        print('   ', event.pos())
        super().mouseMoveEvent(event)

        #self.scene.mouseMoveEvent(event) # this is an error because scene is wrong class???

        # C++ code
        # scene()->update(mapToScene(rect()).boundingRect());
        #
        # this almost works !!!!
        print('   self.rect():', self.rect())
        self.scene().update(self.mapToScene(self.rect()).boundingRect());

        #self.scene().mouseMoveEvent(event) # this is an error because scene is wrong class???
    '''

    def zoom(self, inout):
        logger.info(f'inout:{inout}')
        oldPos = QtCore.QPoint(self.myMouse_x, self.myMouse_y) #
        oldPos = self.mapToScene(oldPos)

        if inout=='in':
            scale = 1.25
        else:
            scale = 1/1.25

        self.scale(scale,scale)

        newPos = QtCore.QPoint(self.myMouse_x, self.myMouse_y)
        newPos = self.mapToScene(newPos)
        delta = newPos - oldPos
        self.translate(delta.y(), delta.x())

    def wheelEvent(self, event):
        """Zoom canvas in response to mouse wheel or track pad on laptop.
        """
        #logger.info('')
        
        wheelZoom = self.myCanvasWidget.options.getOption('Canvas', 'wheelZoom')

        oldPos = self.mapToScene(event.pos())
        if event.angleDelta().y() > 0:
            #self.zoom('in')
            scale = 1 * wheelZoom
        elif event.angleDelta().y() < 0:
            #self.zoom('out')
            scale = 1 / wheelZoom
        else:
            return
        self.scale(scale,scale)
        newPos = self.mapToScene(event.pos())
        delta = newPos - oldPos

        self.translate(delta.y(), delta.x())

    def old_pan(self, direction):
        # TODO: put stepSize in options file
        stepSize = 500.0
        xOffset = 0.0
        yOffset = 0.0
        if direction == 'left':
            xOffset = stepSize
        elif direction == 'right':
            xOffset = -stepSize
        elif direction == 'up':
            yOffset = stepSize
        elif direction == 'down':
            yOffset = -stepSize

        logger.info(f'xOffset:{xOffset} yOffset:{yOffset}')

        self.translate(xOffset,yOffset)

    def keyPressEvent(self, event):
        #print('\n=== myQGraphicsView.keyPressEvent()', event.text())

        # pan is handled by super
        '''
        if event.key() == QtCore.Qt.Key_Left:
            self._getBoundingRect()
            self.pan('left')
        if event.key() == QtCore.Qt.Key_Right:
            self.pan('right')
        if event.key() == QtCore.Qt.Key_Up:
            self.pan('up')
        if event.key() == QtCore.Qt.Key_Down:
            self.pan('down')
        '''

        # zoom
        if event.key() in [QtCore.Qt.Key_Plus, QtCore.Qt.Key_Equal]:
            self.zoom('in')
        elif event.key() == QtCore.Qt.Key_Minus:
            self.zoom('out')

        elif event.key() == QtCore.Qt.Key_F:
            #print('f for bring to front')
            self.changeOrder('bring to front')
        elif event.key() == QtCore.Qt.Key_B:
            #print('b for send to back')
            self.changeOrder('send to back')

        elif event.key() == QtCore.Qt.Key_H:
            # 'h' for show/hide
            selectedItem = self.getSelectedItem()
            if selectedItem is not None:
                filename = selectedItem._fileName
                doShow = False # if we get here, the item is visible, thus, doShow is always False
                self.hideShowItem(filename, doShow)
                # tell the toolbar widget to turn off checkbow
                #todo: this is a prime example of figuring out signal/slot
                #self.myCanvasWidget.toggleVisibleCheck(filename, doShow)
                self.signalToggleVisible.emit(filename, doShow)
                #setCheckedState(fileName, doSHow)
        elif event.key() == QtCore.Qt.Key_I:
            # 'i' is for info
            logger.warning('=== TODO add signal')
            self.myCanvasWidget.userEvent('print stack info')

        elif event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            # (Enter, Return) to set scene to show all items
            self.centerOnCrosshair()

        elif event.key() == QtCore.Qt.Key_M:
            # move motor to selected item
            self.myCanvasWidget.userEvent('move motor to selected item')

        else:
            super(myQGraphicsView, self).keyPressEvent(event)

    def _getBoundingRect(self):
        leftMin = float('Inf')
        topMin = float('Inf')

        logger.info(f'DOES NOTHING {self.scene().sceneRect()}')

        '''
        for idx, item in enumerate(self.scene().items()):
            print(idx, item.sceneRect)
        '''

    def changeOrder(self, this):
        """
        this can be:
            'bring to front': Will bring the selected item BEFORE its previous item
            'send to back': Will put the selected item AFTER its next item

            This does not bring entirely to front or entirely to back???
        """
        logger.info(f'this:{this}')
        if this == 'bring to front':
            selectedItems = self.scene().selectedItems()
            if len(selectedItems) > 0:
                logger.info(f'  bring item to front:{selectedItems}')
                selectedItem = selectedItems[0]
                selectedItem.bringForward()
            else:
                logger.info('  did not find a selected item???')
        elif this == 'send to back':
            selectedItems = self.scene().selectedItems()
            if len(selectedItems) > 0:
                logger.info(f'  send item to back:{selectedItems}')
                selectedItem = selectedItems[0]
                selectedItem.sendBackward()
            else:
                logger.info('  did not find a selected item???')

class myQGraphicsPixmapItem(QtWidgets.QGraphicsPixmapItem):
    """
    To display images in canvas

    Each item is added to a scene (QGraphicsScene)
    """
    #def __init__(self, fileName, index, myLayer, myQGraphicsView, parent=None):
    def __init__(self, fileName, myLayer, theStack, pixMap=None):
        """
        theStack: the underlying bStack, assuming it has at least its header loaded ???
        """
        super().__init__(pixMap)

        # NoButton break left-mouse click selection
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setToolTip(fileName)

        self._fileName = fileName
        self.myLayer = myLayer
        self.myStack = theStack # underlying bStack

        self._isVisible = True
        self._drawSquare = True

        _transform = QtCore.Qt.SmoothTransformation
        self.setTransformationMode(_transform)

        #self.installEventFilter(self)

    def old_sceneEvent(self, event):
        logger.info(event)
        
        # Returns true if the event was recognized and handled; otherwise, (e.g., if the event type was not recognized,) false is returned.
        #if isinstance(event, QtWidgets.QGraphicsSceneMouseEvent):
        #    #self.scene().event(event)
        
        return False

    def getFileName(self):
        return self._fileName
    
    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        #self.drawMyRect(painter)

        _isSelected = self.isSelected()        
        #logger.info(f'_fileName:{self._fileName}, _isSelected:{_isSelected}')

        if _isSelected:
            self.drawFocusRect(painter)
        else:
            self.drawMyRect(painter)

    def drawMyRect(self, painter):
        #print('myQGraphicsPixmapItem.drawFocusRect() self.boundingRect():', self.boundingRect())
        if not self._drawSquare:
            return

        self.focusbrush = QtGui.QBrush()

        self.focuspen = QtGui.QPen(globalSquare['pen'])
        self.focuspen.setColor(globalSquare['penColor'])
        self.focuspen.setWidthF(globalSquare['penWidth'])
        #
        painter.setBrush(self.focusbrush)
        painter.setPen(self.focuspen)

        painter.setOpacity(1.0)

        #painter.drawRect(self.focusrect)
        # ???
        painter.drawRect(self.boundingRect())

    def drawFocusRect(self, painter):
        #print('myQGraphicsPixmapItem.drawFocusRect()')
        self.focusbrush = QtGui.QBrush()
        self.focuspen = QtGui.QPen(globalSelectionSquare['pen'])
        self.focuspen.setColor(globalSelectionSquare['penColor'])
        self.focuspen.setWidthF(globalSelectionSquare['penWidth'])

        painter.setBrush(self.focusbrush)
        painter.setPen(self.focuspen)

        painter.setOpacity(1.0)

        painter.drawRect(self.boundingRect())

    '''
    def mousePressEvent(self, event):
        """
        needed for mouse click+drag
        """
        #print('   myQGraphicsPixmapItem.mousePressEvent()')
        super().mousePressEvent(event)
        #self.scene().mousePressEvent(event)
        #event.setAccepted(False)
    '''

    '''
    def mouseMoveEvent(self, event):
        """
        needed for mouse click+drag
        """
        logger.info('')
        super().mouseMoveEvent(event)
        return
        
        self.scene().mouseMoveEvent(event)
        #event.setAccepted(False)
        #return False
    '''

    def old_mouseReleaseEvent(self, event):
        """
        needed for mouse click+drag
        """
        logger.info('')
        super().mouseReleaseEvent(event)
        #self.scene().mouseReleaseEvent(event)
        #event.setAccepted(False)

    def bringForward(self):
        """
        move this item before its previous sibling

        todo: don't ever move video in front of 2p!
        """
        #print('myQGraphicsPixmapItem.myQGraphicsPixmapItem.bringForward()')
        logger.info('')
        myScene = self.scene()
        previousItem = None

        # debug, list all items
        # for idx, item in enumerate(self.scene().items(QtCore.Qt.DescendingOrder)):
        #     print(idx, item._fileName, item.zValue())

        for item in self.scene().items(QtCore.Qt.DescendingOrder):
            if item == self:
                break
            previousItem = item

        if previousItem is not None:
            logger.info(f'  moving {self._fileName} before previousItem:{previousItem._fileName}')
            # this does not work !!!!
            #self.stackBefore(previousItem)
            previous_zvalue = previousItem.zValue()
            this_zvalue = self.zValue()
            logger.info(f'  previous_zvalue:{previous_zvalue} this_zvalue:{this_zvalue}')
            previousItem.setZValue(this_zvalue)
            self.setZValue(previous_zvalue)
            #self.stackBefore(previousItem)
            #
            self.update()
        else:
            logger.info('   item is already front most')

    def sendBackward(self):
        """
        move this item after its next sibling

        todo: don't every move 2p behind video
        """
        #print('myQGraphicsPixmapItem.myQGraphicsPixmapItem.sendBackward()')
        logger.info('')
        myScene = self.scene()
        nextItem = None
        for item in self.scene().items(QtCore.Qt.AscendingOrder):
            if item == self:
                break
            nextItem = item
        if nextItem is not None:
            logger.info(f'  moving {self._fileName} after nextItem:{nextItem._fileName}')
            # this does not work !!!!
            #self.stackBefore(previousItem)
            next_zvalue = nextItem.zValue()
            this_zvalue = self.zValue()
            nextItem.setZValue(this_zvalue)
            self.setZValue(next_zvalue)
            self.update()
        else:
            logger.info('  item is already front most')

# this was supposed to be an 'x' in the middle of the dotted red square
'''
class myCrosshair(QtWidgets.QGraphicsTextItem):
    def __init__(self, parent=None):
        super(myCrosshair, self).__init__(parent)
        self.fontSize = 50
        self._fileName = ''
        self.myLayer = 'crosshair'
        theFont = QtGui.QFont("Times", self.fontSize, QtGui.QFont.Bold)
        self.setFont(theFont)
        self.setPlainText('XXX')
        self.setDefaultTextColor(QtCore.Qt.red)
        self.document().setDocumentMargin(0)
        # hide until self.setMotorPosition
        self.hide()

    def setMotorPosition(self, x, y):
        if x is None or y is None:
            self.hide()
            print('myCrosshair.setMotorPosition() hid crosshair')
            return

        self.show()

        # offset so it is centered
        x = x
        y = y - self.fontSize/2

        print('myCrosshair.setMotorPosition() x:', x, 'y:', y)

        # 20200912, was this
        #newPnt = self.mapToScene(x, y)

        # 20200912, was this
        #print('  self.setPos() newPnt:', newPnt)

        # 20200912, was this
        #self.setPos(newPnt)

        # 20200912, NOW this
        self.setPos(x, y)
'''

class myCrosshairRectItem(QtWidgets.QGraphicsRectItem):
    """
    To display rectangles in canvas.
    Used for 2p images so we can show/hide max project and still see square
    """
    def __init__(self, myQGraphicsView=None):
        super().__init__()

        self.myQGraphicsView = myQGraphicsView
        
        # todo: add as option
        self._penSize = 10

        self._xPos = None  # motor position
        self._yPos = None
        self.width = None  #693.0
        self.height = None  #433.0

        # NoButton break left-mouse click selection
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)

        #myRect = QtCore.QRectF(self.xPos, self.yPos, self.width, self.height)
        # I really do not understand use of parent ???
        # was this
        #super(QtWidgets.QGraphicsRectItem, self).__init__(myRect)

        self._fileName = ''
        self.myLayer = 'crosshair'

        # tryinig to make scene() itemAt() not report *this
        #self.setEnabled(False) # should be visible but not selectable

        # abb 20200914 removed self
        #self.myCrosshair2 = None
        '''
        self.myCrosshair2 = myCrosshair()
        self.myQGraphicsView.scene().addItem(self.myCrosshair2)
        self.myCrosshair2.setZValue(10001)
        '''

    def setWidthHeight(self, width, height):
        """
        Called when user selects different 'Square Size'
        Use this to set different 2p zooms and video
        """
        logger.info(f'width:{width} height:{height}')
        self._width = width
        self._height = height
        self.setMotorPosition(xMotor=None, yMotor=None) # don't adjust position, just size

    def setMotorPosition(self, xMotor=None, yMotor=None):
        """
        update the crosshair to a new position

        also used when changing the size of the square (Video, 1x, 1.5x, etc)
        """
        #print('myCrosshairRectItem.setMotorPosition() xMotor:', xMotor, 'yMotor:', yMotor)
        if xMotor is not None and yMotor is not None:
            self._xPos = xMotor #- self.width/2
            self._yPos = yMotor #- self.height/2

        # BINGO, DO NOT USE setPos !!! Only use setRect !!!
        #self.setPos(self.xPos, self.yPos)

        if self._xPos is not None and self._yPos is not None:
            logger.info(f'{self._xPos}, {self._yPos}, {self._width}, {self._height}')
            self.setRect(self._xPos, self._yPos, self._width, self._height)

            '''
            if self.myCrosshair2 is not None:
                xCrosshair = self.xPos + (self.width/2)
                yCrosshair = self.yPos + (self.height/2)
                self.myCrosshair2.setMotorPosition(xCrosshair, yCrosshair)
            '''
        else:
            pass
            #print('setMotorPosition() did not set')

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        self.drawCrosshairRect(painter)

    def drawCrosshairRect(self, painter):
        #print('myCrosshairRectItem.drawCrosshairRect()')
        self.focusbrush = QtGui.QBrush()

        self.focuspen = QtGui.QPen(QtCore.Qt.DashLine) # SolidLine, DashLine
        self.focuspen.setColor(QtCore.Qt.red)
        self.focuspen.setWidthF(self._penSize)
        #
        painter.setBrush(self.focusbrush)
        painter.setPen(self.focuspen)

        # THIS IS NECCESSARY !!!! Otherwise the rectangle disapears !!!
        painter.setOpacity(1.0)

        if self._xPos is not None and self._yPos is not None:
            #print('  xxx drawCrosshairRect() self.boundingRect():', self.boundingRect())
            painter.drawRect(self.boundingRect())
        else:
            #print('  !!! myCrosshairRectItem.drawCrosshairRect() did not draw')
            pass
