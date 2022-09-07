
# Switch to AICS image io with bioformats support?

https://allencellmodeling.github.io/aicsimageio/index.html

For this see Tally Lamberts Twitter feed:

https://twitter.com/TalleyJLambert/status/1442643282832592901

And this release info on image.sc

https://forum.image.sc/t/aicsimageio-4-2-0-release/58150

Loading oir gives error

```
RuntimeError: 
BioformatsReader requires the maven ('mvn') executable to be
available in your environment. If you are using conda, you can 
install with `conda install -c conda-forge scyjava`.

Alternatively, install from https://maven.apache.org/download.cgi
```

bioformats_jar is depreciated?
- See: https://github.com/tlambert03/bioformats_jar
- Use scyjava

Install

```
conda create -y -n aics-env python=3.9
conda activate aics-env

pip install aicsimageio
pip install bioformats_jar

# this might install java (no need for java_home?)
conda install -c conda-forge scyjava
```

# Install on m1 Mac

## Install canvas with Java and python-bioformats

Key was to follow CellProfiler install instructions.

1) Download Java 'jdk-8u341-macosx-x64.dmg' from

https://www.oracle.com/java/technologies/downloads/#java8

2) Check the path with `/usr/libexec/java_home -V`

```
2022-08-31 22:13:27.113 java_home[74615:18247987] There was an error parsing the Info.plist for the bundle at URL <0x6000022b2d00>: NSCocoaErrorDomain - 3840
Matching Java Virtual Machines (5):
    18.0.2 (arm64) "Azul Systems, Inc." - "Zulu JRE 18.32.11" /Library/Java/JavaVirtualMachines/zulu-18.jre/Contents/Home
    1.8.341.10 (x86_64) "Oracle Corporation" - "Java" /Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home
    1.8.0_345 (arm64) "Azul Systems, Inc." - "Zulu JRE 8.64.0.19" /Library/Java/JavaVirtualMachines/zulu-8.jre/Contents/Home
    1.8.0_345 (arm64) "Azul Systems, Inc." - "Zulu 8.64.0.19" /Library/Java/JavaVirtualMachines/zulu-8.jdk/Contents/Home
    1.8.0_341 (x86_64) "Oracle Corporation" - "Java SE 8" /Library/Java/JavaVirtualMachines/jdk1.8.0_341.jdk/Contents/Home
/Library/Java/JavaVirtualMachines/zulu-18.jre/Contents/Home
```

3) set path with `pico ~/.zshrc`

```
# abb 20220831, baltimore, trying to get python-javabridge to work
#export JAVA_HOME=/Library/Java/JavaVirtualMachines/zulu-8.jdk/Contents/Home
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_341.jdk/Contents/Home
```

4) make conda env and install
```
conda create -y -n canvas-env python=3.9
conda activate canvas-env
# not PyQt5 like with pip
conda install pyqt  

pip install -e ../.
```

5) Check JAVA_HOME durnig runtime

```
import os
if 'JAVA_HOME' in os.environ:
    logging.info(f"JAVA_HOME is {os.environ['JAVA_HOME']}")
else:
    logging.info("JAVA_HOME is not set")
```

Let user define CANVAS_JAVA_HOME

```
userPath = ''
os.environ['CANVAS_JAVA_HOME'] = userPath
```

## On m1 arm64 macos, download and install jre and jdk from

https://www.azul.com/downloads/?os=macos&architecture=arm-64-bit#download-openjdk

Java is then in something like '/Library/Java/JavaVirtualMachines/zulu-8.jdk/Contents/Home/bin/java'

And then there is this???

```
/usr/libexec/java_home -V
```

yields

```
2022-08-31 17:59:18.781 java_home[66182:18138644] There was an error parsing the Info.plist for the bundle at URL <0x600001b24320>: NSCocoaErrorDomain - 3840
Matching Java Virtual Machines (3):
    18.0.2 (arm64) "Azul Systems, Inc." - "Zulu JRE 18.32.11" /Library/Java/JavaVirtualMachines/zulu-18.jre/Contents/Home
    1.8.0_345 (arm64) "Azul Systems, Inc." - "Zulu 8.64.0.19" /Library/Java/JavaVirtualMachines/zulu-8.jdk/Contents/Home
    1.8.0_345 (arm64) "Azul Systems, Inc." - "Zulu JRE 8.64.0.19" /Library/Java/JavaVirtualMachines/zulu-8.jre/Contents/Home
/Library/Java/JavaVirtualMachines/zulu-18.jre/Contents/Home
```

python-javabridge requires JAVA_HOME to be set, pointing to JDK, not JRE

```
export JAVA_HOME=/Library/Java/JavaVirtualMachines/zulu-18.jdk/Contents/Home

# put JAVA_HOME in .zshrc path, need to remember I did this
mypath="/Library/Java/JavaVirtualMachines/zulu-18.jdk/Contents/Home"
echo “export JAVA_HOME=$(your_path)” >> ~/.zshrc

#or maybe

export JAVA_HOME=/Library/Java/JavaVirtualMachines/zulu-8.jdk/Contents/Home
```

`printenv` is useful

Then in python, this goes into pyinstaller spec file. Here I am following CellProfiler-Analyst .spec file

```
for subdir, dirs, files in os.walk(os.environ["JAVA_HOME"]):
    if 'Contents/' in subdir:
        if len(subdir.split('Contents/')) >1:
            _, subdir_split = subdir.split('Contents/')
            for file in files:
                datas += [(os.path.join(subdir, file), subdir_split)]
```

# opencv fixes

For opencv, using older version of open cv (errors with new version)

```
opencv-python-headless==4.5.3.56
```

## To get opencv to use built in camera on macos laptop

Add to file '/Library/Java/JavaVirtualMachines/zulu-18.jdk/Contents/Info.plist'

this, inside main <dict> ...

```
<key>NSCameraUsageDescription</key>
<string>OpenCV</string>
<key>NSMicrophoneUsageDescription</key>
<string>OpenCV</string>
```

# Linden Sutter Windows Notes

## Path to desktop

"C:\Users\lindenlab\.runelite\Desktop"

## Make venv on windows

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

Problems with plotting pyqtgraph histograms:

https://stackoverflow.com/questions/72016877/pg-plotcurveitem-stepmode-center-issue-with-x-and-y-data-shape

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