import joblib
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
model, vectorizer, encoder = joblib.load(MODEL_PATH)


def predict_user_type(skill: str) -> str:
    test_vec = vectorizer.transform([skill.lower()])
    prediction = model.predict(test_vec)
    return encoder.inverse_transform(prediction)[0]

