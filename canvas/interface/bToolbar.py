"""
20200912
"""

from functools import partial

from qtpy import QtCore, QtWidgets, QtGui

import canvas.canvasUtil

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

class myStatusToolbarWidget(QtWidgets.QToolBar):
    """
    A status toolbar at the bottom of the main window.
    """
    def __init__(self, parent):
        logger.info('')
        super().__init__('Status', parent)

        self.myCanvasWidget = parent

        self.setMovable(False)

        alignLeft = QtCore.Qt.AlignLeft # for HBoxLayout
        alignRight = QtCore.Qt.AlignRight # for HBoxLayout

        # myGroupBox = QtWidgets.QGroupBox()
        # myGroupBox.setTitle('')

        _tmpWidget = QtWidgets.QWidget()

        hBoxLayout = QtWidgets.QHBoxLayout()

        # not used
        '''
        self.lastActionLabel = QtWidgets.QLabel("Last Action: None")
        hBoxLayout.addWidget(self.lastActionLabel)
        '''

        xMousePosition_ = QtWidgets.QLabel("X (um)")
        #xMousePosition_.setMaximumWidth(45)
        self.xMousePosition = QtWidgets.QLabel("None")
        hBoxLayout.addWidget(xMousePosition_, alignment=alignLeft)
        hBoxLayout.addWidget(self.xMousePosition, alignment=alignLeft)

        yMousePosition_ = QtWidgets.QLabel("Y (um)")
        #yMousePosition_.setMaximumWidth(45)
        self.yMousePosition = QtWidgets.QLabel("None")
        hBoxLayout.addWidget(yMousePosition_, alignment=alignLeft)
        hBoxLayout.addWidget(self.yMousePosition, alignment=alignLeft)

        hBoxLayout.addStretch()  # need for alignment to work (QtCore.Qt.AlignLeft)

        self.myFilename = QtWidgets.QLabel("File: None")
        hBoxLayout.addWidget(self.myFilename, alignment=alignRight)


        # finish
        # myGroupBox.setLayout(hBoxLayout)
        # self.addWidget(myGroupBox)
        
        _tmpWidget.setLayout(hBoxLayout)
        self.addWidget(_tmpWidget)

    # def event(self, event):
    #     """Override inherited method so this toolbar does not show in
    #     QMainWindow context menu.
    #     """
    #     if event.type() == QtCore.QEvent.ContextMenu:
    #         logger.info('XXXXXXXXxxxxxx')
    #         return True
    #     return super().event(event)

    def setMousePosition(self, point, filename=None):
        self.xMousePosition.setText(str(round(point.x(),1)))
        self.xMousePosition.repaint()
        self.yMousePosition.setText(str(round(point.y(),1)))
        self.yMousePosition.repaint()

        if filename is not None:
            self.myFilename.setText(filename)
        else:
            self.myFilename.setText('File: None')

