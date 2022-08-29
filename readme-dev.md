
## Path to desktop

"C:\Users\lindenlab\.runelite\Desktop"

## MAke venv

pip install --upgrade pip

python -m venv canvas_env

.\canvas_env\Scripts\activate.bat

## Notes

### ScanImage (vidrio) python reader

https://gitlab.com/vidriotech/scanimagetiffreader-python

Display range: -16 - 138
 
Calibration function: y = a+bx
  a: -32768.000000
  b: 1.000000
  Unit: "gray value"


## Video Size

video width: 1920
video height: 1080
videoWidth/videoHeight: 1.7777

video width: 640
video height: 480
videoWidth/videoHeight: 1.3333

linden video width/height (um)
        "umWidth": 455.2,
        "umHeight": 341.4,
linden width/height (um): 1.3333

### macOS Camera
    videoWidth/videoHeight: 1.7777

        "width": 1920,
        "height": 1080,
        "umWidth": 455.2,
        "umHeight": 256.05,

### linden Camera
    width/height (um): 1.3333

        "width": 640,
        "height": 480,
        "umWidth": 455.2,
        "umHeight": 341.4,

## Windows bugs

Somewhere in canvasStack.py

```
|==============================>>
    |  Traceback (most recent call last):
    |    File "C:\Users\lindenlab\AppData\Local\Programs\Python\Python38\Scripts\canvas-script.py", line 11, in <module>
    |      load_entry_point('Canvas', 'console_scripts', 'canvas')()
    |    File "c:\users\lindenlab\.runelite\desktop\bob\canvas\canvas\interface\canvasApp.py", line 440, in main
    |      sys.exit(app.exec_())
    |    File "c:\users\lindenlab\appdata\local\programs\python\python38\lib\site-packages\pyqtgraph\widgets\GraphicsView.py", line 155, in paintEvent
    |      return QtGui.QGraphicsView.paintEvent(self, ev)
    |    File "c:\users\lindenlab\appdata\local\programs\python\python38\lib\site-packages\pyqtgraph\debug.py", line 93, in w
    |      printExc('Ignored exception:')
    |    --- exception caught here ---
    |    File "c:\users\lindenlab\appdata\local\programs\python\python38\lib\site-packages\pyqtgraph\debug.py", line 91, in w
    |      func(*args, **kwds)
    |    File "c:\users\lindenlab\appdata\local\programs\python\python38\lib\site-packages\pyqtgraph\graphicsItems\PlotCurveItem.py", line 464, in paint
    |      path = self.getPath()
    |    File "c:\users\lindenlab\appdata\local\programs\python\python38\lib\site-packages\pyqtgraph\graphicsItems\PlotCurveItem.py", line 446, in getPath
    |      self.path = self.generatePath(*self.getData())
    |    File "c:\users\lindenlab\appdata\local\programs\python\python38\lib\site-packages\pyqtgraph\graphicsItems\PlotCurveItem.py", line 435, in generatePath
    |      path = fn.arrayToQPath(x, y, connect=self.opts['connect'])
    |    File "c:\users\lindenlab\appdata\local\programs\python\python38\lib\site-packages\pyqtgraph\functions.py", line 1494, in arrayToQPath
    |      arr[1:-1]['y'] = y
    |  ValueError: could not broadcast input array from shape (512) into shape (510)
    ```