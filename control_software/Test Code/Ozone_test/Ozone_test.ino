#include <SPI.h>

#define FULL_SCALE_22BIT    4194303.0

const byte pinSS = 8; //cs pin
const byte pinRDY = 12;

float
    fVolts;
   
union
{
    long            lVal;
    unsigned char   grucB[sizeof(long)];
   
} uPack;

void setup( void )
{
    Serial.begin(9600);
    InitSPI();
       
}//setup

void InitSPI( void )
{
    pinMode( pinRDY, INPUT );       //RDY/SDO
    pinMode( pinSS, OUTPUT );       //slave select
    digitalWrite( pinSS, HIGH );    //ensure SS idles high

    //start the SPI
    SPI.begin();
    SPI.setBitOrder( MSBFIRST );
    SPI.setDataMode( SPI_MODE3 );
    SPI.setClockDivider( SPI_CLOCK_DIV16 );
   
}//InitSPI

void ReadSensor( void )
{
    //set SS low
    digitalWrite( pinSS, LOW );
   
    //wait for conversion complete from RDY pin (it goes low)
    //could add a timeout here if desired
    while( digitalRead( pinRDY ) );

    //
    for( byte i=0; i<3; i++ )
        uPack.grucB[2-i] = SPI.transfer(0x00);

    //long is 4 bytes; data fits in three, fourth is space filler for long in union
    uPack.grucB[3] = 0;

    digitalWrite( pinSS, HIGH );

    //22221111 111111
    //32109876 54321098 76543210
    //xysddddd dddddddd dddddddd
    //
    //x = overflow H
    //y = underflow L
    //s = sign
    //
    //According to device datasheet, the MCP3551 output is VSENS = DATA x VREF / FS
    // where Vref = 5V
    //  and     FS = 22 bits (23 and 24 should play no role)
    //
    fVolts = (float)uPack.lVal * 5.0 / FULL_SCALE_22BIT;
   
}//ReadSensor

void loop(void)
{
    unsigned long
        tNow;
    static unsigned long
        timeReadSensor=0;

    tNow = millis();
    //read the sensor every 1/2-second
    if( millis() - timeReadSensor >= 500ul )
    {
        timeReadSensor = tNow;
       
        ReadSensor();
        Serial.println( fVolts, 5 );

        //do stuff with sensor reading...
           
    }//if

}//loop
