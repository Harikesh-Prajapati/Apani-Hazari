# Apani Hazari 🎓
### AI-Powered Smart Attendance Platform

**Take attendance with a photo. Track every class with ease.**

Apani Hazari is an AI-powered attendance management system that uses face recognition and voice-based attendance to simplify classroom attendance. Teachers can manage subjects and attendance records, while students can track their attendance from their dashboards.

**🚀 Live Demo:** [apani-hazari.streamlit.app](https://apani-hazari.streamlit.app)

<p align="center">
  <img src="screenshots/home.png" alt="Apani Hazari home screen" width="900">
</p>

## ✨ Features

### 👨‍🏫 Teacher Portal
- **Photo-Based Attendance:** Upload or capture classroom photos to identify enrolled students.
- **Voice Attendance:** Support voice-based attendance marking.
- **Subject Management:** Create subjects and share join codes or QR codes.
- **Attendance Records:** Review class attendance and student attendance percentages.

### 🎓 Student Portal
- **Face-Based Login:** Log in using facial recognition.
- **Quick Registration:** Create a student profile with an optional voice sample.
- **Join Classes:** Enter a subject code or use a QR code.
- **Attendance Tracking:** View attendance percentages and status for each subject.

## ⚙️ How It Works

1. Students register their profiles and facial data.
2. The system generates face embeddings to represent registered students.
3. Teachers upload classroom photos for face recognition.
4. Recognized students are presented for attendance review and recording.
5. Teachers and students access attendance information through their respective dashboards.

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | Python, Streamlit |
| Database | Supabase |
| Face Recognition | dlib, face_recognition_models |
| Machine Learning | scikit-learn |
| Voice Processing | Resemblyzer, librosa |
| QR Code Generation | Segno |
| Image Processing | Pillow |

## 🚀 Installation and Setup

### Prerequisites
- Python 3.11
- A Supabase project

### 1. Clone the repository

```bash
git clone https://github.com/Harikesh-Prajapati/Apani-Hazari.git
cd Apani-Hazari
```

### 2. Create a virtual environment

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Supabase

Create `.streamlit/secrets.toml` and add your Supabase credentials:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-key"
```

Keep your credentials private. Never commit secrets to GitHub.

### 5. Run the application

```bash
streamlit run Intelligent_AI_Attendence/app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## 📁 Project Structure

```text
Apani-Hazari/
├── requirements.txt
└── Intelligent_AI_Attendence/
    ├── app.py
    ├── PIPELINE/
    │   ├── face_pipeline.py
    │   └── voice_pipeline.py
    └── src/
        └── screens/
            ├── home_screen.py
            ├── student_screen.py
            ├── teacher_screen.py
            ├── components/
            ├── database/
            └── ui/
```

## 🔮 Future Improvements

- [ ] Export attendance reports to Excel and PDF
- [ ] Notifications for low attendance
- [ ] Face anti-spoofing to reduce photo-based impersonation

## 👨‍💻 Author

**Harikesh Prajapati**

- 💻 GitHub: [Harikesh-Prajapati](https://github.com/Harikesh-Prajapati)
- 💼 LinkedIn: [Harikesh Prajapati](https://www.linkedin.com/in/harikesh-prajapati-05034027a/)
- 🚀 Project: [Apani Hazari](https://github.com/Harikesh-Prajapati/Apani-Hazari)

If you find this project useful, consider giving it a ⭐ on GitHub!
