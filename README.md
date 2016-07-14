## ENTS Plinko

A modified version of the popular [The Price is Right](https://en.wikipedia.org/wiki/List_of_The_Price_Is_Right_pricing_games#Plinko) game.

There are two parts to this repository: The Raspberry Pi code for hosting 2 Plinko boards in a competition setup and the Teensy code for actual board.

### Teensy

The Teensy code (intended for Teensy 3.1/3.2) requires the [FastLED](http://fastled.io/) library. The code is intended to be used in conjunction with reed switches (or some other switch) in the pegs with [Neopixels](https://www.adafruit.com/category/168) in the back to light up the peg. With the puck surrounded by magnets, the reed switches are tripped and the pegs light up or "spark". The buckets at the bottom of the board can be limit switches or similar to detect the puck in the bucket.

The current iteration of the Teensy code uses a significant number of pins. Each bucket requires a pin as well as each peg. 1 pin is also reserved for the LED strip. A future version will be less invasive on the pins.

### Raspberry Pi

This is only required if 2 Plinko boards are being run against each other. The Teensy reports which bucket was scored and the Raspberry Pi detects this and displays it. 2 Plinko boards are required to run this.  