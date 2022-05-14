import time
import datetime
import requests
import json
import subprocess32 as subprocess
import RPi.GPIO as GPIO
from gpiozero import PWMLED
from gpiozero import Motor
from gpiozero import Button
from signal import pause

import sys
# # insert at 1, 0 is the script path (or '' in REPL)
# sys.path.insert(0, '/log/')
sys.path.insert(0, "/home/pi/Documents/Repo/Sphere_summer_project/mycode/")
from log import log
from Audio_Feedback import Audio
# Import the ADS1x15 module.
import Adafruit_ADS1x15
import argparse

button1 = Button(21)
button2 = Button(13)
button3 = Button(5)

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()

motor = Motor(forward=26,backward=20)

GAIN = 1
# led = PWMLED(4)

endpointurl="http://192.168.1.99/query_status.php"
controlshgendpoint="http://192.168.1.99:8161/api/message/SPHERE.CTRL.SHG?type=topic"
username='admin'
password='erehps767'
headers = {"Content-Type": "application/json"}

def get_Host_IP():
    # RetMyIP=str(subprocess.call(["hostname", "-I"]))
    RetMyIP=str(subprocess.check_output(["hostname", "-I"]))[:]  #This will give primary address like 192.168.2.23
    return RetMyIP

def rotate_motor_backward(percent):
    #rotates back the potentiometer
    motor.forward(speed=percent)

def rotate_motor_forward(percent):
    motor.backward(speed=percent)


def value_difference():
    val_current = int(adc.read_adc(1, gain=GAIN))
    time.sleep(0.1)
    val_delayed = int(adc.read_adc(1, gain=GAIN))
    # print("current_adc : {} delayed_adc: {}".format(val_current,val_current))
    return val_current,val_delayed

def manual_rotation(val_current,val_delayed):
    manual_rotation=False

    if abs(val_current-val_delayed)>20:
        manual_rotation=True
    else:
        manual_rotation=False

    return manual_rotation

def goForwardToAdcAngle(angleDegrees,minimumAdcValue,maximumAdcValue):
    angle_ratio=(maximumAdcValue-minimumAdcValue)/320
    angle_adc=minimumAdcValue+angle_ratio * angleDegrees
    if(angle_adc>maximumAdcValue-200):
        angle_adc=maximumAdcValue-200
    start_rotation=False
    speed=0.5
    while True:
        try:
            value = adc.read_adc(1, gain=GAIN)
        except Exception as ex:
            print(ex)
        if value > angle_adc:
            motor.stop()
            print("stopping adc{} angle{}".format(value,(value - minimumAdcValue)/angle_ratio))
            break
        if start_rotation==True:
            speed=0.5
            rotate_motor_forward(speed)
            speed=speed-0.07
            start_rotation=False
        else:
            if speed>0.40:
                speed=speed-0.001
        start_rotation=True
        rotate_motor_forward(speed)

def goBackToAdcAngle(angleDegrees,minimumAdcValue,maximumAdcValue):
    angle_ratio=(maximumAdcValue-minimumAdcValue)/320
    angle_adc=minimumAdcValue+angle_ratio * angleDegrees
    if angle_adc<minimumAdcValue+40:
        angle_adc=minimumAdcValue+40
    start_rotation=False
    speed=0.5
    while True:
        try:
            value = adc.read_adc(1, gain=GAIN)
        except Exception as ex:
            print(ex)
        if value < angle_adc:
            motor.stop()
            print("stopping adc{} angle{}".format(value,(value - minimumAdcValue)/angle_ratio))
            break
        if start_rotation==True:
            speed=0.65
            rotate_motor_backward(speed)
            speed=speed-0.1
            start_rotation=False
        else:
            if speed>0.40:
                speed=speed-0.002
        start_rotation=True
        rotate_motor_backward(speed)


