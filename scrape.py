import requests
import smtplib
from email.mime.text import MIMEText
from argparse import ArgumentParser

import json
from time import sleep
from datetime import date
from datetime import datetime

UNAVAILABLE_DATES = ['d3_9_2017', 'd3_10_2017', 'd3_11_2017', 'd3_12_2017', 'd3_26_2017', 'd3_27_2017',
                     'd3_25_2017']
def scrape():
    days_str = "days = "
    url = "https://www.appointmentcare.com/booking/offleash/select_date"

    #ATTENTION: This data may be instance specific... have not investigated. Can confirm though that my
    # 'authentication token' has never expired.
    data = {
        'utf8' : "✓",
        'authenticity_token' :  "equyTAdvHwkRLSopSbkC0YCDCCxd5T3zlyBmzf0cp5Q=",
        'appointment[service_id]': '1131',
        'appointment[service_details]': '',
        'appointment[schedule_stage]': '1',
        'appointment[employee_id]': '75',
    }
    r = requests.post(url, data=data)
    assert isinstance(r,requests.Response)
    log("status: {0}".format(r.status_code))
    raw = r.content.decode()
    index_start = raw.find(days_str)
    index_end = raw.find('}',index_start)
    dates = raw[index_start+len(days_str):index_end+1].replace('\\','')
    #print(dates)
    date_dict = json.loads(dates)
    assert isinstance(date_dict,dict)
    #log("Number of Keys found: {0}".format(len(date_dict)), True)
    keys = []
    for key, value in date_dict.items():
        #print("{0} : {1}".format(key,value))

        if value:
            keys.append(key)
    #log('DATES FOUND: {0}'.format(keys), True)
    return keys
def send_email(date, me, you, password, smtp_str):
    assert isinstance(date, str)
    msg = MIMEText("ALCON:\r\nA date has opened up for Training: {0}\r\n\r\n-Your Scraper".format(date))
    msg['Subject'] = 'NEW DATE AVAILABLE FOR TRAINING - {0}'.format(date)
    msg['From'] = me
    msg['To'] = you
    server = smtplib.SMTP(smtp_str)
    server.ehlo()
    server.starttls()
    server.login(me, password)
    server.sendmail(me, [you], msg.as_string())
    server.quit()




def log(msg, debug=False):
    right_now = datetime.now().strftime("%Y_%m_%d %H:%M:%S")
    format = "[{0}] - {1}".format(right_now,msg)
    if not debug:
        print(format)

    with open("C:\\test\\scrape_log.txt",'a') as f:
        f.writelines(format+'\n')

def main():
    #initial scrape
    log("MAIN: Offleash K9 Appointment Scraper... performining initial scrape")
    current_scrape = scrape()
    parser = ArgumentParser(description="Scrapes OffleashK9's AppointmentCare service"
                                        " and notifies you if new dates are available")
    parser.add_argument('email_sender', help="the email address to send notifications")
    parser.add_argument('smtp_server', help="the smtp server for sending the email")
    parser.add_argument('email_pwd', help="the password for email_sender account. Must accept tls")
    parser.add_argument('email_recv', help='the email address to send the emails TO')
    args = parser.parse_args()

    SENDER = args.email_sender
    SMTP = args.smtp_server
    RECV = args.email_recv
    PASSWORD = args.email_pwd

    while True:
        #log('sleeping...')
        sleep(10 * 60) # poll every 10 minutes
        #log("Scraping...")

        new_scrape = scrape()
        log('new scrape length: {0}'.format(len(new_scrape)))
        for key in new_scrape:
            if key not in current_scrape and key not in UNAVAILABLE_DATES:
                day = date.today().strftime('%d').lstrip('0')
                month = date.today().strftime('%m').lstrip('0')
                year = date.today().strftime('%Y')
                today = "d{0}_{1}_{2}".format(month,day,year)
                nxt_yr = date.today().year + 1
                nxt_yr = "d{0}_{1}_{2}".format(month,day,nxt_yr)
                if key != today and key != nxt_yr:
                    log('FOUND NEW DATE: {0}'.format(key))
                    send_email(key,SENDER, RECV, PASSWORD, SMTP)


        current_scrape = new_scrape



if __name__ == '__main__':
    main()
    #send_email('today')