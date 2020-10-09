from db_manager import DB
import db_manager
import config
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import string
import re
import pickle

manager = DB(config.DATABASE_PATH)

if not os.path.exists(config.DATABASE_PATH):
    manager.create_table(db_manager.CREATE_TABLE_STATEMENT)
    print("REQUIRED TABLES CREATED..")

from ml import email_scrap
# email_scrap.scrap(manager)
data, email_ids = email_scrap.get_data(manager)


# nltk.download()
nltk.download('stopwords')
##Remove stopwords (does not contribute much in sentence)
stopword = nltk.corpus.stopwords.words('english')

def clean_text(text):
    text_nopunct = "".join([char for char in text if char not in string.punctuation])
    tokens = re.split('\W+', text_nopunct)
    text = [word for word in tokens if word not in stopword]
    return text

vectorizer = TfidfVectorizer(stop_words='english', analyzer=clean_text)

data_matrix=vectorizer.fit_transform(data)
print("\n Feature names Identified :\n")
print(vectorizer.get_feature_names())

#Use KMeans clustering from scikit-learn
from sklearn.cluster import KMeans
#Split data into 3 clusters
kmeans = KMeans(n_clusters=6).fit(data_matrix)

#get Cluster labels.
clusters=kmeans.labels_

pickle.dump(kmeans, open("kmeans.pkl", "wb"))
pickle.dump(vectorizer, open("tfidf.pickle", "wb"))
print("Model Saved")

#Print cluster label and Courses under each cluster
for group in set(clusters):
    print("\nGroup : ",group, "\n-------------------")

    counter = 0
    for i in range(len(data)):
        if ( clusters[i] == group):
            print(clean_text(data[i]))
            payload = {}
            payload['id'] = email_ids[i]
            payload['cluster'] = group
            manager.update_email(payload)
        #     counter = counter + 1
        # if counter > 5:
        #     break


