import pickle
import numpy as np

# Function to load the model, vectorizer, and rules
def load_combined_model(filename="/home/cmoai/modell/combined_department_predictor.pkl"):
    with open(filename, 'rb') as file:
        model, tfidf_vectorizer, rules_map = pickle.load(file)
    return model, tfidf_vectorizer, rules_map

# Function to make predictions based on the text
def predict_department(text, model, tfidf_vectorizer, rules_map):
    # Rule-based prediction
    matched_departments = []
    text = text.lower()
    for dept, keywords in rules_map.items():
        if any(keyword in text for keyword in keywords):
            matched_departments.append(dept)
    
    # Fallback to machine learning model if no rule-based prediction
    if not matched_departments:
        text_tfidf = tfidf_vectorizer.transform([text])
        model_predictions_proba = model.predict_proba(text_tfidf)[0]
        top_3_model_predictions = np.argsort(model_predictions_proba)[-3:][::-1]
        matched_departments = [str(department) for department in top_3_model_predictions]

    # Return top 3 unique departments
    return list(sorted(set(matched_departments), key=lambda x: matched_departments.index(x)))[:3]
