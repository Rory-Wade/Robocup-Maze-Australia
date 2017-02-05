
const int BMP = 20; 
const int LMP = 21; 
const int FMP = 22; 
const int RMP = 23; 

// Direction Control 
const int BDC = 14; //HIGH = forwards
const int LDC = 15; //LOW = forwards
const int FDC = 16; //LOW = forwards 
const int RDC = 17; //HIGH = forwards

int speedVal1 = 0;
int speedVal2 = 100;
int speedVal3 = 200;
int speedVal4 = 255;

void setup() {
     
     pinMode(BMP, OUTPUT);
     pinMode(LMP, OUTPUT);
     pinMode(FMP, OUTPUT);
     pinMode(RMP, OUTPUT);

     pinMode(BDC, OUTPUT);
     pinMode(LDC, OUTPUT);
     pinMode(FDC, OUTPUT);
     pinMode(RDC, OUTPUT);
     
  }

void loop() {

 moveForward(speedVal4,speedVal4,speedVal4,speedVal4);
 delay(2000);
 moveBackwards(speedVal4,speedVal4,speedVal4,speedVal4);
 delay(2000);
 turnLeft(speedVal4,speedVal4);
 delay(2000);
 turnLeft(speedVal4,speedVal4);
 delay(2000);
 }

  void moveForward(int front,int back, int left, int right){ // Wheel Speeds

        //Direction of motors
        digitalWrite(FDC, LOW);
        digitalWrite(BDC, HIGH); 
        digitalWrite(LDC, LOW);
        digitalWrite(RDC, HIGH);

        //Motor Speeds
        analogWrite(FMP, front);
        analogWrite(BMP, back);
        analogWrite(LMP, left);
        analogWrite(RMP, right);
  }

    void turnLeft(int left, int right){ // Wheel Speeds

        //Direction of motors
        digitalWrite(FDC, HIGH);
        digitalWrite(BDC, HIGH);
        digitalWrite(LDC, HIGH);
        digitalWrite(RDC, HIGH);

        //Motor Speeds
        analogWrite(FMP, 0);
        analogWrite(BMP, 0);
        delay(25);
        
        analogWrite(LMP, left);
        analogWrite(RMP, right);
  }

      void turnRight(int left, int right){ // Wheel Speeds

        //Direction of motors
        digitalWrite(FDC, HIGH);
        digitalWrite(BDC, HIGH);
        digitalWrite(LDC, LOW);        
        digitalWrite(RDC, LOW);

        //Motor Speeds
        analogWrite(FMP, 0);
        analogWrite(BMP, 0);
        delay(25);
        
        analogWrite(LMP, left);
        analogWrite(RMP, right);
  }

  void moveBackwards(int front,int back, int left, int right){ // Wheel Speeds

        //Direction of motors
        digitalWrite(FDC, HIGH);
        digitalWrite(BDC, LOW); 
        digitalWrite(LDC, HIGH);
        digitalWrite(RDC, LOW);

        //Motor Speeds
        analogWrite(FMP, front);
        analogWrite(BMP, back);
        analogWrite(LMP, left);
        analogWrite(RMP, right);
  }
