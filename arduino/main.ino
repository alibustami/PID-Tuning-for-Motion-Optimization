#include <MPU6050_light.h>
#include "Wire.h"

#define right_motor_en 10
#define right_motor_f 6
#define right_motor_b 7

#define left_motor_en 11
#define left_motor_f 4
#define left_motor_b 5

MPU6050 mpu(Wire);

const int minimum_speed = 60;
const int maximum_speed = 150;
const int forward_speed = 0;

const int set_point = 90;

// float sum_of_errors = 0;
// float last_error = 0;

// unsigned long prev_time = 0;

float kp;
float ki;
float kd;
unsigned int run_time;
int array_size;
unsigned int dump_rate;

void setup() {
  pinMode(right_motor_en, OUTPUT);
  pinMode(right_motor_f, OUTPUT);
  pinMode(right_motor_b, OUTPUT);

  pinMode(left_motor_en, OUTPUT);
  pinMode(left_motor_f, OUTPUT);
  pinMode(left_motor_b, OUTPUT);

  Serial.begin(9600);

  Wire.begin();

  byte status = mpu.begin();
  while (status != 0) {
  }
  delay(100);
  mpu.calcOffsets();
}

void loop() {
  bool recv_succ = false;
  float recv_data[5] = {-1.0, -1.0, -1.0, -1.0, -1.0};
  while (!recv_succ) {
    if (Serial.available() >= sizeof(float) * 5) {
      Serial.readBytes(reinterpret_cast<char*>(recv_data), sizeof(recv_data));
      Serial.print(recv_data[0], 10);
      Serial.print(" ");
      Serial.print(recv_data[1], 10);
      Serial.print(" ");
      Serial.print(recv_data[2], 10);
      Serial.print(" ");
      Serial.print(recv_data[3]);
      Serial.print(" ");
      Serial.print(recv_data[4]);
      Serial.print(" ");
      if ((recv_data[0] > 0) && (recv_data[1] >= 0) && (recv_data[2] >= 0) &&
          (recv_data[3] > 0) && (recv_data[4] > 0)) {
        recv_succ = true;
        Serial.println(String("done"));
      }
    }
  }
  run_simulation(recv_data);
  recv_succ = false;
  delay(500);
}

void run_simulation(float recv_data[]) {
  float sum_of_errors = 0;
  float last_error = 0;

  kp = recv_data[0];
  ki = recv_data[1];
  kd = recv_data[2];
  run_time = recv_data[3];
  dump_rate = recv_data[4];
  array_size = run_time / dump_rate;

  int* bounds = maxCorrection(recv_data);

  int dump_counter = 0;
  float correction, p, i, d = 0;
  float data[array_size];

  while (dump_counter < array_size) {
    mpu.update();
    unsigned long prev_time = millis();
    while ((millis() - prev_time) < dump_rate) {
      mpu.update();
    };
    float current_angle = mpu.getAngleZ();
    current_angle = correctAngle(current_angle);
    data[dump_counter] = current_angle;

    dump_counter++;

    Serial.println(data[dump_counter - 1], 10);

    // neg error -> robot left, pos error -> robot right
    int error = set_point - current_angle;

    sum_of_errors += error;

    p = error * kp;
    i = sum_of_errors * ki;
    d = (error - last_error) * kd;

    correction = p + i + d;
    Serial.print(correction, 10);
    Serial.print(" ");
    correction = corrrectionMapper(correction, bounds);
    Serial.print(correction, 10);
    Serial.print(" ");

    //    correction = int(correction);
    //    correction = boundSpeed(int(correction));

    controlRobot(correction);

    last_error = error;
  }
  stopMotors();
  sendData(data, array_size);
}

void controlRobot(float correction) {
  _control_right(correction);
  _control_left(-correction);
}

void _control_right(float correction) {
  if (correction > 0) {
    analogWrite(right_motor_en, correction);
    digitalWrite(right_motor_f, HIGH);
    digitalWrite(right_motor_b, LOW);
  } else {
    analogWrite(right_motor_en, -correction);
    digitalWrite(right_motor_f, LOW);
    digitalWrite(right_motor_b, HIGH);
  }
}

void _control_left(float correction) {
  if (correction > 0) {
    analogWrite(left_motor_en, correction);
    digitalWrite(left_motor_f, HIGH);
    digitalWrite(left_motor_b, LOW);
  } else {
    analogWrite(left_motor_en, -correction);
    digitalWrite(left_motor_f, LOW);
    digitalWrite(left_motor_b, HIGH);
  }
}

float boundSpeed(float correction) {
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
void sendData(float data_to_send[], int data_size) {
  bool sent_succ = false;
  String recv_msg = "";
  while (String("angles received") != recv_msg) {
    Serial.println();
    for (int i = 0; i < data_size; i++) {
      Serial.print(data_to_send[i]);
      Serial.print(";");
    }
    Serial.println();
    // while (!Serial.isAvailable());
    delay(50);
    recv_msg = Serial.readString();
  }
}

float correctAngle(float angle) {
  bool is_positive = (angle > 0) ? true : false;
  angle = abs(angle);

  angle = (angle > 180) ? 360 - angle : angle;
  angle = (is_positive) ? angle : -angle;
  return angle;
}

void stopMotors() {
  digitalWrite(left_motor_f, LOW);
  digitalWrite(left_motor_b, LOW);
  digitalWrite(right_motor_f, LOW);
  digitalWrite(right_motor_b, LOW);
}

int corrrectionMapper(float correction, int bounds[]) {
  int lower_range = bounds[0];
  int upper_range = bounds[1];

  int speed_range = 255 - forward_speed;

  int mapped_correction =
      map(correction, lower_range, upper_range, -speed_range, speed_range);
  //  Serial.print(mapped_correction);
  //  Serial.print(" ");
  //  Serial.println(upper_range);
  return mapped_correction;
}

int* maxCorrection(float consts[]) {
  float kp = consts[0];
  float ki = consts[1];
  float kd = consts[2];
  float exec_time = consts[3];

  int max_correction = kp * 360;  // + ki * 360 * exec_time + kd * 360;

  int* correction_bounds = new int[2];
  correction_bounds[0] = -max_correction;
  correction_bounds[1] = max_correction;

  return correction_bounds;
}
