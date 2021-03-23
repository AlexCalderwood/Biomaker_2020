#include <PID_v1.h>

int HP_ON_PIN = 7;
int HP_OFF_PIN = 8;
int NTC_PIN = A0; 

float yL = 12.1;
float yU = 49.9;
float xL = 648.0;
float xU = 265.0;

float resistance;
double target_temp = 22;
double current_temp;
double PIDoutput;
bool heater_state;

int windowSize = 5000;
unsigned long windowStartTime;

//Specify the links and initial tuning parameters
PID myPID(&current_temp, &PIDoutput, &target_temp, 2, 5, 1, DIRECT);


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


void setup()
{
  Serial.begin(9600);

  // Assign pin functions
  pinMode(NTC_PIN, INPUT);
  pinMode(HP_ON_PIN, OUTPUT);
  pinMode(HP_OFF_PIN, OUTPUT);
  // Set heatpump pins to low just in case
  digitalWrite(HP_ON_PIN, LOW);
  digitalWrite(HP_OFF_PIN, LOW);

  // Start the PID clock
  windowStartTime = millis();

  // Assign the PID cycle period (macroscopic)
  myPID.SetOutputLimits(0, windowSize);

  // Turn the PID on
  myPID.SetMode(AUTOMATIC);
}


void loop()
{
  resistance = analogRead(NTC_PIN);
  current_temp = float_map(resistance, xL, xU, yL, yU);
  Serial.print("Res: ");
  Serial.print(resistance);
  Serial.print(", C_tmp: ");
  Serial.print(current_temp);
  
  if (Serial.available() > 0) {
    target_temp = Serial.parseInt();
    while (Serial.available() > 0) {
      Serial.read();
    }
  }

  Serial.print(", T_tmp: ");
  Serial.print(target_temp);

  myPID.Compute();

  Serial.print(", PIDOut: ");
  Serial.print(PIDoutput);

  unsigned long now = millis();
  if (now - windowStartTime > windowSize)
  { // Reset the starttime of the current cycle
    windowStartTime = now;
  }
  if (PIDoutput > now - windowStartTime) {
    // If we are in the HIGH part of the cycle
    if (digitalRead(HP_OFF_PIN) != HIGH) {
      // Other output MUST BE LOW before writing this, to avoid shorting H-bridge
      digitalWrite(HP_ON_PIN, HIGH);
    }
    digitalWrite(HP_OFF_PIN, LOW);
    Serial.print(", HIGH");
  }
  else {
    // If we are in the HIGH part of the cycle
    if (digitalRead(HP_ON_PIN) != HIGH) {
      // Other output MUST BE LOW before writing this, to avoid shorting H-bridge
      digitalWrite(HP_OFF_PIN, HIGH);
    }
    digitalWrite(HP_ON_PIN, LOW);
    Serial.print(", LOW");
  }
  Serial.println();
}
