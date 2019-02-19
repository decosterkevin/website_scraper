import smtplib, ssl
from config import Config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config = Config()


def send_email(sender_email, receiver_email, subject, text, html=None):
    # Try to log in to server and send email
        # create body message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config.EMAIL_USERNAME 
    msg['to'] = receiver_email

    part1 = MIMEText(text, 'plain')
    msg.attach(part1)
    if html:
        part2 = MIMEText(html, 'html')
        msg.attach(part2)
    # instantiate server
    server = smtplib.SMTP(config.EMAIL_HOST,config.EMAIL_PORT)
    server.ehlo() # Can be omitted
    server.starttls() # Secure the connection
    server.ehlo() # Can be omitted
    server.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)


    server.sendmail(sender_email, receiver_email, msg.as_string())
