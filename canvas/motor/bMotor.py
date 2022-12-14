# Author: RObert Cudmore
# Date: 20191208

"""
An abstract class to define a motor interface

This needs to be derived for each type of motor, e.g. (prior, mp285, bruker)

See bPrior for an example
"""

class bMotor(object):
    def __init__(self, type=None):
        self._type = type
        self.swapxy = False

    def readPosition(self):
        """
        Returns:
            (x,y): Tuple of float withx and y position, float
        """
        return None, None, None

    def move(self, direction, umDistance):
        """
        - move stage
        - return self.readPosition()
        """
        theRet = self.readPosition()
        return theRet
    
    def moveto(self, x=None, y=None, z=None):
        pass
