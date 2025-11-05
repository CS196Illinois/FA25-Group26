from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This allows your React app to make requests

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    # Process with your ML model
    result = your_ml_model.predict(data['input'])
    return jsonify({'prediction': result})

if __name__ == '__main__':
    app.run(debug=True, port=5000)