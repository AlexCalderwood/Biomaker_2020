String request;
byte incomingByte;
int receive_time;
int flushed_bytes;


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


void send_ack(String data, int receive_time, int flushed_bytes) {
  data += ", ";
  data += String(millis() - receive_time);
  data += ", ";
  data += String(flushed_bytes);
  Serial.print(data);
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
    send_ack(request, receive_time, flushed_bytes);  // Send return data
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
