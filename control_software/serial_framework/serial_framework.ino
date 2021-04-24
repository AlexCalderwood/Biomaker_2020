int received_bytes;
byte incomingByte;
unsigned long receive_time;
unsigned long last_received;  // Time most recent byte was received
int serial_timeout = 500;  // Time until message is presumed dead and buffer (data array) is emptied
int flushed_bytes;
byte request[25] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
// Request is initialised as 255 which is overwritten as correct data comes in, or not if the request times out

int target_temp;
int R_intensity;
int Y_intensity;
int B_intensity;
int W_intensity;
int W_timeout;

int temp1;
int temp2;
int hum1;
int hum2;
int light; 

int NTC_PIN1 = A0;
int LDR_PIN = A1;
int PLT_COLD = 7;
int PLT_HOT = 8;
int R_PIN = 9;
int Y_PIN 10 ;
int B_PIN = 11;


// LOCAL DATA HANDLING

float float_map(float x, float xL, float xU, float yL, float yU, float zero_thresh) {
  // Maps the value of x (raw reading) to the range of Y (useful units), in linear relation to the lower and upper X bounds.
  // Returns values as floats, and can extrapolate beyond bounds.
  // xL - Raw reading for lower bound of measurement
  // xU - Raw reading for upper bound of measurement
  // yL - Expected value for lower bound (in useful units of your choice)
  // yU - Expected value for upper bound (in useful units of your choice)
  
  if (((xU-xL) > zero_thresh) or ((xU-xL) < -zero_thresh)){
    return (((yU-yL)/(xU-xL)) * (x-xL) + yL);
  }
  else {
    // Denominator is deemed effectively zero
    return -100000000;
  }
}


float read_temperature(int temp_pin) {
  // Reads temperature from "Negative Temperature Coefficient" thermistor
  float resistance = analogRead(temp_pin);
  return float_map(resistance, 648.0, 265.0, 12.1, 49.9, 0.01);
}


float read_light(int light_pin) {
  // Reads light level from "Light Dependent Resistor"
  float resistance = analogRead(light_pin);
  return float_map(resistance, 190.0, 922.0, 0.0, 100, 0.01);
}


void update_data(){
  // Amalgamates data from all local sensors
  temp1 = read_temperature(NTC_PIN1);
  temp2 = 0.0; //read_temperature(NTC_PIN2);
  hum1 = 0.54; //read_humidity(HUM_PIN1);
  hum2 = 0.55; //read_humidity(HUM_PIN2);
  light = read_light(LDR_PIN);
}


void interpret_request(){
  if (request[19] != 0xFF) target_temp = (int) request[19];
  if (request[20] != 0xFF) R_intensity = (int) request[20];
  if (request[21] != 0xFF) Y_intensity = (int) request[21];
  if (request[22] != 0xFF) B_intensity = (int) request[22];
  if (request[23] != 0xFF) W_intensity = (int) request[23];
  if (request[24] != 0xFF) W_timeout = (int) request[24];
}


// CONTROL FUNCTIONS

void set_temperature(int target) {
  // pass
}


void set_lights(int R, int Y, int B, int W, int W_t) {
  // pass
}



// SERIAL HANDLING

void send_ack() {
  Serial.write(request, sizeof(request));
  Serial.write(temp1);
  Serial.write(temp2);
  Serial.write(hum1);
  Serial.write(hum2);
  Serial.write(light);
  Serial.write(millis()- receive_time);
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


void setup() {
  Serial.begin(9600);
}


void loop() {
  int expected_bytes = sizeof(request);  // Number of bytes long the request will be

  if (received_bytes == expected_bytes) { // Update states for newly receieved request
    flushed_bytes = flush_serial();  // Clear any remaining (eroneous) bytes from the buffer and log how many cleared
    interpret_request();  // Read new instructions from request
    update_data();  // Read fresh data from sensors
    send_ack();  // Send return data
    received_bytes = 0;
    for (int i = 0; i<sizeof(request); i++) {
      request[i] = 0xFF;  // Reset data to be all 255
    }
    analogWrite(R_PIN, R_intensity);
    analogWrite(Y_PIN, Y_intensity);
    analogWrite(B_PIN, B_intensity);
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
  else if (received_bytes > 0 and (millis()-last_received) > serial_timeout) {
    received_bytes = expected_bytes; // Jump to the processing, assume nothing else is coming
  }

  set_temperature(target_temp);
  set_lights(R_intensity, Y_intensity, B_intensity, W_intensity, W_timeout);
  
}
