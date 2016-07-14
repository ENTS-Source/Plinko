#include <FastLED.h>

// Plinko configuration
#define LED_PIN       12  // The data pin for the LEDs
#define NUM_LEDS      4   // The number of LEDs/pegs
#define NUM_BUCKETS   5   // The number of buckets. Used to calculate which bucket was activated
#define MODE_BTN_PIN  11  // The button used to change the display mode
#define PEG_PIN_START 14  // Peg pin number start. End is start + NUM_LEDS
#define BUK_PIN_START 19  // Bucket pin number start. End is start + NUM_BUCKETS
#define PEG_SPARK_MIN 150 // milliseconds delay minimum when a peg is tripped
#define PEG_SPARK_MAX 250 // milliseconds delay maximum when a peg is tripped
#define PEG_SPARK_DUR 60  // milliseconds between peg 'spark' color changes
int bucketPointValues[] = { 10, 20, 50, 20, 10 }; // point values for each bucket

// General configuration for wiring
#define PIN_HIGH      LOW
#define BTN_TYPE      INPUT_PULLUP

// LED Configuration
#define L_BRIGHTNESS    255
#define L_TYPE          NEOPIXEL
#define L_COLOR_ORDER   GRB
#define L_UPD_PER_SEC   100 // Number of updates per second (used in display mode)

// Global variables
CRGB leds[NUM_LEDS];
long pegLastChanged[NUM_LEDS];
CRGBPalette16 currentPalette;
TBlendType currentBlending;
bool danceMode = true; // start up in 'dance' mode

void setup() {
  delay(3000); // safety delay for power up

  FastLED.addLeds<L_TYPE, LED_PIN>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(L_BRIGHTNESS);

  currentPalette = RainbowColors_p;
  currentBlending = LINEARBLEND;

  // Configure pins
  pinMode(MODE_BTN_PIN, BTN_TYPE);
  for(int i = 0; i < NUM_LEDS; i++) {
    pinMode(i + PEG_PIN_START, BTN_TYPE);
  }
  for(int i = 0; i < NUM_BUCKETS; i++) {
    pinMode(i + BUK_PIN_START, BTN_TYPE);
  }

  Serial.begin(9600);
}

int startIndex = 0;
bool lastModeState = false;
long lastUpdate = 0; // to prevent quickly changing peg colors

void loop() {
  // check for mode button
  bool modeState = debounceReadPin(MODE_BTN_PIN);
  if(modeState && modeState != lastModeState) {
    danceMode = !danceMode;

    // safety clear of LED states
    for(int i = 0; i < NUM_LEDS; i++) {
      leds[i] = CRGB::Black;
    }
    FastLED.show();
  }
  lastModeState = modeState;
  
  if(danceMode) {
    // show a colorful display on the 'pegs'
    checkPalette();
    startIndex += 1; // motion speed
    showPalette(startIndex);
    FastLED.show();
    FastLED.delay(1000 / L_UPD_PER_SEC);
  } else {
    // actually do the game logic

    // check pegs
    for(int i = 0; i < NUM_LEDS; i++) {
      if(pegActive(i)) {
        pegLastChanged[i] = millis();
      }

      if(millis() - pegLastChanged[i] < random(PEG_SPARK_MIN, PEG_SPARK_MAX)) {
        if(millis() - lastUpdate > PEG_SPARK_DUR) {
          leds[i] = CHSV(random8(), 255, random8());
          lastUpdate = millis();
        }
      } else {
        leds[i] = CRGB::Black;
      }
    }

    // check buckets
    for(int i = 0; i < NUM_BUCKETS; i++) {
      if(bucketActive(i)) {
        Serial.println(bucketPointValues[i]);
        break;
      }
    }

    FastLED.show();
  }
}

bool pegActive(int num) {
  return debounceReadPin(num + PEG_PIN_START); // TODO: Read from shift register if proven better; and maybe drop debounce?
}

bool bucketActive(int num) {
  return debounceReadPin(num + BUK_PIN_START); // TODO: Read from shift register if proven better
}

bool debounceReadPin(int pin) {
  if(digitalRead(pin) == PIN_HIGH) {
    delay(10); // debounce
    return digitalRead(pin) == PIN_HIGH;
  }
  return false;
}

// Function adapted from FastLED example "ColorPalette". Original name: FillLEDsFromPaletteColors
void showPalette(uint8_t colorIndex) {
    uint8_t brightness = 255;
    
    for(int i = 0; i < NUM_LEDS; i++) {
        leds[i] = ColorFromPalette(currentPalette, colorIndex, brightness, currentBlending);
        colorIndex += 3;
    }
}

// Function adapted from FastLED example "ColorPalette". Original name: ChangePalettePeriodically
void checkPalette() {
    uint8_t secondHand = (millis() / 1000) % 60;
    static uint8_t lastSecond = 99;
    
    if(lastSecond != secondHand) {
        lastSecond = secondHand;
        if(secondHand ==  0 || secondHand == 30) { currentPalette = RainbowColors_p;         currentBlending = LINEARBLEND;}
        if(secondHand == 10 || secondHand == 35) { currentPalette = RainbowStripeColors_p;   currentBlending = NOBLEND;}
        if(secondHand == 15 || secondHand == 40) { currentPalette = RainbowStripeColors_p;   currentBlending = LINEARBLEND;}
        if(secondHand == 20 || secondHand == 45) { currentPalette = CloudColors_p;           currentBlending = LINEARBLEND;}
        if(secondHand == 25 || secondHand == 50) { currentPalette = PartyColors_p;           currentBlending = LINEARBLEND;}
    }
}
