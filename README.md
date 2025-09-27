# TechStellars

# Crop Disease Detector

A Flask-based web application that allows users to detect crop diseases by uploading leaf images. The system leverages machine learning to analyze images and provides disease predictions along with recommendations for treatment. It also includes user authentication and a dashboard to track detection history.

---

## Features
- **Crop Disease Detection**: Upload leaf images to identify potential diseases.
- **User Authentication**: Register and log in to manage your detection history.
- **Dashboard**: View past detection results and manage uploaded files.
- **Simple Web Interface**: User-friendly frontend built with HTML templates.
- **Database Storage**: SQLite database to store user data and detection history.

---

## Tech Stack
- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS (Jinja2 templates)
- **Database:** SQLite
- **Image Processing / ML:** Python (OpenCV, TensorFlow or PyTorch if integrated)
- **Deployment:** Gunicorn / Flask Development Server

---

## Project Structure
```
crop_disease_detector/
├── app.py                # Main Flask application
├── database.db           # SQLite database file
├── requirements.txt      # Python dependencies
├── static/
│   └── uploads/          # Uploaded leaf images
│       └── sample_image.webp
└── templates/
    ├── base.html         # Base template
    ├── dashboard.html    # Dashboard page
    ├── detect.html       # Image upload page
    ├── index.html        # Home page
    ├── login.html        # User login page
    ├── register.html     # User registration page
    └── result.html       # Display detection results
```

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/crop_disease_detector.git
cd crop_disease_detector
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize the Database (If Empty)
```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

Or if migrations are set up:
```bash
flask db upgrade
```

### 5. Run the Application
```bash
flask run
```

Or run directly:
```bash
python app.py
```

The app will be accessible at: **http://127.0.0.1:5000/**

---

## Deployment (Production)

### Using Gunicorn (Linux/Mac)
```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

For **Windows**, use:
```bash
waitress-serve --listen=0.0.0.0:8000 app:app
```

---

## Usage
1. Register for a new account.
2. Log in using your credentials.
3. Navigate to the **Detect** page.
4. Upload an image of a crop leaf.
5. View the disease prediction and recommendations.
6. Check your history on the **Dashboard**.

---

## Future Improvements
- Integrate a trained deep learning model for accurate predictions.
- Add support for multiple languages.
- Deploy the app on AWS, Azure, or Heroku.
- Improve the UI using a modern frontend framework like React or Vue.
- Add role-based access control for admin features.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
