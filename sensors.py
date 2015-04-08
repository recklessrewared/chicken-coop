import RPi.GPIO as GPIO
import time
import Adafruit_MCP9808.MCP9808 as MCP9808

#pin numbers
proximity1Pin = 20
proximity2Pin = 16
doorOpenPin = 17 #check that this is accurate
doorClosePin = 18 #same here

# set pins to use GPIO numbering
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

#pin setup
GPIO.setup(proximity1Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(proximity2Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(doorOpenPin, GPIO.OUT)
GPIO.setup(doorClosePin, GPIO.OUT)

#helpful global variables
proximity1 = 0
proximity2 = 0
chickenCount = 0
doorStatus = 0

#convert C to F for temp sensor
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0

#temp sensor creation and initialization
sensor = MCP9808.MCP9808()
sensor.begin()

#read temp sensor
def getTemp():
        temp = sensor.readTempC()
        return temp

#callback function for sensor1
def proximity1_callback(proximity1Pin):
	global proximity1
	global proximity2
	global chickenCount
	#object not detected
	if GPIO.input(proximity1Pin):
		#reset the global variable 
		proximity1 = False #or should it be !proximity1 ?
		print "decrementing proximity1"

	#object detected
	else:
		#increment the proximity 1 variable
		proximity1 = True
		print "incrementing proximity1"
		exception = False

		#proximity1 hit first
		if (proximity1 == True and proximity2 == False):
			#wait for chicken to hit proximity2:
			print "waiting for proximity2 to trigger..."
			t = time.time()
			while True:
				if proximity2 == True:
					print "proximity 2 triggered"
					print "now waiting for both sensors to reset"
					break
				#only wait for 10s, and throw an exception
				if (time.time()-t) >= 10:
					exception = True
					print "you took too long to activate proximity2, throwing exception"
					break

			#wait for the High functions to reset global variables
			t = time.time()
			while True:
				#don't do anything to chickenCount if there was an exception
				if ( exception ):
					print "exception detected... exiting prosimity1 callback function"
					break
				#wait for both sensors to reset their variables
				if ( proximity1 == False and proximity2 == False ):
					#this indicates a chicken leaving
					print "both sensors were reset! decrementing chickencount"
					chickenCount -= 1
					break
				#only wait for 10s, throw exception
				if (time.time()-t) >= 10:
					exception = True
					print "you took too long to reset the sensors, throwing exception"
					break
		
def proximity2_callback(proximity2Pin):
	global proximity1
	global proximity2
	global chickenCount
	if GPIO.input(proximity2Pin):
		#reset the global variable >>> this is probably bad
		proximity2 = False
		print "decrementing proximity2"

	#object detected
	else:
		#increment the proximity 2 variable
		proximity2 = True
		print "incrementing proximity 2"
		exception = False

		#proximity2 hit first
		if (proximity2 == True and proximity1 == False):
			#wait for chicken to hit proximity1:
			print "waiting for proximity1 to trigger..."
			t = time.time()
			while True:
				if proximity1 == True:
					print "proximity 1 triggered"
					print "now waiting for both sensors to reset"
					break
				#only wait for 10s, and throw an exception
				if (time.time()-t) >= 10:
					exception = True
					print "you took too long to activate proximity1, throwing exception"
					break

			#wait for the High functions to reset global variables
			t = time.time()
			while True:
				#don't do anything to chickenCount if there was an exception
				if ( exception ):
					print "exception detected in proximity2 callback...exiting"
					break
				#wait for both sensors to reset their variables
				if ( proximity1 == False and proximity2 == False ):
					#this indicates a chicken entering
					print "both variables were reset, incrementing chickenCount"
					chickenCount += 1
					break
				#only wait for 10s, throw exception
				if (time.time()-t) >= 10:
					exception = True
					print "took too long to reset the sensors...exiting proximity2 callback"
					break

def closeDoor(doorClosePin):
	#turn on door motor
	GPIO.output(doorClosePin,1)
	#wait a couple seconds for it to complete
	time.sleep(1.0)
	#turn off motor
	GPIO.output(doorClosePin,0)
	return None

def openDoor(doorOpenPin):
	#turn on door motor
	GPIO.output(doorOpenPin,1)
	#wait a couple seconds for it to complete
	time.sleep(1.0)
	#turn off motor
	GPIO.output(doorOpenPin,0)
	return None

#proximity
GPIO.add_event_detect(proximity1Pin, GPIO.BOTH, callback=proximity1_callback, bouncetime=300)
GPIO.add_event_detect(proximity2Pin, GPIO.BOTH, callback=proximity2_callback, bouncetime=300)



while True:
	print "Beginning count check loop"
	print "Current chicken count is " + str(chickenCount)
	if (doorStatus == 1):
		print "Opening door"
		openDoor(doorOpenPin)
		doorStatus = 0

	if (chickenCount >= 5 and doorStatus == 0):
		print "Closing door"
		closeDoor(doorClosePin)
		doorStatus = 1
	time.sleep(10.0)

except KeyboardInterrupt:
	GPIO.cleanup()
