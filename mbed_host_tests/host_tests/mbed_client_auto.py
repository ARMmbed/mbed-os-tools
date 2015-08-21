"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import urllib2
import ssl
import base64
import json
import re
import socket
from sys import stdout
import time

import signal
import subprocess
import os

class TestConfiguration():
    
    def __init__(self, test_cfg):
        self.testconfig = test_cfg   
        
    # You can define own PC adress here, for example OWN_PC_ADDRESS = "10.45.2.134"
    OWN_PC_ADDRESS = ""
    # If not defined, address will be defined automatically. Works only if one adapter in use. You can disable extra adapters to get it work.  
    if OWN_PC_ADDRESS == "":
        OWN_PC_ADDRESS = socket.gethostbyname(socket.gethostname())
    BOOTSTRAP_SERVER = OWN_PC_ADDRESS
    BOOTSTRAP_PORT = "5693"
    MDS_SERVER = OWN_PC_ADDRESS
    MDS_PORT = "5683"
    MDS_SERVER_NAME = "test"
    BOOTSTRAP_ADDRESS = "coap://%s:%s" % (BOOTSTRAP_SERVER, BOOTSTRAP_PORT)
    MDS_ADDRESS = "coap://%s:%s" % (MDS_SERVER, MDS_PORT)
    BOOTSTRAP_USER = "admin"
    BOOTSTRAP_PASS = "admin"
    EP_NAME = "testep"
    
    #lwm2mCONF_folder_path = os.path.join(os.getcwd(),'..','lwm2m-CONF')
    lwm2mCONF_folder_path = 'C:\\mbed_tools\\lwm2m-CONF'
    BOOTSTRAP_SERVER_PATH = os.path.join(lwm2mCONF_folder_path,'bootstrap-server','bin')
    BOOTSTRAP_SERVER_CMD = ['runBootstrapServer.bat']
    DEVICE_SERVER_PATH = os.path.join(lwm2mCONF_folder_path,'device-server','bin')
    DEVICE_SERVER_CMD = ['runDS.bat']

class BootstrapServerAdapter():
    def __init__(self, configuration):
        self.config = configuration
        self.context = ssl._create_unverified_context()
    
    def SendRequest(self, req, opener = None):
        if not req:
            return
        if opener:
            result = opener.open(req)
        else:
            result = urllib2.urlopen(req, context=self.context)
        code = result.getcode()
        info = result.info()
        url = result.geturl()
        return result
    
    def CreateAuthRequest(self, address):
        request = urllib2.Request(address)
        auth = base64.encodestring("%s:%s" % (self.config.BOOTSTRAP_USER, self.config.BOOTSTRAP_PASS)).strip()
        request.add_header("Authorization", "Basic %s" % auth)
        request.add_header("Content-Type", "application/json")
        request.add_header("Accept", "application/json")
        return request
    
    def AddOMAServer(self, selftest):
        request = self.CreateAuthRequest("https://%s:8090/rest-api/oma-servers" % self.config.BOOTSTRAP_SERVER)
        
        """ { id: 3, name: "mbed-3", ip-address: "coap://localHOST:5683", security-mode: "NO_SEC" }
        """
        mapping = {"id" : 10, "name" : self.config.MDS_SERVER_NAME, "ip-address" : self.config.MDS_ADDRESS, "security-mode" : "NO_SEC"}
        request.add_data(json.dumps(mapping))
    
        self.SendRequest(request)
 
    
    def GetOMAServers(self):
        servers = None
        request = self.CreateAuthRequest("https://%s:8090/rest-api/oma-servers" % self.config.BOOTSTRAP_SERVER)
        request.get_method = lambda: 'GET'
        result = self.SendRequest(request)
        if result:
            data = result.read()
            print "SERVER RESULT: %s" % data
            servers = json.loads(data)
        return servers
    
    def GetOMAClients(self):
        clients = None
        try:
            request = self.CreateAuthRequest("https://%s:8090/rest-api/oma-clients" % self.config.BOOTSTRAP_SERVER)
            result = self.SendRequest(request)
            if result:
                clients = json.loads(result.read())
        except:
            print "exception"
        return clients
    
    def GetOMAServerId(self, server_name):
        server_id = None
        
        # Get OMA server id
        servers = self.GetOMAServers()
        if servers:
            for oma_server in servers:
                if oma_server["name"] == server_name:
                    server_id = oma_server["id"]
                    break
            
            return server_id
    
    def ClientMappingExists(self, endpointName):
        clients = self.GetOMAClients()
        if clients:
            for client in clients:
                if client["name"] == endpointName:
                    return True
        return False
    
    def AddClientMapping(self, endpointName):
        """ Adds new client with endpointName as name to OMA server.
        """
        
        if not endpointName:
            endpointName = "lwm2m-client-tester"
           
        server_id = self.GetOMAServerId(self.config.MDS_SERVER_NAME)
        
        if not server_id:
            print "No such server exists in bootstrap server"
            return
        
        mapping = {"name" : endpointName, "omaServerId" : server_id}
        
        request = self.CreateAuthRequest("https://%s:8090/rest-api/oma-clients/%s" % (self.config.BOOTSTRAP_SERVER, endpointName))
        request.add_data(json.dumps(mapping))
        result = self.SendRequest(request)
        
    def DeleteClientMapping(self, endpointName):
        opener = urllib2.build_opener(urllib2.HTTPSHandler(context=self.context))
        request = self.CreateAuthRequest("https://%s:8090/rest-api/oma-clients/%s" % (self.config.BOOTSTRAP_SERVER, endpointName))
        request.get_method = lambda: "DELETE"
        result = self.SendRequest(request, opener)

