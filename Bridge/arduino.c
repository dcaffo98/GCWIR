#define INCORRECT_PIN 13
#define CORRECT_PIN 12
#define BUTTON_PIN 2

int msg;

int buttonState = 0;     // current state of the button
int lastButtonState = 0; // previous state of the button
int startPressed = 0;    // the moment the button was pressed
int endPressed = 0;      // the moment the button was released
int holdTime = 0;        // how long the button was hold
int idleTime = 0;        // how long the button was idle
String iState = "idle";
String iFutureState;
void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);
  pinMode(INCORRECT_PIN, OUTPUT);
  pinMode(CORRECT_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);
}

void loop() {
  Serial.flush();
  if (Serial.available() > 0) {
    iFutureState = "idle";
    msg = Serial.read();
    if (iState == "idle" && msg == 0xff) iFutureState = "trasmission started";
    
    if (iState == "trasmission started" && msg == 0x01) iFutureState = "device correct";
    else if (iState == "trasmission started" && msg == 0x02) iFutureState = "device incorrect";
    else if (iState == "trasmission started" ) iFutureState = "idle";
    
    if (iState == "device correct" && msg == 0x01) iFutureState = "turn on correct device";
    else if (iState == "device correct") iFutureState = "turn off correct device";
    
    if (iState == "device incorrect" && msg == 0x01) iFutureState = "turn on incorrect device";
    else if (iState == "device incorrect") iFutureState = "turn off incorrect device";

    if (iFutureState != "turn off correct device" && iFutureState != "turn off incorrect device" &&msg == 0xfe) iFutureState = "idle";
    // onEnter Actions

    if (iFutureState == "turn on correct device") digitalWrite(CORRECT_PIN, HIGH);
    if (iFutureState == "turn off correct device") digitalWrite(CORRECT_PIN, LOW);
    if (iFutureState == "turn on incorrect device") digitalWrite(INCORRECT_PIN, HIGH);
    if (iFutureState == "turn off incorrect device") digitalWrite(INCORRECT_PIN, LOW);
  
    if (iFutureState == "turn off correct device" || iFutureState == "turn off incorrect device") iFutureState = "idle";

    // state transition
    iState = iFutureState;
  }
  else {
    buttonState = digitalRead(BUTTON_PIN); // read the button input

    if (buttonState != lastButtonState) { // button state changed
      updateState();
    }

    lastButtonState = buttonState;
  }
}
void updateState() {
  // the button has been just pressed
  if (buttonState == HIGH) {
    startPressed = millis();

    // the button has been just released
  } else {
    endPressed = millis();
    holdTime = endPressed - startPressed;

    if (holdTime >= 100 && holdTime < 3000) {
      Serial.write(0xff);
      Serial.write(0x03);
      Serial.write(0x01);
      Serial.write(0xfe);
    }

    if (holdTime >= 3000) {
      Serial.write(0xff);
      Serial.write(0x03);
      Serial.write(0x02);
      Serial.write(0xfe);
    }

  }
}