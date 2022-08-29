# Robert Cudmore
# 20191117

import os, sys # to make menus on osx, sys.platform == 'darwin'

import webbrowser # to show help

from PyQt5 import QtCore, QtWidgets, QtGui

#import canvas.interface

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

import canvas

class bMenu:
    #def __init__(self, parentApp : canvas.interface.canvasApp):
    def __init__(self, parentApp):
        """
        parent: canvas.interface.canvasApp
        """
        self.myCanvasApp = parentApp

        if sys.platform.startswith('darwin') :
            self.myMenuBar = QtWidgets.QMenuBar() # parentless menu bar for Mac OS
        else :
            self.myMenuBar = parent.menuBar() # refer to the default one

        file = self.myMenuBar.addMenu("File")
        file.addAction('New Canvas ...', self.newCanvas, QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_N))
        file.addAction('Open Canvas ...', self.openCanvas, QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_O))

        file.addSeparator()

        file.addAction('Save Canvas', self.saveCanvas, QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_S))

        #file.addSeparator()

        file.addAction('Exit', self.quit, QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Q))

        self.myMenuBar.addMenu(file)

        # options menu
        options = self.myMenuBar.addMenu("Options")
        #options.addAction('Load Scope Config ...', self.loadScopeConfig)
        #options.addSeparator()
        #options.addAction('Load Users Config ...', self.loadUserConfig)
        #options.addSeparator()
        options.addAction('Canvas Options ...', self.showOptionsDialog)
        options.addSeparator()
        options.addAction('Load User Options ...', self.loadUserOptions)
        options.addAction('Set Data Path ...', self.setDataPath)
        options.addSeparator()
        options.addAction('Save Canvas Options ...', self.saveOption)
        options.addSeparator()
        options.addAction('Help ...', self.helpMenu)
        options.addAction('About ...', self.aboutMenu)

        self.myMenuBar.addMenu(options)

        # windows menu to show list of open canvas
        self.windowMenu = self.myMenuBar.addMenu("Window")
        self.windowMenu.aboutToShow.connect(self._buildCanvasMenu)
        self._buildCanvasMenu()

        # help

        # video
        self.videoMenu = self.myMenuBar.addMenu("Video")
        self.videoMenu.addAction('Video Window ...', self.showVideoWindow)

    def showVideoWindow(self):
        self.myCanvasApp.toggleVideo()

    def _buildCanvasMenu(self):
        """Dynamically create a 'canvas' menu from open canvas windows.
        
        TODO: canvasApp should keep a list of open canvas widgets.
            Use this to populate.
        """

        logger.info('')
        
        canvasDict = self.myCanvasApp.canvasDict
        
        self.windowMenu.clear()

        canvasList = canvasDict.keys()
        #print('bMenu.buildCanvasMenu() canvasList:', canvasList)

        # get the path to file of the front canvas window
        frontWindow = self.myCanvasApp.activeWindow()
        activeFile = ''
        if isinstance(frontWindow, canvas.interface.canvasWidget):
            activeFile = frontWindow.filePath
            activeFile = os.path.split(activeFile)[1]
            activeFile = os.path.splitext(activeFile)[0]  # no extension

        if len(canvasList) == 0:
            # one 'None' item
            item = self.windowMenu.addAction('None')
            item.setDisabled(True)
        else:
            for canvasName in canvasList:
                item = self.windowMenu.addAction(canvasName)
                item.setCheckable(True)
                if canvasName == activeFile:
                    item.setChecked(True)
                else:
                    item.setChecked(False)
                item.triggered.connect(lambda chk, item=canvasName: self._userSelectCanvas(chk, item))
                #item = windowMenu.addAction(c, lambda item=item: self.doStuff(item))
                #self.connect(entry,QtCore.SIGNAL('triggered()'), lambda item=item: self.doStuff(item))

    def _userSelectCanvas(self, checked, item):
        #print('doStuff() checked:', checked, 'item:', item)
        logger.info(f'checked:{checked} item:{item}')
        self.myCanvasApp.bringCanvasToFront(item)

    def newCanvas(self):
        logger.info('')
        self.myCanvasApp.newCanvas()

    def openCanvas(self):
        logger.info('')
        self.myCanvasApp.load(askUser=True)

    def saveCanvas(self):
        logger.info('')
        self.myCanvasApp.save()

    def quit(self):
        logger.info('')
        #self.myCanvasApp.myApp.quit()
        self.myCanvasApp.myQuit()

    def loadUserOptions(self):
        """Ask user for options file and load into canvas app.
        """
        logger.info('Load user options')
        #optionsFolder = os.path.join(canvas.canvasUtil._getBundledDir(), 'config')
        optionsFolder  = ''
        fname = QtWidgets.QFileDialog.getOpenFileName(caption='Load options file',
                            directory=optionsFolder,
                            filter="Option Files (*.json)")

    def setDataPath(self):
        """
        set ['Users']['xxx']
        """
        logger.info('')
        dirStr = QtWidgets.QFileDialog.getExistingDirectory(None)
        if len(dirStr) > 0:
            self.myCanvasApp.options.setSavePath(dirStr)

    def showOptionsDialog(self):
        logger.info('')
        # options is class canvasOptions, get underlying dict for dialog
        optionsDict = self.myCanvasApp.options.getDict()
        
        optionsDialog = canvas.interface.bOptionsDialog(self.myCanvasApp, optionsDict)
        optionsDialog.acceptOptionsSignal.connect(self.myCanvasApp.slot_UpdateOptions)

        if optionsDialog.exec_():
            #print(optionsDialog.localOptions)
            pass

    def saveOption(self):
        logger.info('')
        self.myCanvasApp.options.optionsSave()

    def aboutMenu(self):
        _aboutDialog = canvas.interface.canvasDialog.aboutDialog()

        if _aboutDialog.exec_():
            #print(optionsDialog.localOptions)
            pass

    def helpMenu(self):
        logger.info('')
        urlStr = 'https://cudmore.github.io/bImPy/canvas'
        webbrowser.open(urlStr, new=2)
