int Rdutycycle = 100;
int Ydutycycle = 100;
int Bdutycycle = 100;
int channel;

const int Rpin = 9;
const int Ypin = 10;
const int Bpin = 11;


void setup() {
  // put your setup code here, to run once:
  pinMode(Rpin, OUTPUT);
  pinMode(Ypin, OUTPUT);
  pinMode(Bpin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    channel = Serial.read();
    if (channel == 82) {
      Rdutycycle = Serial.parseInt();
      Rdutycycle = abs(Rdutycycle) % 256;
    } else if (channel == 89) {
      Ydutycycle = Serial.parseInt();
      Ydutycycle = abs(Ydutycycle) % 256;

    } else if (channel == 66) {
      Bdutycycle = Serial.parseInt();
      Bdutycycle = abs(Bdutycycle) % 256;

    }
    Serial.flush();
    Serial.read();
    Serial.print(channel);
    Serial.print(", ");
    Serial.print(Rdutycycle);
    Serial.print(", ");
    Serial.print(Ydutycycle);
    Serial.print(", ");
    Serial.println(Bdutycycle);

  }

  //RYB
  digitalWrite(Rpin, HIGH);
  delayMicroseconds(Rdutycycle);
  digitalWrite(Rpin, LOW);
  delayMicroseconds(255-Rdutycycle + 10);
  digitalWrite(Ypin, HIGH);
  delayMicroseconds(Ydutycycle);
  digitalWrite(Ypin, LOW);
  delayMicroseconds(255-Ydutycycle + 10);
  digitalWrite(Bpin, HIGH);
  delayMicroseconds(Bdutycycle);
  digitalWrite(Bpin, LOW);
  delayMicroseconds(255-Bdutycycle + 10);

}
