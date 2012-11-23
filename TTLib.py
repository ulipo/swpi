###########################################################################
#     Sint Wind PI
#     Copyright 2012 by Tonino Tarsi <tony.tarsi@gmail.com>
#   
#     Please refer to the LICENSE file for conditions 
#     Visit http://www.vololiberomontecucco.it
# 
##########################################################################

import ftplib
import urllib2
import os
import datetime
import socket
import Image
import ImageFont
import ImageDraw
import time
import config    
import globalvars
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import urllib,urllib2
import cmath ,math
import json
import tempfile    
import sensor_simulator
import ntplib
import tarfile


class RingBuffer(object):
    def __init__(self, size):
        self.data = [None for i in xrange(size)]

    def append(self, x):
        self.data.pop(0)
        self.data.append(x)

    def get(self):
        return self.data
    
    def getMean(self):
        i = 0
        s = 0
        for val in self.data:
            if val != None:
                #print val
                i = i+1
                s = s+val
        if ( i == 0 ):
            return None
        else:       
            return (s/float(i))

    def getMeanDir(self):
        s = 0
        for val in self.data:
            if val != None:
                s = s + cmath.rect(1, math.radians(val)) 
        return math.degrees(cmath.phase(s))


    def getMeanMax(self):
        i = 0
        s = 0
        maxval = None
        for val in self.data:
            if val != None:
                #print val
                i = i+1
                s = s+val
                if ( maxval == None ):
                    maxval = val
                else:
                    maxval = max(maxval,val)
        if ( i == 0 ):
            return None,None
        else:
            return (s/float(i)),maxval


def swpi_update():
    url = ' http://www.vololiberomontecucco.it/swpi/swpi-src.tar.gz'
    urllib.urlretrieve(url,filename='swpi-src.tar.gz')
    t = tarfile.open('swpi-src.tar.gz', 'r:gz')
    t.extractall('../')  
    os.remove("swpi-src.tar.gz")


def SetTimeFromNTP(ntp_server):
    try:
        c = ntplib.NTPClient()
        date_str = c.request(ntp_server, version=3)
        if (date_str != None ):
            os.system("sudo date -s '%s'" %  time.ctime(date_str.tx_time))
            log("System time adjusted from NPT server : " + ntp_server)
            return True
        return False
    except:
        log("ERROR - Failed to set time system from ntp server")
        return False




def logData(serverfile):
    mydata = []
    mydata.append(('last_measure_time',NoneToNull(globalvars.meteo_data.last_measure_time)))
    mydata.append(('idx',NoneToNull(globalvars.meteo_data.idx)))
    mydata.append(('wind_dir_code',NoneToNull(globalvars.meteo_data.wind_dir_code)))
    mydata.append(('wind_dir',NoneToNull(globalvars.meteo_data.wind_dir)))
    mydata.append(('wind_ave',NoneToNull(globalvars.meteo_data.wind_ave)))
    mydata.append(('wind_gust',NoneToNull(globalvars.meteo_data.wind_gust)))
    mydata.append(('temp_out',NoneToNull(globalvars.meteo_data.temp_out)))
    mydata.append(('abs_pressure',NoneToNull(globalvars.meteo_data.abs_pressure)))
    mydata.append(('hum_out',NoneToNull(globalvars.meteo_data.hum_out)))
    mydata.append(('rain',NoneToNull(globalvars.meteo_data.rain)))
    mydata.append(('rain_rate',NoneToNull(globalvars.meteo_data.rain_rate)))
    mydata.append(('temp_in',NoneToNull(globalvars.meteo_data.temp_in)))
    mydata.append(('hum_in',NoneToNull(globalvars.meteo_data.hum_in)))
    mydata.append(('wind_chill',NoneToNull(globalvars.meteo_data.wind_chill)))
    mydata.append(('temp_apparent',NoneToNull(globalvars.meteo_data.temp_apparent)))
    mydata.append(('dew_point',NoneToNull(globalvars.meteo_data.dew_point)))
    mydata.append(('uv',NoneToNull(globalvars.meteo_data.uv)))
    mydata.append(('illuminance',NoneToNull(globalvars.meteo_data.illuminance)))
    mydata.append(('winDayMin',NoneToNull(globalvars.meteo_data.winDayMin)))
    mydata.append(('winDayMax',NoneToNull(globalvars.meteo_data.winDayMax)))
        
    mydata.append(('winDayGustMin',NoneToNull(globalvars.meteo_data.winDayGustMin)))
    mydata.append(('winDayGustMax',NoneToNull(globalvars.meteo_data.winDayGustMax)))
    
    mydata.append(('TempOutMin',NoneToNull(globalvars.meteo_data.TempOutMin)))
    mydata.append(('TempOutMax',NoneToNull(globalvars.meteo_data.TempOutMax)))
    
    mydata.append(('TempInMin',NoneToNull(globalvars.meteo_data.TempInMin)))
    mydata.append(('TempInMax',NoneToNull(globalvars.meteo_data.TempInMax)))
    
    mydata.append(('UmOutMin',NoneToNull(globalvars.meteo_data.UmOutMin)))
    mydata.append(('UmOutMax',NoneToNull(globalvars.meteo_data.UmOutMax)))
    
    mydata.append(('UmInMin',NoneToNull(globalvars.meteo_data.UmInMin)))
    mydata.append(('UmInMax',NoneToNull(globalvars.meteo_data.UmInMax)))
    
    mydata.append(('PressureMin',NoneToNull(globalvars.meteo_data.PressureMin)))
    mydata.append(('PressureMax',NoneToNull(globalvars.meteo_data.PressureMax)))
    
       
    mydata.append(('wind_dir_ave',NoneToNull(globalvars.meteo_data.wind_dir_ave)))

    
    mydata=urllib.urlencode(mydata)
    
    req=urllib2.Request(serverfile, mydata)
    
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    try:
        page=urllib2.urlopen(req).read()
        log( "Data sent to server : " + page )
    except:
        log(  "Error connecting to server : " + serverfile )
        pass

