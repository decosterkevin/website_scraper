import smtplib, ssl
from config import Config
config = Config()


def send_email(sender_email, receiver_email, subject, text):
    # Try to log in to server and send email
    try:
        header = 'To:' + receiver_email + '\n' + 'From: ' + config.EMAIL_USERNAME + '\n' + 'Subject:' + subject + '\n'
        server = smtplib.SMTP(config.EMAIL_HOST,config.EMAIL_PORT)
        print(text)
        server.ehlo() # Can be omitted
        server.starttls() # Secure the connection
        server.ehlo() # Can be omitted
        server.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)


        server.sendmail(sender_email, receiver_email, header + text)
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit() 