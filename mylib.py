import time
import smbus

class DFRobot_AS3935:
    def __init__(self, address, bus = 1):
        self.address = address
        self.i2cbus = smbus.SMBus(bus)

    def writeByte(self, register, value):
        self.i2cbus.write_byte_data(self.address, register, value)

    def readData(self, register):
        self.register = self.i2cbus.read_i2c_block_data(self.address, register)

    def manualCal(self, capacitance, location, disturber):
        self.powerUp()
        if location == 1:
            self.setIndoors()
        else:
            self.setOutdoors()

        if disturber == 0:
            self.disturberDis()
        else:
            self.disturberEn()

        self.setIrqOutputSource(0)
        time.sleep(0.5)
        self.setTuningCaps(capacitance)

    def setTuningCaps(self, capVal):
        if capVal > 120:
            self.singRegWrite(0x08, 0x0F, 0x0F)
        else:
            self.singRegWrite(0x08, 0x0F, capVal >> 3)

        self.singRegRead(0x08)
        print('capacitance set to 8x%d'%(self.register[0] & 0x0F))

    def powerUp(self):
        self.singRegWrite(0x00, 0x01, 0x00)
        self.calRCO()
        self.singRegWrite(0x08, 0x20, 0x20)
        time.sleep(0.002)
        self.singRegWrite(0x08, 0x20, 0x00)

    def powerDown(self):
        self.singRegWrite(0x00, 0x01, 0x01)

    def calRCO(self):
        self.writeByte(0x3D, 0x96)
        time.sleep(0.002)

    def setIndoors(self):
        self.singRegWrite(0x00, 0x3E, 0x24)

    def setOutdoors(self):
        self.singRegWrite(0x00, 0x3E, 0x1C)

    def disturberDis(self):
        self.singRegWrite(0x03, 0x20, 0x20)

    def disturberEn(self):
        self.singRegWrite(0x03, 0x20, 0x00)

    def singRegWrite(self, regAdd, dataMask, regData):
        self.singRegRead(regAdd)
        newRegData = (self.register[0] & ~dataMask)|(regData & dataMask)  
        self.writeByte(regAdd, newRegData)
        print('wrt: %02x'%newRegData)
        self.singRegRead(regAdd)
        print('Act: %02x'%self.register[0])

    def singRegRead(self,regAdd):
        self.readData(regAdd)

    def getInterrupt(self):
        time.sleep(0.01)
        self.singRegRead(0x03)
        intSrc = self.register[0]&0x0F
        if intSrc == 0x08:
            return 1
        elif intSrc == 0x04:
            return 2
        elif intSrc == 0x01:
            return 3
        else:
            return 0

    def reset(self):
        self.writeByte(0x3C, 0x96)
        time.sleep(0.002)

    def setLcoFdiv(self,fdiv):
        self.singRegWrite(0x03, 0xC0, (fdiv & 0x03) << 6)

    def setIrqOutputSource(self, irqSelect):
        if irqSelect == 1:
            self.singRegWrite(0x08, 0xE0, 0x20)
        elif irqSelect == 2:
            self.singRegWrite(0x08, 0xE0, 0x40)
        elif irqSelect == 3:
            self.singRegWrite(0x08, 0xE0, 0x80)
        else:
            self.singRegWrite(0x08, 0xE0, 0x00)

    def getLightningDistKm(self):
        self.singRegRead(0x07)
        return self.register[0]&0x3F

    def getStrikeEnergyRaw(self):
        self.singRegRead(0x06)
        nrgyRaw = (self.register[0]&0x1F) << 8
        self.singRegRead(0x05)
        nrgyRaw |= self.register[0]
        nrgyRaw <<= 8
        self.singRegRead(0x04)
        nrgyRaw |= self.register[0]
        
        return nrgyRaw/16777

    def setMinStrikes(self, minStrk):
        if minStrk < 5:
            self.singRegWrite(0x02, 0x30, 0x00)
            return 1
        elif minStrk < 9:
            self.singRegWrite(0x02, 0x30, 0x10)
            return 5
        elif minStrk < 16:
            self.singRegWrite(0x02, 0x30, 0x20)
            return 9
        else:
            self.singRegWrite(0x02, 0x30, 0x30)
            return 16

    def clearStatistics(self):
        self.singRegWrite(0x02, 0x40, 0x40)
        self.singRegWrite(0x02, 0x40, 0x00)
        self.singRegWrite(0x02, 0x40, 0x40)

    def getNoiseFloorLv1(self):
        self.singRegRead(0x01)
        return (self.register[0] & 0x70) >> 4

    def setNoiseFloorLv1(self, nfSel):
        if nfSel <= 7:
            self.singRegWrite(0x01, 0x70, (nfSel & 0x07) << 4)
        else:
            self.singRegWrite(0x01, 0x70, 0x20)
        
    def getWatchdogThreshold(self):
        self.singRegRead(0x01)
        return self.register[0] & 0x0F

    def setWatchdogThreshold(self, wdth):
        self.singRegWrite(0x01, 0x0F, wdth & 0x0F)

    def getSpikeRejection(self):
        self.singRegRead(0x02)
        return self.register[0] & 0x0F

    def setSpikeRejection(self, srej):
        self.singRegWrite(0x02, 0x0F, srej & 0x0F)







