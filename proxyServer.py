from functools import cache
from genericpath import isdir, isfile
import mimetypes
import os
import re
import socket
import subprocess 
import sys
from typing import OrderedDict #insertion order is followed
import urllib.request

class serverCache:
    def __init__(self) -> None:
        self.cache=OrderedDict()
        self.capacity=5

    def checkPresence(self,key:str):
        if key in self.cache:
            self.cache.move_to_end(key)
            return 1
        else: 
            return -1
    
    def placeNewKey(self,key,value)->None:
        if(len(self.cache)<self.capacity):
            self.cache[key]=value
        elif(len(self.cache)>=self.capacity):
            self.cache.popitem(last=False) #remove last key
            self.cache[key]=value
            


class HTTPServer:
    def __init__(self, ip,port):
        self.path="C:\\Users\\PAVAN\\OneDrive\\Documents\\ComputerSystems\\3"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip,port))
        sock.listen(1)
        self.sc=serverCache()
        while True:
                connection,clientAddress = sock.accept()
                with connection:
                    urlRcvd=connection.recv(1024)
                    uri=self.getURI(urlRcvd)
                    if self.isValidURL(uri)==True:
                        if(uri!="favicon.ico"):
                            #print("URI:" +uri)
                            code, c_type, c_length, data = self.getRequestedData(uri)
                    else:
                        data= "<h1>file  doesnot exist</h1>" #fnf 
                        code,c_type, c_length, data = 404, "text/html", len(data), data.encode() 
                    response = self.response_headers(code, c_type, c_length).encode() + data
                    connection.sendall(response)
                    connection.close()
        
    def isValidURL(self,str):
     # Regex to check valid URL
        regex = ("((http|https)://)(www.)?" +
                "[a-zA-Z0-9@:%._\\+~#?&//=]" +
                "{2,256}\\.[a-z]" +
                "{2,6}\\b([-a-zA-Z0-9@:%" +
                "._\\+~#?&//=]*)")
        
        # Compile the ReGex
        p = re.compile(regex)
    
        if (str == None):
            return False
    
        # Return if the string        # matched the ReGex
        if(re.search(p, str)):
            return True
        else:
            return False  

    def getURI(self,data):
        msgStr=data.decode()
        start=msgStr.find("://")+\
            len("://")
        msgStr=msgStr[start:]
        end=msgStr.find(" ")
        msgStr=msgStr[:end]
        msgStr= msgStr.strip()
        fileURI=msgStr
        #print("file requested: "+fileURI)
        return fileURI
        
    def getRequestedData(self,url):
        urlRcvd=''
        urlRcvd+=str(url.decode())
        if(self.sc.checkPresence(urlRcvd)):
            data=self.sc.cache[urlRcvd]
        else:
            data=urllib.request.urlopen(url)
            self.sc.placeNewKey(urlRcvd,data)
        return 200, "text/html", len(data), data.encode() 
       
            
    
    def response_headers(self, status_code, content_type, length):
        line = "\n"
       
        response_code = {200: "200 OK",404:"404 file not found"}
        
        headers = ""
        headers += "HTTP/1.1 " + response_code[status_code] + line
        headers += "Content-Type: " + content_type + line
        headers += "Content-Length: " + str(length) + line
        headers += "Connection: close" + line
        headers += line
        return headers

def main():
    # test harness checks for your web server on the localhost and on port 8888
    # do not change the host and port
    # you can change  the HTTPServer object if you are not following OOP
    HTTPServer('127.0.0.1', 8888)

if __name__ == "__main__":
    main()