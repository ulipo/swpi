###########################################################################
#     Sint Wind PI
# 	  Copyright 2012 by Tonino Tarsi <tony.tarsi@gmail.com>
#   
#     Please refer to the LICENSE file for conditions 
#     Visit http://www.vololiberomontecucco.it
# 
##########################################################################
"""Classes and methods for handling Web and Cam commands."""

import sqlite3
from PIL import Image, ImageFont, ImageDraw
import time
import os
from TTLib  import *
import sun
import math
import subprocess

class webcam(object):
	"""Class defining generic webcams."""

	def __init__(self, deviceNumber,cfg):
		if (deviceNumber == 1):
			self.device = cfg.webcamDevice1
			self.captureresolution = cfg.webcamdevice1captureresolution 
			self.finalresolution = cfg.webcamdevice1finalresolution
			self.caprureresolutionX = cfg.webcamdevice1captureresolutionX
			self.caprureresolutionY = cfg.webcamdevice1captureresolutionY
			self.finalresolutionX = cfg.webcamdevice1finalresolutionX
			self.finalresolutionY = cfg.webcamdevice1finalresolutionY
		elif (deviceNumber == 2):
			self.device = cfg.webcamDevice2
			self.captureresolution = cfg.webcamdevice2captureresolution 
			self.finalresolution = cfg.webcamdevice2finalresolution
			self.caprureresolutionX = cfg.webcamdevice2captureresolutionX
			self.caprureresolutionY = cfg.webcamdevice2captureresolutionY
			self.finalresolutionX = cfg.webcamdevice2finalresolutionX
			self.finalresolutionY = cfg.webcamdevice2finalresolutionY
		else:
			log( "ERROR Only 2 webcams are allowed in this version of the software"	)
			
		self.cfg = cfg
		self.god=sun.sun(lat=cfg.location_latitude,int=cfg.location_longitude)

	# Old function


	def capture(self,filename):
		if ( self.god.daylight() ):
			options = self.cfg.cameraPI_day_settings
			log("Webcam active day")
		else:
			options = self.cfg.cameraPI_night_settings
			log("Webcam active night")
		try:
			if options.upper() == "NONE":
				log("Webcam not active")
				return False
#		try:

			if ( self.cfg.captureprogram == "ffmpeg" ):
				snapCommand = "ffmpeg -loglevel quiet -t 1  -f video4linux2 -vframes 1 -s " + self.captureresolution + " -i " + self.device + " " + filename
			elif ( self.cfg.captureprogram == "uvccapture" ):
				snapCommand = "uvccapture -m -S80 -B80 -C80 -G80 -x" + self.captureresolutionX + "-y" + self.captureresolutionX + " -d" + self.device + " -o " + filename
			elif ( self.cfg.captureprogram == "fswebcam" ):
				snapCommand = "fswebcam -c fswebcam.conf -r %s -d %s --save %s" %( self.captureresolution,self.device,filename)
			elif ( self.cfg.captureprogram == "ipcam" ):
				snapCommand ="wget -O " + filename + " " + self.device
		
			
			#log( "Getting images with command : " + snapCommand)
			os.system(snapCommand )

			if ( not os.path.isfile(filename)):
				log( "ERROR in capturing webcam image on : " + filename + " "+ self.device )
				return False
					
			return True
		except ValueError:
			log( " ERROR in capturing webcam image on : " + self.device )
			return False

