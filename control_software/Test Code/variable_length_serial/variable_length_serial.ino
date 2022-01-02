void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}



int parseUInt() {
  /*
      Function to read 16-bit UNSIGNED integers from buffer.
      If only a single byte is received, the most-significant byte is assumed to be 0
      If no bytes are in the buffer, returns -1
  */
  int firstByte = Serial.read();      // Read as integers to obtain possible -1 from read()
  int secondByte = Serial.read();

  if (secondByte == -1) {
    secondByte = 0;                   // If most-significant byte is missing, set to 0
  }
  if (firstByte == -1) {
    return -1;                        // If least-significant byte is missing (i.e. no bytes in buffer), abort
  }

  unsigned int combined = (byte) secondByte;        // Set MSB as first 8 bits of combined
  combined = (combined << 8) | ((byte) firstByte);  // Shift MSB right, and or with LSB
  return combined;
}

int writeInt16(int input) {
  /*
     Function to write 16-bit integers to Serial
     Bytes are written from least to most significant
  */

  byte firstByte = input & 255;           //   255 = 00000000 11111111
  byte secondByte = (input >> 8) & 255;   //  Isolate most-significant byte
  int written = 0;
  written += Serial.write(firstByte);     // Serial.write returns number of bytes written
  written += Serial.write(secondByte);    // In this case should always return 1
  return written;                         // Return number of bytes written
}

unsigned int input = 0;
byte count = 0;
//unsigned int request[6] = {65355, 65355, 65355, 65355, 65355, 6535}

void loop() {
  if (Serial.available() > 1) {           // Check for both bytes of 16-bit int to arrive before reading, otherwise reads two separate bytes into two 16-bit ints
    // Read UInt from the serial buffer
    input = parseUInt();
    //Serial.print(input);
    // Check that number is successfully converted to denery
    //input -= 1;
    //input = input / 2;
    //count += 1;
    // Send back number after checks
    int written = writeInt16(input);
    //Serial.write(written);

    // Clear the remaining buffer
    //if (Serial.peek() == 13) {            // 13 = \r = newline character
    //  while (Serial.available() > 0) {    // Flush out any remaining serial
    //    Serial.read();
    //  }
    //}
  }
  
}
