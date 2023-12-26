#include "Wire.h"
#include <MPU6050_light.h>

#define right_motor_en 10
#define right_motor_f 6
#define right_motor_b 7

#define left_motor_en 11
#define left_motor_f 4
#define left_motor_b 5

MPU6050 mpu(Wire);

const int minimum_speed = 30;
const int maximum_speed = 150;


const int set_point = 90;

float sum_of_errors = 0;
float last_error = 0;

float data_batch[6]; // current angle, set point, error, correction speed before spliting, right motor speed, left motor speed

// int dump_counter = 0;
unsigned long start_time = 0;
unsigned long prev_time = 0;

int kp;
int ki;
int kd;
unsigned int run_time;
int array_size;
unsigned int dump_rate;

void setup(){
  pinMode(right_motor_en, OUTPUT);
  pinMode(right_motor_f, OUTPUT);
  pinMode(right_motor_b, OUTPUT);

  pinMode(left_motor_en, OUTPUT);
  pinMode(left_motor_f, OUTPUT);
  pinMode(left_motor_b, OUTPUT);

  Serial.begin(9600);

  Wire.begin();

  byte status = mpu.begin();
  while(status != 0){}
  delay(100);
  mpu.calcOffsets();
  // Serial.println(String("done setup"));
}

void loop(){
  float recv_data[5];
  if (Serial.available()){
    // Serial.println(String("revieving"));
    for (int i = 0; i < 5; i++){
      recv_data[i] = Serial.parseFloat();
    }
    // Serial.println(String("done revieving"));
    run_simulation(recv_data);
  }
  // Serial.println(String("stopping motors"));
  stop_motors();
  delay(500);
}

void run_simulation(float recv_data[]){
  // Serial.println(String("running simulation"));
  kp = recv_data[0];
  ki = recv_data[1];
  kd = recv_data[2];
  run_time = recv_data[3];
  dump_rate = recv_data[4];
  array_size = run_time / dump_rate;

  int dump_counter = 0;
  float correction, p, i, d = 0;
  float data[array_size];

  mpu.update();
  int current_angle = mpu.getAngleZ();
  current_angle = correct_angle(current_angle);
  // Serial.println(String("start looping"));
  while (dump_counter < array_size) {
    // Serial.print(String("loop: "));
    // Serial.println(String(dump_counter));
    prev_time = millis();
    while ((millis() - prev_time) < dump_rate);
    data[dump_counter] = current_angle;
    dump_counter++;

    int error = set_point - current_angle; // neg error -> robot left, pos error -> robot right

    sum_of_errors += error;

    p = error * kp;
    i = sum_of_errors * ki;
    d = (error - last_error) * kd;


    correction = p+i+d;

    correction = int(correction);
    correction = pull_down_speed(int(correction));


    control_robot(correction);

    last_error = error;
  }
  // Serial.println(String("done looping"));
  // Serial.println(String("sending data"));
  for (int i = 0; i < 5; i++){
    send_data(data, array_size);
  }
}

void _control_right(int correction){
  if (correction > 0){
    analogWrite(right_motor_en, correction);
    digitalWrite(right_motor_f, HIGH);
    digitalWrite(right_motor_b, LOW);
    data_batch[4] = float(correction);
  } else {
    analogWrite(right_motor_en, -correction);
    digitalWrite(right_motor_f, LOW);
    digitalWrite(right_motor_b, HIGH);
    data_batch[5] = float(-correction);
  }
}

void _control_left(int correction){
  if (correction > 0){
    analogWrite(left_motor_en, correction);
    digitalWrite(left_motor_f, HIGH);
    digitalWrite(left_motor_b, LOW);
  } else {
    analogWrite(left_motor_en, -correction);
    digitalWrite(left_motor_f, LOW);
    digitalWrite(left_motor_b, HIGH);
  }
}

void control_robot(int correction){
    _control_right(correction);
    _control_left(-correction);
}

int pull_down_speed(int correction){
  bool correction_is_positive;
  correction_is_positive = (correction > 0) ? true : false;

  correction = abs(correction);
  correction = (correction > maximum_speed) ? maximum_speed : correction;
  correction = (correction < minimum_speed) ? minimum_speed : correction;

  correction = (correction_is_positive) ? correction : -correction;

  return correction;
  }

/**
 * @brief send data to serial monitor in csv format
 *
 * @param data_to_send
 * @param data_size
 */
void send_data(float data_to_send[], int data_size){
  String data_string = "";
    for (int i = 0; i < data_size; i++){
      data_string += String(data_to_send[i]) + ",";
    }
    Serial.println(data_string);
  // Serial.println(String("done sending data"));
}

float correct_angle(float angle){
  bool is_positive = (angle > 0) ? true : false;
  angle = abs(angle);

  angle = (angle > 180) ? 360 - angle : angle;
  angle = (is_positive) ? angle : -angle;
  return angle;
}

void initialize_array(float arr[], float value){
  for (int i = 0; i < array_size; i++){
    arr[i] = value;
  }
}

void fill_array(float arr[], float value){
  for (int i = 0; i < array_size; i++){
    if (arr[i] == 181){
      arr[i] = value;
    }
  }
}

void stop_motors(){
  digitalWrite(left_motor_f, LOW);
  digitalWrite(left_motor_b, LOW);
  digitalWrite(right_motor_f, LOW);
  digitalWrite(right_motor_b, LOW);
}
