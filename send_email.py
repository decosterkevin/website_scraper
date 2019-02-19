import smtplib, ssl
from config import Config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config = Config()


def send_email(sender_email, receiver_email, subject, text, html=None):
    """ Email sender

    Use the following environment variable (in Config())
    - config.EMAIL_USERNAME (STARTLS authentification)
    - config.EMAIL_PASSWORD (STARTLS authentification)
    - config.SMTP_HOST (the STMP server url)
    - config.STMP_PORT (the STMP server post number, default 587)
    
    Parameters
    ----------
    sender_email : str
        The email sender
    receiver_email : str
        The email recipient
    subject : str
        The email subject
    text : str
        The plain test message
    html : str, optional
        The HTML parsed message (the default is None, which only create an email using the plain text message)
    
    """

    # Try to log in to server and send email
        # create body message
    try:
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
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit() 