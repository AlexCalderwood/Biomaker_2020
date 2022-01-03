int pinHot = 1;
int pinCold = 2;


void setup() {
  Serial.begin(9600);
  pinMode(pinHot, OUTPUT);
  pinMode(pinCold, OUTPUT);
  digitalWrite(pinHot, LOW);
  digitalWrite(pinCold, LOW);

}

void loop() {
  if (Serial.available() > 0){
    int inp = Serial.parseInt();
    if (inp == 7){
      digitalWrite(pinCold, LOW);
      delay(1);
      digitalWrite(pinHot, HIGH);
      Serial.println("hot!");
    }
    else if (inp == 8) {
      digitalWrite(pinHot, LOW);
      delay(1);
      digitalWrite(pinCold, HIGH);
      Serial.println("cold!");      
    }
    else if (inp == 9){
      digitalWrite(pinHot, LOW);
      digitalWrite(pinCold, LOW);
      Serial.println("off"); 
    }
  }
  // put your main code here, to run repeatedly:

}
