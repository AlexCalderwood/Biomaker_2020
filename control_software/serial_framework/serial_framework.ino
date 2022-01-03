/*
    Serial Framework

    Features:
    4-channel light control
    Limit switch safety
    6 temperature sensors
    Simple overhead peltier control
    Advanced 2-channel bed peltier control
    serial comnmunication with Raspberry Pi
    Display live data to touch screen(?)

    Process:
    Repeatedly log temperatures
    Adjust peltier operation to achieve target temperatures
    Check limit-switch status
    Set light parameters
    Send data to touchscreen(?)
    Run fluorescence if necessary(?)
    Wait for request from pi
    Respond to request from pi
*/


// Pin definitions

int TIC0_PIN = A0;      // Roof TIC
int TIC1_PIN = A1;      // Bed TIC
int TIC2_PIN = A2;      // Bed TIC
int TIC3_PIN = A3;      // Bed TIC
int TIC4_PIN = A4;      // Bed TIC
int TIC5_PIN = A5;      // Bed TIC
int BED_PLR1A_PIN = 1;  // Bed PLR 1 pin A (Right, cold)
int BED_PLR1B_PIN = 2;  // Bed PLR 1 pin B (Right, hot)
int BED_PLR2A_PIN = 3;  // Bed PLR 2 pin A (Left, cold)
int BED_PLR2B_PIN = 4;  // Bed PLR 2 pin B (Left, hot)
int BLUE_PIN = 6;       // Blue LED control pin (255 = OFF)
int LS_PIN = 8;         // Limit switch pin
int IR_PIN = 9;         // IR LED control pin (255 = OFF)
int WHITE_PIN = 10;     // White LED control pin (255 = OFF)
int RED_PIN = 11;       // Red LED control pin (255 = OFF)
int ROOF_PLR_PIN = 12;  // Roof peltier control pin (HIGH = ON)
int LED_POWER_PIN = 7; // 48V Powersupply relay (Normally-Open)


// Definitions for target parameters

float target_temp = 23.0;
int B_intensity = 255;
int I_intensity = 255;
int W_intensity = 255;
int R_intensity = 255;
int ACTIVATE_CFI = 0;
int ENABLE_LEDs = 1;            // Controls mains relay for LEDs
int ENABLE_BPLRs = 0;           // Controls bed-peltiers (forces them into 'off' state if false)

// Definitions for measured parameters

float temp0;
float temp1;
float temp2;
float temp3;
float temp4;
float temp5;

float read_temperature(int TIC_PIN, float Vref = 5.00, float m = -2.28, float c = 442.0) {
  int raw_input = analogRead(TIC_PIN);
  float temperature = (raw_input - c) / m;
  return temperature;

}

void update_data() {
  // Amalgamates data from all local sensors
  temp0 = read_temperature(TIC0_PIN, 4.98);
  temp1 = read_temperature(TIC1_PIN, 4.98);
  temp2 = read_temperature(TIC2_PIN, 4.98);
  temp3 = read_temperature(TIC3_PIN, 4.98);
  temp4 = read_temperature(TIC4_PIN, 4.98);
  temp5 = read_temperature(TIC5_PIN, 4.98);
  /*
    Serial.print("Temperatures: ");
    Serial.print(temp0);
    Serial.print(", ");
    Serial.print(temp1);
    Serial.print(", ");
    Serial.print(temp2);
    Serial.print(", ");
    Serial.print(temp3);
    Serial.print(", ");
    Serial.print(temp4);
    Serial.print(", ");
    Serial.println(temp5);
  */
}


// Definitions for limit switch

bool DOOR_CLOSED = false;
bool CURRENT_STATE = false;
unsigned long last_toggle;

bool update_limit_switch() {
  int debounce_period = 50;  //ms
  CURRENT_STATE = digitalRead(LS_PIN);
  if (CURRENT_STATE != DOOR_CLOSED && (millis() - last_toggle) >= debounce_period) {
    DOOR_CLOSED = CURRENT_STATE;  // Only read when value changes
    last_toggle = millis();  // To deal with debounce of the switch
    //Serial.print("Door closed: ");
    //Serial.println(DOOR_CLOSED);
  }
}


// Definitions for serial communication

//#################################### REQUEST AND REPLY SPECIFIC INFO ##########################
/*
   When adding a new request/reply:
   1. Add length (excluding pk) to request_lengths
   2. Make sure request array is long enough to hold new request
   3. Add new case to interpret_request
   4. Add new reply to send_reply
   5. Update RPI reply_lengths
*/



