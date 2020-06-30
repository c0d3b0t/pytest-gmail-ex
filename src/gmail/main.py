from __future__ import print_function
import pickle
import os.path
from urlextract import URLExtract
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import email
from apiclient import errors
from email.parser import BytesParser, Parser
from email.policy import default
from bs4 import BeautifulSoup as BSHTML
from os import environ as env

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# URLs
links = []
images = []

def get_results():
    credentials = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'src/gmail/credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    service = build('gmail', 'v1', credentials=credentials, cache_discovery=False)

    service_results = service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
    messages = service_results.get('messages', [])

    if not messages:
        print('No messages found.')
        exit()
    else:
        for msg in messages:
            parse_message(service, 'me', msg['id'])

    results = {
        'links': filter_links(),
        'images': images
    }

    return results


def parse_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_str)
        headers = Parser(policy=default).parsestr(mime_msg.as_string())

        if verify_from(headers):
            if mime_msg.is_multipart():
                for payload in mime_msg.get_payload():
                    extract_links(payload.get_payload())
                    extract_images(payload.get_payload())
            else:
                extract_links(mime_msg.get_payload())
                extract_images(mime_msg.get_payload())

        return mime_msg

    except errors.HttpError:
        print(errors.HttpError)


def extract_links(message):
    extractor = URLExtract()
    urls = extractor.find_urls(message)

    for url in urls:
        links.append(url)


def extract_images(message):
    soup = BSHTML(message, 'html.parser')
    imgs = soup.findAll('img')

    if len(imgs) > 0:
        for img in imgs:
            images.append(img['src'])


def verify_from( headers ):
    valid_sender_hosts = ["example1.com", "example2.com"]
    hosts = [item.strip() for item in valid_sender_hosts]
    sender = headers['From']
    host = sender.split('<')[1].replace('>', '').split('@')[1]
    return host in hosts


def filter_links():
    # returning unique list of links
    return list(dict.fromkeys(links))


if __name__ == '__main__':
    get_results()