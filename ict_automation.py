# currently disabling the file until we can figure out why it's breaking. 

exit(0)

# py libs

import ssl
import smtplib
from mutagen.id3._util import (ID3NoHeaderError)
from mutagen.id3._frames import (
    TIT2,  # title
    TPE1,  # artist
    TALB,  # album
)
from mutagen.mp3 import MP3
from mutagen.id3 import (
    ID3)
import youtube_dl
from email.message import EmailMessage
from dataclasses import dataclass
import os
import datetime
import shutil
import logging
import json
import argparse


# example url:
#   https://soundcloud.com/indiancountrytoday/ict-newscast-for-june-26-2023
timestamp = datetime.datetime.now()
todaysdate = timestamp.strftime("%B-%#d-%Y") # the %#d is to get the date without a leading 0

# if todays date is a weekend... exit
dayoftheweek = datetime.datetime.today().weekday()


parser = argparse.ArgumentParser()

parser.add_argument("-d", "--date", 
                    type=str, 
                    default=todaysdate, 
                    help="format MONTH-DD-YYYY e.g. June-23-2023, in case you want to download a different date than today, the DD should not have a leading 0"
                )
args = parser.parse_args()
downloaded_ep_date = args.date

# set up for logging:
home_dir = os.path.expanduser('~')
music_dir = os.path.join(home_dir, 'Music', '- Indian Country Today')
logging.basicConfig(filename=os.path.join(
    music_dir, 'ict_newscast.log'), level=logging.INFO)


@dataclass
class Config:
    source_email: str
    destination_emails: list[str]
    email_password: str
    port: int


def send_email(content: str, subject: str) -> None:

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = config.source_email
    msg['To'] = config.destination_emails
    msg.set_content(content)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", config.port, context=context) as server:
        server.login(config.source_email, config.email_password)
        server.send_message(msg)


if dayoftheweek >= 5:
    exit(0)

logging.info(f'Started {downloaded_ep_date} at {timestamp}')
config = {}
config_path = f'ict_config.json'
with open(config_path, 'r') as config_fd:
    try:
        config = Config(**json.load(config_fd))

    except Exception as err:
        logging.info(
            f'check config file - something is broken.{Exception=} {err=}. Exiting...')
        exit()


# check to see if the file has already been put in for today. If so, exit
nextkast_dir = os.path.join('C:', os.sep, 'NextKast', 'Music', 'ICT Full News')
old_ep_files = [f for f in os.listdir(
    nextkast_dir) if f.endswith('.mp3')]

logging.info(f'Old files: {old_ep_files}')

for show in old_ep_files:
    showpath = os.path.join(nextkast_dir, show)
    # ctime = os.path.getctime(showpath)
    mtime = os.path.getmtime(showpath)
    readable_mtime = datetime.datetime.fromtimestamp(
        mtime).strftime("%B-%d-%Y")
    if readable_mtime == downloaded_ep_date:
        logging.info(
            f'Script exiting, based on the file: {showpath} with the modified time {readable_mtime}')
        exit(0)


ict_soundcloud_url = 'https://soundcloud.com/indiancountrytoday/'
episode_url = ict_soundcloud_url + 'ict-newscast-for-' + downloaded_ep_date

logging.info(f'Attempting to download from URL: {episode_url}')
# example URL to check
# episode_url = 'https://soundcloud.com/indiancountrytoday/ict-newscast-for-june-27-2023'
output_name = os.path.join(
    music_dir, f'Indian Country Today - Full News.mp3')

# ignore this
# newtag_outputname = os.path.join(
#     music_dir, f'Indian Country Today - Full News id3v2.3 attmpt.mp3')

# shutil.copy2(output_name, newtag_outputname)
# output_name = newtag_outputname


try:
    os.remove(output_name)
except:
    ...

ydl_opts = {
    'outtmpl': output_name
    # 'quiet': True
}

try:
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([episode_url])
# except youtube_dl.utils.DownloadError:
except Exception as e:
    if timestamp.hour >= 15:
        send_email(f'Tried to download from: {episode_url}',
                   f'ICT {downloaded_ep_date} failed to be entered - check if show was uploaded.')
    logging.info(f'ytdl failed, exiting due to error: {e}')
    exit(1)

logging.info(f'Success, file saved to: {output_name}')


logging.info(f'Adding ID3 tags to {output_name}')
song_name = 'Indian Country Today'


try:
    id3 = ID3(output_name)
except ID3NoHeaderError:
    id3 = ID3()
except Exception as err:
    logging.info(f'ERROR: {err}')
    send_email(
        f'could not add ID3 tag to the file downloaded for ICT {err}', 'error writing metadata to ict, please enter it manually')
    exit()

id3.add(TIT2(encoding=3, text=song_name))
id3.add(TPE1(encoding=3, text=song_name))
id3.add(TALB(encoding=3, text=song_name))
id3.save(output_name, v2_version=3)


try: 
    mp3_tag = MP3(output_name)
    song_length_secs = mp3_tag.info.length
    logging.info(f'file is length: {mp3_tag.info.length}')
    if song_length_secs < (60 * 25):
        send_email(f'{song_length_secs=}\n{episode_url=}', 'ICT Error: Todays episode was found to be shorter than 25 minutes. Please manually review.')
except:
    pass


logging.info(f'ID3 tags added to {output_name}')

logging.info('removing old files')
nextkast_dir = os.path.join('C:', os.sep, 'NextKast', 'Music', 'ICT Full News')
old_ep_files = [f for f in os.listdir(
    nextkast_dir) if f.endswith('.mp3')]

# delete the old show files and copy the new ones
for f in old_ep_files:
    os.remove(os.path.join(nextkast_dir, f))

logging.info('old files removed')
logging.info('copying new file')
# move new episode files to the nextkast folder
dst = os.path.join(nextkast_dir, os.path.basename(output_name))
shutil.copy2(output_name, dst)

# get the current time in local time zone
logging.info('script success, sending email')
send_email(f'episode link {episode_url}\n', f'ICT {todaysdate} has been entered courtesy of the ICT Newscast Bot')