class myScopeToolbarWidget(QtWidgets.QToolBar):
    def __init__(self, parent):
        """
        A Toolbar for controlling the scope. This includes:
            - reading and moving stage/objective position
            - setting the size of a crosshair/box to show current motor position
            - setting x/y step size
            - showing a video window
            - capturing single images from video camera
            - importing scanning files from scope
        """
        #print('myScopeToolbarWidget.__init__')
        super(QtWidgets.QToolBar, self).__init__('Scope Controller', parent)

        self.myCanvasWidget = parent

        # works but butons become stupid
        #self.setStyleSheet("""background-color: #19232D;""")

        myVerticalSpacer = 12
        myAlign = QtCore.Qt.AlignLeft # for HBoxLayout

        myGroupBox = QtWidgets.QGroupBox()
        myGroupBox.setTitle('Scope Controller')
        #myGroupBox.setFlat(True)

        # main v box
        vBoxLayout = QtWidgets.QVBoxLayout()
        vBoxLayout.setSpacing(4)

        #
        # arrows for left/right, front/back
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(2)

        buttonName = 'move stage left'
        iconPath = canvas.canvasUtil._getIcon('left-arrow.png')
        icon  = QtGui.QIcon(iconPath)
        leftButton = QtWidgets.QPushButton()
        leftButton.setCheckable(False)
        leftButton.setIcon(icon)
        leftButton.setFixedWidth(10)
        leftButton.setToolTip('Move stage left')
        leftButton.clicked.connect(partial(self.on_button_click,buttonName))

        buttonName = 'move stage right'
        iconPath = canvas.canvasUtil._getIcon('right-arrow.png')
        icon  = QtGui.QIcon(iconPath)
        rightButton = QtWidgets.QPushButton()
        rightButton.setCheckable(False)
        rightButton.setIcon(icon)
        rightButton.setFixedWidth(10)
        rightButton.setToolTip('Move stage right')
        rightButton.clicked.connect(partial(self.on_button_click,buttonName))

        buttonName = 'move stage back'
        iconPath = canvas.canvasUtil._getIcon('up-arrow.png')
        icon  = QtGui.QIcon(iconPath)
        backButton = QtWidgets.QPushButton()
        backButton.setCheckable(False)
        backButton.setIcon(icon)
        backButton.setToolTip('Move stage back')
        backButton.clicked.connect(partial(self.on_button_click,buttonName))

        buttonName = 'move stage front'
        iconPath = canvas.canvasUtil._getIcon('down-arrow.png')
        icon  = QtGui.QIcon(iconPath)
        frontButton = QtWidgets.QPushButton()
        frontButton.setCheckable(False)
        frontButton.setIcon(icon)
        frontButton.setToolTip('Move stage front')
        frontButton.clicked.connect(partial(self.on_button_click,buttonName))

        buttonName = 'move stage up'
        iconPath = canvas.canvasUtil._getIcon('up-arrow.png')
        icon  = QtGui.QIcon(iconPath)
        upButton = QtWidgets.QPushButton()
        upButton.setCheckable(False)
        upButton.setIcon(icon)
        upButton.setToolTip('Move objective up')
        upButton.clicked.connect(partial(self.on_button_click,buttonName))

        buttonName = 'move stage down'
        iconPath = canvas.canvasUtil._getIcon('down-arrow.png')
        icon  = QtGui.QIcon(iconPath)
        downButton = QtWidgets.QPushButton()
        downButton.setCheckable(False)
        downButton.setIcon(icon)
        downButton.setToolTip('Move objective down')
        downButton.clicked.connect(partial(self.on_button_click,buttonName))

        zStepLabel = QtWidgets.QLabel("Left/Right Step (um)")
        self.zStepSpinBox = QtWidgets.QDoubleSpinBox()
        self.zStepSpinBox.setMinimum(0.0)
        self.zStepSpinBox.setMaximum(10000.0) # need something here, otherwise max is 100

        grid.addWidget(leftButton, 1, 0) # row, col
        grid.addWidget(rightButton, 1, 2) # row, col
        grid.addWidget(backButton, 0, 1) # row, col
        grid.addWidget(frontButton, 2, 1) # row, col
        grid.addWidget(upButton, 0, 3) # row, col
        grid.addWidget(self.zStepSpinBox, 1, 3) # (1,3) should be z-step
        grid.addWidget(downButton, 2, 3) # row, col

        vBoxLayout.addLayout(grid)

        #
        # x/y step size
        grid2 = QtWidgets.QGridLayout()

        xStepLabel = QtWidgets.QLabel("Left/Right Step (um)")
        self.xStepSpinBox = QtWidgets.QDoubleSpinBox()
        self.xStepSpinBox.setMinimum(0.0)
        self.xStepSpinBox.setMaximum(10000.0) # need something here, otherwise max is 100
        #self.xStepSpinBox.setValue(1000)
        #self.xStepSpinBox.valueChanged.connect(self.stepValueChanged)

        yStepLabel = QtWidgets.QLabel("Front/Back Step (um)")
        self.yStepSpinBox = QtWidgets.QDoubleSpinBox()
        self.yStepSpinBox.setMinimum(0)
        self.yStepSpinBox.setMaximum(10000) # need something here, otherwise max is 100
        #self.yStepSpinBox.setValue(500)
        #self.yStepSpinBox.valueChanged.connect(self.stepValueChanged)

        # set values of x/y step to Video
        self.crosshairSizeChoice('Video')

        grid2.addWidget(xStepLabel, 0, 0) # row, col
        grid2.addWidget(self.xStepSpinBox, 0, 1) # row, col
        grid2.addWidget(yStepLabel, 1, 0) # row, col
        grid2.addWidget(self.yStepSpinBox, 1, 1) # row, col

        vBoxLayout.addSpacing(myVerticalSpacer) # space before video
        vBoxLayout.addLayout(grid2)

        #
        # read position and report x/y position
        readPositionHBoxLayout = QtWidgets.QHBoxLayout()
        #gridReadPosition = QtWidgets.QGridLayout()

        buttonName = 'read motor position'
        readPositionButton = QtWidgets.QPushButton('Read Position')
        readPositionButton.setToolTip('Read Motor Position')
        readPositionButton.setCheckable(False)
        readPositionButton.clicked.connect(partial(self.on_button_click,buttonName))

        # we will need to set these from code
        xStagePositionLabel_ = QtWidgets.QLabel("X (um)")
        self.xStagePositionLabel = QtWidgets.QLabel("None")
        yStagePositionLabel_ = QtWidgets.QLabel("Y (um)")
        self.yStagePositionLabel = QtWidgets.QLabel("None")

        '''
        gridReadPosition.addWidget(readPositionButton, 0, 0) # row, col
        gridReadPosition.addWidget(xStagePositionLabel_, 0, 1) # row, col
        gridReadPosition.addWidget(self.xStagePositionLabel, 0, 2) # row, col
        gridReadPosition.addWidget(yStagePositionLabel_, 0, 3) # row, col
        gridReadPosition.addWidget(self.yStagePositionLabel, 0, 4) # row, col
        '''
        readPositionHBoxLayout.addWidget(readPositionButton, myAlign) # row, col
        readPositionHBoxLayout.addWidget(xStagePositionLabel_, myAlign) # row, col
        readPositionHBoxLayout.addWidget(self.xStagePositionLabel, myAlign) # row, col
        readPositionHBoxLayout.addWidget(yStagePositionLabel_, myAlign) # row, col
        readPositionHBoxLayout.addWidget(self.yStagePositionLabel, myAlign) # row, col

        vBoxLayout.addSpacing(myVerticalSpacer) # space before video
        vBoxLayout.addLayout(readPositionHBoxLayout)

        #
        # center crosshair
        crosshair_hBoxLayout = QtWidgets.QHBoxLayout()
        buttonName = 'center canvas on motor position'
        iconPath = canvas.canvasUtil._getIcon('focus.png')
        icon  = QtGui.QIcon(iconPath)
        # QToolButton
        centerCrosshairButton = QtWidgets.QPushButton('Center')
        #centerCrosshairButton = QtWidgets.QToolButton('Center')
        centerCrosshairButton.setToolTip('Center canvas on curent motor position')
        centerCrosshairButton.setIcon(icon)
        centerCrosshairButton.setCheckable(False)
        centerCrosshairButton.clicked.connect(partial(self.on_button_click,buttonName))
        crosshair_hBoxLayout.addWidget(centerCrosshairButton)

        squareSizeLabel_ = QtWidgets.QLabel("Square Size")
        comboBox = QtWidgets.QComboBox()
        comboBox.addItem("Video")
        comboBox.addItem("1x")
        comboBox.addItem("1.5x")
        comboBox.addItem("2x")
        comboBox.addItem("2.5x")
        comboBox.addItem("3x")
        comboBox.addItem("3.5x")
        comboBox.addItem("4x")
        comboBox.addItem("4.5x")
        comboBox.addItem("5x")
        comboBox.addItem("5.5x")
        comboBox.addItem("6x")
        comboBox.addItem("Hide")
        comboBox.activated[str].connect(self.crosshairSizeChoice)
        crosshair_hBoxLayout.addWidget(squareSizeLabel_)
        crosshair_hBoxLayout.addWidget(comboBox)

        vBoxLayout.addSpacing(myVerticalSpacer) # space before video
        vBoxLayout.addLayout(crosshair_hBoxLayout)

        #
        # show video window and grab video
        video_hBoxLayout = QtWidgets.QHBoxLayout()

        buttonName = 'Live Video'
        iconPath = canvas.canvasUtil._getIcon('video.png')
        icon  = QtGui.QIcon(iconPath)
        liveVideoButton = QtWidgets.QPushButton('Video Window')
        liveVideoButton.setToolTip('Show Live Video Window')
        liveVideoButton.setIcon(icon)
        liveVideoButton.setCheckable(True)
        liveVideoButton.clicked.connect(partial(self.on_button_click,buttonName))

        buttonName = 'Grab Image'
        iconPath = canvas.canvasUtil._getIcon('camera.png')
        icon  = QtGui.QIcon(iconPath)
        grabVideoButton = QtWidgets.QPushButton(buttonName)
        grabVideoButton.setToolTip('Grab image from video')
        grabVideoButton.setIcon(icon)
        grabVideoButton.setCheckable(False)
        grabVideoButton.clicked.connect(partial(self.on_button_click,buttonName))

        video_hBoxLayout.addWidget(liveVideoButton)
        video_hBoxLayout.addWidget(grabVideoButton)

        vBoxLayout.addSpacing(myVerticalSpacer) # space before video
        vBoxLayout.addLayout(video_hBoxLayout)

        #
        # import new files from scope
        scope_hBoxLayout = QtWidgets.QHBoxLayout()

        buttonName = 'Import From Scope'
        iconPath = canvas.canvasUtil._getIcon('import.png')
        icon  = QtGui.QIcon(iconPath)
        importScopeFilesButton = QtWidgets.QPushButton(buttonName)
        importScopeFilesButton.setCheckable(False)
        importScopeFilesButton.setIcon(icon)
        importScopeFilesButton.setToolTip('Import images from scope')
        importScopeFilesButton.clicked.connect(partial(self.on_button_click,buttonName))

        buttonName = 'Canvas Folder'
        iconPath = canvas.canvasUtil._getIcon('folder.png')
        icon  = QtGui.QIcon(iconPath)
        showCanvasFolderButton = QtWidgets.QPushButton('Show Folder')
        showCanvasFolderButton.setToolTip('Show canvas folder')
        showCanvasFolderButton.setCheckable(False)
        showCanvasFolderButton.setIcon(icon)
        showCanvasFolderButton.clicked.connect(partial(self.on_button_click,buttonName))

        scope_hBoxLayout.addWidget(importScopeFilesButton)
        scope_hBoxLayout.addWidget(showCanvasFolderButton)

        vBoxLayout.addSpacing(myVerticalSpacer) # space before video
        vBoxLayout.addLayout(scope_hBoxLayout)

        #
        # finalize

        #
        # add
        myGroupBox.setLayout(vBoxLayout)

        # finish
        self.addWidget(myGroupBox)

    #def visibilityChanged(self, visible):
    def setVisible(self, visible):
        """PyQt signal. Over-ride to show/hide crosshair.
        
        TODO: This is over complicated. Our scene can not have the myCrosshair during offline analysis
        """
        #print('xxx visibilityChanged:', visible)
        #print('xxx setVisible:', visible)
        super().setVisible(visible)

        # add/remove myCrosshair from scene.
        self.myCanvasWidget.getGraphicsView().setCrosshairVisible(visible)  # will actually addItem/removeItem from scene()
        
        '''
        if visible:
            #self.myCanvasWidget.getGraphicsView().myCrosshair.show()
            #myCrosshair = self.myCanvasWidget.getGraphicsView().myCrosshair
            #self.myCanvasWidget.getGraphicsView().scene().addItem(myCrosshair)

        else:
            #self.myCanvasWidget.getGraphicsView().myCrosshair.hide()
            #myCrosshair = self.myCanvasWidget.getGraphicsView().myCrosshair
            #self.myCanvasWidget.getGraphicsView().scene().removeItem(myCrosshair)
        '''

    def crosshairSizeChoice(self, text):
        logger.info(f'text:{text}')
        options = self.myCanvasWidget.options
        if text == 'Hide':
            # todo: remove red dotted square like turning off motor controller
            #umWidth = 0
            #umHeight = 0
            #self.myCanvasWidget.getGraphicsView().myCrosshair.setWidthHeight(umWidth, umHeight)
            # new
            # will actually addItem/removeItem from scene()
            self.myCanvasWidget.getGraphicsView().setCrosshairVisible(False)
        elif text=='Video':
            umWidth = options.getOption('video', 'umWidth')
            umHeight = options.getOption('video', 'umHeight')
            stepFraction = options.getOption('video', 'motorStepFraction')
            # set step size
            xStep = umWidth - (umWidth*stepFraction)
            yStep = umHeight - (umHeight*stepFraction)
            self.setStepSize(xStep, yStep)
            # set visible red rectangle
            self.myCanvasWidget.getGraphicsView().setCrosshairVisible(True)
            self.myCanvasWidget.getGraphicsView().myCrosshair.setWidthHeight(umWidth, umHeight)
        else:
            # assuming each option is of form(1x, 1.5x, etc)
            text = text.strip('x')
            zoom = float(text)
            zoomOneWidthHeight = options.getOption('Scope', 'zoomOneWidthHeight')
            stepFraction = options.getOption('Scope', 'motorStepFraction')
            # set step size
            _zoomWidthHeight = zoomOneWidthHeight / zoom
            xStep = _zoomWidthHeight - (_zoomWidthHeight*stepFraction) # always square
            yStep = _zoomWidthHeight - (_zoomWidthHeight*stepFraction)
            self.setStepSize(xStep, yStep)
            # set visible red rectangle
            self.myCanvasWidget.getGraphicsView().setCrosshairVisible(True)
            self.myCanvasWidget.getGraphicsView().myCrosshair.setWidthHeight(_zoomWidthHeight, _zoomWidthHeight)

    def getStepSize(self):
        xStep = self.xStepSpinBox.value()
        yStep = self.yStepSpinBox.value()
        return xStep, yStep

    def setStepSize(self, xStep, yStep):
        self.xStepSpinBox.setValue(xStep)
        self.yStepSpinBox.setValue(yStep)

    '''
    def stepValueChanged(self):
        xStep = self.xStepSpinBox.value()
        yStep = self.yStepSpinBox.value()
        print('myScopeToolbarWidget.stepValueChanged() xStep:', xStep, 'yStep:', yStep)
    '''

    #@QtCore.pyqtSlot()
    def on_button_click(self, name):
        logger.info(f'{name}')
        self.myCanvasWidget.userEvent(name)

