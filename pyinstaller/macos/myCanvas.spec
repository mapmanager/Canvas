# -*- mode: python ; coding: utf-8 -*-

# needed for napari
#import vispy.glsl
#import vispy.io

block_cipher = None

hiddenimports=[
    'pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5',
    'pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt5',
    'pyqtgraph.imageview.ImageViewTemplate_pyqt5',
    ]

# needed for napari
#data_files = [
#    (os.path.dirname(vispy.glsl.__file__), os.path.join("vispy", "glsl")),
#    (os.path.join(os.path.dirname(vispy.io.__file__), "_data"), os.path.join("vispy", "io", "_data")),
#]
data_files = []

a = Analysis(
    ['../canvas/interface/bCanvasApp.py'],
    pathex=['/Users/cudmore/opt/miniconda3/envs/canvas-env/lib/python3.9/site-packages/'],
    binaries=[],
    datas=data_files,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Canvas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Canvas',
)
app = BUNDLE(
    coll,
    name='Canvas.app',
    icon=None,
    bundle_identifier=None,
)