// Request is initialised as 65535 which is overwritten as correct data comes in, or not if the request times out
unsigned int request[5] = {65535, 65535, 65535, 65535, 65535};
unsigned int CFI_recipe[500];
int CFI_instructions = 0;
int received_ints = 0;
int expected_ints = 1;
unsigned long receive_time;
unsigned long last_received;  // Time most recent byte was received
int serial_timeout = 500;  // Time until message is presumed dead and buffer (data array) is emptied
int flushed_bytes = 0;

int request_lengths[9] = {  // Length of each message, excluding PK at start of each message
  // 0. Read diagnostics, []
  0,
  // 1. Set lights, [Blue, IR, White, Red]
  4,
  // 2. Set temperature, [T]
  1,
  // 3. Read temperature, []
  0,
  // 4. Set CFI procedure, [instructions, 500]
  1 + (sizeof(CFI_recipe)/sizeof(unsigned int)),
  // 5. Trigger CFI, [yes/no]
  1,
  // 6. Enable/disable LEDs, [enable/disable]
  1,
  // 7. Enabled/disable bed peltiers, [enable/disable]
  1,
  // 8. Read CFI_recipe
  1
};

int parseUInt() {
  /*
      Function to read 16-bit UNSIGNED integers from buffer.
      If only a single byte is received, the most-significant byte is assumed to be 0
      If no bytes are in the buffer, returns -1
  */
  int firstByte = Serial.read();      // Read as integers to obtain possible -1 from read()
  int secondByte = Serial.read();
  if (secondByte == -1) {
    secondByte = 0;                   // If most-significant byte is missing, set to 0
  }
  if (firstByte == -1) {
    return -1;                        // If least-significant byte is missing (i.e. no bytes in buffer), abort
  }
  unsigned int combined = (byte) secondByte;        // Set MSB as first 8 bits of combined
  combined = (combined << 8) | ((byte) firstByte);  // Shift MSB right, and or with LSB
  return combined;
}


int writeInt16(int input) {
  /*
     Function to write 16-bit integers to Serial
     Bytes are written from least to most significant
  */

  byte firstByte = input & 255;           //   255 = 00000000 11111111
  byte secondByte = (input >> 8) & 255;   //  Isolate most-significant byte
  int written = 0;
  written += Serial.write(firstByte);     // Serial.write returns number of bytes written
  written += Serial.write(secondByte);    // In this case should always return 1
  return written;                         // Return number of bytes written
}


int read_request() {
  /*
     Reads from buffer any request the Pi may send, and writes it as integers to *request* array
  */

  if (received_ints == expected_ints and received_ints > 0) {                 // A non-zero message is fully received
    return 1;

  } else if (received_ints > 0 and ((unsigned long)(millis() - last_received)) > serial_timeout) {
    received_ints = expected_ints;                                          // Jump to the processing, assume nothing else is coming

  } else if (Serial.available() > 1) {                                        // If at least one 16-bit int has been received
    if (request[0] == 4 and received_ints >= 2) {                              // If CFI procedure (PK=4) is being set, and PK + instructions have arrived
      CFI_recipe[received_ints - 2] = parseUInt();                            // Save data to the CFI_recipe array instead
    } else {
      request[received_ints] = parseUInt();                                   // Insert the new int into the request array (any error in receiving is read as 65535 (error state))
    }
    last_received = millis();
    received_ints += 1;                                                       // Update number of ints received

    if (received_ints == 1) {                                                 // If this is the first int of a new message (the PK)
      receive_time = last_received;                                         // Note time of arrival of first int
      if (request[0] == 65535 or request[0] >= (sizeof(request_lengths)/sizeof(request_lengths[0]))) {     // If error occured receiving PK
        request[0] = 65535;
        expected_ints = 1;                                                    // Abort rest of message
      } else {
        expected_ints = request_lengths[request[0]] + 1;                      // Choose the correct request length based on the PK just received
      }
    }
  }
  return 0;                                                                   // No full message has been received
}


int interpret_LED_intensity(int brightness) {
  /*
     Takes in Uint (0-255, 0 is off, 255 is bright), and returns value LEDs will use (programmatically, 255 is off, 0 is bright)
  */
  if (brightness == 65535) {                      // If erroneous value slips through somewhere (e.g. CFI)
    brightness = 0;                               // Set lights to off (safest)
  }
  brightness = constrain(brightness, 0, 255);     // Limit values between 0 and 255
  return 255 - brightness;                        // Convert user value to programmatic value
}

