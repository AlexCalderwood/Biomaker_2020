#include <dht.h>

dht DHT;

float res1;
float res2;
float temp1;
float temp2;


// Assuming linear relationship over short range
float yL = 12.1;
float yU = 49.9;
float xL = 648.0;
float xU = 265.0;

int DHT11_PIN = 6;
int NTC1_PIN = A1;
int NTC2_PIN = A2;

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
  res1 = analogRead(NTC1_PIN);
  res2 = analogRead(NTC2_PIN);
  int chk = DHT.read11(DHT11_PIN);
  temp1 = float_map(res1, xL, xU, yL, yU);
  temp2 = float_map(res2, xL, xU, yL, yU);
  Serial.print(temp1);
  Serial.print("°C, ");
  Serial.print(temp2);
  Serial.println("°C");
  //Serial.print(DHT.temperature);
  //Serial.print("°C, ");
  //Serial.println(DHT.humidity);
  delay(5000);
}