def UploadData(cfg):
    mydata = {} 
    
    mydata['last_measure_time'] = (globalvars.meteo_data.last_measure_time.strftime("[%d/%m/%Y-%H:%M:%S]"))
    mydata['idx'] = (globalvars.meteo_data.idx.strftime("[%d/%m/%Y-%H:%M:%S]"))
    mydata['wind_dir_code'] = (globalvars.meteo_data.wind_dir_code)
    mydata['wind_dir'] = (globalvars.meteo_data.wind_dir)
    mydata['wind_ave'] = (globalvars.meteo_data.wind_ave)
    mydata['wind_gust'] = (globalvars.meteo_data.wind_gust)
    mydata['temp_out'] = (globalvars.meteo_data.temp_out)
    mydata['abs_pressure'] = (globalvars.meteo_data.abs_pressure)
    mydata['hum_out'] = (globalvars.meteo_data.hum_out)
    mydata['rain'] = (globalvars.meteo_data.rain)
    mydata['rain_rate'] = (globalvars.meteo_data.rain_rate)
    mydata['temp_in'] = (globalvars.meteo_data.temp_in)
    mydata['hum_in'] = (globalvars.meteo_data.hum_in)
    mydata['wind_chill'] = (globalvars.meteo_data.wind_chill)
    mydata['temp_apparent'] = (globalvars.meteo_data.temp_apparent)
    mydata['dew_point'] = (globalvars.meteo_data.dew_point)
    mydata['uv'] = (globalvars.meteo_data.uv)
    mydata['illuminance'] = (globalvars.meteo_data.illuminance)
    mydata['winDayMin'] = (globalvars.meteo_data.winDayMin)
    mydata['winDayMax'] = (globalvars.meteo_data.winDayMax)
        
    mydata['winDayGustMin'] = (globalvars.meteo_data.winDayGustMin)
    mydata['winDayGustMax'] = (globalvars.meteo_data.winDayGustMax)
    
    mydata['TempOutMin'] = (globalvars.meteo_data.TempOutMin)
    mydata['TempOutMax'] = (globalvars.meteo_data.TempOutMax)
    
    mydata['TempInMin'] = (globalvars.meteo_data.TempInMin)
    mydata['TempInMax'] = (globalvars.meteo_data.TempInMax)
    
    mydata['UmOutMin'] = (globalvars.meteo_data.UmOutMin)
    mydata['UmOutMax'] = (globalvars.meteo_data.UmOutMax)
    
    mydata['UmInMin'] = (globalvars.meteo_data.UmInMin)
    mydata['UmInMax'] = (globalvars.meteo_data.UmInMax)
    
    mydata['PressureMin'] = (globalvars.meteo_data.PressureMin)
    mydata['PressureMax'] = (globalvars.meteo_data.PressureMax)
    
       
    mydata['wind_dir_ave'] = (globalvars.meteo_data.wind_dir_ave)
    
    #print mydata
    

    
    j = json.dumps(mydata)
    objects_file = './meteo.txt'

    f = open(objects_file,'w')
    f.write(j + "\n")
    f.close()
    
    
    sendFileToServer(objects_file,'meteo.txt',cfg.ftpserver,cfg.upload_folder,cfg.ftpserverLogin,cfg.ftpserverPassowd)

    
    