class myToolbarWidget(QtWidgets.QToolBar):
    """Toolbar to
        - set contrast of canvas items
        - select extent of change.
        - show file list as tree
    """
    signalSetContrast = QtCore.Signal(object, object, object)  # (list of filename, min, max)
    signalSelectFile = QtCore.Signal(object, object)  # (filename, doZoom)

    def __init__(self, parent=None):
        #print('bToolbar.py myToolbarWidget.__init__')
        super().__init__('Layers', parent)

        # works but buttons become stupid
        #self.setStyleSheet("""background-color: #19232D;""")

        self.myCanvasWidget = parent

        #
        # layers
        layersGroupBox = QtWidgets.QGroupBox('Layers')
        #layersGroupBox.setStyleSheet("""background-color: red;""")
        layersHBoxLayout = QtWidgets.QHBoxLayout()

        checkBoxName = 'Video Layer'
        self.showVideoCheckBox = QtWidgets.QCheckBox('Image')
        self.showVideoCheckBox.setToolTip('Toggle video layer on and off')
        self.showVideoCheckBox.setCheckState(2) # Really annoying it is not 0/1 False/True but 0:False/1:Intermediate/2:True
        self.showVideoCheckBox.clicked.connect(partial(self.on_checkbox_click, checkBoxName, self.showVideoCheckBox))
        #self.addWidget(self.showVideoCheckBox)
        layersHBoxLayout.addWidget(self.showVideoCheckBox)

        checkBoxName = 'Video Squares Layer'
        self.showVideoSquaresCheckBox = QtWidgets.QCheckBox('Squares')
        self.showVideoSquaresCheckBox.setToolTip('Toggle video squares on and off')
        self.showVideoSquaresCheckBox.setCheckState(2) # Really annoying it is not 0/1 False/True but 0:False/1:Intermediate/2:True
        self.showVideoSquaresCheckBox.clicked.connect(partial(self.on_checkbox_click, checkBoxName, self.showVideoSquaresCheckBox))
        layersHBoxLayout.addWidget(self.showVideoSquaresCheckBox)

        checkBoxName = '2P Max Layer'
        self.show2pMaxCheckBox = QtWidgets.QCheckBox('Scanning')
        self.show2pMaxCheckBox.setToolTip('Toggle scanning layer on and off')
        self.show2pMaxCheckBox.setCheckState(2) # Really annoying it is not 0/1 False/True but 0:False/1:Intermediate/2:True
        self.show2pMaxCheckBox.clicked.connect(partial(self.on_checkbox_click, checkBoxName, self.show2pMaxCheckBox))
        #self.addWidget(self.show2pMaxCheckBox)
        layersHBoxLayout.addWidget(self.show2pMaxCheckBox)

        checkBoxName = '2P Squares Layer'
        self.show2pSquaresCheckBox = QtWidgets.QCheckBox('Squares')
        self.show2pSquaresCheckBox.setToolTip('Toggle scanning squares on and off')
        self.show2pSquaresCheckBox.setCheckState(2) # Really annoying it is not 0/1 False/True but 0:False/1:Intermediate/2:True
        self.show2pSquaresCheckBox.clicked.connect(partial(self.on_checkbox_click, checkBoxName, self.show2pSquaresCheckBox))
        #self.addWidget(self.show2pSquaresCheckBox)
        layersHBoxLayout.addWidget(self.show2pSquaresCheckBox)

        layersGroupBox.setLayout(layersHBoxLayout)
        self.addWidget(layersGroupBox)

        #
        # radio buttons to select type of contrast (selected, video layer, scope layer)
        self.contrastGroupBox = QtWidgets.QGroupBox('Image Contrast')

        contrastVBox = QtWidgets.QVBoxLayout()

        contrastRadioHBoxLayout = QtWidgets.QHBoxLayout()
        self.selectedContrast = QtWidgets.QRadioButton('Selected')
        self.videoLayerContrast = QtWidgets.QRadioButton('Video')
        self.scopeLayerContrast = QtWidgets.QRadioButton('Scope')

        # default to selecting 'Selected' image (for contrast adjustment)
        self.selectedContrast.setChecked(True)

        contrastRadioHBoxLayout.addWidget(self.selectedContrast)
        contrastRadioHBoxLayout.addWidget(self.videoLayerContrast)
        contrastRadioHBoxLayout.addWidget(self.scopeLayerContrast)

        contrastVBox.addLayout(contrastRadioHBoxLayout)

        # contrast sliders
        # min
        self.minSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.minSlider.setMinimum(0)
        self.minSlider.setMaximum(255)
        self.minSlider.setValue(0)
        self.minSlider.valueChanged.connect(partial(self.on_contrast_slider, 'minSlider', self.minSlider))
        self.minSlider.sliderReleased.connect(partial(self.on_contrast_slider_released, 'minSlider', self.minSlider))
        #self.addWidget(self.minSlider)
        contrastVBox.addWidget(self.minSlider)
        # max
        self.maxSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.maxSlider.setMinimum(0)
        self.maxSlider.setMaximum(255)
        self.maxSlider.setValue(255)
        self.maxSlider.valueChanged.connect(partial(self.on_contrast_slider, 'maxSlider', self.maxSlider))
        self.maxSlider.sliderReleased.connect(partial(self.on_contrast_slider_released, 'maxSlider', self.maxSlider))
        #self.addWidget(self.maxSlider)
        contrastVBox.addWidget(self.maxSlider)

        self.contrastGroupBox.setLayout(contrastVBox)
        self.addWidget(self.contrastGroupBox)

        #
        # file list (tree view)
        self.fileList = myTreeWidget(self.myCanvasWidget)
        self.fileList.signalSelectFile.connect(self.slot_selectFile)

        self.addWidget(self.fileList)

        #numVideoFiles = len(self.myCanvasWidget.getCanvas().videoFileList)
        # new
        for _file, canvasDict in self.myCanvasWidget.getCanvas().getFileDictList().items():
            # new
            self.fileList.appendFile(canvasDict)
            
            # old
            # canvasStack = canvasDict['canvasStack']
            # stackType = canvasDict['stackType']
            # if stackType == 'video':
            #     self.fileList.appendStack(canvasStack, 'Video Layer')
            # elif stackType == 'scanning':
            #     self.fileList.appendStack(canvasStack, '2P Max Layer')

        # old
        # for idx, videoFile in enumerate(self.myCanvasWidget.getCanvas().videoFileList):
        #     #print('   myToolbarWidget appending videoFile to fileList (tree):', videoFile._fileName)
        #     self.fileList.appendStack(videoFile, 'Video Layer')

        # numScopeFiles = len(self.myCanvasWidget.getCanvas().scopeFileList)
        # for idx, scopeFile in enumerate(self.myCanvasWidget.getCanvas().scopeFileList):
        #     #print('   myToolbarWidget appending scopeFile to fileList (tree):', scopeFile._fileName)
        #     self.fileList.appendStack(scopeFile, '2P Max Layer')

    def slot_selectFile(self, filename, doZoom):
        self.signalSelectFile.emit(filename, doZoom)

    # new
    def appendFile(self, canvasFileDict:dict):
        self.fileList.appendFile(canvasFileDict)

    def old_appendScopeFile(self, newStack):
        self.fileList.appendStack(newStack, '2P Max Layer') #type: ('Video Layer', '2P Max Layer')

    def old_appendVideo(self, newStack):
        self.fileList.appendStack(newStack, 'Video Layer') #type: ('Video Layer', '2P Max Layer')

    def getSelectedContrast(self):
        if self.selectedContrast.isChecked():
            return 'selected'
        elif self.videoLayerContrast.isChecked():
            return 'Video Layer'
        elif self.scopeLayerContrast.isChecked():
            return '2P Max Layer'

    def on_contrast_slider_released(self, name, object):
        adjustThisLayer = self.getSelectedContrast()
        theMin = self.minSlider.value()
        theMax = self.maxSlider.value()

        logger.info(f'name:{name} adjustThisLayer:{adjustThisLayer} theMin:{theMin} theMax:{theMax}')

        itemList = self.myCanvasWidget.getGraphicsView().getSelectionFromContext(adjustThisLayer)
        fileNameList = [x.getFileName() for x in itemList]
        self.signalSetContrast.emit(fileNameList, theMin, theMax)

    def on_contrast_slider(self, name, object):
        """Adjust the contrast of one selected item or an entire layer.

        This responds dynamically as slider is moved.
        When slide is released, final value is stored with 'on_contrast_slider_released'.
        """
        theMin = self.minSlider.value()
        theMax = self.maxSlider.value()

        # todo: work out the strings I am using !!!!!!!!!!!!!
        adjustThisLayer = self.getSelectedContrast()
        logger.info(f'  adjustThisLayer:{adjustThisLayer}')
        logger.info(f'  theMin:{theMin} theMax:{theMax}')

        itemList = self.myCanvasWidget.getGraphicsView().getSelectionFromContext(adjustThisLayer)
        for item in itemList:
            # TODO: use canvasWidget setContrast_item()
            self.myCanvasWidget.getGraphicsView().setContrast_Item(item, theMin, theMax)
            
            '''
            itemStack = item.myStack
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

            imageStackHeight, imageStackWidth = itemStack.shape

            myQImage = QtGui.QImage(itemStack, imageStackWidth, imageStackHeight,
                                    QtGui.QImage.Format_Indexed8)

            #
            # try and set color
            if adjustThisLayer == '2P Max Layer':
                colors=[]
                for i in range(256):
                    colors.append(QtGui.qRgb(i/4,i,i/2))
                myQImage.setColorTable(colors)

            pixmap = QtGui.QPixmap(myQImage)
            pixmap = pixmap.scaled(umWidth, umHeight,
                            aspectRatioMode=QtCore.Qt.KeepAspectRatio,
                            transformMode=QtCore.Qt.SmoothTransformation,
                            )

            item.setPixmap(pixmap)
            '''

    def setSelectedItem(self, filename):
        """
        Respond to user clicking on the image and select the file in the list.
        """
        #print('myToolbarWidget.setSelectedItem() filename:', filename)
        self.fileList.setSelectedItem(filename)

        '''
        # todo: use self._findItemByFilename()
        items = self.fileList.findItems(filename, QtCore.Qt.MatchFixedString, column=0)
        if len(items)>0:
            item = items[0]
            #print('   item:', item)
            self.fileList.setCurrentItem(item)
        '''

    def setCheckedState(self, filename, doShow):
        """
        set the visible checkbox
        """
        #print('myToolbarWidget.setCheckedState() filename:', filename, 'doShow:', doShow)
        self.fileList.setCheckedState(filename, doShow)

        '''
        item = self._findItemByFilename(filename)
        if item is not None:
            column = 0
            item.setCheckState(column, doShow)
        '''

    '''
    def _findItemByFilename(self, filename):
        """
        Given a filename, return the item. Return None if not found.
        """
        items = self.fileList.findItems(filename, QtCore.Qt.MatchFixedString, column=0)
        if len(items)>0:
            return items[0]
        else:
            return None
    '''

    '''
    def mousePressEvent(self, event):
        print('myToolbarWidget.mousePressEvent()')
    '''

    '''
    def keyPressEvent(self, event):
        print('myToolbarWidget.keyPressEvent() event:', event)
        print('   enable bring to front and send to back')
    '''

    '''
    @QtCore.pyqtSlot()
    def on_button_click(self, name):
        print('=== myToolbarWidget.on_button_click() name:', name)
    '''

    #@QtCore.pyqtSlot()
    def on_checkbox_click(self, name, checkBoxObject):
        logger.info(f'name:{name} checkBoxObject:{checkBoxObject}')
        checkState = checkBoxObject.checkState()

        if name == 'Video Layer':
            self.myCanvasWidget.getGraphicsView().hideShowLayer('Video Layer', checkState==2)
        if name =='Video Squares Layer':
            self.myCanvasWidget.getGraphicsView().hideShowLayer('Video Squares Layer', checkState==2)
        if name == '2P Max Layer':
            self.myCanvasWidget.getGraphicsView().hideShowLayer('2P Max Layer', checkState==2)
        if name == '2P Squares Layer':
            self.myCanvasWidget.getGraphicsView().hideShowLayer('2P Squares Layer', checkState==2)

