from time import sleep_ms

MY_ALTITUDE = 9.0  # metres above mean sea level (AMSL)

READ_INTERVAL = 5000  # milliseconds


class MPL115A1:
    """Read pressure and temperature from MPL115A1 SPI sensor.

    Adapted from https://github.com/FaBoPlatform/FaBoBarometer-MPL115-Python

    Sources:
    http://www.nxp.com/assets/documents/data/en/data-sheets/MPL115A1.pdf
    https://learn.adafruit.com/micropython-hardware-spi-devices/spi-master.

    As shown in section 3.6 of the datasheet, each 1-byte command is followed
    by reading a 1-byte value (during which the master sends a dummy 0x00).

    After a sequence of commands and reads, an extra 0x00 byte is sent.

    The whole sequence is contained between CS enable and CS disable.

    Constants have been defined for the sequence of commands and dummy
    bytes to read coefficients (CMD_COEFS), start measurement (CMD_START)
    and read pressure and temperature data (CMD_DATA).
    """

    CMD_COEFS = bytearray(b'\x88\x00\x8A\x00\x8C\x00\x8E\x00\x90\x00\x92\x00\x94\x00\x96\x00\x00')
    CMD_START = bytearray(b'\x24\x00')
    CMD_DATA = bytearray(b'\x80\x00\x82\x00\x84\x00\x86\x00\x00')

    def __init__(self, spi, cs, altitude=0.0):
        self.cs = cs
        self._spi_enable(False)
        self.spi = spi
        self._get_coefficients()
        self.P = 0  # measured pressure at observer's altitude
        self.P0 = 0  # calculated pressure at mean sea level
        self.T = 0  # measured temperature
        self.altitude = altitude

    def _spi_enable(self, b=True):
        self.cs.value(0) if b else self.cs.value(1)

    def _spi_disable(self):
        self._spi_enable(False)

    def _convert_data(self, lsb, msb):
        value = lsb | (msb << 8)
        if (value & (1 << 16 - 1)):
            value -= (1 << 16)
        return value

    def _get_coefficients(self):
        data = bytearray(len(self.CMD_COEFS))
        self._spi_enable(True)
        self.spi.write_readinto(self.CMD_COEFS, data)
        self._spi_enable(False)
        self.a0 = self._convert_data(data[3], data[1])
        self.b1 = self._convert_data(data[7], data[5])
        self.b2 = self._convert_data(data[11], data[9])
        self.c12 = self._convert_data(data[15], data[13])
        self.a0 = float(self.a0) / (1 << 3)
        self.b1 = float(self.b1) / (1 << 13)
        self.b2 = float(self.b2) / (1 << 14)
        self.c12 = float(self.c12) / (1 << 24)

    def take_readings(self):
        data = bytearray(len(self.CMD_DATA))
        self._spi_enable(True)
        self.spi.write(self.CMD_START)
        self._spi_enable(False)
        sleep_ms(3)
        self._spi_enable(True)
        self.spi.write_readinto(self.CMD_DATA, data)
        self._spi_enable(False)
        padc = ((data[1] << 8) | data[3]) >> 6
        tadc = ((data[5] << 8) | data[7]) >> 6
        pcomp = self.a0 + (self.b1 + self.c12 * tadc) * padc + self.b2 * tadc
        self.P = pcomp * ((1150.0 - 500.0) / 1023.0) + 500.0
        self.P0 = self.P / pow(1.0 - (self.altitude / 44330.0), 5.255)
        self.T = 25.0 - (tadc - 512.0) / 5.35

def main(barometer):
    while True:
        barometer.take_readings()
        print('T: {t:.1f}C  P: {p:.0f}kPa  P0: {p0:.0f}kPa'.
              format(t=barometer.T, p=barometer.P, p0=barometer.P0))
        sleep_ms(READ_INTERVAL)

if __name__ == '__main__':
    from machine import Pin, SPI
    spi = SPI(0)
    spi.init(baudrate=1000000)
    barometer = MPL115A1(spi, Pin(22, Pin.OUT), altitude=MY_ALTITUDE)
    main(barometer)