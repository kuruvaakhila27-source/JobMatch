# 💼 JobMatch

AI-powered job search and resume matching platform that helps users find relevant live jobs, compare skills, identify skill gaps, and save job opportunities.

## 🚀 Features

### 📄 Resume Analysis
Upload a PDF resume and automatically extract skills from it.

### 🌐 Live Job Search
Search real job listings based on:
- Job role
- Location
- Number of jobs

### 🎯 Smart Job Matching
Compare resume skills with job requirements and generate a match percentage.

### 🔎 Job Filters
Filter jobs by:
- 📍 Location
- ⭐ Minimum match percentage
- 🏢 Company

### 📌 Save Jobs
Save interesting job opportunities for later.

- 📌 Save Job
- 🗑️ Remove Saved Job
- 🚀 View / Apply Job

### 📊 Dashboard
View useful job-search statistics:

- 🌐 Total live jobs
- ⭐ Strong matches
- 📈 Average match score
- 📌 Saved jobs

### 🧠 Resume Skill Gap Summary
Identify frequently requested skills that are missing from the uploaded resume.

### 🕘 Search History
Keep track of previous job searches.

### 🎨 Professional UI
Clean and user-friendly Streamlit interface for an easy job-search experience.

---

## 🛠️ Tech Stack

- Python
- Streamlit
- SQLite
- PDF Resume Parsing
- Job Search API
- Natural Language Processing
- Machine Learning

---

## 📂 Project Structure

```text
JobMatch/
│
├── app.py
├── database.py
├── resume_parser.py
├── job_search.py
├── matcher.py
├── requirements.txt
├── .gitignore
└── README.md
---
⚙️ How to Run
1. Clone the repository
git clone https://github.com/kuruvaakhila27-source/JobMatch.git
cd JobMatch
2. Create a virtual environment
python -m venv venv
3. Activate the virtual environment
Windows:
venv\Scripts\activate
4. Install dependencies
pip install -r requirements.txt
5. Run the application
streamlit run app.py
The application will open in your browser.
🔄 Application Flow
📄 Upload Resume
       ↓
🧠 Extract Resume Skills
       ↓
🔎 Enter Job Role & Location
       ↓
🌐 Search Live Jobs
       ↓
🎯 Calculate Match Score
       ↓
⚠️ Identify Skill Gaps
       ↓
🔎 Filter Jobs
       ↓
📌 Save Jobs
       ↓
🚀 View / Apply
📊 Example
A resume containing:
Python
Java
Artificial Intelligence
Machine Learning
can be compared against live AI/ML job listings.
The application highlights:
✅ Matching skills
⚠️ Missing skills
📊 Match percentage
💼 Experience requirements
🌐 Relevant job opportunities
🎯 Project Goal
JobMatch aims to make job searching more efficient by connecting a candidate's existing skills with real-world job requirements.
It helps users understand:
How well does this job match my current skills?
What skills should I improve?
🔮 Future Improvements
🤖 AI-powered job recommendations
📧 Personalized job alerts
📈 Career analytics
🧠 AI resume improvement
🎤 AI interview preparation
☁️ Cloud deployment
🔐 User authentication
💬 AI career assistant
