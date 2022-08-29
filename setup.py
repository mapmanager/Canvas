from setuptools import setup, find_packages

includePackages = ['canvas', 'canvas.*', 'canvas.inter*face']

setup(
    name='Canvas',
    version='0.1.0',
	description='',
	long_description='',
	author='Robert Cudmore',
	author_email='robert.cudmore@gmail.com',
	url='https://github.com/cudmore/bImPy',
    keywords=['in vivo', 'two photon', 'laser scanning microscopy'],
    
    packages=find_packages(include=includePackages, exclude=[]),

    install_requires=[
        # backend
        'numpy',
        'pandas',
        'matplotlib',
        'tifffile',
        'scikit-image',

        # frontend
        #'pyqt',  # does not work with pip install on m1 arm64 mac, install manually with conda
        'pyqtgraph',
        'qdarkstyle',
		'h5py',
        #'opencv-python-headless',
        'opencv-python-headless==4.5.3.56',
		#'opencv-contrib-python-headless',
		'pyserial'
    ],
    extras_require={
        # bioformats depends on python-javabridge which requires path to JDK/JRE
        'bioformats': ['python-bioformats'],
    },

    entry_points={
        'console_scripts': [
            'canvas=canvas.interface.canvasApp:main',
        ]
    },

)
