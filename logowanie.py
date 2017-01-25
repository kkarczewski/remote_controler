#! /usr/bin/env python3.4
#! -*- coding: utf-8 -*-
'''
Created on 27 lip 2015

@author: kamil@justnet.pl
'''

# #############################################################################
# standard modules (moduly z biblioteki standarowej pythona)
# #############################################################################
import os
import sys
import re
import time
import argparse
import subprocess
import pipes
import getpass
import csv
import datetime
import base64
import xml.etree.ElementTree as ET
#import uuid
#import types
#import shutil
NAME = __file__
SPLIT_DIR = os.path.dirname(os.path.realpath(NAME))
SCRIPT_DIR = SPLIT_DIR + './' + os.path.basename(NAME)
LIB_DIR = SCRIPT_DIR + '/cache/lib/'
TMP_DIR = SPLIT_DIR + '/tmp/'
sys.path.insert(0,TMP_DIR)
#List of lib to install
import_list = [
#   ('sqlalchemy','1.0.8','SQLAlchemy-1.0.8.egg-info'),
   ('paramiko','1.15.2','paramiko-1.15.2.dist-info'),
   ('colorama','0.3.3','colorama-0.3.3.egg-info')]

for line in import_list:
   try:
      if os.path.isdir(TMP_DIR+line[0]):
         pass
#         print('Found installed '+line[0]+line[1]+' in '+line[2])
      else:
         try:
            import pip
         except:
            print("Use sudo apt-get install python3-pip")
            sys.exit(1)
         print('No lib '+line[0]+'-'+line[1])
         os.system("python"+sys.version[0:3]+" -m pip install '"+line[0]+'=='+line[1]+"' --target="+LIB_DIR+" -b "+TMP_DIR)
      module_obj = __import__(line[0])
      globals()[line[0]] = module_obj
   except ImportError as e:
      print(line[0]+' is not installed')

# #############################################################################
# constants, global variables
# #############################################################################
OUTPUT_ENCODING = 'utf-8'
LOGGER_PATH = TMP_DIR+'/logfile.xml'
LOG_VERSION = 1.0
DIRECTORY = './'
# #############################################################################
# functions
# #############################################################################

#CZYTANIE Z PLIKU
def readfile(file_name):
   try:
      with open(file_name, 'r') as file:
         templines = [line.rstrip('\n') for line in file]
         lines=([])
         for line in templines:
            if not '#' in line:
               lines.append(line)
   except (IOError, OSError):
      print >> sys.stderr, "Can't open file."
      sys.exit(1)
   return lines

# Kolorowanie ok
def print_ok(output):
   print(colorama.Fore.GREEN+output,colorama.Fore.RESET)

# Kolorowanie błędu
def print_err(error):
   print(colorama.Fore.RED+error,colorama.Fore.RESET)

def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

# LOGI
def my_logger(ERROR_FLAG,subcmd,outmsg):
   id_log = 1
   if not os.path.exists(LOGGER_PATH):
      root = ET.Element('root')
      root.set('version','1.0')
   else:
      tree = ET.parse(LOGGER_PATH)
      root = tree.getroot()
      for child in root:
         id_log+=1
   log = ET.SubElement(root, 'log')
   log.set('id_log',str(id_log))
   date = ET.SubElement(log,'date')
   date.text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')
   cmdline = str()
   for line in sys.argv:
      cmdline += line+' '
   command = ET.SubElement(log,'command')
   command.set('encoding','plain')
   command.text = cmdline
   subcommands = ET.SubElement(log,'subcommands')
   subcommands.set('error_flag',ERROR_FLAG)
   subcmd_str=str()
   for one in subcmd:
      subcmd_str+=one+','
   subcommands.text = subcmd_str[:-1]
   output = ET.SubElement(log,'output')
   output.set('encoding','base64')
   output.text = (base64.b64encode(outmsg.encode(OUTPUT_ENCODING))).decode(OUTPUT_ENCODING)
   indent(root)
   if not os.path.exists(LOGGER_PATH):
      tree = ET.ElementTree(root)
   tree.write(LOGGER_PATH,encoding=OUTPUT_ENCODING,xml_declaration=True,method='xml')
   
