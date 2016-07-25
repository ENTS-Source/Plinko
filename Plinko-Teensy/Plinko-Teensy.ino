#include <FastLED.h>

// Plinko configuration
#define LED_PIN       22  // The data pin for the LEDs
#define MODE_BTN_PIN  23  // The button used to change the display mode
#define PEG_PIN_START 1   // Peg pin number start. End is start + NUM_LEDS
#define BUK_PIN_START 14  // Bucket pin number start. End is start + NUM_BUCKETS
#define NUM_LEDS      9   // The number of LEDs/pegs
#define NUM_BUCKETS   5   // The number of buckets. Used to calculate which bucket was activated
#define PEG_SPARK_MIN 150 // milliseconds delay minimum when a peg is tripped
#define PEG_SPARK_MAX 250 // milliseconds delay maximum when a peg is tripped
#define PEG_SPARK_DUR 60  // milliseconds between peg 'spark' color changes
#define PEG_COOLDOWN  250 // milliseconds for a peg to not be counted once activated for points
#define BUK_COOLDOWN  5000
int pegPointValues[] = { 5, 5, 30, 30, 10, 5, 5, 20, 20 };
int bucketPointValues[] = { 10, 20, 50, 20, 10 };

// LED Configuration
#define L_BRIGHTNESS    255
#define L_TYPE          NEOPIXEL
#define L_UPD_PER_SEC   100 // Number of updates per second (used in dance mode)

// Global variables
CRGB leds[NUM_LEDS];
unsigned long pegLastChanged[NUM_LEDS];
unsigned long bucketLastChanged[NUM_BUCKETS];
CRGBPalette16 currentPalette;
TBlendType currentBlending;
bool danceMode = true; // start up in 'dance' mode
int startIndex = 0;
bool lastModeState = false;
long lastUpdate = 0; // to prevent quickly changing peg colors
bool bucketStates[NUM_BUCKETS];
int points = 0;
unsigned long lastHeartbeat = 0;

// Prototypes
void checkPalette();
void showPalette(uint8_t colorIndex);
bool debounceReadPin(int pin);
bool bucketActive(int num);
bool pegActive(int num);

void setup() {
  pinMode(13, OUTPUT);
  digitalWrite(13, HIGH);
  delay(3000); // safety delay for power up
  digitalWrite(13, LOW);

  FastLED.addLeds<L_TYPE, LED_PIN>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(L_BRIGHTNESS);

  currentPalette = RainbowColors_p;
  currentBlending = LINEARBLEND;

  // Configure pins
  for(int i = 0; i < NUM_LEDS; i++) {
    pinMode(i + PEG_PIN_START, INPUT_PULLUP);
    pegLastChanged[i] = 0;
  }
  for(int i = 0; i < NUM_BUCKETS; i++) {
    pinMode(i + BUK_PIN_START, INPUT_PULLUP);
    bucketLastChanged[i] = 0;
  }
  pinMode(MODE_BTN_PIN, INPUT_PULLUP);

  Serial.begin(9600);
}

void loop() {
  if(millis() - lastHeartbeat > 1000) {
    Serial.println("H");
    lastHeartbeat = millis(); 
  }
  
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
        if (millis() - pegLastChanged[i] >= PEG_COOLDOWN) {
          points = points + pegPointValues[i];
          Serial.println("P" + String(points));
        }
        pegLastChanged[i] = millis();
      }

      if(millis() - pegLastChanged[i] < random(PEG_SPARK_MIN, PEG_SPARK_MAX)) {
        if(millis() - lastUpdate > PEG_SPARK_DUR) {
          leds[i] = CHSV(random8(), 255, 255);
          lastUpdate = millis();
        }
      } else {
        leds[i] = CRGB::Black;
      }
    }

    // check buckets
    for(int i = 0; i < NUM_BUCKETS; i++) {
      bool isActive = bucketActive(i);
      bool wasActive = bucketStates[i];
      bucketStates[i] = isActive;
      if(isActive && !wasActive && (millis() - bucketLastChanged[i] > BUK_COOLDOWN)) {
        if(millis() - bucketLastChanged[i] > BUK_COOLDOWN) {
          points += bucketPointValues[i];
          Serial.println("F" + String(points));
        }
        bucketLastChanged[i] = millis();
        points = 0;
        break;
      }
    }

    FastLED.show();
  }
}

bool pegActive(int num) {
  return digitalReadFast(num + PEG_PIN_START) == LOW;
}

bool bucketActive(int num) {
  return debounceReadPin(num + BUK_PIN_START);
}

bool debounceReadPin(int pin) {
  if(digitalRead(pin) == LOW) {
    delay(10); // debounce
    return digitalRead(pin) == LOW;
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
