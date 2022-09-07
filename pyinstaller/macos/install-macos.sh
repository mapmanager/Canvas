pyinstaller \
	--noconfirm \
	--clean \
	--onedir \
	--windowed \
	--path /Users/cudmore/opt/miniconda3/envs/bimpy-env/lib/python3.9/site-packages/ \
	--name Canvas \
    --hidden-import pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5 \
    ../canvas/interface/bCanvasApp.py

#	--hidden-import tables \
#	--icon ../sanpy/interface/icons/sanpy_transparent.icns \
#    --icon ../canvas/icons/canvas-color-64.png \
#    --add-data "/Users/cudmore/opt/miniconda3/envs/sanpy-env/lib/python3.9/site-packages/pyqtgraph/colors:pyqtgraph/colors" \

# hidden imports for pyqtgraph
#    --hidden-import pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5 \
#    --hidden-import pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt5 \
#    --hidden-import pyqtgraph.imageview.ImageViewTemplate_pyqt5	../interface/bCanvasApp.py
