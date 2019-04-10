//Analog pin for moisture sensor
int moisturePin = A0;
//Digital pin for the Water Valve
int valvePin = 13; //using led for testing
//Moisture data
int data = 0;
//String to hold incoming serial data
String inputString = "";
//whether the string is complete
bool stringComplete = false;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(valvePin, OUTPUT);
//  digitalWrite(valvePin, 1);
/*
  //Initialize timer1 
  noInterrupts();           // disable all interrupts
  TCCR1A = 0;
  TCCR1B = 0;

  //Set prescaler to 1024
  TCCR1B |= (1 << CS10);       
  TCCR1B |= (1 << CS12);
  
  //Enable timer overflow interrupt
  TIMSK1 |= (1 << TOIE1);
  //Enable all interrupts
  interrupts();
*/
}

void loop() {
  // put your main code here, to run repeatedly:
  //Read moisture value
  data = analogRead(moisturePin);
  //Send value to the serial port
  Serial.println("moisture:" + String(data));
  //Check if we have received a serial command
  readSerial();
  Serial.flush();
  delay(1000);
}

void serialEvent() {
  while (Serial.available()) {
    //Get the new byte:
    char inChar = (char)Serial.read();
    //If the incoming character is a newline, set a flag
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      //Add character to the inputString:
      inputString += inChar;
    }
  }
}

void readSerial() {
  //Read serial port
  if (stringComplete) {
    //Open Water Valve
    if (inputString == "open")
    {
      //Open valve for four seconds
      //preload timer (4s/(1/(16MHz/1024(prescaler value)))=62500
      //TCNT1 = 62500;
      digitalWrite(valvePin, 1);
      Serial.println("valve:" + String(digitalRead(valvePin)));
    }
    //Close Water Valve
    if (inputString.equalsIgnoreCase("close"))
    {
      //Close Water Valve
      //Turn off water valve
      digitalWrite(valvePin, 0);
      Serial.println("valve:" + String(digitalRead(valvePin)));
    }
    // clear the string:
    inputString = "";
    stringComplete = false;
  }  
}

//Timer routine
// interrupt service routine that wraps a user defined function supplied by attachInterrupt
ISR(TIMER1_OVF_vect)
{
  //Turn off water valve
  digitalWrite(valvePin, 0);
}
