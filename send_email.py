# author - Sabyasachee

import ssl
import smtplib

def send_emails(responses):
    with open("files/account.txt") as fr:
        lines = fr.read().strip().split("\n")
        account = lines[0].split("=")[1].strip()
        app_passwd = lines[2].split("=")[1].strip()

    port = 465  
    smtp_server = "smtp.gmail.com"
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(account, app_passwd)

        for response in responses:
            server.sendmail(account, [response["To"]], response.as_string())
            print(f"email sent to {response['To']}")