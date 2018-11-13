import time
from mylib import DFRobot_AS3935
import RPi.GPIO as GPIO
from datetime import datetime

AS3935_I2C_ADDR1 = 0X01
AS3935_I2C_ADDR2 = 0X02
AS3935_I2C_ADDR3 = 0X03

AS3935_CAPACITANCE = 96
IRQ_PIN = 37

AS3935_INDOORS = 0
AS3935_OUTDOORS = 1
AS3935_MODE = AS3935_INDOORS

AS3935_DIST_DIS = 0
AS3935_DIST_EN = 1
AS3935_DIST = AS3935_DIST_EN

GPIO.setmode(GPIO.BOARD)

sensor = DFRobot_AS3935(AS3935_I2C_ADDR3, bus = 1)
sensor.reset()
sensor.manualCal(AS3935_CAPACITANCE, AS3935_MODE, AS3935_DIST)

#sensor.setLcoFdiv(0)
#sensor.setIrqOutputSource(3)

def handle(channel):
    global sensor
    time.sleep(0.005)
    intSrc = sensor.getInterrupt()
    if intSrc == 1:
        lightningDistKm = sensor.getLightningDistKm()
        print('Lightning occurs!')
        print('Distance: %dkm'%lightningDistKm)

        lightningEnergyVal = sensor.getStrikeEnergyRaw()
        print('Intensity: %d '%lightningEnergyVal)
    elif intSrc == 2:
        print('Disturber discovered!')
    elif intSrc == 3:
        print('Noise level too high!')
    else:
        pass

GPIO.setup(IRQ_PIN, GPIO.IN)
GPIO.add_event_detect(IRQ_PIN, GPIO.RISING, callback = handle)

while True:
    time.sleep(1.0)
