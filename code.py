from functools import cache
from genericpath import isdir, isfile
import mimetypes
import os
import socket
import subprocess
import sys
from typing import OrderedDict #insertion order is followed

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
                    data=connection.recv(1024)
                    uri=self.getURI(data)
                    if(uri!="favicon.ico"):
                        print("URI:" +uri)
                        code, c_type, c_length, data = self.getRequestedData(uri)
                        response = self.response_headers(code, c_type, c_length).encode() + data
                        connection.sendall(response)
                        connection.close()
        
        
    def getURI(self,data):
        msgStr=data.decode()
        start=msgStr.find("GET /")+\
            len("GET /")
        msgStr=msgStr[start:]
        end=msgStr.find(" ")
        msgStr=msgStr[:end]
        msgStr= msgStr.strip()
        fileURI=msgStr
        print("file requested: "+fileURI)
        return fileURI
        
        
    def getRequestedData(self, uri):
        data=''
        if uri=="": #if nothing is obtained, disp list of files
            for files in os.listdir(self.path):
                if(isdir(files)):
                    data+='<a href="'+files+'">'+files+"</a> <br>"+"\n"        
            return 200, "text/html", len(data), data.encode()

        fileReqd=''
        for top, dirs, files in os.walk(self.path) : 
            for dir in dirs:
                if dir.endswith(uri):
                    fileReqd+=os.path.join(top, dir)
                    break
            if fileReqd!="": break
            
            for file in files:
                if file.endswith(uri):
                    fileReqd+=os.path.join(top, file)
                    break

        if fileReqd=="":
                data = "<h1>file  doesnot exist</h1>" #fnf 
                return 404, "text/html", len(data), data.encode()   

                                
        if isdir(fileReqd): #dir => list all files
            for files in os.listdir(fileReqd):
                data+='<a href="'+files+'">'+files+"</a> <br>"+"\n"
            return 200, "text/html", len(data), data.encode()    

        


        elif isfile(fileReqd): # file=>fnf, none, exec, non exec              
            if "bin" in fileReqd: #exec file
                if "." in fileReqd:
                    if self.sc.checkPresence(fileReqd)==1:
                        data=self.sc.cache[fileReqd]
                    else:
                        result = subprocess.run(
                                                [sys.executable, "-c", "import sys; print(exec(sys.stdin.read()))"],
                                                input=open(fileReqd, "rb").read(),
                                                capture_output=True
                                                )
                        data=result.stdout
                        data=data.decode()
                        cut=data.find("None")
                        data=data[:cut]
                        data=data.strip()
                        self.sc.placeNewKey(fileReqd,data)
                    return 200, "text/html", len(data), data.encode()

                if fileReqd.endswith("ls"):
                    cp=os.path.join(self.path,'bin')
                    if self.sc.checkPresence(cp)==1:
                        data=self.sc.cache[cp]
                    else:
                        for files in os.listdir(cp):
                            data+='<a>'+files+"</a> <br>"+"\n"  
                        self.sc.placeNewKey(fileReqd,data) 
                    return 200, "text/html", len(data), data.encode()     
                
                
                elif fileReqd.endswith("du"):
                    cp=os.path.join(self.path,"bin")
                    if self.sc.checkPresence(cp)==1:
                        data=self.sc.cache[cp]
                    else:
                        for top, dirs, files in os.walk(cp):
                            for f in files:
                                fp = os.path.join(cp, f)
                                size = os.stat(fp).st_size
                                data+='<a>'+f+" "+str(size)+"</a> <br>"+"\n" 
                        self.sc.placeNewKey(fileReqd,data)
                    return 200, "text/html", len(data), data.encode()

            else:  #normal file
                if self.sc.checkPresence(fileReqd)==1:
                    data=cache[fileReqd]
                else:
                    data= open(fileReqd,'rb').read()
                fileType=mimetypes.MimeTypes().guess_type(fileReqd)[0]
                return 200, fileType, len(data), data 

            
    
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