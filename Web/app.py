from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import requests
import script

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index-main.html')
    
@app.route('/pred')
def preds():
    return render_template("index.html")

@app.route('/quiz')
def quiz():
    result = request.args.get('result', None)
    return render_template("quiz.html", result=result)

@app.route('/tech')
def tech():
    return render_template("tech.html")

@app.route('/schedule')
def schedule():

    return render_template("schedule.html")

@app.route("/predict")
def predict():
    api_url = "http://127.0.0.1:5500/getStressPredictionOutput"

    try:
        response = requests.get(api_url)
        result = response.json()["prediction_file"]
        if response.status_code == 200:
            return redirect(url_for('quiz', result=result))
        else:
            return f"Error: {response.status_code}", response.status_code
    except requests.RequestException as e:
        return f"Request failed: {e}", 500

@app.route("/send", methods=["GET", "POST"])
def send():
    try:
        data = request.get_json()  # Receive JSON data from JavaScript
        email = data.get("email")
        message = data.get("message")
        datetime = data.get("datetime")
        frequency = data.get("frequency")

        print("Received Data from JavaScript:", data)  # Debugging

        if not email:
            return jsonify({"error": "No email provided"}), 400

        # Call your Python function
        script.send_email(email)  

        return jsonify({"status": "success", "message": "Email sent!"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)