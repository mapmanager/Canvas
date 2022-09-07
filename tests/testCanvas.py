import canvas

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

def test_canvas():
    """Test loading a canvas with just video."""
    logger.info('===')
    path = '/Users/cudmore/data/canvas/20220907_tstCanvas000/20220907_tstCanvas000_canvas.json'

    c = canvas.bCanvas(path)

    df = c.stackListToDf()
    print('stackListToDf returned')
    print(df)

    assert c.numVideoFiles() == 4
    assert c.numFiles() == 4  # both (scanning, video)

    '''
    # copy some new files into canvas folder and run this ...
    newStackDictList = c.importNewScopeFiles()
    for newStack in newStackDictList:
        pprint(newStack)
    '''

if __name__ == '__main__':
    import canvas.canvasJavaBridge
    
    try:
        _started = canvas.canvasJavaBridge._startJavaBridge()

        test_canvas()

    finally:
        if _started:
            canvas.canvasJavaBridge._stopJavaBridge()
