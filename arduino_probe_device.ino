/*
 * Speaker impedance measurement
 * an Arduino328p based device
 * 
 * GameInstance.com
 * 2018
 */

#include <SerialCommand.h>  // https://github.com/gameinstance/lib-arduino

static const byte CURRENT_PROBE = A0;
static const byte SIGNAL_PROBE = A1;

static const float VCC_ARDUINO = 5.05;      // volts
static const int ADC_RESOLUTION = 65536;    // units
static const int ADC_RESOLUTION_BITS = 16;  // bits

unsigned long curent_value = 0, signal_value = 0;
double curent_voltage = 0, signal_voltage = 0;

unsigned long ReadMultiDecimated(byte pin, byte bits = ADC_RESOLUTION_BITS) {
  // 
  unsigned long total = 0;
  bits -= 10;
  int N = B00000001 << (2 * bits);
  for (int i = 0; i < N; i++) {
    // 
    total += analogRead(pin);
  }
  return total >> bits;
}

double GetVoltage(unsigned long value, unsigned long resolution = ADC_RESOLUTION, float vcc = VCC_ARDUINO) {
  // 
  return (double) value / (resolution - 1) * vcc;
}

class MySerialCommand : public SerialCommand {

  public:

    /// default constructor
    MySerialCommand() : SerialCommand() {
      // 
    };
    /// destructor
    virtual ~MySerialCommand() {
      // 
    };


  protected:

    /// runs the command
    bool Run() {
      // 
      switch (data[0]) {
        // 
        case '?':
          // identify
          Identify();
          return true;
        case 'p':
          // probes the voltages
          Probe();
          return true;
      }
      // unknown command
      Serial.println("Unknown command!");
      return false;
    };
    /// identifies the app
    void Identify() {
      // 
      Serial.println("Speaker Impedance Measurement - GameInstance.com");
    };
    /// proves the voltages
    bool Probe() {
      // 
      delay(250);
      curent_value = ReadMultiDecimated(CURRENT_PROBE);
      curent_voltage = GetVoltage(curent_value);
      signal_value = ReadMultiDecimated(SIGNAL_PROBE);
      signal_voltage = GetVoltage(signal_value);
      Serial.print(curent_voltage, 10);
      Serial.print(" ");
      Serial.println(signal_voltage, 10);
    };
};

MySerialCommand sc;

void setup() {
  // 
  for (int i = 2; i <= 13; i ++) {
    // 
      pinMode(i, OUTPUT);
      digitalWrite(i, LOW);
  }
  pinMode(CURRENT_PROBE, INPUT);
  pinMode(SIGNAL_PROBE, INPUT);
  Serial.begin(9600);
}

void loop() {
  // 
  if (sc.Read()) {
    // 
    sc.Execute();
  }
}
