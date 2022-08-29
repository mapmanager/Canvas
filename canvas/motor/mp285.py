import serial, time, struct
import traceback

from canvas.motor.bMotor import bMotor

import logging
logger = logging.getLogger('canvasApp')

class mp285(bMotor):
    def __init__(self, port='COM4'):
        """
        port: serial port, on windows like 'COM5'

        linen sutter is COM4
        """
        super().__init__(type='mp285')

        self.swapxy = True
        self.verbose = True

        self.eol = '\r'
        self._port = port
        self._baud = 9600
        self._timeout = 5 # second

        self.stepSize = 0.04
        #self.stepSize = 0.2

        self._ser = None

        #todo: make interface so user can set this
        ok = self.setVelocity('medium')

        '''
        self.open()
        print('reading 1')
        r1 = self.ser.read(1)
        print('  r1:', r1)
        print('reading 2')
        r2 = self.ser.read(1)
        print('  r2:', r2)
        print('mp285.__init__() done')
        self.close()
        '''

    def open(self):
        if self._ser is not None:
            logger.info(f'Port already opened on port:{self._port}')
        else:
            try:
                self._ser = serial.Serial(port=self._port, baudrate=self._baud,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=self._timeout)
            #except (FileNotFoundError) as e:
            #    print('\nexception: mp285.open() FileNotFoundError')
            #    print('  e:', e)
            #    print(traceback.format_exc())
            #    raise
            except (serial.SerialException) as e:
                logger.error('serial.SerialException')
                logger.error(f'  e:{e}')
                return False
                #print(traceback.format_exc())
                #raise
            except:
                logger.error('Unknown exception')
                logger.error(traceback.format_exc())
                return False
                #raise

        return True

    def close(self):
        if self._ser is None:
            logger.warning('Serial port not opened')
        else:
            self._ser.close()
            self._ser = None

    def setVelocity(self, fastSlow, openPort=True):
        """
        fastSlow: in ('fast', 'medium', 'slow')

        Returns:
            true/false

        Note: The lower 15 bits (Bit 14 through 0) contain
        the velocity value. The high-order bit (Bit 15) is
        used to indicate the microstep-to-step resolution:
            0= 10, 1 = 50 uSteps/step

        Constant kFastVelocity = 30000
        Constant kSlowVelocity = 1500

        theVel = kFastVelocity
        //set bit 15 to 0
        theVel = theVel & ~(2^15)
        //set bit 15 to 1
        theVel = theVel | (2^15)

        Variable outType = 0 //unsigned short (16-bit) integer
        outType = outType | (2^4) //16-bit integer
        outType = outType | (2^6) //unsigned

        velocity: u-steps/second from 1000-10000
            (1000 is accurate, 7000 is not)
        """
        def set_bit(value, bit):
            return value | (1<<bit)

        if fastSlow == 'fast':
            theVelocity = 30000
        elif fastSlow == 'medium':
            theVelocity = 6000 #3000
        elif fastSlow == 'slow':
            theVelocity = 1500
        else:
            logger.warning(f'Did not understand fastSlow: {fastSlow}')
            return False

        logger.info(f'fastSlow:{fastSlow} theVelocity:{theVelocity}')

        bVelocity = '{:b}'.format(theVelocity)
        #print('before set bit 15 bVelocity:', bVelocity)

        #velb = struct.pack('H',int(theVelocity))
        theVelocity = set_bit(theVelocity, 15)

        bVelocity = '{:b}'.format(theVelocity)
        #print(' after set bit 15 bVelocity:', bVelocity)

        # > is big-endian
        # < is little endian
        # H: unsigned short
        binaryVelocity = struct.pack('<H', theVelocity)

        if openPort and not self.open():
            return False

        try:
            self._ser.write(b'V' + binaryVelocity + b'\r')
            self._ser.read(1)
        except:
            logger.error('  Unknown exception')
            logger.error(traceback.format_exc())
            return False
        finally:
            if openPort:
                self.close()

        return True

    def readPosition(self, openPort=True, verbose=True):
        if verbose:
            logger.info(f'openPort:{openPort}')

        theRet = (None, None, None)

        if openPort and not self.open():
            return theRet

        try:
            self._ser.write(b'c\r')

            resp = self._ser.read(13) # 12 +1 (3 4-byte signed long numbers + CR)
            resp = resp.rstrip() # strip of trailing '\r'

            if len(resp) == 0:
                logger.error('  Did not get resp')
            elif b'\t' in resp:
                # occasional error
                logger.error('  resp contained "\\t" resp: "{resp}"')
            elif b'%' in resp:
                # occasional error
                logger.error('  resp contained "%" resp: "{resp}"')
            else:
                # > is big-endian
                # < is little endian
                stepTuple = struct.unpack('<lll', resp) # < is little-endian
                micronList = [x*self.stepSize for x in stepTuple]
                # abb hopkins, swaping x/y
                #theRet = (micronList[0], micronList[1], micronList[2])
                theRet = (micronList[1], micronList[0], micronList[2])
        except:
            logger.error('  Unknown exception')
            logger.error(traceback.format_exc())
        finally:
            if openPort: self.close()

        # abb hopkins, swap x/y
        # _tmp = theRet[0]
        # theRet[0] = theRet[1]
        # theRet[1] = _tmp

        if verbose:
            logger.info(f'  returning: "{theRet}')
        return theRet

    # def moveto(self, direction, umDistance):
    #     return self.move(direction, umDistance)

    def move(self, direction, umDistance, openPort=True):
        """
        direction: str:  in ['left', 'right', 'front', 'back']
        umDistance: int: Not sure on units yet
        """

        logger.info(f'direction:{direction} umDistance:{umDistance}')

        theRet = (None, None, None)

        if openPort and not self.open():
            return theRet

        try:

            (x,y,z) = self.readPosition(openPort=False)
            logger.info('  original position:{x}, {y}, {z}')

            if x is None or y is None or z is None:
                logger.error('  Did not get good original position')
                return theRet

            # todo: these need to map to correct direction when looking at video
            if direction == 'left':
                y -= umDistance
            elif direction == 'right':
                y += umDistance
            elif direction == 'front':
                x += umDistance
            elif direction == 'back':
                x -= umDistance
            elif direction == 'up':
                # polarity is correct?
                z -= umDistance
            elif direction == 'down':
                # polarity is correct
                z += umDistance

            logger.info(f'  moving to new position:{x}, {y}, {z}')

            # convert um to step
            x = int(x / self.stepSize)
            y = int(y / self.stepSize)
            z = int(z / self.stepSize)

            xyzb = struct.pack('lll',x,y,z) # convert integer values into bytes
            startt = time.time() # start timer
            self._ser.write(b'm' + xyzb + b'\r') # send position to controller; add the "m" and the CR to create the move command

            cr = []
            cr = self._ser.read(1) # read carriage return and ignore
            endt = time.time() # stop timer

            if len(cr)== 0:
                logger.error(f'  did not finish moving before timeout {self._timeout} sceonds')
            else:
                logger.info(f'  completed in {round((endt-startt),2)} seconds')

            logger.info('  after move, reading again')
            theRet = self.readPosition(openPort=False)
            logger.info(f'  final position:{x}, {y}, {z}')

        except:
            logger.error('  Unknown exception')
            logger.error(traceback.format_exc())

        finally:
            if openPort:
                self.close()

        return theRet

def test_mp285():
    m = mp285()

    #m.setVelocity('fast')

    (x,y,z) = m.readPosition()
    print('  test_mp285 readPosition() x:', x, 'y:', y, 'z:', z)

    (x,y,z) = m.move('left', 500)
    print('  test_mp285 after moveto() x:', x, 'y:', y, 'z:', z)

if __name__ == '__main__':
    test_mp285()