def NoneToNull(var):
    if ( var == None ):
        return "Null"
    else:
        return var
    
def DBFielsToNumbet(var):
    if ( var == None ):
        return None
    else:
        return var    
    
    
def waitForHandUP():
    if ( not globalvars.bAnswering):
        return
    else:
        log("Waiting for HangUP ...")
        for i in range (1,100):
            if (  globalvars.bAnswering):
                time.sleep(1)
            else:
                globalvars.bAnswering = False
                return
            
def waitForCameraCapture():
    if ( not globalvars.bCapturingCamera):
        return
    else:
        log("Waiting cameras to capture ...")
        for i in range (1,100):
            if (  globalvars.bCapturingCamera):
                time.sleep(1)
            else:
                globalvars.bCapturingCamera = False
                return


def log(message) :
    print datetime.datetime.now().strftime("[%d/%m/%Y-%H:%M:%S]") , message

def getFileName(path):
    return os.path.basename(path)

def addTextandResizePhoto(filename,finalresolutionX,finalresolutionY,cfg,version=None):
    textColor = (255,255,0)
    offsetUpper = 20
    offsetBottom = 32
    marginLeft = 10
    MarginRight = 10
    bgrColor = (50, 30, 255)
    
    #font_path = "./fonts/arial.ttf"
    font_path = "./fonts/LucidaBrightDemiItalic.ttf"
    font = ImageFont.truetype(font_path, 15, encoding='unic')
    
    img1 = Image.open(filename)
    w, h = img1.size
    
    if ( w != finalresolutionX or h != finalresolutionY ):
        new_size=[finalresolutionX, finalresolutionY]
        img2 = img1.resize(new_size) 
        img1 = img2.copy()
        
    img = Image.new("RGB", (finalresolutionX,finalresolutionY+offsetUpper+offsetBottom), bgrColor)
    img.paste(img1, (0,offsetUpper,finalresolutionX,finalresolutionY+offsetUpper))
        
    w, h = img.size
    draw = ImageDraw.Draw(img)
    
    text =  cfg.webcamLogo
    draw.text((marginLeft, 0),text,textColor,font=font)
    
    text =   datetime.datetime.now().strftime("Data : %d/%m/%Y - %H:%M:%S ")
    width, height = font.getsize(text)
    draw.text((w-width-MarginRight-17, 0),text,textColor,font=font)
    
    font = ImageFont.truetype(font_path, 13, encoding='unic')
    
    # Adding Meteo information
    if (  globalvars.meteo_data.status == 0 ):
 
        delay = (datetime.datetime.now() - globalvars.meteo_data.last_measure_time)
        delay_seconds = int(delay.total_seconds())
        
        if (delay_seconds < 900 ):    

            text = "Direzione del vento: " + globalvars.meteo_data.wind_dir_code + " - Intensita: " + str(globalvars.meteo_data.wind_ave) + " km/h  - Raffica: " + str(globalvars.meteo_data.wind_gust)  + " km/h" 
            if (globalvars.meteo_data.temp_out  != None) : 
                text = text + " - Temperatura: " + str(globalvars.meteo_data.temp_out) + " C"
            if (globalvars.meteo_data.abs_pressure != None ) : 
                text = text + " - Pressione: " + str(globalvars.meteo_data.abs_pressure) + " hpa"         
            
            width, height = font.getsize(text)
            draw.text((32+marginLeft, h-offsetBottom),text,textColor,font=font)
            
            text = ""
            if (globalvars.meteo_data.hum_out  != None) : 
                text = text + "Umidita : " + str(globalvars.meteo_data.hum_out) + " % - "
            
            text = text + "Ultima misura: " + str(globalvars.meteo_data.last_measure_time)
            width, height = font.getsize(text)
            draw.text((32+marginLeft, h-height),text,textColor,font=font)
            
    else:
        text = "Nessun dato meteo - status = " + str(globalvars.meteo_data.status)
        width, height = font.getsize(text)
        draw.text((marginLeft, h-offsetBottom),text,textColor,font=font)
    
    if ( version != None):
        font = ImageFont.truetype(font_path, 11, encoding='unic')
        text = "(Sint Wind PI : " + version + ")"
        width, height = font.getsize(text)
        draw.text((w-width-MarginRight, h-height),text,textColor,font=font)            
    
    
    if ( os.path.isfile("./fonts/windsock.png") ):
        im_windsock = Image.open("./fonts/windsock.png")
        # Box for paste is (left, upper, right, lower).
        img.paste(im_windsock,(int(marginLeft/2),h-offsetBottom+2),im_windsock)
    
    if ( os.path.isfile("./fonts/rpi_logo.png") ):
        im_logo = Image.open("./fonts/rpi_logo.png")
        # Box for paste is (left, upper, right, lower).
        img.paste(im_logo,(w-17,0),im_logo)   
    
    img.save(filename)
    
    if ( not os.path.isfile(filename)):
        return False
    
    log("Processed image :" + filename )
    return True


