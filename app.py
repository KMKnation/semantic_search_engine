# import the Flask class from the flask module
from flask import Flask, render_template, request, send_from_directory, make_response
import os
import db_manager
import json
from db_manager import DB
import config
import pickle
from inference import infer, get_vector
import re
import string
import nltk
from scipy.spatial import distance

current_dir = os.curdir
# create the application object
app = Flask(__name__)
app.config['DATABASE_PATH'] = os.path.join(os.curdir, 'db/db.sqlite')


global kmeans
global vectorizer
global lda
stopword = nltk.corpus.stopwords.words('english')


def clean_text(text):
    text = text.replace('[image: Google]', '')
    text_nopunct = "".join([char for char in text if char not in string.punctuation])
    tokens = re.split('\W+', text_nopunct)
    tokens = [word.lower() for word in tokens]
    text = [word for word in tokens if word not in stopword]
    text = [word for word in text if len(word) > 1]

    return text


kmeans = pickle.load(open("kmeans.pkl", "rb"))
vectorizer = pickle.load(open('tfidf.pickle', "rb"))
lda = pickle.load(open('lda.pickle', "rb"))

def init():
    global manager

    data_dir = os.path.join(os.curdir, 'db')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    manager = DB(app.config['DATABASE_PATH'])

    if not os.path.exists(app.config['DATABASE_PATH']):
        manager.create_table(db_manager.CREATE_TABLE_STATEMENT)
        print("REQUIRED TABLES CREATED..")


    print("VECTORIZER LOADED")




# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/test.db'

@app.route('/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


# use decorators to link the function to a url
@app.route('/')
def home():
    # return "Hello, World!"  # return a string
    return render_template('search.html')


'''
API DEVELOPMENT
'''


def sort_list(list1, accordingto):
    zipped_pairs = zip(accordingto, list1)
    z = [x for _, x in sorted(zipped_pairs)]
    return z


@app.route('/get_relevant', methods=['POST'])
def get_invite():
    result = {"error": 1}
    try:

        query = json.loads(request.data.decode('utf-8'))['query']
        group, query_vec = infer(query, kmeans, vectorizer, lda)


        resultDf = manager.get_emails(group[0])

        data = []
        euclidean_score = []
        for index, row in resultDf.iterrows():
            email_data = dict(row)

            score = distance.euclidean(query_vec, get_vector(row['content'], vectorizer, lda))

            if score < 0.5:
                email_data['euclidean'] = score
                data.append(email_data)
                euclidean_score.append(score)

        data = sorted(data, key=lambda k: k['euclidean'], reverse=False)

        result['data'] = data
        result["error"] = 0

        return make_response(json.dumps(result), 200)
    except Exception as err:
        result["message"] = str(err)
        return make_response(json.dumps(result), 404)



# start the server with the 'run()' method
if __name__ == '__main__':

    init()

    app.run(debug=True)
