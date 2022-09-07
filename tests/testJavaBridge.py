import testJavaBridge
import canvas.canvasJavaBridge

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

def testJavaBridge():
    """Start and stop Javabridge.
    """
    logger.info('')
    withBioFormats = True
    
    _started = canvas.canvasJavaBridge._startJavaBridge(withBioFormats=withBioFormats)
    logger.info(f'_started:{_started}')
    
    _stopped = canvas.canvasJavaBridge._stopJavaBridge()
    logger.info(f'_stopped:{_stopped}')

if __name__ == '__main__':
    testJavaBridge()