wind_rose = {
    0:  "N",
    22.5:  "NNE",
    45: "NE",
    67.5 :"ENE",
    90: "E",
    112.5: "ESE",
    127:"SE",
    149.5: "SSE",
    180:"S",
    202.5: "SSW",
    225:"SW",
    247.5: "WSW",
    270:"W",
    295.5:"WNW",
    315:"NW",
    337.5:"NNW"}


def angle2direction(angle):
    return wind_rose[angle]
    
    

def direction2angle(direction):
    return [item[0] for item in wind_rose() if item[1] == direction]



def mean(numberList):
    if len(numberList) == 0:
        return 0
    floatNums = [float(x) for x in numberList]
    return sum(floatNums) / len(numberList)

def isnumeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def sendFileToServer(filename,name,server,destFolder,login,password):
    try:
        s = ftplib.FTP(server,login,password) 	# Connect
        f = open(filename,'rb')                # file to send
        s.cwd(destFolder)
        s.storbinary('STOR ' + name, f)         # Send the file
        f.close()                                # Close file and FTP
        s.quit() 
        log("Sent file to server : " + name)
        return True
    except:
        log("Error sending  file to server : " + name)
        return False

def internet_on():
    try:
        urllib2.urlopen('http://74.125.113.99',timeout=1)
        #urllib2.urlopen('http://74.125.113.99')
        return True
    except :
        pass	
        return False
    
def systemRestart():
    if os.name != 'nt':
        os.system("sudo reboot")
    else:
        print " Sorry can not rebbot windows"
        
def systemHalt():
    if os.name != 'nt':
        os.system("sudo halt")
    else:
        print " Sorry can not rebbot windows"        

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("gmail.com", 80)) 
    except Exception, e:
        #log("something wrong in get IP. Exception type is %s" % ( e))
        return None
    ip = (s.getsockname()[0])
    s.close()
    return ip


def waitForIP():
    # wait maximum 2 minute for a valid IP
    log("Waiting for a valid IP ...")
    n = 60
    for i in range(1,n):
        theIP = getIP()
        if ( theIP != None):
            return theIP
        log("No IP yet. Retrying ..%d" % (n-i) )
        time.sleep(2)
    return None

def SendMail(cfg, subject, text, attach):
    try:
        msg = MIMEMultipart()
        
        msg['From'] = "Sint Wind PI"
        msg['To'] = cfg.mail_to
        msg['Subject'] = subject
        
        #cfg.gmail_user.encode('utf-8')
        #cfg.gmail_pwd.encode('utf-8')        
        
        gmail_user = cfg.gmail_user
        gmail_pwd = cfg.gmail_pwd

        msg.attach(MIMEText(text))
        if (attach != "" ): 
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(attach, 'rb').read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                'attachment; filename="%s"' % os.path.basename(attach))
            msg.attach(part)
        
        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmail_user, gmail_pwd)
        mailServer.sendmail(cfg.gmail_user, cfg.mail_to, msg.as_string())
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()
        log("Mail sent to :" + cfg.mail_to)
        return True
    except Exception as e:
        log ("ERROR sending mail" )
        print "Exeption", e
        return False
    



if __name__ == '__main__':
 
    configfile = 'swpi.cfg'
    if not os.path.isfile(configfile):
        "Configuration file not found"
        exit(1)    
    cfg = config.config(configfile)
    
    swpi_update()
    
    
    
#    rb = RingBuffer(cfg.number_of_measure_for_wind_average_gust_calculation)
#    rb.append(10)
#    wind_ave,wind_gust = rb.getMeanMax()
    
#    sensor = sensor_simulator.Sensor_Simulator(cfg)
#            
#
#                
#    sensor.GetData()
#    
#    print "addTextandResizePhoto"
#    addTextandResizePhoto("F:/jessica2/temp/DSC00192.JPG",800,600,cfg)
#    print "done"
    
    #print SendMail(cfg,"DB","DB attached","./db/swpi.s3db") 
    
    #for i in range (1,360):
    #    print  str(i) + str(angle2direction(i))