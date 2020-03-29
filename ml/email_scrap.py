import imaplib
import os
import email
import re

EMAIL_DATASET_PATH = os.path.join(os.getcwd(), 'emails')
if not os.path.exists(EMAIL_DATASET_PATH):
    os.mkdir(EMAIL_DATASET_PATH)


def search_content(mail, data, manager):
    # search and return uids instead
    i = len(data[0].split()) # data[0] is a space separate string
    for x in range(i):
        latest_email_uid = data[0].split()[x] # unique ids wrt label selected
        result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        # fetch the email body (RFC822) for the given ID
        raw_email = email_data[0][1]

        #continue inside the same for loop as above
        raw_email_string = raw_email.decode('utf-8')
        payload = {}
        payload['email_id'] = x
        # converts byte literal to string removing b''
        email_message = email.message_from_string(raw_email_string)
        subject = email_message['Subject']
        payload['subject'] = subject

        # this will loop through all the available multiparts in mail
        for part in email_message.walk():
            if part.get_content_type() == "text/plain": # ignore attachments/html
                body = part.get_payload(decode=True)
                try:
                    content = body.decode('utf-8')
                    content = content.replace("'", "")
                    payload['content'] = content
                    formatted = content.replace('\r', '').replace('\n', ' ')
                    formatted = re.sub('[^ ]+\.[^ ]+','',formatted)
                    formatted = formatted + " " + subject
                    save_string = str("email_" + str(x) + ".eml")
                    with open(os.path.join(EMAIL_DATASET_PATH, save_string), 'a') as file:
                        file.write(formatted)
                        print(str(x) + ' email found and saved')
                        payload['training_content'] = formatted
                        manager.insert_email(payload)
                except Exception as err:
                    print(err)

            else:
                continue

        # if x == 9000:
        # break

def scrap(manager):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    # imaplib module implements connection based on IMAPv4 protocol
    mail.login("asfinavayani1@gmail.com", "V@yani1995")
    # >> ('OK', [username at gmail.com Vineet authenticated (Success)'])

    mail.list() # Lists all labels in GMail
    mail.select('inbox') # Connected to inbox.

    result, data = mail.uid('search', None, "ALL")
    # search_content(mail, data, manager)


def get_data(manager):
    df = manager.get_emails()
    data = []
    email_ids = []
    for index, row in df.iterrows():
        line = row['training_content']
        line = line.replace(r'\r', "")
        line = line.replace(r'\n', " ")
        line = line.replace('\\xe2\\x80\\x99', "'")
        line = line.rstrip()
        line = line.lstrip()
        data.append(line)
        email_ids.append(row['email_id'])
    return data, email_ids
