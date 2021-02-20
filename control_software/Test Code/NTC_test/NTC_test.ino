float resistance;
float temp;

// Assuming linear relationship over short range
float yL = 12.1;
float yU = 49.9;
float xL = 648.0;
float xU = 265.0;

int NTC_PIN = A0;

// Prototype function for optional parameters?
float float_map(float x, float xL, float xU, float yL, float yU);

float float_map(float x, float xL, float xU, float yL, float yU) {
  // Maps the value of x to the upper and lower Y bounds, in linear relation to the upper and lower X bounds.
  // Returns values as floats to n d.p., and can extrapolate beyond bounds.
  if (((xU-xL) > 0.01) or ((xU-xL) < -0.01)){
    return (((yU-yL)/(xU-xL)) * (x-xL) + yL);
  }
  else {
    return -100000000;
  }
  
}

void setup() {
  Serial.begin(9600);
}

void loop() {
  resistance = analogRead(NTC_PIN);
  temp = float_map(resistance, xL, xU, yL, yU);
  Serial.print("Resistance: ");
  Serial.println(resistance);
  Serial.print("Temp: ");
  Serial.println(temp);
  delay(1000);
}
