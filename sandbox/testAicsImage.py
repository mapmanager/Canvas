"""
"""

import sys
from pprint import pprint

#import aicsimageio
#from aicsimageio.formats import FORMAT_IMPLEMENTATIONS
from aicsimageio import AICSImage

# print('FORMAT_IMPLEMENTATIONS:')
#pprint(FORMAT_IMPLEMENTATIONS)

#sys.exit(1)

path = '/Users/cudmore/data/example-oir/20190416__0001.oir'

# fails on oir, reader not found
# For potentially more information and to help debug,
# try loading the file directly with the desired file format reader
# instead of with the AICSImage object.
img = AICSImage(path)

# import aicsimageio
# this open a java bin as an app?
#img = aicsimageio.readers.BioformatsReader(path)

# this does not work
# from aicsimageio.readers.BioformatsReader import BioFile
#img = BioFile(path)

# bioformats_jar is depreciated, use this ... form
# https://github.com/tlambert03/bioformats_jar 
# import jpype
# import scyjava
# scyjava.config.endpoints.append('ome:formats-gpl:6.7.0')
# scyjava.start_jvm()
# loci = jpype.JPackage("loci")
# loci.common.DebugTools.setRootLevel("ERROR")