import joblib


MODEL_PATH = r"C:\\Users\\Home\\Documents\\Projects\\TeamUps\\teamups\\main\\learning_model\\model.pkl"
model, vectorizer, encoder = joblib.load(MODEL_PATH)


def predict_user_type(skill: str) -> str:
    test_vec = vectorizer.transform([skill.lower()])
    prediction = model.predict(test_vec)
    return encoder.inverse_transform(prediction)[0]

