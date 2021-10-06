/*
 * FOR ARDUINO LEONARDO ONLY (EXTRA ANALOG INPUT PINS)
 * 
 */


int TempIC_Pin = A6;
int raw_input;
int mV_reading;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(TempIC_Pin, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  raw_input = analogRead(TempIC_Pin);
  mV_reading = map(raw_input, 0, 1024, 0, 5000);
  Serial.print(raw_input);
  Serial.print(", ");
  Serial.println(mV_reading);
  delay(1000);
}
