
Make a fresh conda environment.

Not always needed, can reuse existing.

```
conda create -y -n canvas-pyinstaller-env python=3.9
conda activate canvas-pyinstaller-env

conda install pyqt

pip install -e ../.
```

Install pyinstaller
```
pip install pyinstaller
```

Run pyinstaller with premade spec file

```
pyinstaller --noconfirm --clean myCanvas.spec
```

## Troubleshooting

Need to specify some hidden import for pyqtGraph. Do this in `myCanvas.spec`

```
hiddenimports=[
    'pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5',
    'pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt5',
    'pyqtgraph.imageview.ImageViewTemplate_pyqt5',
    ]
```

Some times need to upgrade pip and setuptools.

```
pip install --upgrade pip setuptools
```
