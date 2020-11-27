# import the Flask class from the flask module
from argparse import ArgumentParser
from scipy.spatial import distance
from flask import Flask, render_template, request, send_from_directory, make_response
import os
import db_manager
import json
from db_manager import DB
import config
import pickle
import re
import base64
import string
import nltk
from bs4 import BeautifulSoup

current_dir = os.curdir


# create the application object
app = Flask(__name__)
app.config['DATABASE_PATH'] = os.path.join(os.curdir, 'db/db.sqlite')

isReTrained = False
global kmeans
global vectorizer
stopword = nltk.corpus.stopwords.words('english')


def decode(text):
    text = base64.urlsafe_b64decode(text).decode('utf-8')
    return text

def get_vector(text, vectorizer):
    custom_data = [text]
    custom_matrix = vectorizer.transform(custom_data)
    return custom_matrix


def infer(text, kmeans, vectorizer):
    custom_data = [text]
    custom_matrix = vectorizer.transform(custom_data)
    group = kmeans.predict(custom_matrix)
    return group, custom_matrix


def clean_text(text):
    text = BeautifulSoup(str(text), "lxml").text
    text_nopunct = "".join([char for char in text if char not in string.punctuation])
    tokens = re.split('\W+', text_nopunct)
    tokens = [word.lower() for word in tokens]
    text = [word for word in tokens if word not in stopword]
    text = [word for word in text if len(word) > 1]
    return text

kmeans = pickle.load(open("kmeans.pkl", "rb"))
vectorizer = pickle.load(open('tfidf.pickle', "rb"))

data_dir = os.path.join(os.curdir, 'db')
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

manager = DB(app.config['DATABASE_PATH'])

if not os.path.exists(app.config['DATABASE_PATH']):
    manager.create_table(db_manager.CREATE_TABLE_STATEMENT)
    print("REQUIRED TABLES CREATED..")

a = 1
if a == 0:
    resultDf = manager.get_all_emails()
    for index, row in resultDf.iterrows():
        # tokenized = clean_text(row['content'])
        payload = {}
        payload['id'] = row['email_id']
        cluster, _ = infer(row['subject'], kmeans, vectorizer)
        payload['cluster'] = cluster[0]
        manager.update_email(payload)
        print(payload)


def build_argparser():
    parser = ArgumentParser()
    parser.add_argument("-q", "--query", required=True, type=str,
                        help="Please provide any sentece to search related mails")
    parser.add_argument("-n", "--number", required=True, type=int, default=5,
                        help="Please provide number of emails to show")

    return parser


def main(args):
    group, query_vec = infer(args.query, kmeans, vectorizer)

    resultDf = manager.get_emails(group[0])

    data = []
    euclidean_score = []
    for index, row in resultDf.iterrows():
        email_data = dict(row)
        body = decode(row['content'])
        score = distance.euclidean(query_vec.toarray(), get_vector(body, vectorizer).toarray())

        if score > 0:
            email_data['euclidean'] = score
            data.append(email_data)
            euclidean_score.append(score)

    data = sorted(data, key=lambda k: k['euclidean'], reverse=False)
    return data


if __name__ == '__main__':
    # arg = '-q "Reminder - 1 day left to make your EMI payment..."'.split(' ')
    # args = build_argparser().parse_args(arg)
    args = build_argparser().parse_args()

    data = main(args)
    for i in range(args.number):
        print("{} - {} - {}".format(i, str(data[i]['subject']), str(data[i]['euclidean'])))
        print('============')
