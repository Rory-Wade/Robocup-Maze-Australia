//Receiver Code

int led = 13;
String data;
bool haveData = 0;

void setup() {
  Serial.begin(9600);
  Serial3.begin(9600);
  pinMode(led, OUTPUT);
}

void loop() {
  Serial3.print("HEY");
  delay(200);
  haveData = readData();
  if (haveData) {
   Serial.print(data);
   if (data=="ON  ") {
      digitalWrite(led, HIGH);
       Serial3.write("LON ");    // Send Ack
    }
    else if (data=="OFF "){
      digitalWrite(led, LOW);
       Serial3.write("LOFF");    // Send Ack
    }
  }
}

bool readData () {
  int i = 0;
  data="";
  if (Serial3.available()) {
    delay(20); //allows all serial sent to be received together
    while (Serial3.available()) {
      char inChar = Serial3.read();
      data=data + inChar;
      i++;
    }
   return 1;
  }
}
