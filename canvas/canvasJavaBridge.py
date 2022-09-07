# Author: Robert Cudmore
# Date: 20190704

import time
import traceback

import skimage # this is needed or else javabridge fails to import ???

try:
    import javabridge
except (ModuleNotFoundError) as e:
    pass

try:
    import bioformats
except (ModuleNotFoundError) as e:
    pass

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

def _startJavaBridge(withBioFormats=True):
    """Start Javabridge.
    """
    
    if javabridge is None:
        return
    
    _started = False
    if javabridge.get_env() is None:
        if withBioFormats:
            class_path=bioformats.JARS

            # logger.info('bioformats.JARS')
            # for _item in bioformats.JARS:
            #     print('  ', _item)

        else:
            class_path = None
        

        javabridge.start_vm(run_headless=True, class_path=class_path)

        # turn off logging
        try:
            _DebugTools = javabridge.JClassWrapper('loci.common.DebugTools')
            _DebugTools.enableLogging()
            _DebugTools.setRootLevel("WARN")
        except (javabridge.jutil.JavaException) as e:
            logger.error(f'Exception while turning off logging: {e}')

        try:
            _LogbackTools = javabridge.JClassWrapper("loci.common.LogbackTools")
            _LogbackTools.enableLogging()
            _LogbackTools.setRootLevel("WARN")
        except (javabridge.jutil.JavaException) as e:
            logger.error(f'Exception while turning off logging: {e}')

        _started = True
    else:
        logger.warning(f'  javabridge is already started')
        _started = False
    return _started

def _stopJavaBridge():
    if javabridge is None:
        return
    
    _stopped = False
    if javabridge.get_env() is not None:
        _stopped = True
        javabridge.kill_vm()
    return _stopped

if __name__ == '__main__':
    _started = _startJavaBridge()

    logger.info('running')

    if _started:
        _stopJavaBridge()