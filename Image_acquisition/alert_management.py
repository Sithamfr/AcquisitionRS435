import smtplib, ssl, socket
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# PARAMS
hostname = socket.gethostname()
smtp_server = "smtp.gmail.com"
sender_email = ""  # ---> Enter your address here
password = ""  # ---> Enter your password here
receiver_email = [""] # ---> Enter your receivers here

# FUNCTION TO SEND MAIL ALERTS
def send_alert(e,status,dtime):

    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = ', '.join(receiver_email)
    
    if len(status)>0 and status[0].replace('\n','')=="0": #error already happened
            message = f"""\
            <html><head></head><body><p>
            The error is still present at {dtime} : <i>{e}</i>.<br>
            <b>{hostname} is automatically rebooting now.</b>
            </p></body></html>"""
            dtime = status[1]
            first_time_error = False
    else: #error happened for first time
        with open('last_acquisition_status','w') as f:
            f.write(f"0\n{dtime}")
        message = f"""\
        <html><head></head><body>
        <p><u>Description :</u><br>
        Acquisition failed for <b>{hostname}</b> the <b>{dtime}</b>.<br>
        Please find attached the error message :
        <i>{e}</i></p>
        <p><u>Solution :</u><br>
        Please check the connection of the camera to the Raspberry Pi.
        It is also possible that the camera was already used by another process that blocked the access to it.
        If it is impossible to access physically, please reboot the Raspberry Pi.
        <br><b>If the error persists, {hostname} will be automatically rebooted.</b>
        </p></body></html>"""
        first_time_error = True
    
    msg['Subject'] = f"Error during acquisition for {hostname} [{dtime}]"
    msg.attach(MIMEText(message,'html'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        
    return first_time_error

# FUNCTION TO REBOOT SYSTEM
def reboot_pi(T):
    time.sleep(T)
    os.system('sudo reboot')
