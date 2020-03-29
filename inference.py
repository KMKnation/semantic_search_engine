
def infer(text, kmeans, vectorizer):
    custom_data = [text]
    custom_matrix=vectorizer.transform(custom_data)
    group = kmeans.predict(custom_matrix)
    return group

# print(infer("Hey your "))
