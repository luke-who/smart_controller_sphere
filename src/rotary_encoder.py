from gpiozero import Button
from signal import pause
import os,sys
import argparse
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
clk = Button(17)
dt = Button(18)
button = Button(27)

countName=None
countSingle=None
#Who is first ? 
clock_first= None
#previous tick long ago ? 
click_time=time.time()

count=0
remainder = 0

def clk_edge():
    global clock_first
    global click_time
    global count
    global remainder
    if time.time()-click_time > 0.07:
        clock_first = None
        click_time=time.time()
        #print('Reset encoder')
    if clock_first is None:
        #print("Clock first")
        clock_first= True
    elif clock_first is False:
        #print('count up')
        clock_first= None
        count =count +1
        remainder = count % 25
        print(remainder)
    else: 
        print('double clock , ERROR')
        clock_first= None

    
def dt_both_edge():
        global clock_first
        global click_time
        global count
        global remainder
        if time.time()-click_time > 0.07:
                clock_first = None
                click_time=time.time()
                #print('Reset encoder')
        if clock_first is None:
                #print("dt first")
                clock_first= False
        elif clock_first is True:
                #print('count down')
                clock_first= None
                count=count-1
                remainder = count % 25
                print(remainder)
        else: 
                print('double dt , ERROR')
                clock_first= None
        return remainder
    

def main():
        button.when_pressed = pausing
        clk.when_pressed = clk_edge
        dt.when_pressed = dt_both_edge

        try:
                while True:
                        # if button.is_active==False:
                        pause()
                        # else:
                        #         break
        except KeyboardInterrupt:
                print("Ctrl+c exit")


def pausing():
        hours = dt_both_edge()
        print("Pausing for {} hours".format(hours))
        sys.exit()

def delete(button):
    print("Past {} hours file deleted".format(button))

if __name__ == "__main__":
   main()