void interpret_request() {
  switch (request[0]) {
    case 0:  //Read diagnostics
      break;
    case 1:  //Set lights, [PK, Blue, IR, White, Red]
      if (request[1] != 65535) B_intensity = interpret_LED_intensity(request[1]);
      if (request[2] != 65535) I_intensity = interpret_LED_intensity(request[2]);
      if (request[3] != 65535) W_intensity = interpret_LED_intensity(request[3]);
      if (request[4] != 65535) R_intensity = interpret_LED_intensity(request[4]);
      break;
    case 2:  //Set temperature, [PK, T]
      if (request[1] != 65535) target_temp = ((float) request[1]) / 10.0;
      break;
    case 3:  //Read temperature, [PK]
      break;
    case 4:  //Set CFI procedure [PK, instructions, 500]
    if (request[1] != 65535) CFI_instructions = request[1];
      break;
    case 5:  //Trigger CFI [PK, yes/no]
      if (request[1] != 65535) ACTIVATE_CFI = request[1];
      break;
    case 6:  //Enable/disable LEDs [PK, enable/disable]
      if (request[1] != 65535) ENABLE_LEDs = request[1];
      break;
    case 7:  //Enabled/disable bed peltiers [PK, enable/disable]
      if (request[1] != 65535) ENABLE_BPLRs = request[1];
      break;
    case 8:
      break;
  }
}


