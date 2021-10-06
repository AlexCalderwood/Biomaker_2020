/*
 * WIRING INSTRUCTIONS
 * 
 * CONNECT PIN 3 TO GROUND VIA 1k+ RESISTOR
 * CONNECT PIN 3 TO +5V VIA NORMALLY-OPEN LIMIT-SWITCH
 * 
 */

int switchPin = 8;
bool DOOR_CLOSED = false;
bool CURRENT_STATE = false;
int debounce_period = 50;  //ms
long last_toggle;

void setup() {
  Serial.begin(9600);
  pinMode(switchPin, INPUT);  // MUST SET AS INPUT TO AVOID SINKING FATAL CURRENT THROUGH PIN
}

void loop() {
  // put your main code here, to run repeatedly:
  CURRENT_STATE = digitalRead(switchPin);
  if (CURRENT_STATE != DOOR_CLOSED && (millis()-last_toggle) >= debounce_period){
    DOOR_CLOSED = CURRENT_STATE;  // Only read when value changes
    last_toggle = millis();  // To deal with debounce of the switch
    Serial.print("Door closed: ");
    Serial.println(DOOR_CLOSED);
  }
  
}
