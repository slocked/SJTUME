#include <SPI.h>
#include <Ethernet.h>
#include <Wire.h>
#include <math.h>


byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

#define door1 6
#define door2 7


// if you don't want to use DNS (and reduce your sketch size)
// use the numeric IP instead of the name for the server:
IPAddress server(121,42,159,28);  
//char server[] = "www.sjtume.cn";  

// Set the static IP address to use if the DHCP fails to assign
IPAddress ip(192, 168, 0, 177);


EthernetClient client;


bool begin1 = false;
bool begin2 = false;
bool over1 = false;
bool over2 = true;
char d1_old = 'N';
char d2_old = 'N';
char d1_new = 'N';
char d2_new = 'N';
char c = ' ';



void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  pinMode(door1, OUTPUT);
  pinMode(door2, OUTPUT);
  digitalWrite(door1, HIGH);
  digitalWrite(door2, HIGH);
  
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // start the Ethernet connection:
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
    // try to congifure using IP address instead of DHCP:
    Ethernet.begin(mac, ip);
  }
  // give the Ethernet shield a second to initialize:
  delay(1000);
  Serial.println("connecting...");
  printIPAddress();

}



void loop() {
  digitalWrite(door1, HIGH);
  digitalWrite(door2, HIGH);
 
  if (client.available()) {
    c = client.read();
      Serial.print(c);
      if (begin1){
        d1_new = c;
        begin1 = false;
        over1 = true;
      }
      if (over2 && c=='['){
        begin1 = true;
        over2 = false;
      }
      if (begin2){
        d2_new = c;
        begin2 =false;
        over2 = true;
      }
      if (over1 && c=='['){
        begin2 = true;
        over1 = false;
      }


      if (d1_old != d1_new){
        digitalWrite(door1, LOW);
        delay(1000);
        Serial.println(" ");
        Serial.println("open door1");
      }
      if (d2_old != d2_new){
        digitalWrite(door2, LOW);
        Serial.println(" ");
        delay(1000);
        Serial.println("open door2");
      }

      d1_old = d1_new;
      d2_old = d2_new;

 
  }
  
  if (!client.connected()) {
      Serial.println(" ");
      Serial.print("door1:");
      Serial.println(d1_old);
      Serial.print("door2:");
      Serial.print(d2_old);
      delay(1000);
         getData();
  }
}


void printIPAddress(void){
  Serial.print("My IP address: ");
  for (byte thisByte = 0; thisByte < 4; thisByte++) {
    // print the value of each byte of the IP address:
    Serial.print(Ethernet.localIP()[thisByte], DEC);
    Serial.print(".");
  }
  Serial.println();
}



void getData(void) {
  if (client.connect(server, 80)) {
    Serial.println("connecting...");
    client.println("GET /door");
    client.println("Connection: close");
    client.println();   
  } 
  else {
    Serial.println("connection failed");
    client.stop();}
}
