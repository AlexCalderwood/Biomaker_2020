String request;
byte incomingByte;
unsigned long receive_time;
int flushed_bytes;
String data;

int target_temp;
int R_intensity;
int Y_intensity;
int B_intensity;
int W_intensity;
int W_timeout;

int NTC_PIN1 = A0;
int LDR_PIN = A1;


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


String collect_data(){
  // Amalgamates data from all local sensors
  float temp1 = read_temperature(NTC_PIN1);
  float temp2 = 0.0; //read_temperature(NTC_PIN2);
  float hum1 = 0.54; //read_humidity(HUM_PIN1);
  float hum2 = 0.55; //read_humidity(HUM_PIN2);
  float light = read_light(LDR_PIN);
  return String(temp1) + ", " + String(temp2) + ", " + String(hum1) + ", " + String(hum1) + ", " + String(light);
}


void interpret_request(String request){
  target_temp = request.substring(21, 23).toInt();
  R_intensity = request.substring(25, 28).toInt();
  Y_intensity = request.substring(30, 33).toInt();
  B_intensity = request.substring(35, 38).toInt();
  W_intensity = request.substring(40, 43).toInt();
  W_timeout = request.substring(45, 46).toInt();
}


// CONTROL FUNCTIONS

void set_temperature(int target) {
  // pass
}


void set_lights(int R, int Y, int B, int W, int W_t) {
  // pass
}



// SERIAL HANDLING

void send_ack(String request, String data, unsigned long receive_time, int flushed_bytes) {
  request += ", ";
  request += data;
  request += ", ";
  request += String(millis() - receive_time);
  request += ", ";
  request += String(flushed_bytes);
  Serial.println(request);
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
  int request_length = 46;  // Number of bytes long the request will be

  if (request.length() == request_length) { // Update states for newly receieved request
    flushed_bytes = flush_serial();  // Clear any remaining (eroneous) bytes from the buffer and log how many cleared
    interpret_request(request);
    data = collect_data();
    send_ack(request, data, receive_time, flushed_bytes);  // Send return data
    request = "";
  }
  else if (Serial.available() > 0) { // Request is being received (ongoing)
    if (request.length() == 0) {
      // This code only runs once per request
      receive_time = millis();
    }
    // read the incoming byte:
    incomingByte = Serial.read();
    if (incomingByte != 10) {  // If incoming byte isn't a new-line character
      request += char(incomingByte);
    }
  }

  set_temperature(target_temp);
  set_lights(R_intensity, Y_intensity, B_intensity, W_intensity, W_timeout);
  
}
