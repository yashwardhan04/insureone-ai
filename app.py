import numpy as np
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mail import Mail, Message
import pandas as pd
from difflib import get_close_matches
import joblib
from pymongo import MongoClient
import os
from datetime import datetime
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId  # NEW: Import ObjectId for MongoDB _id handling
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

bcrypt = Bcrypt(app)

# --- MongoDB Configuration ---
MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = "insureone_db"
COLLECTION_NAME_ESTIMATES = "estimates"
COLLECTION_NAME_USERS = "users"

client = None
db = None
users_collection = None
estimates_collection = None

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    estimates_collection = db[COLLECTION_NAME_ESTIMATES]
    users_collection = db[COLLECTION_NAME_USERS]
    client.admin.command('ping')
    print("MongoDB connection successful (SSL verification bypassed for development)! REMEMBER TO REMOVE tlsAllowInvalidCertificates=True IN PRODUCTION.")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

# Load FAQ data
faq_df = pd.read_csv('faq/faq.csv')
questions = faq_df['Question'].tolist()
answers = faq_df['Answer'].tolist()

# Load trained model
model = joblib.load('model/insurance_model.pkl')

# Mail Configurations
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mail = Mail(app)

# --- Routes ---

@app.route('/')
def home():
    user_logged_in = 'user_id' in session
    username = session.get('username') if user_logged_in else None
    return render_template('index.html', user_logged_in=user_logged_in, username=username)

@app.route('/contact')
def contact():
    user_logged_in = 'user_id' in session
    username = session.get('username') if user_logged_in else None
    return render_template('contact.html', user_logged_in=user_logged_in, username=username)

@app.route('/about')
def about():
    user_logged_in = 'user_id' in session
    username = session.get('username') if user_logged_in else None
    return render_template('about.html', user_logged_in=user_logged_in, username=username)

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    name = data['name']
    email = data['email']
    message_body = data['message']

    msg = Message(subject=f"New Contact from {name}",
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[app.config['MAIL_USERNAME']],
                  body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message_body}")
    
    mail.send(msg)
    return jsonify({"success": True})

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_question = data.get('question', '').strip().lower()

    if not user_question:
        return jsonify({'answer': "Please ask a valid question."})

    matches = get_close_matches(user_question, questions, n=1, cutoff=0.5)
    if matches:
        index = questions.index(matches[0])
        return jsonify({'answer': answers[index]})
    else:
        return jsonify({'answer': "Sorry, I couldn't find an answer to that question."})

