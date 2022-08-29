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


