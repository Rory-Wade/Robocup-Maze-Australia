//Sender Code

int led = 13;
bool haveData = 0;
String data;

void setup() {
  Serial.begin(9600);
  Serial3.begin(9600);
  pinMode(led, OUTPUT);     
  digitalWrite(led, LOW);    // turn the LED off by making the voltage LOW
  }


bool getData () {
  int i = 0;
  data="";
  if (Serial3.available()) {
    delay(20); //allows all serial sent to be received together
    while (Serial3.available() && i < 4) {
      char inChar=Serial3.read();
      data=data + inChar;
      i++;
    }
   return 1;
  }
}


void loop() {
  Serial3.write("ON  ");     // Send "ON" signal
  digitalWrite(led, HIGH);   // turn the LED ON
  haveData = getData();
  if (haveData) {
   Serial.println(data);
   }
  delay(50);               // wait for a second

  Serial3.write("OFF ");    // Send "OFF" signal
  digitalWrite(led, LOW);    // turn the LED off by making the voltage LOW
  delay(50);               // wait for a second  
}

