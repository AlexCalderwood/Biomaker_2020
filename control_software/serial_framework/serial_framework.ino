/* 
 *  Serial Framework
 *  
 *  Features:
 *  4-channel light control
 *  Limit switch safety
 *  6 temperature sensors
 *  Simple overhead peltier control
 *  Advanced 2-channel bed peltier control
 *  serial comnmunication with Raspberry Pi
 *  Display live data to touch screen(?)
 *  
 *  Process:
 *  Repeatedly log temperatures
 *  Adjust peltier operation to achieve target temperatures
 *  Check limit-switch status
 *  Set light parameters
 *  Send data to touchscreen(?)
 *  Run fluorescence if necessary(?)
 *  Wait for request from pi
 *  Respond to request from pi
 */


// Pin definitions

int TIC0_PIN = A0;      // Roof TIC
int TIC1_PIN = A1;      // Bed TIC
int TIC2_PIN = A2;      // Bed TIC
int TIC3_PIN = A3;      // Bed TIC
int TIC4_PIN = A4;      // Bed TIC
int TIC5_PIN = A5;      // Bed TIC
int BED_PLR1A_PIN = 1;  // Bed PLR 1 pin A
int BED_PLR1B_PIN = 2;  // Bed PLR 1 pin B
int BED_PLR2A_PIN = 3;  // Bed PLR 2 pin A
int BED_PLR2B_PIN = 4;  // Bed PLR 2 pin B
int BLUE_PIN = 6;       // Blue LED control pin (255 = OFF)
int LS_PIN = 8;         // Limit switch pin
int IR_PIN = 9;         // IR LED control pin (255 = OFF)
int WHITE_PIN = 10;     // White LED control pin (255 = OFF)
int RED_PIN = 11;       // Red LED control pin (255 = OFF)
int ROOF_PLR_PIN = 12;  // Roof peltier control pin (HIGH = ON)


// Definitions for target parameters

int target_temp;
int B_intensity;
int I_intensity;
int W_intensity;
int R_intensity;
bool ACTIVATE_CFI;


int ml_intensity;
int al_intensity;
int al_duration;  // (s)
int al_kaustki_duration;  // (s)
int sp_intensity;
int sp_duration;  // (10s of ms)
int rf_intensity;  // Red flash intensity
int rf_duration;  // Red flash duration (ms)
int da_time;  // dark adjustment time (minutes)
int sp_period;  // time between sps after AL reengaged (s)
int sp_repeat_duration; // time for periodic SPs to continue


// Definitions for measured parameters

int temp0;
int temp1;
int temp2;
int temp3;
int temp4;
int temp5;

int read_temperature(int temp_pin) {
  // Reads temperature from Temperature IC
  int raw = analogRead(temp_pin);
  return (raw - 2100.7)/(-10.791);  // Derived from least-squares fit (from excel) of LMT86 data between 0 and 40 degrees C
}

void update_data(){
  // Amalgamates data from all local sensors
  temp0 = read_temperature(TIC0_PIN);
  temp1 = read_temperature(TIC1_PIN);
  temp2 = read_temperature(TIC2_PIN);
  temp3 = read_temperature(TIC3_PIN);
  temp4 = read_temperature(TIC4_PIN);
  temp5 = read_temperature(TIC5_PIN);
}


// Definitions for limit switch

bool DOOR_CLOSED = false;
bool CURRENT_STATE = false;
unsigned long last_toggle;

bool update_limit_switch() {
  int debounce_period = 50;  //ms
  CURRENT_STATE = digitalRead(LS_PIN);
  if (CURRENT_STATE != DOOR_CLOSED && (millis()-last_toggle) >= debounce_period){
    DOOR_CLOSED = CURRENT_STATE;  // Only read when value changes
    last_toggle = millis();  // To deal with debounce of the switch
  }
}


// Definitions for serial communication

int received_bytes;
byte incomingByte;
unsigned long receive_time;
unsigned long last_received;  // Time most recent byte was received
int serial_timeout = 500;  // Time until message is presumed dead and buffer (data array) is emptied
int flushed_bytes;
byte request[25] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
// Request is initialised as 255 which is overwritten as correct data comes in, or not if the request times out

void interpret_request(){
  if (request[0] != 0xFF) target_temp = 255 - (int) request[19];
  if (request[1] != 0xFF) B_intensity = 255 - (int) request[20];
  if (request[2] != 0xFF) I_intensity = 255 - (int) request[21];
  if (request[3] != 0xFF) R_intensity = 255 - (int) request[22];
  if (request[4] != 0xFF) W_intensity = 255 - (int) request[23];
  if (request[5] != 0xFF) W_intensity = (bool) request[23];
}

void send_ack() {
  Serial.write(request, sizeof(request));
  Serial.write(temp0);
  Serial.write(temp1);
  Serial.write(temp2);
  Serial.write(temp3);
  Serial.write(temp4);
  Serial.write(temp5);
  Serial.write((unsigned long)(millis()- receive_time));
  Serial.write(flushed_bytes);
}

