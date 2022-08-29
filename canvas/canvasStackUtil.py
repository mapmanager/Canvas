import os
from pprint import pprint

import tifffile

from canvas.canvasLogger import get_logger
logger = get_logger(__name__)

def imsave(path, imageData, tifHeader=None, overwriteExisting=False):
    """
    Save 3d image data into file path with tif header information

    Args:
        path: full path to file to save
        imageData: 3d numpy ndarray with order (slices, x, y)
        tifHeader: dictionary with keys ['xVoxel'], ['yVoxel'], ['zVoxel'] usually in um/pixel
    """

    if os.path.isfile(path) and not overwriteExisting:
        logger.error(f'File already exists and overwriteExisting is False, path:{path}')
        return None

    # default
    resolution = (1., 1.)
    metadata = {'spacing':1, 'unit':'pixel'}

    tiffHeader_lower = {}
    for k,v in tifHeader.items():
        k = k.lower()
        tiffHeader_lower[k] = v

    if tifHeader is not None:
        xVoxel = tiffHeader_lower['xvoxel']
        yVoxel = tiffHeader_lower['yvoxel']
        zVoxel = tiffHeader_lower['zvoxel']

        resolution = (1./xVoxel, 1./yVoxel)
        metadata = {
            'spacing': zVoxel,
            'unit': tiffHeader_lower['unit'], # could be ('micron', 'um', 'pixel')
        }

        # Add all from tifHeader
        for k,v in tiffHeader_lower.items():
            #k = k.lower()
            metadata[k] = v

    # my volumes are zxy, fiji wants TZCYXS
    #volume.shape = 1, 57, 1, 256, 256, 1  # dimensions in TZCYXS order
    if len(imageData.shape) == 2:
        numSlices = 1
        numx = imageData.shape[0]
        numy = imageData.shape[1]
    elif len(imageData.shape) == 3:
        numSlices = imageData.shape[0]
        numx = imageData.shape[1]
        numy = imageData.shape[2]
    else:
        logger.error(f'Can only save 2d or 3d data, got shape: {imageData.shape}')
        return False

    dtypeChar = imageData.dtype.char
    if dtypeChar == 'e':
        # see: https://github.com/matplotlib/matplotlib/issues/15432
        logger.warning('Not saving as ImageJ .tif file (There will be no header information.')
        logger.warning('    This happend with np.float16, dtype.char is "e". np.float16 will not open in Fiji or Matplotlib')
        tifffile.imwrite(path, imageData) #, ijmetadata=ijmetadata)
    else:
        # this might change in caller?
        # this DOES change caller
        imageData = imageData.copy()
        imageData.shape = 1, numSlices, 1, numx, numy, 1

        #print('bTiffFile.imsave() is saving with metadata:')
        #print(metadata)

        logger.info('Saving metadata (tifffile will save all keys as lower case):')
        logger.info(f'  resolution:{resolution}')
        pprint(metadata)
        
        if tifffile.__version__ == '0.15.1':
            # older interface, used by aics-segmentation
            tifffile.imsave(path, imageData, imagej=True, resolution=resolution, metadata=metadata) #, ijmetadata=ijmetadata)
        else:
            # newer interface, changed on 2018.11.6
            tifffile.imwrite(path, imageData, imagej=True, resolution=resolution, metadata=metadata) #, ijmetadata=ijmetadata)

    return True
