String request;
byte incomingByte;
int receive_time;
int flushed_bytes;
String data;

int NTC_PIN = A0;
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


float read_temperature() {
  // Reads temperature from "Negative Temperature Coefficient" thermistor
  float resistance = analogRead(NTC_PIN);
  return float_map(resistance, 648.0, 265.0, 12.1, 49.9, 0.01);
}


float read_light() {
  // Reads light level from "Light Dependent Resistor"
  float resistance = analogRead(LDR_PIN);
  return float_map(resistance, 190.0, 922.0, 0.0, 100, 0.01);
}


String collect_data(){
  // Amalgamates data from all local sensors
  float temp = read_temperature();
  float light = read_light();
  return String(temp) + ", " + String(light);
}


// SERIAL HANDLING

void send_ack(String request, String data, int receive_time, int flushed_bytes) {
  request += ", ";
  request += data;
  request += ", ";
  request += String(millis() - receive_time);
  request += ", ";
  request += String(flushed_bytes);
  Serial.print(request);
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
  // put your setup code here, to run once:
  Serial.begin(9600);
}


void loop() {
  // put your main code here, to run repeatedly:
  int request_length = 11;  // Number of bytes long the request will be
  
  if (request.length() == request_length) {
    flushed_bytes = flush_serial();  // Clear any remaining (eroneous) bytes from the buffer and log how many cleared
    data = collect_data();
    send_ack(request, data, receive_time, flushed_bytes);  // Send return data
    request = "";
  }
  else if (Serial.available() > 0) {
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
}