int flush_serial() {
  // Flush the rest of the buffer by reading it all to nowhere
  int buffer_delay = 2;  // ms for host to write byte to buffer - will vary with connected device!
  
  int flushed_bytes = 0;
  delay(buffer_delay);
  while (Serial.available() > 0) {
    flushed_bytes += 1;
    Serial.read();
    delay(buffer_delay);
  }
  return flushed_bytes;
}


// CONTROL FUNCTIONS


void update_bed_peltier_control(int targetTemp, int objTemp, int pinA, int pinB) {
  // ONLY VALID FOR BED PELTIERS - SEE update_roof_peltier_control for roof control function

  bool PUMP_ON;
  bool HEAT_ON;
  
  float hotCutoff = targetTemp + 0.0;  // Offset from target temperature above which heating will stop
  float coldCutoff = targetTemp - 0.25; // Offset from target temperature below which cooling will stop
  // Triggers represent maximum and minimum acceptable temperatures for target
  float hotTrigger = targetTemp - 0.75; // Offset from target temperature below which heating will start
  float coldTrigger = targetTemp + 0.5; // Offset from target temperature above which cooling will start
  
  float extremeHotLimit = 55.0;// Upper operating temp for peltier, above this it will shut down (e.g. thermal runaway)
  float hotLimit = 50.0; // Upper temperature limit for heating, peltier will not heat object beyond this limit
  float coldLimit = -5.0; // Lower temperature limit for cooling, peltier will not cool object beyond this limit
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
      digitalWrite(pinA, LOW);
      delay(1);
      digitalWrite(pinB, HIGH);
    } else {
      digitalWrite(pinB, LOW);
      delay(1);
      digitalWrite(pinA, HIGH);
    }
  } else {
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, LOW);
  }
}

bool OVERHEAT;
void update_roof_peltier_control(int targetTemp, int objTemp, int plrPin) {
  // ONLY VALID FOR ROOF PELTIERS - SEE update_bed_peltier_control for bed control function

  bool PUMP_ON;
  float coldCutoff = targetTemp - 0.25; // Offset from target temperature below which cooling will stop
  // Trigger represents maximum acceptable temperatures for target
  float coldTrigger = targetTemp + 0.5; // Offset from target temperature above which cooling will start
  
  float extremeHotLimit = 45.0;// Upper operating temp for peltier, above this it will shut down lights and peltier (e.g. thermal runaway)
  float coldLimit = -5.0; // Lower temperature limit for cooling, peltier will not cool object beyond this limit
  
  if (objTemp > coldTrigger) {
  
    // Way above target temperature
    PUMP_ON = true;
  } else if (objTemp < coldCutoff) {
    // If object is too cold and being cooled
    PUMP_ON = false;
  }

  if (objTemp < coldLimit) {
    // If peltier is trying to cool past coldLimit, it should stop trying.
    PUMP_ON = false;
  }
  if (objTemp > extremeHotLimit) {
    // Pump shuts off above this limit to avoid possible thermal runaway
    PUMP_ON = false;
    OVERHEAT = true;
  }

  if (PUMP_ON) {
    digitalWrite(ROOF_PLR_PIN, HIGH);
  } else {
    digitalWrite(ROOF_PLR_PIN, LOW);
  }
}

void set_lights() {
  // Sets the lights based on target light values
  analogWrite(BLUE_PIN, B_intensity);
  analogWrite(IR_PIN, I_intensity);
  analogWrite(WHITE_PIN, W_intensity);
  analogWrite(RED_PIN, R_intensity);

  if (OVERHEAT) {
    // If module is overheating seriously, turn off all the lights
    analogWrite(BLUE_PIN, 255);
    analogWrite(IR_PIN, 255);
    analogWrite(WHITE_PIN, 255);
    analogWrite(RED_PIN, 255);
    // TRIP SAFETY - REQUIRE A SAFETY RESET
  }
}

