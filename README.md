# 🛡️ InsureOne AI - AI-Powered Insurance Estimator

Welcome to **InsureOne AI**, a full-stack web application that helps users estimate their ideal health insurance coverage using machine learning. Designed with simplicity, speed, and user privacy in mind, it also features an intelligent FAQ chatbot and user account tracking.

---

## 🚀 Live Demo  
[👉 Try It Here](https://your-app-name.onrender.com)


---

## 🧠 Features

✅ **AI-Powered Insurance Estimation**  
Get a personalized estimate for your insurance coverage based on age, income, lifestyle, and health conditions.

✅ **User Authentication**  
Secure registration and login system using Flask sessions and bcrypt.

✅ **“What-If” Scenarios**  
See how changing your habits (e.g., quitting smoking) could improve your insurance estimate.

✅ **FAQ Chatbot**  
A built-in chatbot answers common insurance-related questions using fuzzy matching on a dataset.

✅ **Email Contact Form**  
Users can send messages directly to the admin’s email via a contact form.

✅ **MongoDB Integration**  
All estimates and users are stored securely in MongoDB Atlas.

✅ **Responsive UI**  
Built using Bootstrap 5 for a clean, responsive user experience across devices.

---

## 🏗️ Tech Stack

| Category         | Tools Used                        |
|------------------|------------------------------------|
| Backend          | Flask, Python                     |
| Frontend         | HTML5, CSS3, Bootstrap 5          |
| Machine Learning | scikit-learn, joblib              |
| Database         | MongoDB Atlas                     |
| Authentication   | Flask-Bcrypt, Flask Sessions      |
| Email            | Flask-Mail                        |
| Environment      | python-dotenv                     |

---

## 🧪 Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yashwardhan04/insureone-ai.git
cd insureone-ai
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your_secret_key
MAIL_USERNAME=your_gmail_address
MAIL_PASSWORD=your_app_password
MONGO_URI=your_mongodb_connection_string
```

### 5. Run the App
```bash
python app.py
```
Visit: `http://localhost:5000`

---

## 📂 Folder Structure
```
insureone-ai/
├── app.py
├── templates/
├── static/
├── model/                   # Trained ML model (.pkl)
├── faq/faq.csv              # Chatbot dataset
├── requirements.txt
├── .env                     # DO NOT SHARE PUBLICLY
├── .gitignore
```

---

## 🔐 Security Notes
- `.env` file is used to store secrets and is excluded via `.gitignore`.
- Passwords are hashed using bcrypt.

---

## 📌 TODO / Future Enhancements
- [ ] Deploy on Render / Railway
- [ ] Add charts for estimate breakdown
- [ ] Admin dashboard for analytics
- [ ] SMS/email report for users

---

## 🙌 Acknowledgements
- Icons by [Flaticon](https://flaticon.com)
- Bootstrap by [getbootstrap.com](https://getbootstrap.com)

---

## 👤 Author
**Yashwardhan Srivastava**  
[GitHub](https://github.com/yashwardhan04) • [LinkedIn](www.linkedin.com/in/yashwardhan-srivastava)

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
