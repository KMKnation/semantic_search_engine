from __future__ import print_function
import pickle
import os.path
import base64
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import db_manager
from db_manager import DB


def decode(text):
    text = base64.urlsafe_b64decode(text).decode('utf-8')
    return text

def encode(text):
    text = base64.urlsafe_b64encode(text.encode('utf-8'))
    return text.decode('utf-8')


counter = 1

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def getLabels(service, userId='me'):
    results = service.users().labels().list(userId=userId).execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])
    return

def getThreads(manager, service, userId='me', pageToken=None):
    global counter
    result = service.users().threads().list(userId=userId).execute()

    if 'nextPageToken' in result:
        threads, nextPageToken, resultSizeEstimate = result['threads'], result['nextPageToken'], result[
            'resultSizeEstimate']
    else:
        threads = result['threads']
        nextPageToken = None

    for output in threads:
        tdata = service.users().messages().get(userId=userId, id=output['id']).execute()

        try:
            if tdata['payload']['body']['size'] > 0:
                data = tdata['payload']['body']['data']
                # content = data.encode('utf-8')
                print(tdata['snippet'])
                payload = {
                    'email_id': counter,
                    'subject': tdata['snippet'],
                    'content': data

                }
                manager.insert_email(payload)
                print('INSERT SUCCESS !! {}'.format(counter))
            else:
                print(tdata['snippet'])
                payload = {
                    'email_id': counter,
                    'subject': tdata['snippet'],
                    'content': encode(tdata['snippet'])
                }
                manager.insert_email(payload)
                print('INSERT SUCCESS !! {}'.format(counter))


            counter = counter + 1
        except Exception as err:
            print(err)

    if nextPageToken != None:
        getThreads(manager, service, userId, nextPageToken)
        print('Querying next page = {}'.format(nextPageToken))

    return


def getMessages(manager, service, userId='me', pageToken=None):
    result = service.users().messages().list(userId=userId, pageToken=pageToken, maxResults=50).execute()
    if 'nextPageToken' in result:
        messages, nextPageToken, resultSizeEstimate = result['messages'], result['nextPageToken'], result[
            'resultSizeEstimate']
    else:
        messages = result['messages']
        nextPageToken = None

    for output in messages:
        tdata = service.users().messages().get(userId=userId, id=output['id']).execute()

        try:
            if tdata['payload']['body']['size'] > 0:
                data = tdata['payload']['body']['data']
                # content = data.encode('utf-8')
                content = decode(data)
                print(tdata['snippet'])
                payload = {
                    'email_id': output['id'],
                    'subject': tdata['snippet'],
                    'content': data

                }
                manager.insert_email(payload)
                print('INSERT SUCCESS !!')
            else:
                print(tdata['snippet'])
                payload = {
                    'email_id': output['id'],
                    'subject': tdata['snippet'],
                    'content': encode(tdata['snippet'])
                }
                manager.insert_email(payload)
                print('INSERT SUCCESS !! {}'.format(counter))

        except Exception as err:
            print(err)

    if nextPageToken != None :
        getMessages(manager, service, userId, nextPageToken)
        print('Querying next page = {}'.format(nextPageToken))

    return


def main(manager):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    getMessages(manager, service)

    df = manager.get_all_emails()
    df.to_csv('data.csv')


if __name__ == '__main__':

    data_dir = os.path.join(os.curdir, 'db')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    DATABASE_PATH = os.path.join(os.curdir, 'db/db.sqlite')
    manager = DB(DATABASE_PATH)

    if not os.path.exists(DATABASE_PATH):
        manager.create_table(db_manager.CREATE_TABLE_STATEMENT)
        print("REQUIRED TABLES CREATED..")

    main(manager)