class LWM2MClientAutoTest():
    """ A simple LWM2M client test that sends bootstrap and mds server information to 
        DUT and waits for test result print from DUT.
    """
    
    #testconfig = TestConfiguration()
                
    """ Function for configuring test parameters of DUT.
    """
    def send_configuration(self, selftest):
        selftest.notify("HOST: Waiting for DUT to start...")
        
        c = selftest.mbed.serial_readline()
        if c is None:
            selftest.print_result(selftest.RESULT_IO_SERIAL)
            return
        selftest.notify(c.strip())

        selftest.notify("HOST: Sending test configuration to DUT...")
        config_str = "<%s><%s><%s>\r\n" % (self.testconfig.BOOTSTRAP_ADDRESS, self.testconfig.MDS_ADDRESS, self.testconfig.EP_NAME)
        selftest.notify("HOST: Sending configuration: %s" % config_str)
        selftest.mbed.serial_write(config_str)

    def read_endpointname(self, selftest):
        epname = None
        read = ""
        while True:
            inp = selftest.mbed.serial_readline(64)
            if inp:
                read += inp
            if "endpoint_name=" in read:
                break
            
        name = re.search("endpoint_name=([\w:-]+)", inp)
        if name:
            epname = name.group(1)
            selftest.notify("HOST: Using endpoint name: %s" % epname)
            
        return epname
    
    def suite_result_check(self, ser, selftest):
        m = re.search("Suite: result (success|failure)", ser)
        if not m:
            return selftest.RESULT_FAILURE
        
        if m.group(1) == "success":
            return selftest.RESULT_SUCCESS
        
        return selftest.RESULT_FAILURE
                        
    def createServer(self, cmd):  
        status = -1
        p = None
        succ_resp = 'Started'
        
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        except Exception as ex:
            print('Host: Exception starting subprocess %s' %str(ex))
            return status, p
              
        cnt = 0
        max_cnt = 20
        startTime = time.time()
        while cnt < max_cnt:
            line = p.stdout.readline()
            print(line)
            if (succ_resp in line):
                status = 0
                print('Host: Server started OK')
                break
            cnt = cnt+1
            if cnt >= max_cnt:
                print('Host: Server starting timeout: %s sec\n' % (time.time() - startTime) )    
                break
        return status, p
  
    def stopServers(self):  
        _lines = os.popen('wmic process where caption="java.exe" get commandline,processid').read()
        _lines = re.sub("\s\s+" , " ", _lines).strip(os.linesep)
        _lines_list = _lines.split('java')
        _found_processes = []
        servers_found = False
        PIDlist = []
        for item in _lines_list:
            if ('bootstrapserver') in item:
                _found_processes.append(item)
                servers_found = True
            if ('deviceserver') in item:
                _found_processes.append(item)
                servers_found = True
        
        if servers_found == True:
            for item in  _found_processes:
                PIDlist.append(item.split(' ')[-2])
            for _pid in PIDlist:
                os.system('taskkill /F /PID %s' %_pid)  
                print('HOST: Server (pid: %s) killed OK' %_pid)  
        
    def test(self, selftest):
        result = selftest.RESULT_PASSIVE
        testoutput = ""
        
        self.stopServers()
        time.sleep(5.0)
        
        self.testconfig = TestConfiguration(selftest.mbed.test_cfg)

        selftest.notify("HOST: Running folder: %s" %(os.getcwd()))
        
        selftest.notify("HOST: PC IP address to be used by servers: %s" %self.testconfig.OWN_PC_ADDRESS)           

        os.chdir(self.testconfig.BOOTSTRAP_SERVER_PATH)
        selftest.notify("HOST: Bootstrap Server folder %s" %self.testconfig.BOOTSTRAP_SERVER_PATH)
        status, _p = self.createServer(self.testconfig.BOOTSTRAP_SERVER_CMD)
        
        os.chdir(self.testconfig.DEVICE_SERVER_PATH)

        selftest.notify("HOST: Device Server folder %s" %self.testconfig.DEVICE_SERVER_PATH)
        status, _p = self.createServer(self.testconfig.DEVICE_SERVER_CMD)       
        time.sleep(30)
     
        #Add endpoint name as a client to OMA bootstrap server if it doesn't already exist
        bootstrap_server = BootstrapServerAdapter(self.testconfig)
        selftest.notify("HOST: BootstrapServerAdapter done")
        
        bootstrap_server.AddOMAServer(selftest)
        selftest.notify("HOST: AddOMAServer done")        
        
        if not bootstrap_server.ClientMappingExists(self.testconfig.EP_NAME):
            selftest.notify("HOST: Adding OMA bootstrap client mapping for %s" % self.testconfig.EP_NAME)
            bootstrap_server.AddClientMapping(self.testconfig.EP_NAME)
            time.sleep(1)
            if bootstrap_server.ClientMappingExists(self.testconfig.EP_NAME):
                selftest.notify("HOST: client added successfully")
        
        time.sleep(2)
        
        # Send test configuration to MUT
        self.send_configuration(selftest)
        
        start_time = time.time()
        try:
            while True:
                c = selftest.mbed.serial_read(512)
                if c is None:
                    result = selftest.RESULT_IO_SERIAL
                stdout.write(c)
                stdout.flush()
                testoutput += c
                # Check for suite result
                if "Suite: result" in testoutput:
                    result = self.suite_result_check(testoutput, selftest)
                    break
                    
        except KeyboardInterrupt, _:
            selftest.notify("\r\n[CTRL+C] exit")
            result = selftest.RESULT_ERROR
        
        selftest.notify("HOST: Deleting OMA bootstrap client mapping for %s" % self.testconfig.EP_NAME)
        
        bootstrap_server.DeleteClientMapping(self.testconfig.EP_NAME)

        #self.stopServers()
        
        elapsedTime = time.time() - start_time
        selftest.notify("HOST:Test completed in %.0f seconds\n" % elapsedTime)
        
        return result
