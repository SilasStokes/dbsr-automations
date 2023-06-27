import smtplib
import ssl
import requests
from pprint import pprint
from time import sleep
import random
from fake_useragent import UserAgent
import datetime
from twilio.rest import Client

import json
from email.message import EmailMessage
# "hfrancis@unitedindians.org",
# "ronnie@daybreakstarradio.com"


config = {}
config_path = f'config.json'
with open(config_path, 'r') as config_fd:
    config = json.load(config_fd)

try:
    assert 'source_email' in config
    assert 'destination_emails' in config
    assert 'email_password' in config
    assert 'ios_url' in config
    assert 'android_url' in config
    # twilio asserts:
    assert 'twilio_account_sid' in config
    assert 'twilio_auth_token' in config
    assert 'twilio_phone_number' in config
    assert 'destination_phone_numbers' in config
except Exception as e:
    print(f'Error with config file. {e=}')
    quit()
    
sms_client = Client(config['twilio_account_sid'], config['twilio_auth_token'])

ios_email = f'''
Silas' python script encounter'd an error while parsing the iOS app store for the DBSR App. This program is a beta though and this could be a false positive.
Check the following links before escalating. 
iOS app store link: {config["ios_url"]}
Developer Portal (credentials to access needed): {config["ios_developer_url"]}
'''

android_email = f'''
Silas' python script encounter'd an error while parsing the android app store for the DBSR App. This program is a beta though and this could be a false positive.
Check the following links before escalating. 
android app store link: {config["android_url"]}
'''

def send_email(content: str):
    msg = EmailMessage()
    msg['Subject'] = f'iOS App Down!'
    msg['From'] = config['source_email']
    msg['To'] = config['destination_emails']
    msg.set_content(content)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(config['source_email'], config['email_password'])
        server.send_message(msg)
    message = sms_client.messages.create(
        body=f'{content}',
        from_=config['twilio_phone_number'],
        to=config['destination_phone_numbers'][0]
    )
    quit()

port = 465
browser_useragent = UserAgent()
while True:
    now = datetime.datetime.now()
    headers = {
        'User-agent': browser_useragent.random
    }
    timeout = 0
    
    # do iOS store
    try:
        req = requests.get(config['ios_url'])
    except Exception as exc:
        print(f'[{now}] iOS Request failed - {Exception=}, {exc=}')
        # sleep(10)
        continue

    if req.status_code == 200:
        print(f'[{now}] iOS App up')
    elif req.status_code == 429:
        timeout = req.headers.get('Retry-After', 0) # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Retry-After
        print(f'[{now}] Too many requests... sleeping {timeout} seconds')
        sleep(int(timeout))
    else:
        content = f'Timestamp: [{now}]\n{ios_email}'
        print(f'[{now}] request failed! App maybe down! Check link {config["ios_url"]}')

        send_email(content)
        print(f'[{now}] request failed! App maybe down! Check link {config["ios_url"]}')
        
    print(f'[{now}] iOS Request Result: {req.status_code=}, {req.reason=}')
    now = datetime.datetime.now()
    # requesting Android page
    try:
        req = requests.get(config['android_url'])
    except Exception as exc:
        print(f'[{now}] Android request failed - {Exception=}, {exc=}')
        # sleep(10)
        continue

    if req.status_code == 200:
        print(f'[{now}] Android App up')
    elif req.status_code == 429:
        timeout = req.headers.get('Retry-After', 0) # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Retry-After
        print(f'[{now}] Too many requests... sleeping {timeout} seconds')
        sleep(int(timeout))
    else:
        content = f'Timestamp: [{now}]\n{android_email}'
        print(f'[{now}] request failed! App maybe down! Check link {config["android_url"]}')
        send_email(content)
        
    print(f'[{now}] Android Request Result: {req.status_code=}, {req.reason=}')

    # print(f'[{now}] header information:')
    # print(req.headers)
    minutes_to_wait = random.randint(5,15)
    print(f'[{now}] waiting {minutes_to_wait} minutes before trying again...')
    sleep(60*minutes_to_wait)