class CalibrationValues:
    def __init__(self):
        self.minimum=0
        self.maximum=25300
    def calibrate(self):
        speed=0.5
        start_rotation=False
        calibration_duration=15
        start_time=time.time()
        while True:
            try:
                value = adc.read_adc(1, gain=GAIN)
            except Exception as ex:
                print(ex)
            if value > self.maximum:
                self.maximum=value
            if value < self.minimum:
                self.minimum=value
            if start_rotation==True:
                speed=0.65
                rotate_motor_backward(speed)
                speed=speed-0.1
                start_rotation=False
            else:
                if speed>0.40:
                    speed=speed-0.002
            start_rotation=True
            rotate_motor_backward(speed)
            if(time.time()-start_time)>calibration_duration:
                motor.stop()
                break

    def tickBackWards(self):
        speed=0.5
        rotate_motor_backward(speed)
        time.sleep(0.02)
        motor.stop()
        value=adc.read_adc(1, gain=GAIN)
        adc_angle=(value-self.minimum)/(self.maximum-self.minimum)*320
        print("stopping adc{} angle{}".format(value,adc_angle))

class Time_Comparison(CalibrationValues):
    def __init__(self):
        self.current_time=time.strftime("%H%M%S",time.localtime())
        #Testing for hours
        self.finish_time=""
        self.next_time=""
        #Testing for minutes
        self.finish_minute=""
        self.next_minute=""

        self.midnight_time="000000"
        value=adc.read_adc(1, gain=GAIN)
        # Calibrate=CalibrationValues()
        self.angle=(value-CalibrationValues().minimum)/(CalibrationValues().maximum-CalibrationValues().minimum)*320

        #Divide the degree into hours:every 20 degree count as an increase of 1 hour
        if int(self.angle)%20>=0 and int(self.angle)%20<10:
            self.chosen_hour=int(int(self.angle/10)/2)
        elif int(self.angle)%20>=10 and int(self.angle)%20<20:
            self.chosen_hour=int((int(self.angle/10)-1)/2)
        
        self.next_angle=(self.chosen_hour*20)-10
    #Testing for hours
    def Finish_Time(self):
        #convert hour from str to int
        current_hour=int(self.current_time[:2])
        #minute&second remain as str
        current_minute=self.current_time[2:4]
        current_second=self.current_time[4:]

        future_hr = (self.chosen_hour+current_hour)%24
        #convert int back to str
        if future_hr<10:
            self.finish_time='0'+str(future_hr)+current_minute+current_second
        else:
            self.finish_time=str(future_hr)+current_minute+current_second

        return self.finish_time

    def Next_Time(self):
        #convert hour from str to int
        current_hour=int(self.current_time[:2])
        #minute&second remain as str
        current_minute=self.current_time[2:4]
        current_second=self.current_time[4:]

        next_hr = (1+current_hour)%24
        #convert int back to str
        if next_hr<10:
            self.next_time='0'+str(next_hr)+current_minute+current_second
        else:
            self.next_time=str(next_hr)+current_minute+current_second

        return self.next_time

    #Testing for minutes
    def Finish_Minute(self):
        current_hour=self.current_time[:2]
        current_minute=int(self.current_time[2:4])
        current_second=self.current_time[4:]

        future_min = (self.chosen_hour+current_minute)%60
        #convert int back to str
        if future_min<10:
            self.finish_minute=current_hour+'0'+str(future_min)+current_second
        else:
            self.finish_minute=current_hour+str(future_min)+current_second

        return self.finish_minute

    def Next_Minute(self):
        current_hour=self.current_time[:2]
        current_minute=int(self.current_time[2:4])
        current_second=self.current_time[4:]

        next_min = (1+current_minute)%60
        #convert int back to str
        if next_min<10:
            self.next_minute=current_hour+'0'+str(next_min)+current_second
        else:
            self.next_minute=current_hour+str(next_min)+current_second

        return self.next_minute


    #fix the 0 degree problem(it might never reach zero!) and degrees that are divisible by 10
    def calibrate_degree(self):
        #adjust the current angle for every 20 degree, keep the value of int(self.angle/10) an odd number
        if self.angle > 0 and self.angle < 180:
            if int(self.angle)%20>=0 and int(self.angle)%20<7 or int(self.angle)%20<0:
                self.angle=(int(self.angle/10)+1)*10
                goForwardToAdcAngle((self.angle),calValues.minimum,calValues.maximum)
                print("adjusted to angle {}".format(self.angle))
            elif int(self.angle)%20>13 and int(self.angle)%20<19 :
                self.angle=int(self.angle/10)*10
                goBackToAdcAngle(self.angle,calValues.minimum,calValues.maximum)
                print("adjusted to angle {}".format(self.angle))


