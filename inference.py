import pickle
import re
import string
import nltk
stopword = nltk.corpus.stopwords.words('english')

def clean_text(text):
    text_nopunct = "".join([char for char in text if char not in string.punctuation])
    tokens = re.split('\W+', text_nopunct)
    text = [word for word in tokens if word not in stopword]
    return text

kmeans = pickle.load(open("kmeans.pkl", "rb"))
vectorizer = pickle.load(open('tfidf.pickle', "rb"))

custom_data = ["Read a new story from Wattpad"]

custom_matrix=vectorizer.transform(custom_data)
group = kmeans.predict(custom_matrix)

print(group)