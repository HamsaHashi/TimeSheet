#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 20, 4);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  lcd.init();
  lcd.clear();
  lcd.backlight();
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  Serial.println("Log in or log out?");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("System start...");
  delay(1000);
  lcd.clear();
}

// this in not needed, as this information is already in the script. 
String userID(int ID){
  if(id == 1) return "Rebekka";
  if(id == 2) return "Lars";
  if(id == 3) return "Bjørnar"; 
  if(id == 4) return "Ole";
  if(id == 5) return "Magda";
  if(id == 6) return "Hamsa";
  
  return "Unknown user. Cannot log.";
}


void loop() {

  if(Serial.available() == 0){

  lcd.setCursor(0, 0);
  lcd.print("[1] Log in");

  lcd.setCursor(0, 1);
  lcd.print("[2] Log out");

  }

  // put your main code here, to run repeatedly:
  else if(Serial.available() > 0) {
    String input = Serial.readString();
    input.trim();
    Serial.print("Reciving input: ");
    Serial.println(input);

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.println("Reciving input");

    delay(1000);


    if(input == "Log in"){
      digitalWrite(2, HIGH);
      Serial.println("You have logged in");

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Welcome <3");
      lcd.setCursor(0, 1);
      lcd.print("Magdalena"); //ID of the logger

      delay(2000);
      digitalWrite(2, LOW);
    }
    else if(input == "Log out"){
      digitalWrite(3, HIGH);
      Serial.println("You have logged out");

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Good bye!");
      lcd.setCursor(0, 1);
      lcd.print("Magdalena"); //ID of the logger

      delay(2000);
      digitalWrite(3, LOW);
    }

    else{
      Serial.println("Invalid input");

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Invalid input.");
    }
  }

}
