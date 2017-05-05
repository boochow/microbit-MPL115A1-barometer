# MPL115A1 barometer for the BBC micro:bit

MicroPython program for the BBC micro:bit that displays pressure and temperature readings from the NXP MPL115A1 SPI-connected sensor.

## Credits

The program was adapted for the micro:bit from this code for the I2C version of the sensor (MPL115A2): https://github.com/FaBoPlatform/FaBoBarometer-MPL115-Python

## Usage

Connect the MPL115A1 to the micro:bit.  The default micro:bit SPI pins are shown below, but you can select different pins in the program.

MPL115A1 pin | micro:bit pin
-|-
SCLK | 13
MISO | 14
MOSI | 15
CS | 16
VDD | 3V
GND | GND

Edit the program to set `MY_ALTITUDE` to your altitude (metres above mean sea level).

Flash the program onto the micro:bit.

Check the values displayed:

- Temperature `T` should be sensible.
- Pressure `P` should be 1000hPa plus or minus 100.
- Pressure `P0` should be lower than `P`.

## Notes

If you are using a ready-made MPL115A1 breakout board, the following connections may already have been taken care of.  If not, connect the pins as shown.

MPL115A1 pin | connections
-|-
CAP | 1uF capacitor to GND
SHDN | VDD

The MPL115A1 datasheet says ...

> The sensor die is sensitive to light exposure. Direct light exposure through the port hole can lead to varied accuracy of pressure
measurement. Avoid such exposure to the port during normal operation.

Two items need further investigation:

- Forum threads about the MPL115A1  somewhere that claimed the temperature calculation algorithm in the datasheet is wrong, giving consistently low readings.  See https://github.com/hackscribble/microbit-MPL115A1-barometer/issues/1

- This version of the code retains the formula for calculating sea level pressure (P0) that was used in the original program.  It is different from that shown in source [3] below, which factors in temperature as well as altitude.

## History

#### 1.0 (5 May 2017)

First version.


## Sources

1. Datasheet: http://www.nxp.com/assets/documents/data/en/data-sheets/MPL115A1.pdf

2. Background on MicroPython SPI: https://learn.adafruit.com/micropython-hardware-spi-devices/spi-master.

3. Information about adjusting pressure for altitude: http://keisan.casio.com/exec/system/1224575267