void send_reply() {
  writeInt16(request[0]);                                                         // Send PK
  //for (int i=1; i < (sizeof(request)/sizeof(request[0])); i++) {
  //  writeInt16(request[i]);
  //}
  switch (request[0]) {
    case 0:  //Read diagnostics, [PK]
      writeInt16((unsigned int) (target_temp * 10));
      writeInt16(B_intensity);
      writeInt16(I_intensity);
      writeInt16(W_intensity);
      writeInt16(R_intensity);
      writeInt16(ACTIVATE_CFI);
      writeInt16(ENABLE_LEDs);
      writeInt16(ENABLE_BPLRs);
      break;
    case 1:  //Set lights, [PK, Blue, IR, White, Red]
      break;
    case 2:  //Set temperature, [PK, T]
      break;
    case 3:  //Read temperature, [PK]
      writeInt16((unsigned int) (temp0 * 10));
      writeInt16((unsigned int) (temp1 * 10));
      writeInt16((unsigned int) (temp2 * 10));
      writeInt16((unsigned int) (temp3 * 10));
      writeInt16((unsigned int) (temp4 * 10));
      writeInt16((unsigned int) (temp5 * 10));
      break;
    case 4:  //Set CFI procedure [PK, instructions, 500]
      //for (int i=0; i < (sizeof(CFI_recipe)/sizeof(unsigned int)); i++) {
      //  writeInt16(CFI_recipe[i]);
      //}
      break;
    case 5:  //Trigger CFI [PK, yes/no]
      break;
    case 6:  //Enable/disable LEDs [PK, enable/disable]
      break;
    case 7:  //Enabled/disable bed peltiers [PK, enable/disable]
      break;
    case 8:
      for (int i=0; i<(sizeof(CFI_recipe)/sizeof(CFI_recipe[0]));i++){
        writeInt16(CFI_recipe[i]);
      }
  }
  unsigned long ul_elapsed_time = (unsigned long) (millis() - receive_time);      // Do this on different line to constrain (see docs)
  unsigned int elapsed_time = constrain(ul_elapsed_time, 0, 65535);               // Avoid overflows
  writeInt16(elapsed_time);                                                       // Send elapsed time since start of message
  writeInt16(flushed_bytes);                                                      // Send number of erroneous extra bytes received
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


void update_bed_peltier_control(float targetTemp, float objTemp, int pinA, int pinB) {
  // ONLY VALID FOR BED PELTIERS - SEE update_roof_peltier_control for roof control function

  bool PUMP_ON;
  bool HEAT_ON;

  float hotCutoff = targetTemp + 0.0;  // Offset from target temperature above which heating will stop
  float coldCutoff = targetTemp - 0.0; // Offset from target temperature below which cooling will stop
  // Triggers represent maximum and minimum acceptable temperatures for target
  float hotTrigger = targetTemp - 0.5; // Offset from target temperature below which heating will start
  float coldTrigger = targetTemp + 1; // Offset from target temperature above which cooling will start

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

  /*
    Serial.println(pinA);
    Serial.print("PUMP ON: ");
    Serial.println(PUMP_ON);
    Serial.print("HEAT ON: ");
    Serial.println(HEAT_ON);
    Serial.print(objTemp);
    Serial.print(", ");
    Serial.println(targetTemp);
    Serial.println();
  */

  if (not ENABLE_BPLRs) {                  // Bed peltier override
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
  float coldCutoff = targetTemp - 1; // Offset from target temperature below which cooling will stop
  // Trigger represents maximum acceptable temperatures for target
  float coldTrigger = targetTemp + 1; // Offset from target temperature above which cooling will start

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


void update_LED_relay() {
  if (ENABLE_LEDs) {
    digitalWrite(LED_POWER_PIN, HIGH);
  } else {
    digitalWrite(LED_POWER_PIN, LOW);
  }
}


unsigned long CFI_start = 0;
unsigned long next_change = 0;
int CFI_state = -1;
int old_B = 0;
int old_I = 0;
int old_W = 0;
int old_R = 0;

void activate_CFI() {
  /*  Function to enact any fast-changing procedures that the Pi may not be able to communicate in time, e.g. quick pulses in CFI. The procedure must be written into CFI_recipe in advance.
   *  CFI_recipe has a maximum of 100 states, each with a max duration of 65545ms. Therefore a recipe can last at most 6554.5s, or ~1h50 minutes
   */
   if (CFI_state == -1) {                                               // During first iteration
    CFI_start = millis();                                               // Record start time
    old_B = B_intensity;                                                // Save state of lights
    old_I = I_intensity;
    old_W = W_intensity;
    old_R = R_intensity;
   }
  if ((unsigned long) (millis()-CFI_start) >= next_change) {            // If the state needs to change
    if (CFI_state < (CFI_instructions-1)) {                             // While there are instructions still to complete (CFI might not use all 500)
      CFI_state += 1;                                                   // Move to new state
      B_intensity = interpret_LED_intensity(CFI_recipe[(CFI_state*5)]);                          // Update lights
      I_intensity = interpret_LED_intensity(CFI_recipe[(CFI_state*5) + 1]);
      W_intensity = interpret_LED_intensity(CFI_recipe[(CFI_state*5) + 2]);
      R_intensity = interpret_LED_intensity(CFI_recipe[(CFI_state*5) + 3]);
      next_change += CFI_recipe[(CFI_state*5) + 4];                       // Add on duration of next state onto time until change
    } else {                                                              // Time has run out on last instruction
      ACTIVATE_CFI = 0;                                                   // End CFI
      CFI_start = 0;                                                      // Reset all variables 
      next_change = 0;
      CFI_state = -1;
      B_intensity = old_B;                                                // Revert lights to original state
      I_intensity = old_I;
      W_intensity = old_W;
      R_intensity = old_R;
    }
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
  pinMode(LED_POWER_PIN, OUTPUT);

  digitalWrite(BED_PLR1A_PIN, LOW);
  digitalWrite(BED_PLR1B_PIN, LOW);
  digitalWrite(BED_PLR2A_PIN, LOW);
  digitalWrite(BED_PLR2B_PIN, LOW);
  analogWrite(BLUE_PIN, 255);
  analogWrite(IR_PIN, 255);
  analogWrite(WHITE_PIN, 255);
  analogWrite(RED_PIN, 255);
  digitalWrite(ROOF_PLR_PIN, LOW);
  digitalWrite(LED_POWER_PIN, LOW);

  Serial.begin(9600);
}


void loop() {

  update_data();
  update_bed_peltier_control(target_temp, temp5, BED_PLR1A_PIN, BED_PLR1B_PIN);
  update_bed_peltier_control(target_temp, temp5, BED_PLR2A_PIN, BED_PLR2B_PIN);
  update_roof_peltier_control(target_temp, temp0, ROOF_PLR_PIN);
  update_limit_switch();
  update_LED_relay();

  if (ACTIVATE_CFI) {
    activate_CFI();
  }

  if (DOOR_CLOSED) {
    set_lights();
  } else {
    analogWrite(BLUE_PIN, 255);
    analogWrite(IR_PIN, 255);
    analogWrite(WHITE_PIN, 220);
    analogWrite(RED_PIN, 255);
  }

  // update_display();



  if (read_request() == 1) {
    flushed_bytes = flush_serial();                                           // Clear any remaining (eroneous) bytes from the buffer and log how many cleared
    interpret_request();                                                      // Carry out action of request
    send_reply();                                                             // Send return data
    received_ints = 0;
    for (int i = 0; i < (sizeof(request)/sizeof(request[0])); i++) {
      request[i] = 65535;                                                     // Reset data to be all 65535
    }
  }

}
