## Install

On m1 mac, need to use conda because PyQt is not available in pip (Aug 2022)

Needs to conda install pyqt

```
conda create -y -n canvas-env python=3.9
conda activate canvas-env

conda install pyqt  

```

Then proceed with installing Canvas

```
pip install -e .
```

## Run

On command line

```
canvas
```

## Notes

### ScanImage (vidrio)

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