class myTreeWidget(QtWidgets.QTreeWidget):

    signalSelectFile = QtCore.Signal(object, object)  # (filename, doZoom)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.myCanvasWidget = parent

        myColumns = ['Index', 'File', 'Type', 'xPixels', 'yPixels', 'numSlices'] # have to be unique
        self.myColumns = {}
        for idx, column in enumerate(myColumns):
            self.myColumns[column] = idx

        self.setHeaderLabels(myColumns) # 'Show'])
        self.setColumnWidth(self.myColumns['Index'], 85)  # because rows are checkable, this needs to be wider
        self.setColumnWidth(self.myColumns['File'], 200)
        self.setColumnWidth(self.myColumns['Type'], 45)
        self.setColumnWidth(self.myColumns['xPixels'], 65)
        self.setColumnWidth(self.myColumns['yPixels'], 65)
        self.setColumnWidth(self.myColumns['numSlices'], 65)

        self.itemClicked.connect(self.fileSelected_callback)
        #self.itemSelectionChanged.connect(self.fileSelected_callback)
        self.itemChanged.connect(self.fileSelected_changed)  # used for visible checkbox

        # TODO: To do this need to use model and sort proxy
        #self.setSortingEnabled(True)

    def appendFile(self, canvasFileDict : dict):
        """
        Args:
            canvasDict: from canvas.bCanvas._defaultFileDict
        """
        canvasStack = canvasFileDict['canvasStack']
        stackType = canvasFileDict['stackType']
        isVisible = canvasFileDict['isVisible']

        myIndex = self.topLevelItemCount()

        item = QtWidgets.QTreeWidgetItem(self)
        item.setText(self.myColumns['Index'], str(myIndex+1))

        item.setText(self.myColumns['File'], canvasStack.getFileName())

        if stackType == 'video':
            item.setText(self.myColumns['Type'], 'v')
        elif stackType == 'scanning':
            item.setText(self.myColumns['Type'], '2p')
        else:
            logger.error(f'got unknown type:{stackType}')
            item.setText(self.myColumns['Type'], 'Unknown')

        item.setText(self.myColumns['xPixels'], str(canvasStack.pixelsPerLine))
        item.setText(self.myColumns['yPixels'], str(canvasStack.linesPerFrame))
        item.setText(self.myColumns['numSlices'], str(canvasStack.numImages))
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)

        #item.setCheckState(0, QtCore.Qt.Checked)
        if canvasFileDict['isVisible']:
            item.setCheckState(0, QtCore.Qt.Checked)
        else:
            item.setCheckState(0, False)
        
        #self.insertTopLevelItems(0, item)
        self.addTopLevelItem(item)

    def old_appendStack(self, theStack, type):
        """
        type: ('Video Layer', '2P Max Layer')
        """

        myIndex = self.topLevelItemCount()

        item = QtWidgets.QTreeWidgetItem(self)
        item.setText(self.myColumns['Index'], str(myIndex+1))

        item.setText(self.myColumns['File'], theStack.getFileName())

        if type == 'Video Layer':
            item.setText(self.myColumns['Type'], 'v')
        elif type == '2P Max Layer':
            item.setText(self.myColumns['Type'], '2p')
        else:
            logger.error(f'got unknown type:{type}')
            item.setText(self.myColumns['Type'], 'Unknown')

        item.setText(self.myColumns['xPixels'], str(theStack.pixelsPerLine))
        item.setText(self.myColumns['yPixels'], str(theStack.linesPerFrame))
        item.setText(self.myColumns['numSlices'], str(theStack.numImages))
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Checked)

        #self.insertTopLevelItems(0, item)
        self.addTopLevelItem(item)

    def setSelectedItem(self, filename):
        """
        Respond to user clicking on the image and select the file in the list.
        """
        items = self.findItems(filename, QtCore.Qt.MatchFixedString, column=self.myColumns['File'])
        item = None
        if len(items)>0:
            item = items[0]
            #self.setCurrentItem(item)
        else:
            logger.warning(f'Did not find filename:{filename}')
        #
        self.setCurrentItem(item)

    def setCheckedState(self, filename, doShow):
        """
        set the visible checkbox
        """
        items = self.findItems(filename, QtCore.Qt.MatchFixedString, column=self.myColumns['File'])
        if len(items)>0:
            item = items[0]
            column = 0
            item.setCheckState(column, doShow)

    def keyPressEvent(self, event):
        #print('myTreeWidget.keyPressEvent() event.text():', event.text())

        # todo: fix this, this assumes selected file in list is same as selected file in graphics view !
        if event.key() == QtCore.Qt.Key_F:
            #print('f for bring to front')
            self.myCanvasWidget.getGraphicsView().changeOrder('bring to front')
        elif event.key() == QtCore.Qt.Key_B:
            #print('b for send to back')
            self.myCanvasWidget.getGraphicsView().changeOrder('send to back')

        elif event.key() == QtCore.Qt.Key_I:
            selectedItems = self.selectedItems()
            logger.info(f'key i selectedItems:{selectedItems}')
            self.myCanvasWidget.userEvent('print stack info')

        elif event.key() == QtCore.Qt.Key_Left:
            super(myTreeWidget, self).keyPressEvent(event)
        elif event.key() == QtCore.Qt.Key_Right:
            super(myTreeWidget, self).keyPressEvent(event)
        elif event.key() == QtCore.Qt.Key_Up:
            super(myTreeWidget, self).keyPressEvent(event)
        elif event.key() == QtCore.Qt.Key_Down:
            super(myTreeWidget, self).keyPressEvent(event)
        else:
            logger.warning('  key not handled:text: {event.text()} modifyers:{event.modifiers()}')
            super(myTreeWidget, self).keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """
        open a stack on a double-click
        """
        logger.info('')
        selectedItems = self.selectedItems()
        if len(selectedItems) > 0:
            selectedItem = selectedItems[0]
            fileName = selectedItem.text(self.myColumns['File'])
            type = selectedItem.text(self.myColumns['Type']) # in ['v', '2p']
            if type == 'v':
                layer = 'Video Layer'
            elif type == '2p':
                layer = '2P Max Layer'
            else:
                # error
                layer = None
            if layer is not None:
                self.myCanvasWidget.openStack(fileName, layer)

    def fileSelected_changed(self, item, col):
        """
        Called when user clicks on check box

        TODO: only respond to column 0 and use column name xxx.
        """
        filename = item.text(self.myColumns['File'])
        if col != 0:
            return
        if not filename:
            return
        isNowChecked = item.checkState(0) # 0:not checked, 2:is checked
        doShow = True if isNowChecked==2 else False
        #logger.info(f'col:{col} filename:{filename} isNowChecked:{isNowChecked} doShow:{doShow}')
        self.myCanvasWidget.getGraphicsView().hideShowItem(filename, doShow)

    def fileSelected_callback(self):
        """
        Respond to user click in the file list (selects a file)
        """
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        #isShift = modifiers == QtCore.Qt.ShiftModifier
        isControl = modifiers == QtCore.Qt.ControlModifier

        logger.info(f'isControl:{isControl}')

        theItems = self.selectedItems()
        if len(theItems) > 0:
            theItem = theItems[0]
            #selectedRow = self.fileList.currentRow() # self.fileList is a QTreeWidget
            filename = theItem.text(self.myColumns['File'])

            # visually select image in canvas with yellow square
            # self.myCanvasWidget.getGraphicsView().setSelectedItem(filename)

            # zoom
            # if isControl:
            #     self.myCanvasWidget.getGraphicsView().zoomSelectedItem(filename)

            self.signalSelectFile.emit(filename, isControl)

        else:
            logger.info('  no selected items')