# Wywołanie polecenia w terminalu
def os_call(*args,progress_char='*',verbose=1):
   n = 0
   done_cmd = list()  
   out = list()
   for cmd in args:
      p = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=DIRECTORY)
      (output,err) = p.communicate()
      n = n+1
      ast = progress_char*n
      if err or 'ERROR' in str(output) or 'Exception' in str(output):
         done_cmd.append(cmd)
         ERROR_FLAG = 'T'
         print_err(cmd)
         if err:
            print_err(err.decode(OUTPUT_ENCODING))
            out.append(err.decode(OUTPUT_ENCODING))
            break
         else:
            print_err(output.decode(OUTPUT_ENCODING))
            out.append(output.decode(OUTPUT_ENCODING))
            break
      else:
         ERROR_FLAG = 'F'
         done_cmd.append(cmd)
         out.append(output.decode(OUTPUT_ENCODING))
         if verbose == 2:
            print(ast,end="\r")
            time.sleep(1)
            print_ok(cmd)
            print_ok(output.decode(OUTPUT_ENCODING))
         elif verbose == 1:
            print_ok(output.decode(OUTPUT_ENCODING))
         else:
            print(ast,end='\r')
   return ERROR_FLAG,done_cmd,out

# CSV write example
def csv_write(file_name, temp):
   with open(file_name, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile, delimiter=temp)
      writer.writerow(['example','date','for','csv'])
      writer.writerow(['example']*4)
# CSV read example
def csv_read(file_name, temp):
   with open(file_name, 'r', newline='') as csvfile:
      reader = csv.reader(csvfile, delimiter=temp)
      for row in reader:
         print(row)

# SQLAlchemy simple example
def simple_query(query):
   dbpass=getpass.getpass("DB Password: ")
   engine = sqlalchemy.create_engine("mysql+pymysql://sandbox:"+dbpass+"@195.54.47.34/sandbox")
#   engine = sqlalchemy.create_engine(dialect+driver://username:password@host:port/database)
   connection = engine.connect()
   result = connection.execute(query)
   for row in result:
      print(row)
   connection.close()

#Wykonanie skryptu
def logonScript(server,loginssh,scriptPath,nosuBool):
   serverPath = loginssh+"@"+server+":"
   os.system("scp "+scriptPath+" "+serverPath)
   (path,scriptname) = os.path.split(scriptPath)
   ssh = paramiko.SSHClient()
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   ssh.connect(server,port=22,username=loginssh,password=globals()["sshpass"])
   print_ok(server+': Connected')
   logdata = server+': Connected\n ./'+scriptname+'\n'
   if nosuBool==True:
      #nosu TAK
      stdin,stdout,stderr = ssh.exec_command("chmod +x "+scriptname+" && ./"+scriptname)
      error = stderr.readlines()
      output = stdout.readlines()
      ssh.close()
      if error:
         ERROR_FLAG = 'T'
         print_err('Script execute: Failed')
         for err in error:
            print_err(err)
            logdata += err+'\n'
         print_ok(server+': Disconnected')
         logdata += server+': Disconnected\n'
      else:
         ERROR_FLAG = 'F'
         print_ok('Script execute: Done')
         logdata += 'Script execute: Done\n'
         for line in output:
            print(line)
            logdata+=line+'\n'
         logdata+=server+': Dosconnected\n'
         print_ok(server+': Disconnected')
         logdata+=server+': Done\n'
         print_ok(server+': Done')
   else:
      #nosu NIE
      supass = getpass.getpass('Root password: ')
      channel = ssh.invoke_shell()
      channel.send('su\n')
      time.sleep(1)
      output = channel.recv(1024)
      channel.send(supass+'\n')
      time.sleep(1)
      output += channel.recv(1024)
      channel.send('whoami\n')
      time.sleep(1)
      isroot = channel.recv(9999)
      listroot = isroot.decode(OUTPUT_ENCODING).split()
      listroot.append('user')
      if listroot[1] == 'root':
         channel.send('chmod +x '+scriptname+'\n')
         time.sleep(1)
         output += channel.recv(1024)
         channel.send('./'+scriptname+'\n')
         time.sleep(1)
         if channel.recv_stderr_ready():
            ERROR_FLAG='T'
            error = channel.recv_stderr(2048)
            logdata+=error+'\n'
            print_err(error)
         else:
            ERROR_FLAG='F'
            output += channel.recv(1024)
            logdata+=output.decode(OUTPUT_ENCODING)+'\n'
            print_ok('Script execute: Done')
            logdata+='Script execute: Done\n'
         ssh.close()
         print_ok(server+': Disconnected')
         logdata+=server+': Disconnected\n'
         print_ok(server+': Done')
         logdata+=server+': Done\n'
      else:
         ERROR_FLAG = 'T'
         logdata+=output.decode(OUTPUT_ENCODING)+'\n'
         print_err('No root rights')
         logdata+='No root rights\n'
         print_err('Script execute: Failed')
         logdata+='Script execute: Failed\n'
         ssh.close()
         print_ok(server+': Disconnected')
         logdata+=server+': Disconnected\n'
   return ERROR_FLAG,'./'+scriptname,logdata