class Execute(Time_Comparison):
    def __init__(self):
        self.duration=''
        self.stoppedUntil_sec_HMS=''
        self.status_code=000
        try:
            R=requests.get(endpointurl)
            self.JsonBody=json.loads(R.text)
            # print(self.JsonBody)
            self.status_code=R.status_code
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print(e)

        self.stopped=self.JsonBody['stopped']
        if self.stopped==False:
            self.duration='0h'
        elif self.stopped==True:
            self.stoppedFor=self.JsonBody['stoppedFor']     #There's no value for 'stoppedFor' if self.stopped==False
            if self.stoppedFor<0:
                self.duration='forever'
            else:
                self.stoppedUntil_sec=(self.JsonBody['stoppedUntil'])['sec']    #There's no value for 'stoppedUntil_sec' if self.stopped==False
                self.stoppedUntil_sec_HMS=datetime.datetime.fromtimestamp(int(self.stoppedUntil_sec)).strftime('%H%M%S')
                # print(self.stoppedUntil_sec_HMS)
                if self.stoppedUntil_sec_HMS=='000000':     #UTC time(GMT) instead of local BST time which is '010000'
                    self.duration='today'
                else:
                    if int(self.stoppedFor/3600000) <=8 and int(self.stoppedFor/3600000) >=0:
                        self.duration=str(int(self.stoppedFor/3600000))+'h'

        # print(self.duration)

    def Pause(self,chosen_hour):
        # STOP RECORDING PAYLOAD FOR nh
        payload_for_pause_before='{"jsonrpc":"2.0","method":"pause","params":{"delay":0, "duration": "'
        payload_for_pause_suffix='","modality": "all"},"id":"genie_12345","dest":"node-red","src":"genie"}'
        payload_for_pause=payload_for_pause_before+chosen_hour+payload_for_pause_suffix
        print(payload_for_pause)
        payload_pause_json=json.loads(payload_for_pause)
        try:
            r = requests.post(controlshgendpoint, json=payload_pause_json,  auth=(username, password),headers=headers)
            self.status_code=r.status_code
            # print(r.status_code)
            # print(r.text)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print(e)
        r=requests.get(endpointurl)
        self.status_code=r.status_code



    def Start(self):
        #START RECORDING PAYLOAD
        payload_for_start='{"jsonrpc":"2.0","method":"start","params":{"delay":0, "modality": "all"},"id":"index.php_863310","dest":"node-red","src":"web_wp6"}'
        print(payload_for_start)
        payload_start_json=json.loads(payload_for_start)
        try:
            r = requests.post(controlshgendpoint, json=payload_start_json, auth=(username, password),headers=headers)
            self.status_code=r.status_code
            # print(r.status_code)
            # print(r.text)
        except requests.exceptions.RequestException as e:
            print(e)
        r=requests.get(endpointurl)
        self.status_code=r.status_code

    def Delete(self,chosen_hour):
        #DELETE CERTAIN AMOUNT OF HOURS' DATA
        payload_for_delete_before='{"jsonrpc":"2.0","method":"delete","params":{"duration": "'
        payload_for_delete_suffix='","unit": "h","modality": "all"},"id":"genie_12345","dest":"node-red","src":"genie"}'
        payload_for_delete=payload_for_delete_before+chosen_hour+payload_for_delete_suffix
        # print(payload_for_delete)
        payload_delete_json=json.loads(payload_for_delete)
        try:
            r = requests.post(controlshgendpoint, json=payload_delete_json, auth=(username, password),headers=headers)
            self.status_code=r.status_code
            # print(r.status_code)
            # print(r.text)
        except requests.exceptions.RequestException as e:
            print(e)
        r=requests.get(endpointurl)
        self.status_code=r.status_code


#Calibration
calValues=CalibrationValues()
#calValues.calibrate()
angle_ratio=(calValues.maximum-calValues.minimum)/320
print("Minimum value:{} maximum value:{} ohms_per_degree{}".format(calValues.minimum,calValues.maximum,angle_ratio))

get=Time_Comparison()
start_time=get.current_time
# Testing for hours
finish_time=get.Finish_Time()
next_time=get.Next_Time()
# Testing for minutes
finish_minute=get.Finish_Minute()
next_minute=get.Next_Minute()


