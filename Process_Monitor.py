# Automation Script which accept Time Interval from user and create Log file in that
# directory which contains information of all running processes
# After creating the log file send that log file through mail

import psutil
import os
import time
import schedule
from sys import *
import urllib3
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


def is_connected():
    try:
        urllib3.connectionpool.connection_from_url('http://216.58.192.142', timeout = 1)
        return True
    
    except urllib3.urlError as err:
        return False
    
    except Exception as E:
        print("Error : Not Connected",E)


def MailSender(filename, time):
    try:
        fromAddr = "ABC@gmail.com"      # from address
        toAddr = "XYZ@gmial.com"        # To address

        msg = MIMEMultipart()

        msg['From'] = fromAddr
        msg['To'] = toAddr

        body = """
                Hello %s,

                Please find attached document which contains Log of Running Processes.
                Log file is created at : %s

                This is Auto-Generated mail.
                
                Thanks and Regards
                """%(toAddr, time)
        
        subject = """Process Log Generated at : %s""" %(time)
        
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        attachment = open(filename, 'rb')

        p =MIMEBase('application', 'octet-stream')

        p.set_payload((attachment).read())

        encoders.encode_base64(p)

        p.add_header('Content-Deposition',"attachment; filename = %s" %(filename))

        msg.attach(p)

        s = smtplib.SMTP('smtp.gmail.com',587)

        s.starttls()

        s.login(fromAddr, "-----------")  # password

        text = msg.as_string()

        s.sendmail(fromAddr, toAddr, text)

        s.quit()

        print("Log file successfully send throgh mail")

    except Exception as E:
        print("Unable to send mail ",E)


def ProcessLog(log_dir = "ProcessLogs"):

    if(not os.path.exists(log_dir)):
        try:
            os.mkdir(log_dir)
        except:
            pass

    separator = "-"*80
    timestamp = time.ctime()
    timestamp = timestamp.replace(" ", "_")
    timestamp = timestamp.replace(":", "-")
    timestamp = timestamp.replace("/", "_")

    log_path = os.path.join(log_dir, "ProcessLog %s.log"%timestamp)
    f = open(log_path, "w")
    f.write(separator + '\n')
    f.write("Log of Running Process at : "+time.ctime() + '\n')
    f.write(separator + '\n')

    listprocess = []

    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs = ['pid', 'name', 'username'])
            pinfo['vms'] = proc.memory_info().vms / (1024 * 1024)
            listprocess.append(pinfo)

        except(psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    for element in listprocess:
        f.write("%s\n"%element)

    print("Log File is Successfully generated at Location = %s"%(log_path))

    connected = is_connected()

    if connected:
        startTime = time.time()
        MailSender(log_path, time.ctime())
        endTime = time.time()

        print("Tool %s seconds to send Mail"%(endTime - startTime))
    
    else:
        print("There is No Internet Connection")


def main():

    print("--------------- Process Monitor with Periodic Memory Log and Mail ---------------")

    if(len(argv) != 2):
        print("Error : Invalid number of Arguments")
        exit()

    if((argv) == '--H' or (argv) == '--h'):
        print("This Script is used to record Log of running Processes and send it over Mail")
        exit()
    
    if((argv) == '--U' or (argv) == '--u'):
        print("Usage : ApplicationName Time_In_Min_To_Schedule_Mail")
        exit()

    try:
        schedule.every(int(argv[1])).minutes.do(ProcessLog)
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    except ValueError:
        print("Error : Invalid DataType of Input")

    except Exception as E:
        print("Error : Invalid Input ",E)


if __name__ == "__main__":
    main()    