@app.route('/estimate', methods=['POST'])
def estimate():
    try:
        data = request.get_json()

        required_fields = ['age', 'gender', 'smoker', 'lifestyle', 'income', 'conditions']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        try:
            age = int(data['age'])
            if not (18 <= age <= 100):
                return jsonify({"error": "Age must be an integer between 18 and 100."}), 400
        except ValueError:
            return jsonify({"error": "Age must be a valid integer."}), 400

        gender = data['gender']
        if gender not in ["Male", "Female"]:
            return jsonify({"error": "Gender must be 'Male' or 'Female'."}), 400

        smoker = data['smoker']
        if smoker not in ["Yes", "No"]:
            return jsonify({"error": "Smoker status must be 'Yes' or 'No'."}), 400

        lifestyle = data['lifestyle']
        valid_lifestyles = ["Active", "Moderate", "Sedentary"]
        if lifestyle not in valid_lifestyles:
            return jsonify({"error": f"Lifestyle must be one of: {', '.join(valid_lifestyles)}."}), 400

        income_from_frontend = data['income']
        valid_incomes = ["< 25000", "25000-50000", "50000-100000", "> 100000"]
        if income_from_frontend not in valid_incomes:
            return jsonify({"error": f"Income must be one of: {', '.join(valid_incomes)}."}), 400
        income_bracket_value = income_from_frontend

        conditions_from_frontend = data['conditions']
        if not isinstance(conditions_from_frontend, list):
            return jsonify({"error": "Conditions must be a list."}), 400
        
        valid_conditions = ["Diabetes", "Hypertension", "Heart Disease", "None"]
        for cond in conditions_from_frontend:
            if cond not in valid_conditions:
                return jsonify({"error": f"Invalid condition: '{cond}'. Valid conditions are: {', '.join(valid_conditions)}."}), 400
        
        pre_existing_condition_value = 'Yes' if conditions_from_frontend and 'None' not in conditions_from_frontend else 'No'

        base_input_df = pd.DataFrame([[age, gender, smoker, lifestyle, income_bracket_value, pre_existing_condition_value]],
                                     columns=['Age', 'Gender', 'Smoker', 'Lifestyle', 'IncomeBracket', 'PreExistingCondition']) 
        
        current_prediction = model.predict(base_input_df)[0]
        estimated_amount = max(0, round(current_prediction, 2))

        try:
            estimate_data = {
                "age": age,
                "gender": gender,
                "smoker": smoker,
                "lifestyle": lifestyle,
                "income_bracket": income_bracket_value,
                "pre_existing_conditions": conditions_from_frontend,
                "pre_existing_condition_flag": pre_existing_condition_value,
                "estimated_amount": estimated_amount,
                "timestamp": datetime.now()
            }
            if 'user_id' in session and estimates_collection is not None:
                estimate_data['user_id'] = ObjectId(session['user_id']) 
                estimates_collection.insert_one(estimate_data)
                print(f"Estimate for user {session['user_id']} saved to MongoDB successfully!")
            elif estimates_collection is not None:
                estimates_collection.insert_one(estimate_data)
                print(f"Estimate for age {age} saved to MongoDB successfully (no user_id)!")
            else:
                print("MongoDB estimates collection not initialized, skipping database save.")
        except Exception as mongo_e:
            print(f"Error saving estimate to MongoDB: {mongo_e}")

        what_if_scenarios = []

        def calculate_hypothetical_estimate(temp_df):
            return max(0, round(model.predict(temp_df)[0], 2))

        if smoker == "Yes":
            temp_df = base_input_df.copy()
            temp_df['Smoker'] = "No"
            hypo_estimate = calculate_hypothetical_estimate(temp_df)
            if hypo_estimate > estimated_amount:
                what_if_scenarios.append({
                    "scenario": "If you stop smoking",
                    "estimate": hypo_estimate,
                    "difference": round(hypo_estimate - estimated_amount, 2)
                })

        if lifestyle != "Active":
            temp_df = base_input_df.copy()
            temp_df['Lifestyle'] = "Active"
            hypo_estimate = calculate_hypothetical_estimate(temp_df)
            if hypo_estimate > estimated_amount:
                what_if_scenarios.append({
                    "scenario": "If you adopt an Active lifestyle",
                    "estimate": hypo_estimate,
                    "difference": round(hypo_estimate - estimated_amount, 2)
                })

        income_map_for_prediction = {
            "< 25000": 0, "25000-50000": 1, "50000-100000": 2, "> 100000": 3
        }
        current_income_idx = income_map_for_prediction[income_bracket_value]
        next_income_bracket_value = None
        for k, v in income_map_for_prediction.items():
            if v == current_income_idx + 1:
                next_income_bracket_value = k
                break

        if next_income_bracket_value and current_income_idx < len(income_map_for_prediction) - 1:
            temp_df = base_input_df.copy()
            temp_df['IncomeBracket'] = next_income_bracket_value
            hypo_estimate = calculate_hypothetical_estimate(temp_df)
            if hypo_estimate > estimated_amount:
                what_if_scenarios.append({
                    "scenario": f"If you move to a higher income bracket (e.g., {next_income_bracket_value})",
                    "estimate": hypo_estimate,
                    "difference": round(hypo_estimate - estimated_amount, 2)
                })

        return jsonify({'estimate': estimated_amount, 'what_if_scenarios': what_if_scenarios})

    except Exception as e:
        print(f"Error during estimate calculation or processing: {e}")
        return jsonify({"error": "An internal server error occurred. Please try again."}), 500

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if users_collection is not None and users_collection.find_one({"username": username}):
        return jsonify({"error": "Username already exists."}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user_data = {
        "username": username,
        "password": hashed_password,
        "created_at": datetime.now()
    }

    if users_collection is not None:
        users_collection.insert_one(user_data)
    else:
        return jsonify({"error": "User registration failed due to database error."}), 500

    return jsonify({"message": "User registered successfully!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if users_collection is None:
        return jsonify({"error": "Login failed due to database error."}), 500

    user = users_collection.find_one({"username": username})

    if user and bcrypt.check_password_hash(user['password'], password):
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        return jsonify({"message": "Login successful!", "username": user['username']}), 200
    else:
        return jsonify({"error": "Invalid username or password."}), 401

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({"message": "Logged out successfully!"}), 200

@app.route('/my_estimates', methods=['GET'])
def my_estimates():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized. Please log in.'}), 401

    if estimates_collection is None:
        return jsonify({"error": "Estimates database is unavailable."}), 500

    user_id_str = session['user_id']
    
    try:
        user_estimates = list(estimates_collection.find({'user_id': ObjectId(user_id_str)}).sort('timestamp', -1))
        for estimate in user_estimates:
            estimate['_id'] = str(estimate['_id'])
            if 'user_id' in estimate:
                estimate['user_id'] = str(estimate['user_id'])
            if 'timestamp' in estimate and isinstance(estimate['timestamp'], datetime):
                estimate['timestamp'] = estimate['timestamp'].isoformat()
            
        return jsonify({'estimates': user_estimates}), 200
    except Exception as e:
        print(f"Error fetching user estimates: {e}")
        return jsonify({"error": "An error occurred while fetching your estimates."}), 500

if __name__ == '__main__':
    app.run(debug=True)