#Automate Manual rotation:
# for i in range(9):
#     goForwardToAdcAngle((i*2+1)*10,calValues.minimum,calValues.maximum)
#     time.sleep(1)
# goBackToAdcAngle(10,calValues.minimum,calValues.maximum)


# Audio.play_Adventure_Time()
while True:
    execute=Execute()
    Get=Time_Comparison()
    current_time=Get.current_time

    #Pausing for costumised hours
    chosen_hour=Get.chosen_hour
    chosen_angle=Get.angle

    val_current,val_delayed=value_difference()
    ##DELETE PART
    if button1.is_pressed:
        button1.wait_for_press()
        execute.Delete("1")
        print("Deleting 1 hrs data!")
        button1.wait_for_release()
        Audio.beep(1)   #Beep once
        log.log_this(Host_IP=get_Host_IP(),Mode="Delete 1h",stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=finish_time)
    elif button2.is_pressed:
        button2.wait_for_press()
        execute.Delete("6")
        print("Deleting 6 hrs data!")
        button2.wait_for_release()
        Audio.beep(2)   #Beep twice
        log.log_this(Host_IP=get_Host_IP(),Mode="Delete 6h",stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=finish_time)
    elif button3.is_pressed:
        button3.wait_for_press()
        execute.Delete("24")
        print("Deleting 24 hrs data!")
        button3.wait_for_release()
        Audio.beep(4)   #Beep three times
        log.log_this(Host_IP=get_Host_IP(),Mode="Delete 24h",stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=finish_time)

    ##PAUSE PART
    if manual_rotation(val_current,val_delayed)==True:
        start_time=current_time
        # Testing for hours
        finish_time=Get.Finish_Time()
        next_time=Get.Next_Time()
        # Testing for minutes
        finish_minute=Get.Finish_Minute()
        next_minute=Get.Next_Minute()

        #The Pause() function need to be in the manual_rotation()==True statement to avoid sending pausing signals all the time when manual_rotation()==False
        if chosen_angle > 0 and chosen_angle <20:
            if execute.stopped==True:    #This means other device could've set a pause but the user trying to change that on this device
                #START RECORDING
                execute.stopped=False
            elif execute.stopped==False:     #The system's already started recording so it's fine
                continue
            execute.Start()
        elif chosen_angle >= 20 and chosen_angle < 180:
            if execute.stopped==False:
                execute.stopped=True
            elif execute.stopped==True:
                if execute.duration!=str(chosen_hour)+'h':
                    execute.duration='{}h'.format(chosen_hour)
                else:
                    continue
            # STOP RECORDING PAYLOAD FOR nh
            execute.Pause("{}h".format(chosen_hour))
            if chosen_hour>=1 or chosen_hour<=8:
                Audio.beep(1)
        elif chosen_angle > 180 and chosen_angle < 240:
            if execute.stopped==False:
                execute.stopped=True
            elif execute.stopped==True:
                if execute.duration!='today':
                    execute.duration='today'
                else:
                    continue
            # STOP RECORDING PAYLOAD TODAY
            execute.stoppedUntil_sec_HMS='000000'
            execute.Pause("today")
            Audio.play_Super_Mario()
            time.sleep(0.5)
        elif chosen_angle > 240 and chosen_angle < 300:
            if execute.stopped==False:
                execute.stopped=True
            elif execute.stopped==True:
                if execute.duration!='forever':
                    execute.duration='forever'
                else:
                    continue
            # STOP RECORDING PAYLOAD FOREVER
            execute.Pause("forever")
            time.sleep(0.5)
            Audio.play_Super_Mario_Underworld()
        log.log_this(Host_IP=get_Host_IP(),manual_rotation=True,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=finish_time)


    elif manual_rotation(val_current,val_delayed)==False:
        #Define degrees
        if chosen_angle > 1 and chosen_angle < 180:
            if chosen_angle < 20:
                if execute.stopped==True:
                    if execute.duration=='today':
                        goForwardToAdcAngle(210,calValues.minimum,calValues.maximum)
                        log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=execute.stoppedUntil_sec_HMS)    #finish_time=execute.stoppedUntil_sec_HMS
                    elif execute.duration=='forever':
                        goForwardToAdcAngle(270,calValues.minimum,calValues.maximum)
                        log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time)
                    elif int(execute.duration[0])>=0 and int(execute.duration[0])<=8:   #Any other given hours etc. say '1h'
                        C_hour=int(execute.duration[0])
                        goForwardToAdcAngle((C_hour*2+1)*10,calValues.minimum,calValues.maximum)
                        log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=execute.stoppedUntil_sec_HMS)
                else:
                    # START RECORDING PAYLOAD
                    # execute.Start()
                    continue
            elif chosen_angle >= 20:
                if execute.stopped==True:
                    print(execute.duration)
                    if execute.duration=='today':
                        goForwardToAdcAngle(210,calValues.minimum,calValues.maximum)
                        log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=execute.stoppedUntil_sec_HMS)
                    elif execute.duration=='forever':
                        goForwardToAdcAngle(270,calValues.minimum,calValues.maximum)
                        log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time)
                    elif int(execute.duration[0])>=0 or int(execute.duration[0])<=8:
                        C_hour=int(execute.duration[0])
                        if chosen_hour > int(execute.duration[0]):
                            goBackToAdcAngle((C_hour*2+1)*10,calValues.minimum,calValues.maximum)
                            log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=execute.stoppedUntil_sec_HMS)
                        elif chosen_hour < int(execute.duration[0]):
                            goForwardToAdcAngle((C_hour*2+1)*10,calValues.minimum,calValues.maximum)
                            log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=execute.stoppedUntil_sec_HMS)
                        elif chosen_hour == int(execute.duration[0]):
                            if current_time!=next_minute:
                                # print("current time:{} next time: {} start time:{} finish time: {} angle: {}".format(current_time,next_minute,start_time,execute.stoppedUntil_sec_HMS,chosen_angle))
                                continue
                            elif current_time==next_minute:
                                next_minute=Get.Next_Minute()
                                Get.calibrate_degree()
                                if chosen_hour==1:
                                    continue
                                else:
                                    # STOP RECORDING PAYLOAD
                                    execute.Pause("{}h".format(Get.chosen_hour-1))
                                goBackToAdcAngle(Get.next_angle,calValues.minimum,calValues.maximum)
                                execute.duration='{}h'.format(Get.chosen_hour-1)
                                # print(execute.duration)
                                log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=execute.stoppedUntil_sec_HMS)
                                time.sleep(1)
                elif execute.stopped==False:
                    goBackToAdcAngle(10,calValues.minimum,calValues.maximum)
                    log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time)

        #Pausing for the rest of the day
        elif chosen_angle > 180 and chosen_angle < 240:
            if execute.stopped==True:
                if execute.duration=='forever':
                    goForwardToAdcAngle(270,calValues.minimum,calValues.maximum)
                    log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time)
                elif execute.duration=='today':
                    if current_time==Get.midnight_time:
                        goBackToAdcAngle(10,calValues.minimum,calValues.maximum)
                        log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=execute.stoppedUntil_sec_HMS)
                        execute.Start()
                    else:
                        continue
                elif int(execute.duration[0])>=0 or int(execute.duration[0])<=8:
                    C_hour=int(execute.duration[0])
                    goBackToAdcAngle((C_hour*2+1)*10,calValues.minimum,calValues.maximum)
                    log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=execute.stoppedUntil_sec_HMS)

            elif execute.stopped==False:
                goBackToAdcAngle(10,calValues.minimum,calValues.maximum)
                log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time)

        # Pausing forever
        elif chosen_angle > 240 and chosen_angle < 300:
            if execute.stopped==True:
                if execute.duration=='forever':
                    continue
                elif execute.duration=='today':
                    goBackToAdcAngle(210,calValues.minimum,calValues.maximum)
                    log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=execute.stoppedUntil_sec_HMS)
                elif int(execute.duration[0])>=0 or int(execute.duration[0])<=8:
                    C_hour=int(execute.duration[0])
                    goBackToAdcAngle((C_hour*2+1)*10,calValues.minimum,calValues.maximum)
                    log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time,finish_time=execute.stoppedUntil_sec_HMS)

            elif execute.stopped==False:
                goBackToAdcAngle(10,calValues.minimum,calValues.maximum)
                log.log_this(Host_IP=get_Host_IP(),manual_rotation=False,stopped=execute.stopped,duration=execute.duration,status_code=execute.status_code,degree=chosen_angle,start_time=start_time)

            continue
