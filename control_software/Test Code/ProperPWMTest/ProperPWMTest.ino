int dutycycle =247;
int outPin = 6;


// 6 is blue
// 9 is IR
// 10 is white
// 11 is red

void setup() {
  // put your setup code here, to run once:
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(6, OUTPUT);
  analogWrite(11,255);
  analogWrite(10,255);
  analogWrite(9,255);
  analogWrite(6,255);
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
  analogWrite(outPin, dutycycle);
  

}
