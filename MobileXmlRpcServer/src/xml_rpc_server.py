#/*
# * @author Alireza Sahami
# *
# *
# * Copyright (C) 2009 Pervasive Computing Group, University of Duisuburg Essen
# * Contact person: Alireza Sahami (alireza.sahami@uni-due.de)
# *
# * This library is free software; you can redistribute it and/or
# * modify it under the terms of the GNU Lesser General Public
# * License as published by the Free Software Foundation; either
# * version 2.1 of the License, or (at your option) any later version.
# *
# * This library is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# * Lesser General Public License for more details.
# *
# * You should have received a copy of the GNU Lesser General Public
# * License along with this library; if not, write to the Free Software
# * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# */

#import gps, gsm

import sys, e32, socket, urllib
import globalui

#apid = None
#this next line brings up the access point menu
#apid = socket.select_access_point()
#if not apid:
#    sys.exit()
#apo = socket.access_point(apid)
#socket.set_default_access_point(apo)
#apo.start()
#try:
#    ip = apo.ip()
#    print u"Connected to WiFi as %s" % ip
#except:
#    print u"Failed to connect to WiFi"


menuitems = []
aps = socket.access_points()
for k in aps:
    menuitems.append(k['name'])
menuitems.append(u'LOCAL')
id = globalui.global_popup_menu(menuitems, u'Select AP')
if id < len(aps):
    print id, aps[id]
    apo = socket.access_point(aps[id]['iapid'])
    socket.set_default_access_point(apo)
    apo.start()
    try:
        ip = apo.ip()
    except:
        globalui.global_note(u"Could not Connect!, EXIT")
        sys.exit()
else:
    # bind to localhost
    ip = "127.0.0.1"

globalui.global_note(u"Your IP:"+ unicode(str(ip)))


sys.path.append('e:\\python\\libs')
import socketserver
from simplexmlrpcserver import SimpleXMLRPCServer

class Logger:
    def __init__(self, filename='e:\\log.txt'):
        self.outfile = open(filename,'a')
        self.write("======== LOG START =============================")
        # redirect standard outputs,errors
        (self.oldStdErr,self.oldStdOut) = (sys.stderr,sys.stdout)
        (sys.stderr,sys.stdout) = (self, self)
    def write(self, text):
        self.outfile.write(text)
    def write_err(self, text):
        self.outfile.write("Error"+text)
    def end(self):
        self.outfile.close()
        (sys.stderr,sys.stdout) = (self.oldStdErr, self.oldStdOut)
    def close(self):
        self.end()

class PhoneInfo:
    """ provides functions to get information from the phone"""
    acc_result="Error"
    gps_result="Error"
    def __init__(self):
        self.__initsensor()
        self.__initgps()

    def __initgps(self):
        try:
            import positioning as gps
            gps.select_module(gps.default_module())
            gps.set_requestors([{"type":"service","format":"application","data":"gps_app"}])
            gps.position(course=1,satellites=0,callback=self.__gps_cb, interval=5000000,partial=0)#intervall at 5 seconds atm
            e32.ao_sleep(3)
        except ImportError:
            self.gps_result="Error"
    def __gps_cb(self, data):
        self.gps_result=str(data)

    def __initsensor(self):
        try:
            import sensor
            accsensor=sensor.sensors()['AccSensor']
            self.acc_sensor=sensor.Sensor(accsensor['id'],accsensor['category'])
            self.acc_sensor.connect(self.__acc_cb)
        except ImportError:
            self.acc_result=""
    def __acc_cb(self,data):
        self.acc_result=str(data)

    def acc_data(self):
        return self.acc_result
    def gps_data(self):
        return self.gps_result
    def gsm_data(self):
        try:
            import location as gsm
            return str(gsm.gsm_location())
        except ImportError:
            return "ERROR"

class stoppableXMLRPCServer (SimpleXMLRPCServer):
    """ provides a way to stop the SimpleXMLRPCServer"""
    def stop(self):
        self.running = False
        return 0
    def serve_forever(self):
        self.running = True
        self.register_function(self.stop, 'stop')
        while self.running:
            self.handle_request()

# start logger

l = Logger()
print "Log Initialized..."
# instantiate server
server = stoppableXMLRPCServer((str(ip),8000))
server.register_introspection_functions()
# example: register a python library function
server.register_function(pow)

# example: register a defined function
def adder_function(x,y):
    return x+y

def test_function():
    return "HelloXMLRPC"

server.register_function(adder_function, 'add')
server.register_function(test_function, 'test')

# example: register an object instance
class MyFuns:
    def div(self,x,y):
        return int(x) // int(y)

server.register_instance(MyFuns())
# this is the real deal!
server.register_instance(PhoneInfo())

# launch the server
# it can be stopped by connecting to XMLRPC service and issuing stop() function
server.serve_forever()
print "Log closed"
l.end()

