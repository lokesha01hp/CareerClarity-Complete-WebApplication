from flask import Flask, render_template, request
import joblib
import numpy as np

app = Flask(__name__)

# Load the model and vectorizer
model = joblib.load('career_prediction_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    traits = [
        request.form.get('trait1'),
        request.form.get('trait2'),
        request.form.get('trait3'),
        request.form.get('trait4'),
        request.form.get('trait5'),
    ]
    
    answers_text = ' '.join(traits)
    
    vectorized_answers = vectorizer.transform([answers_text])
    
    # Predict the career
    predicted_career = model.predict(vectorized_answers)[0]
    
    return render_template('result.html', predicted_career=predicted_career)

if __name__ == '__main__':
    app.run(debug=True, port = 8082)
