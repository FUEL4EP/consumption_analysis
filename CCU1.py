import sys
import xmlrpclib

server_url = 'http://192.168.101.200:2001/';
server = xmlrpclib.Server(server_url);

result = server.listDevices();

print result;
