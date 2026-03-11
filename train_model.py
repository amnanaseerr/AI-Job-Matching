import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder

# load dataset
data = pd.read_csv("dataset/resumes.csv")

print("Columns in dataset:", data.columns)

# try to automatically detect columns
text_col = None
label_col = None

for col in data.columns:
    if "resume" in col.lower() or "text" in col.lower():
        text_col = col
    if "category" in col.lower() or "label" in col.lower():
        label_col = col

if text_col is None:
    text_col = data.columns[0]

if label_col is None:
    label_col = data.columns[1]

print("Using text column:", text_col)
print("Using label column:", label_col)

X = data[text_col].astype(str)
y = data[label_col].astype(str)

# encode labels
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# vectorize text
vectorizer = TfidfVectorizer(stop_words="english")
X_vec = vectorizer.fit_transform(X)

# train model
model = MultinomialNB()
model.fit(X_vec, y_encoded)

# save files
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
pickle.dump(encoder, open("encoder.pkl", "wb"))

print("Training complete")
print("Files created: model.pkl, vectorizer.pkl, encoder.pkl")