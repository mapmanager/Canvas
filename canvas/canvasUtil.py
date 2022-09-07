
import os
import sys
import pathlib
import shutil

from qtpy import QtCore

# TODO: move this to a utils.py like in bimpy
# TODO: to use py installer we need to always create/use <user>/Documents

import canvas.interface

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

def _getBundledDir():
    """
    """
    if getattr(sys, 'frozen', False):
        # we are running in a bundle (frozen)
        bundle_dir = sys._MEIPASS
    else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))    
    return bundle_dir

def _getIcon(iconFile : str):
    """
    Get full path to an icon file.
    """
    codeFolder = _getBundledDir()
    iconPath = os.path.join(codeFolder, 'interface', 'icons', iconFile)
    return iconPath

def getVersionInfo() -> dict:
    """Get version of important Python packages.
    """
    versionDict = {}

    # python
    import platform
    versionDict['Python'] = platform.python_version()

    # numpy
    import numpy as np
    versionDict['NumPy'] = np.__version__

    # pandas
    import pandas as pd
    versionDict['Pandas'] = pd.__version__

    # pyqt (interface)
    PYQT_VERSION_STR = QtCore.PYQT_VERSION_STR
    versionDict['PyQt'] = PYQT_VERSION_STR

    # pyqtgraph (interface)
    from pyqtgraph import __version__
    versionDict['pyqtGraph'] = __version__

    # opencv (interface)
    from cv2 import __version__
    versionDict['python-opencv'] = __version__

    # python-bioformats
    from bioformats import __version__
    versionDict['python-bioformats'] = __version__

    # python-javabridge
    from javabridge import __version__
    versionDict['python-javabridge'] = __version__

    # JAVA_HOME
    # on macOs m1 laptop, this is '/Library/Java/JavaVirtualMachines/jdk1.8.0_341.jdk/Contents/Home'
    if 'JAVA_HOME' in os.environ:
        #logging.info(f"JAVA_HOME is {os.environ['JAVA_HOME']}")
        versionDict['JAVA_HOME'] = os.environ['JAVA_HOME']
    else:
        #logging.info("JAVA_HOME is not set")
        versionDict['JAVA_HOME'] = 'Not defined'

    # this works but we can't start/stop javabridge
    '''
    if javabridge.get_env() is None:
        javabridge.start_vm(run_headless=True)
    versionDict['find_javahome'] = javabridge.locate.find_javahome()
    if javabridge.get_env() is not None:
        javabridge.kill_vm()
    '''

    # canvas app
    canvasVersion = canvas.interface.canvasApp.__version__
    versionDict['Canvas App'] = canvasVersion
     
    # canvas
    canvasVersion = canvas.bCanvas.__version__
    versionDict['Canvas Backend'] = canvasVersion

    # canvas options

    # canvas file

    return versionDict

def _getUserDocumentsFolder():
    """Get folder from <user> path (not sanpy path).
    """
    userPath = pathlib.Path.home()
    userDocumentsFolder = os.path.join(userPath, 'Documents')
    if not os.path.isdir(userDocumentsFolder):
        logger.error(f'Did not find path "{userDocumentsFolder}"')
        logger.error(f'   Using "{userPath}"')
        return userPath
    else:
        return userDocumentsFolder

def _getUserCanvasFolder():
    userDocumentsFolder = _getUserDocumentsFolder()
    sanpyFolder = os.path.join(userDocumentsFolder, 'Canvas')
    return sanpyFolder

def _getScopeOptionsFolder():
    canvasFolder = _getUserCanvasFolder()
    scopeOptionsFolder = os.path.join(canvasFolder, 'scopeoptions')
    return scopeOptionsFolder

def _getLogFolder():
    canvasFolder = _getUserCanvasFolder()
    logFolder = os.path.join(canvasFolder, 'log')
    return logFolder

def _addUserPath():
    """Make user SanPy folder and add it to the Python sys.path
    
    Returns:
        True: IF we made the folder (first time SAnPY is running)
    """
    
    logger.info('')
    madeUserFolder = _makeCanvasFolders()  # make <user>/Documents/SanPy if necc
            
    userSanPyFolder = _getUserCanvasFolder()

    # if userSanPyFolder in sys.path:
    #     sys.path.remove(userSanPyFolder)

    if not userSanPyFolder in sys.path:
        logger.info(f'Adding to sys.path: {userSanPyFolder}')
        sys.path.append(userSanPyFolder)

    logger.info('sys.path is now:')
    for path in sys.path:
        logger.info(f'    {path}')

    return madeUserFolder

def _makeCanvasFolders():
    """Make Canvas folder in <user>/Documents path.

    If no Documents folder then make 'canvas'' folder directly in <user> path.
    """
    userDocumentsFolder = _getUserDocumentsFolder()

    madeUserFolder = False
    
    # main <user>/DOcuments/SanPy folder
    canvasFolder = _getUserCanvasFolder()
    if not os.path.isdir(canvasFolder):
        logger.info(f'Making <user>/Canvas folder "{canvasFolder}"')
        madeUserFolder = True
        #
        # copy entire xxx into <user>/Documents/SanPy
        _bundDir = _getBundledDir()
        
        # folder supplied with distribution that is copied inter <user>/Documents
        _srcPath = pathlib.Path(_bundDir) / '_userFiles' / 'Canvas'
        _dstPath = pathlib.Path(canvasFolder)

        logger.info(f'    copying folder tree to <user>/Documents/Canvas folder')
        logger.info(f'    _srcPath:{_srcPath}')
        logger.info(f'    _dstPath:{_dstPath}')
        shutil.copytree(_srcPath, _dstPath)
    
    return madeUserFolder

if __name__ == '__main__':
    from pprint import pprint
    pprint(getVersionInfo())