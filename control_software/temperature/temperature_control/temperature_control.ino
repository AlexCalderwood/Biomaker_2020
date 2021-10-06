
// Pinout
int COLD_PIN = 7;  // Pin to set high to make pump cool object
int HOT_PIN = 8;  // Pin to set high to make pump heat object
int NTC_OBJ_PIN = A0;  // Temperature sensor at object

// Control flags
bool PUMP_ON = true;  // Control flag for pumping or not
bool HEAT_ON = false;  // Control flag for heating or cooling (only takes effect when PUMP_ON is true)

// Hysteretic control reduces flicker, and therefore peltier fatigue (LARGE HYSTERESIS IS ADVISED, e.g. <0.5Hz flicker)
// All temperatures in degrees CELSIUS
float objTemp;  // Measured object temperature
float targetTemp = 25.0;  // Temperature to aim for
// Cutoff offsets should lie within the Trigger offsets
float hotCutoff = targetTemp + 0.0;  // Offset from target temperature above which heating will stop
float coldCutoff = targetTemp - 0.25; // Offset from target temperature below which cooling will stop
// Triggers represent maximum and minimum acceptable temperatures for target
float hotTrigger = targetTemp - 0.75; // Offset from target temperature below which heating will start
float coldTrigger = targetTemp + 0.5; // Offset from target temperature above which cooling will start

float extremeHotLimit = 55.0;// Upper operating temp for peltier, above this it will shut down (e.g. thermal runaway)
float hotLimit = 50.0; // Upper temperature limit for heating, peltier will not heat object beyond this limit
float coldLimit = -5.0; // Lower temperature limit for cooling, peltier will not cool object beyond this limit

float probeRes;  // Temperature probe resistance

// Assuming linear relationship over short range
float yL = 12.1;
float yU = 49.9;
float xL = 648.0;
float xU = 265.0;

float float_map(float x, float xL, float xU, float yL, float yU) {
  // Maps the value of x to the upper and lower Y bounds, in linear relation to the upper and lower X bounds.
  // Returns values as floats to n d.p., and can extrapolate beyond bounds.
  if (((xU-xL) > 0.01) or ((xU-xL) < -0.01)){
    return (((yU-yL)/(xU-xL)) * (x-xL) + yL);
  }
  else {
    return -100000000;
  }
  
}


void setup() {
  Serial.begin(9600);
  pinMode(COLD_PIN, OUTPUT);
  pinMode(HOT_PIN, OUTPUT);
  pinMode(NTC_OBJ_PIN, INPUT);
  digitalWrite(COLD_PIN, LOW);
  digitalWrite(HOT_PIN, LOW);
}

void loop() {
  // put your main code here, to run repeatedly:

  probeRes = analogRead(NTC_OBJ_PIN);
  objTemp = float_map(probeRes, xL, xU, yL, yU);
  
  if (objTemp > coldTrigger) {
    // Way above target temperature
    PUMP_ON = true;
    HEAT_ON = false;
  } else if (objTemp < hotTrigger) {
    // Way below target temperature
    PUMP_ON = true;
    HEAT_ON = true;
  } else if (objTemp > hotCutoff and HEAT_ON) {
    // If object is too hot and being heated
    PUMP_ON = false;
  } else if (objTemp < coldCutoff and not HEAT_ON) {
    // If object is too cold and being cooled
    PUMP_ON = false;
  }

  if ((objTemp > hotLimit and HEAT_ON) or (objTemp < coldLimit and not HEAT_ON)) {
    // If peltier is trying to heat past hotLimit or cool past coldLimit, it should stop trying (trying to recover is OK).
    PUMP_ON = false;
  }
  if (objTemp > extremeHotLimit) {
    // Pump shuts off above this limit to avoid possible thermal runaway
    PUMP_ON = false;
  }

  if (PUMP_ON) {
    if (HEAT_ON) {
      digitalWrite(COLD_PIN, LOW);
      delay(1);
      digitalWrite(HOT_PIN, HIGH);
    } else {
      digitalWrite(HOT_PIN, LOW);
      delay(1);
      digitalWrite(COLD_PIN, HIGH);
    }
  } else {
    digitalWrite(COLD_PIN, LOW);
    digitalWrite(HOT_PIN, LOW);
  }

  Serial.print("Target: ");
  Serial.print(targetTemp);
  Serial.print(", ");
  Serial.print("Object: ");
  Serial.print(objTemp);
  Serial.print(", ");
  Serial.print("Pump on: ");
  Serial.print(PUMP_ON);
  Serial.print(", ");
  Serial.print("Heat on: ");
  Serial.println(HEAT_ON);
  delay(500);
  
}