void activate_CFI() {
  int CFI_state = 0;

  unsigned long CFI_start;
  unsigned long rf_start;
  unsigned long sp_start;
  int red_delay;
  int sp_delay;
  unsigned long al_start;
  
  while ((not OVERHEAT) and (CFI_state != 200) and (DOOR_CLOSED)) {
    switch (CFI_state) {
        
      case 0:  // Dark adaption initiated 
        analogWrite(BLUE_PIN, ml_intensity);
        analogWrite(IR_PIN, 255);
        analogWrite(WHITE_PIN, 255);
        analogWrite(RED_PIN, 255);
        CFI_start = millis();
        CFI_state = 10;
        break;
        
      case 10: // Wait for dark adaption timeout
        if ((unsigned long)(millis() - CFI_start) > (da_time * 3600 * 1000)) {
          CFI_state = 20;
        }
        break;
        
      case 20:  // Trigger red light
        analogWrite(RED_PIN, rf_intensity);
        rf_start = millis();
        CFI_state = 30;
        break;
        
      case 30: // Wait for red light timout
        if ((unsigned long)(millis() - rf_start) > rf_duration) {
          analogWrite(RED_PIN, 255);
          CFI_state = 40;
        }
        break;

      case 40: // Wait a short time after red is gone
        red_delay = 50;  // ms
        if ((unsigned long)(millis() - rf_start) > (rf_duration + red_delay)) {
          CFI_state = 50;
        }
        break;

      case 50:  // Activate first SP
        analogWrite(BLUE_PIN, sp_intensity);
        sp_start = millis();
        CFI_state = 60;
        break;

      case 60:  // Wait for SP timeout
        if ((unsigned long)(millis() - sp_start) > sp_duration) {
          analogWrite(BLUE_PIN, 255);
          CFI_state = 70;
        }
        break;

      case 70:  // Wait short time after sp
      sp_delay = 50;  // ms
        if ((unsigned long)(millis() - sp_start) > (sp_duration + sp_delay)) {
          CFI_state = 80;
        }
        break;

      case 80:  // Trigger AL
        analogWrite(BLUE_PIN, al_intensity);
        al_start = millis();
        CFI_state = 90;

      case 90:  // Wait out until end of SP duration
        if ((unsigned long)(millis() - al_start) > (al_duration)) {
          analogWrite(BLUE_PIN, 255);
          CFI_state = 200; // Abort CFI procedure
        }
        break;
      update_data();
      update_bed_peltier_control(target_temp, temp5, BED_PLR1A_PIN, BED_PLR1B_PIN);
      update_roof_peltier_control(target_temp,temp0, ROOF_PLR_PIN);
      update_limit_switch();  
    }
    analogWrite(BLUE_PIN, 255);
    analogWrite(IR_PIN, 255);
    analogWrite(WHITE_PIN, 255);
    analogWrite(RED_PIN, 255);
    ACTIVATE_CFI = false;
  }
}


void setup() {
  
  pinMode(TIC0_PIN, INPUT);
  pinMode(TIC1_PIN, INPUT);
  pinMode(TIC2_PIN, INPUT);
  pinMode(TIC3_PIN, INPUT);
  pinMode(TIC4_PIN, INPUT);
  pinMode(TIC5_PIN, INPUT);
  pinMode(BED_PLR1A_PIN, OUTPUT);
  pinMode(BED_PLR1B_PIN, OUTPUT);
  pinMode(BED_PLR2A_PIN, OUTPUT);
  pinMode(BED_PLR2B_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  pinMode(LS_PIN, INPUT);
  pinMode(IR_PIN, OUTPUT);
  pinMode(WHITE_PIN, OUTPUT);
  pinMode(RED_PIN, OUTPUT);
  pinMode(ROOF_PLR_PIN, OUTPUT);

  digitalWrite(BED_PLR1A_PIN, LOW);
  digitalWrite(BED_PLR1B_PIN, LOW);
  digitalWrite(BED_PLR2A_PIN, LOW);
  digitalWrite(BED_PLR2B_PIN, LOW);
  pinMode(BLUE_PIN, 255);
  pinMode(IR_PIN, 255);
  pinMode(WHITE_PIN, 255);
  pinMode(RED_PIN, 255);
  digitalWrite(ROOF_PLR_PIN, LOW);

  Serial.begin(9600);
}


void loop() {

  update_data();
  update_bed_peltier_control(target_temp, temp5, BED_PLR1A_PIN, BED_PLR1B_PIN);
  update_roof_peltier_control(target_temp,temp0, ROOF_PLR_PIN);
  update_limit_switch();
  if (DOOR_CLOSED) {
    set_lights();
  } else {
    analogWrite(BLUE_PIN, 255);
    analogWrite(IR_PIN, 255);
    analogWrite(WHITE_PIN, 255);
    analogWrite(RED_PIN, 255);
  }
  // update_display();
  if (ACTIVATE_CFI) {
    activate_CFI();
  }

  int expected_bytes = sizeof(request);  // Number of bytes long the request will be

  if (received_bytes == expected_bytes) { // Update states for newly receieved request
    flushed_bytes = flush_serial();  // Clear any remaining (eroneous) bytes from the buffer and log how many cleared
    interpret_request();  // Read new instructions from request
    send_ack();  // Send return data
    received_bytes = 0;
    for (int i = 0; i<sizeof(request); i++) {
      request[i] = 0xFF;  // Reset data to be all 255
    }
  }
  else if (Serial.available() > 0) { // Request is being received (ongoing)
    if (received_bytes == 0) {
      // This code only runs once per request
      receive_time = millis();  // Time when first byte of message was received
    }
    // read the incoming byte:
    incomingByte = Serial.read();
    if (incomingByte != 10) {  // If incoming byte isn't a new-line character
      request[received_bytes] = incomingByte;
      received_bytes = received_bytes + 1;
      last_received = millis();
    }
  }
  else if (received_bytes > 0 and ((unsigned long)(millis()-last_received)) > serial_timeout) {
    received_bytes = expected_bytes; // Jump to the processing, assume nothing else is coming
  }
  
}
