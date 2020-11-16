#!/usr/bin/python3

"""
sprinkler.py:  This python script is used to control the
Raspberry Pi 4 GPIO pins for a lawn sprinkler application.
It must be run as root to access the GPIO hardware.

Not that the relay board used with this controller
uses 5V signalling and the 3V3 output is no enough
to disable the relay.  Instead of setting the output
to high, it is disabled (set to input) turning off
the pull-down relay.  Not ideal, but it works.
"""

__author__    = "Steven A. Guccione"
__date__      = "August 21, 2020"
__copyright__ = "Copyright (c) 2020 by Steven A. Guccione"

import argparse
import requests
import RPi.GPIO as GPIO
import time
import json

if __name__ == '__main__':

   # Number of seconds to delay between zones
   DELAY = 3
   
   # Parse command line parameters
   parser = argparse.ArgumentParser()
   parser.add_argument("json", nargs=1, help="JSON configuration file")
   parser.add_argument("--percent", type=int, help="run time percent (default=100,max=500)",
                       choices=range(1,500), default=100)
   parser.add_argument("--silent", help="run silently", default=False, action='store_true')
   parser.add_argument("--debug", help="debug flag", action='store_true')
   args = parser.parse_args()

   if args.debug:
      print("Loading configuration file: ", args.json[0])

   with open(args.json[0], 'r') as json_file:
      json_data = json.load(json_file)
  
   # Use Broadcomm pin numbering
   GPIO.setmode(GPIO.BCM)

   schedule = json_data["schedule"]
   zone_to_bcm = json_data["zone"]
   if args.debug:
      print("Schedule:", schedule)
      print("Zones:", zone_to_bcm)

   start_time = time.time()
   if not args.silent:
      print("Starting at", time.asctime(time.localtime(start_time)))

   # Run schedule
   try:
      for s in schedule:

         zone = s[0]
         minutes = s[1]
         if len(s) == 3:
            desc = s[2]
         else:
            desc = zone
            
         bcm_number = zone_to_bcm[zone]

         output = "Running zone " + desc + " for "
         output = output + "{:0.2f}".format(minutes*args.percent/100) + " minutes."
         if args.debug:
            output = output + "  (BCM=" + str(bcm_number) +")"
         if not args.silent:
            print(output)
         
         # Turn on output and set to low (pull down)
         GPIO.setup(bcm_number, GPIO.OUT)
         GPIO.output(bcm_number, GPIO.LOW)
         time.sleep(minutes*args.percent*60/100)

         # Turn off pin
         GPIO.setup(bcm_number, GPIO.IN)
         time.sleep(DELAY)

   # Exit on CTRL-C
   except KeyboardInterrupt:
      print("Execution interrupted.  Exiting.")
   # Any other error
   except Exception as e:
      print("Unknown error detected.  Exiting.")
      print(e)
   finally:
      if args.debug:
         print("Perfoming GPIO clean up.")
      GPIO.cleanup()

   end_time = time.time()
   elapsed_time = end_time - start_time
   elapsed_time_str= time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
   if not args.silent:
      print("Done at", time.asctime(time.localtime(end_time)))
      print("Total run time:  ", elapsed_time_str)
   
   SystemExit(0)
