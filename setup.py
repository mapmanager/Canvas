from setuptools import setup, find_packages

includePackages = ['canvas', 'canvas.*', 'canvas.interface']

setup(
    name='Canvas',
    version='0.1.1',
	description='',
	long_description='',
	author='Robert Cudmore',
	author_email='robert.cudmore@gmail.com',
	url='https://github.com/cudmore/canvas',
    keywords=['in vivo', 'two photon', 'laser scanning microscopy', 'microscopy'],
    
    packages=find_packages(include=includePackages, exclude=[]),

    install_requires=[
        # backend
        'numpy',
        'pandas',
        'matplotlib',
        'tifffile',
        'scikit-image',
        'python-bioformats',  # includes python-javabridge
        'python-javabridge',
        # frontend
        #'pyqt',  # does not work with pip install on m1 arm64 mac, install manually with conda
        'pyqtgraph',
        'qdarkstyle',
		'h5py',

		'pyserial'
        'opencv-python-headless==4.5.3.56',
		#'opencv-contrib-python-headless',
    ],
    # extras_require={
    #     # bioformats depends on python-javabridge which requires path to JDK/JRE
    #     'bioformats': ['python-bioformats'],
    # },

    entry_points={
        'console_scripts': [
            'canvas=canvas.interface.canvasApp:main',
        ]
    },

)
