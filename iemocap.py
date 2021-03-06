# author = Sabyasachee Baruah

import re
import csv
import sys
import imaplib
import smtplib
import ssl
import pandas as pd
import email
import datetime

from send_email import send_emails
from parse_request import parse_body

def respond_requests(iemocap_password):
    '''
    respond_requests searches for new IEMOCAP requests and responds to them.

    Input
    ====

    iemocap_password - The active password to iemocap dataset.

    Working
    ====

        1. Login to account using file/account.txt credentials.
        2. Search INBOX for emails with SUBJECT = 'IEMOCAP Release Form' since 02-Apr-2020.
        3. Filter out emails that you have already responded.
        4. For each new email -
            i.   Parse the email body.
            ii.  Choose a response amongst - Approve, Reject, Industry.
            iii. If you choose Reject, enter the reason for rejection.
        5. Approved requests are sent IEMOCAP password. 
            Rejected requests are sent rejection reason and asked to resubmit request.
            Industrial requests are ignored.
        6. Approved and Industrial requests are saved to files/.
            Message IDs of rejected requests are saved to files/error_message_ids.txt
    '''

    with open("files/account.txt") as fr:
        lines = fr.read().strip().split("\n")
        account = lines[0].split("=")[1].strip()
        app_passwd = lines[2].split("=")[1].strip()

    iemocap_response = f"""
    Thank you for your interest in IEMOCAP corpus. Please use this password {iemocap_password} with the username iemocap. Password will expire in 48 hours. Downloads link below.
Full database: http://sail.usc.edu/databases/iemocap/ (md5 hash: 521be1e5eec425ae21fdc27c763ca813)
Without Videos: http://sail.usc.edu/databases/iemocap/small/ (md5 hash: 6f2e6ecb72dd45a9af6b801ee999cb5a)"""
    error_response = "Please fill the request form again here - https://sail.usc.edu/iemocap/release_form.php"
    industry_response = "We are sorry to inform you that the dataset is not available for commercial purposes. Thank you for your understanding."

    M = imaplib.IMAP4_SSL("imap.gmail.com")
    print("logging in...")
    M.login(account, app_passwd)
    
    M.select("INBOX")
    print("searching iemocap emails in INBOX...")
    _, data = M.search(None, 'SUBJECT "IEMOCAP Release Form" SINCE 13-Aug-2020')
    inbox_msg_ids = data[0].split()
    
    M.select("[Gmail]/Spam")
    print("searching iemocap emails in SPAM...")
    _, data = M.search(None, 'SUBJECT "IEMOCAP Release Form" SINCE 13-Aug-2020')
    spam_msg_ids = data[0].split()

    iemocap_df = pd.read_csv("files/iemocap_2020.csv", index_col=None)
    industry_df = pd.read_csv("files/iemocap_industry_2020.csv", index_col=None)
    prev_msg_ids = list(iemocap_df["msg_id"].apply(lambda x: x[2:-1].encode()).values)
    prev_msg_ids += list(industry_df["msg_id"].apply(lambda x: x[2:-1].encode()).values)
    with open("files/error_message_ids.txt") as fr:
        lines = fr.read().strip().split("\n")
        for line in lines:
            prev_msg_ids.append(line.encode())
    
    new_inbox_msg_ids = [x for x in inbox_msg_ids if x not in prev_msg_ids]
    new_spam_msg_ids = [x for x in spam_msg_ids if x not in prev_msg_ids]
    new_msg_ids = [("INBOX", x) for x in new_inbox_msg_ids] + [("[Gmail]/Spam", x) for x in new_spam_msg_ids]

    old_email_addresses = iemocap_df["email"].tolist() + industry_df["email"].tolist()

    if len(new_msg_ids) == 0:
        print("No new requests...")
        return
    print(f"{len(new_msg_ids)} new requests recieved...\n\n")

    approved_records = []
    industry_records = []
    error_msg_ids = []
    responses = []

    selected_msg_box = None

    for i, (msg_box, msg_id) in enumerate(new_msg_ids):
        if not selected_msg_box or selected_msg_box != msg_box:
            M.select(msg_box)
            selected_msg_box = msg_box
        _, data = M.fetch(msg_id, "(RFC822)")
        
        if data[0] is None:
            print(f"{i + 1}/{len(new_msg_ids)}. null data")
            error_msg_ids.append(msg_id)
            continue

        message = email.message_from_bytes(data[0][1])
        
        if not message.is_multipart():
            body = message.get_payload()
            date = message["Date"]
            print(f"{i + 1}/{len(new_msg_ids)}. MESSAGE ID = {msg_id}, DATE = {date}")

            try:
                parsed_output = parse_body(body)
                
                if parsed_output["address"] not in old_email_addresses:
                    parsed_output["msg_id"] = msg_id
                    parsed_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(date)))
                    now = datetime.datetime.now()
                    parsed_output["request_date"] = datetime.datetime.strftime(parsed_date, "%d %b %Y")
                    parsed_output["response_date"] = datetime.datetime.strftime(now, "%d %b %Y")
                    for key, value in parsed_output.items():
                        print(f"{key:15s} = {value}")
                    print()
                    
                    print("1. Approve")
                    print("2. Correct")
                    print("3. Industry")
                    print("4. Stash")
                    print("5. Next")
                    print("6. Quit\n")
                    action = input("Enter action number?\t")
                    
                    response = email.message.Message()
                    response["Message-ID"] = email.utils.make_msgid()
                    response["In-Reply-To"] = message["Message-ID"]
                    response["References"] = message["Message-ID"]
                    response["To"] = message["From"]
                    response["From"] = account
                    response["Subject"] = message["Subject"]
                    if action == "1":
                        response.set_payload(iemocap_response)
                        responses.append(response)
                        approved_records.append(parsed_output)
                    elif action == "2":
                        error_msg_ids.append(msg_id)
                        error_message = input("What is wrong with the request?\t")
                        response.set_payload(error_message + "\n" + error_response)
                        responses.append(response)
                    elif action == "3":
                        response.set_payload(industry_response)
                        responses.append(response)
                        industry_records.append(parsed_output)
                    elif action == "4":
                        error_msg_ids.append(msg_id)
                    elif action == "6":
                        return
                else:
                    print('Already replied to email address')

            except Exception as e:
                print("Error occurred" + str(e))
                error_msg_ids.append(msg_id)
        else:
            print(f"{i + 1}/{len(new_msg_ids)}. MESSAGE ID = {msg_id}, multipart message ignored")
            error_msg_ids.append(msg_id)
        print("================================================================================================\n")

    with open("files/error_message_ids.txt", "ab") as fw:
        for msg_id in error_msg_ids:
            fw.write(msg_id + b"\n")

    if len(responses) > 0:
        action = input("Do you want to send emails? (y/n)\t")
        if action == "n":
            return
    else:
        return

    if len(responses) > 0:
        print("sending emails...")
        send_emails(responses)
        print()

    approved_df = pd.DataFrame.from_dict(approved_records)
    new_industry_df = pd.DataFrame.from_dict(industry_records)

    if approved_df.shape[0]:
        print("Approved Records =>")
        print(approved_df)
        print()
    if new_industry_df.shape[0]:
        print("Industry Records =>")
        print(new_industry_df)

    iemocap_df = pd.concat([iemocap_df, approved_df])
    industry_df = pd.concat([industry_df, new_industry_df])
    iemocap_df.to_csv("files/iemocap_2020.csv", index=False, quoting=csv.QUOTE_ALL)
    industry_df.to_csv("files/iemocap_industry_2020.csv", index=False, quoting=csv.QUOTE_ALL)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python iemocap.py password")
        sys.exit(0)
    iemocap_password = sys.argv[1]
    respond_requests(iemocap_password)
