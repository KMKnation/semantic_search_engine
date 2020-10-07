
def infer(text, kmeans, vectorizer, lda):
    custom_data = [text]
    custom_matrix=vectorizer.transform(custom_data)
    custom_matrix = lda.transform(custom_matrix)
    group = kmeans.predict(custom_matrix)
    return group, custom_matrix


def get_vector(text, vectorizer, lda):
    custom_data = [text]
    custom_matrix=vectorizer.transform(custom_data)
    custom_matrix = lda.transform(custom_matrix)
    return custom_matrix



# print(infer("Hey your "))
