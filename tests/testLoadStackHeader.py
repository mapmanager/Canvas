"""
Test loading stack header.
"""

import canvas

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

def testLoadScanImage_header():
    logger.info('===')
    # 1 channel time-series
    path = '/Users/cudmore/data/patrick/GCaMP Time Series 2.tiff'
    _csh = canvas.canvasStackHeader(path)
    #_csh.print()
    assert _csh.numchannels == 1
    assert _csh.numimages == 300
    assert _csh.xpixels == 512
    assert _csh.ypixels == 512
    assert _csh.xVoxel == 0.39550475776195526
    assert _csh.yVoxel == 0.39550475776195526

def testLoadOir_header():
    logger.info('===')
    import canvas.canvasJavaBridge
    
    # TODO: add canvasJavaScript_isLoaded() to test if javabridge/bioformats is installed
    
    canvas.canvasJavaBridge._startJavaBridge()
    
    try:
        # 2-channel line scan
        path = '/Users/cudmore/data/example-oir/20190429_tst2_0011.oir'
        _csh = canvas.canvasStackHeader(path)
        #_csh.print()
        assert _csh.numchannels == 2
        assert _csh.numimages == 1
        assert _csh.xpixels == 32
        assert _csh.ypixels == 256
        assert _csh.xVoxel == 1.988737822087164
        assert _csh.yVoxel == 1.988737822087164
        
        # 2-channel frame-scan time-series (channel 2 is super dim)
        path = '/Users/cudmore/data/example-oir/20190429_tst2_0009.oir'
        _csh = canvas.canvasStackHeader(path)
        #_csh.print()
        assert _csh.numchannels == 2
        assert _csh.numimages == 7
        assert _csh.xpixels == 512
        assert _csh.ypixels == 512
        assert _csh.xVoxel == 0.994368911043582
        assert _csh.yVoxel == 0.994368911043582

    finally:
        canvas.canvasJavaBridge._stopJavaBridge()

if __name__ == '__main__':
    testLoadScanImage_header()
    testLoadOir_header()