# Funkcja dla passwd
def logonPasswd(server,loginssh,verboseBool):
   ssh = paramiko.SSHClient()
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   ssh.connect(server,port=22,username=loginssh,password=globals()["sshpass"])
   print_ok(server+': Connected')
   logdata=server+': Connected\n'
   stdin,stdout,stderr = ssh.exec_command(afterSshCmd)
   stdin.write(globals()["sshpass"]+'\n')
   stdin.write(globals()["newpass"]+'\n')
   stdin.write(globals()["renewpass"]+'\n')
   stdin.flush()
   error = stderr.readlines()
   output = stdout.readlines()
   ssh.close()
   if error and not output:
      ERROR_FLAG = 'T'
      for line in error:
         print(line)
         logdata+=line+'\n'
   if error and output:
      ERROR_FLAG = 'F'
      for line in output:
         print(line)
         logdata+=line+'\n'
   print_ok(server+': Disconnected')
   logdata+=server+': Disconnected\n'
   logdata+=server+': Done\n'
   print_ok(server+': Done')
   return ERROR_FLAG,'passwd',logdata

#WYWOŁANIE KOMENDY Z ODPOWIEDNIMI PARAMETRAMI
def logonCmd(server,loginssh,afterSshCmd,nosuBool,verboseBool):
   ssh = paramiko.SSHClient()
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   ssh.connect(server, port=22, username=loginssh, password=globals()["sshpass"])
   print_ok(server+': Connected')
   logdata=server+': Connected\n'
   if nosuBool==True:
      stdin,stdout,stderr = ssh.exec_command(afterSshCmd)
      output = stdout.readlines();
      error = stderr.readlines()
      if verboseBool==True:
         #nosu TAK, verbose TAK
         print(afterSshCmd)
         if error:
            ERROR_FLAG = 'T'
            for err in error:
               print_err(err)
               logdata+=err+'\n'
            ssh.close()
            logdata+=server+': Disconnected\n'
            print_ok(server+': Disconnected\n')
         else:
            ERROR_FLAG = 'F'
            for line in output:
               logdata+=line+'\n'
               print(line)
            ssh.close()
            print_ok(server+': Disconnected')
            logdata+=server+': Disconnected\n'
            print_ok(server+': Done')
            logdata+=server+': Done\n'
      else:
         #nosu TAK, verbose NIE
         if error:
            ERROR_FLAG = 'T'
            for err in error:
               print_err(err)
               logdata+=err+'\n'
            ssh.close()
            print_ok(server+': Disconnected')
            logdata+=server+': Disconnected\n'
         else:
            ERROR_FLAG = 'F'
            ssh.close()
            print_ok(server+': Disconnected')
            logdata+=server+': Disconnected'
            print_ok(server+': Done')
            logdata+=server+': Done\n'
   else:
      supass = getpass.getpass('Root password: ')
      channel = ssh.invoke_shell()
      channel.send('su\n')
      time.sleep(1)
      output = channel.recv(1024)
      channel.send(supass+'\n')
      time.sleep(1)
      output += channel.recv(1024)
      channel.send('whoami\n')
      time.sleep(1)
      isroot = channel.recv(9999)
      listroot = isroot.decode(OUTPUT_ENCODING).split()
      listroot.append('user')
      if listroot[1]=='root':
         channel.send(afterSshCmd+'\n')
         time.sleep(1)
         output += channel.recv(1024)
         ERROR_FLAG = 'F'
         if verboseBool==True:
            #verbose TAK, nosu NIE
            print(output.decode(OUTPUT_ENCODING))
            logdata+=output.decode(OUTPUT_ENCODING)+'\n'
            ssh.close()
            print_ok(server+': Disconnected')
            logdata+=server+': Disconnected'
            print_ok(server+': Done')
            logdata+=server+': Done'
         else:
            #verbose NIE, nosu NIE
            logdata+=output.decode(OUTPUT_ENCODING)+'\n'
            ssh.close()
            print_ok(server+': Disconnected')
            logdata+=server+': Disconnected'
            print_ok(server+': Done')
            logdata+=server+': Done'
      else:
         ERROR_FLAG = 'T'
         logdata+=output.decode(OUTPUT_ENCODING)
         print_err('No root rights')
         logdata+='No root rights.\nCommand execute: Failed\n'
         print_err('Command execute: Failed')
         ssh.close()
         print_ok(server+': Disconnected')
         logdata+=server+': Disconnected\n'
   return ERROR_FLAG,afterSshCmd,logdata
