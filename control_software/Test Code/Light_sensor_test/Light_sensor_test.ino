float resistance;
float light;

// Assuming linear relationship over short range
float yL = 0.0;
float yU = 100;
float xL = 190.0;
float xU = 922.0;

int LDR_PIN = A1;

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
  resistance = analogRead(LDR_PIN);
  light = float_map(resistance, xL, xU, yL, yU);
  Serial.print("Resistance: ");
  Serial.println(resistance);
  Serial.print("Light: ");
  Serial.println(light);
  delay(1000);
}
