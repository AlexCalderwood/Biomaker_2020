int dutycycle = 5;

void setup() {
  // put your setup code here, to run once:
  pinMode(6, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    dutycycle = Serial.parseInt();
    Serial.read();
    if (dutycycle < 0) {
      dutycycle = 0;
    } else if (dutycycle > 255) {
      dutycycle = 255;
    }
    Serial.println(dutycycle);
  }
  analogWrite(6, dutycycle);
  

}