# ##############################################################################
# classes
# #############################################################################

class SomeClass:

   def __init__(self, some_param1, some_param2, some_param3):
      pass

   def some_method(self, some_param1):
      pass

# #############################################################################
# operations
# #############################################################################


#Wywołanie dla poleceń na liście serwerów
def allservers(file_name):
   servers = readfile(file_name)
   for server in servers:
      subcmd = list()
      ERROR_FLAG,cmd,outmsg = logonCmd(server,loginssh,afterSshCmd,nosuBool,verboseBool)
      if nosuBool==False:
         subcmd.append("su -c '"+cmd+"'")
      else:
         subcmd.append(cmd)
      my_logger(ERROR_FLAG,subcmd,outmsg)
#Wywołanie dla scryptów na liście serwerów
def allServersScript(file_name):
   servers = readfile(file_name)
   for server in servers:
      subcmd = list()
      ERROR_FLAG,cmd,outmsg = logonScript(server,loginssh,scriptPath,nosuBool)
      subcmd.append(cmd)
      my_logger(ERROR_FLAG,subcmd,outmsg)
#Wywołanie zmiany hasła na liście serwerów
def allPasswd(file_name):
   servers = readfile(file_name)
   for server in servers:
      subcmd = list()
      ERROR_FLAG,cmd,outmsg = logonPasswd(server,loginssh,verboseBool)
      subcmd.append(cmd)
      my_logger(ERROR_FLAG,subcmd,outmsg)

# main app 
# #############################################################################
if __name__ == '__main__':
# Czytanie arugmentów
   parser = argparse.ArgumentParser(prog='logowanie.py' ,description="Remote controler for server. Server list from file. Command, login as argument.", epilog="Example of usage: ./logowanie.py -l kamil -sl file1.txt -c 'ls -l' -n")
   parser.add_argument("--serverlist", "-sl", help="File name with server addresses, default server_list")
   parser.add_argument("--login", "-l", help="Username to ssh, default jadmin")
   parser.add_argument("--verbose", "-v", action="store_true", help="Tracking executed commands and their output.")
   parser.add_argument("--cmd", "-c", help="Command to execute after ssh")
   parser.add_argument("--script", "-s", help="Path and name of script to execute on server after ssh.")
   parser.add_argument("--nosu", "-n", action="store_true", help="Variable shows that we switch user to root or not with su, default with su.")
   args = parser.parse_args()
   cmdBool = False
   scriptBool = False
# Brak argumentów - wyświetl pomoc
   try:
      if not len(sys.argv) > 1:
         out = 'Need more argument'
         parser.print_help()
         sys.exit('Need more argument. See help.')
      if args.serverlist:
         file_name=args.serverlist
      else:
         file_name="server_list"
      if args.login:
         loginssh=args.login
      else:
         loginssh="jadmin"
      if args.cmd:
         afterSshCmd = args.cmd
         cmdBool = True
         scriptBool = False
      if args.script:
         scriptPath = args.script
         scriptBool = True
         cmdBool = False
         afterSshCmd = 'skip'
      if args.verbose:
         verboseBool = True
      else:
         verboseBool = False
      if args.nosu:
         nosuBool = True
      else:
         nosuBool = False
      if cmdBool==False and scriptBool==False:
         parser.print_help()
#wywołanie funkcji odpowiedzialnych za uruchamianie komendy lub skryptu
      elif afterSshCmd == 'passwd':
         sshpass = getpass.getpass('SSH password: ')
         newpass = getpass.getpass('New password: ')
         while newpass == sshpass:
            newpass = getpass.getpass('New password must be different then current: ')
         renewpass = getpass.getpass('Re-enter new password: ')
         while renewpass != newpass:
            renewpass = getpass.getpass('Different password. Re-enter correctly: ')
         allPasswd(file_name)
      elif cmdBool == True:
         sshpass = getpass.getpass('SSH password: ')
         allservers(file_name)
      else:
         sshpass = getpass.getpass('SSH password: ')
         allServersScript(file_name)
   except Exception as e:
      cmd = str()
      for one_arg in sys.argv:
         cmd+=one_arg+' '
      list_cmd =list()
      list_cmd.append(cmd)
      err_msg = str(e)
      msg = (base64.b64encode(err_msg.encode(OUTPUT_ENCODING))).decode(OUTPUT_ENCODING)
      my_logger('T',list_cmd,msg)
      print(e)
