import sqlite3
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
import joblib


connector = sqlite3.connect(r"C:\\Users\\Home\Documents\\Projects\\TeamUps\\teamups\\db.sqlite3")
cursor = connector.cursor()


cursor.execute("SELECT id, skills, score, score_count, type FROM main_user")
rows = cursor.fetchall()


# Data Preprocessing
skills = [row[1].lower() for row in rows]
characters = [row[4].lower() for row in rows]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(skills)

encoder = LabelEncoder()
y = encoder.fit_transform(characters)

model = KNeighborsClassifier(n_neighbors=1)
model.fit(X, y)


joblib.dump((model, vectorizer, encoder), "model.pkl")

