/* Minimum_Source*/
int incomingByte = 0;
void setup() {
  // put your setup code here, to run once:
Serial2.begin(9600);

pinMode(BOARD_LED_PIN, OUTPUT);
}

void loop() {
 
 // send data only when you receive data:
        if (Serial2.available() > 0) {
                // read the incoming byte:
                incomingByte = Serial2.read();
        if (incomingByte==0)
                  digitalWrite(BOARD_LED_PIN, HIGH); // set to as HIGH LED is turn-off
                  delay(); 
          
        else
                  digitalWrite(BOARD_LED_PIN, LOW);
        }
}

