## IEMOCAP Request Responder

This repository contains a program to respond to IEMOCAP dataset requests automatically.

Steps to run the program -

1. Generate new IEMOCAP password in `sbaruah@sail.usc.edu`

2. ``python iemocap.py iemocap_password``

3. For each request, select action -

    a. _Approve_ - if request details are correct.

    b. _Reject_ - if request details are incorrect. The program will prompt you again, asking for the reason. Enter your answer.

    c. _Industry_ - if request comes from an industry or for non-academic purposes.

    d. _Quit_ - if you want to quit the process.

4. IEMOCAP password is emailed to approved requests. 
Your reason for rejection is emailed to rejected requests, with the message to submit a new request. 
No email is sent to industry-source requests.

The details of approved and industry-source requests are saved to _iemocap_2020.csv_ and _iemocap_industry_2020.csv_.
The message ids of rejected or erroneous requests are saved to error_message_ids.txt.