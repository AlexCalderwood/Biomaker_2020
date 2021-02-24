String request;
byte incomingByte;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.read();
    if (incomingByte != 10) {  // If incoming byte isn't a new-line character
      request += char(incomingByte);
    }
  }
  if (request.length() == 8) {  // If all bytes of the request (current time) are received
    Serial.print(request);  // Send return data
    request = "";
    while (Serial.available() > 0) {
      // flush the the rest of the buffer by reading it all to nowhere
      Serial.read();
    }
  }
}
