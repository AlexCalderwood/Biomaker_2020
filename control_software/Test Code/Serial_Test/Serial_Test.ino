int i = 0;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  //Serial.print("Hello computer!");
  Serial.println(i);
  i = i + 1;
  delay(2000);
}
