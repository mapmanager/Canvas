import numpy as np

from ScanImageTiffReader import ScanImageTiffReader

path = '/Users/cudmore/data/patrick/GCaMP Time Series 1.tiff'

sit = ScanImageTiffReader(path)
data = sit.data()
print(data.shape)

sliceNum = 79

oneSlice = data[sliceNum,:,:]

print(sliceNum, oneSlice.shape, np.min(oneSlice), np.max(oneSlice))
