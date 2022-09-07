"""
Test loading of stack header and data.
"""

import canvas

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

def testLoadScanImage():
    logger.info(f'===')
    
    # 1 channel time-series
    path = '/Users/cudmore/data/patrick/GCaMP Time Series 2.tiff'
    _cs = canvas.canvasStack(path)
    #_cs.header.print()
    assert _cs.dataIsLoaded() == True
    assert _cs.getStack(1).shape == (300, 512, 512)
    assert _cs.getStack(2) == None

    # # 1 channel z-stack
    path = '/Users/cudmore/data/patrick/JBslideTEST_00004.tiff'
    _cs = canvas.canvasStack(path)
    #_cs.header.print()
    assert _cs.dataIsLoaded() == True
    assert _cs.getStack(1).shape == (61, 512, 512)

    # # 1-st image in folder ???
    # path = '/Users/cudmore/Library/CloudStorage/Box-Box/data/canvas/512by512by1zoom5/xy512z1zoom5bi_00001_00001.tif'
    # _cs = canvas.canvasStack(path)
    # _cs.header.print()

def testLoadOlympus():
    logger.info(f'===')

    import canvas.canvasJavaBridge
    
    # TODO: add canvasJavaScript_isLoaded() to test if javabridge/bioformats is installed
    
    canvas.canvasJavaBridge._startJavaBridge()
    
    try:
        # 2-channel line scan
        path = '/Users/cudmore/data/example-oir/20190429_tst2_0011.oir'
        
        # 2-channel frame-scan time-series (channel 2 is super dim)
        path = '/Users/cudmore/data/example-oir/20190429_tst2_0009.oir'

        _cs = canvas.canvasStack(path)
        _cs.print()
    finally:
        canvas.canvasJavaBridge._stopJavaBridge()

if __name__ == '__main__':
    testLoadScanImage()
    #testLoadOlympus()

