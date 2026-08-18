import re
import PyPDF2


# ============================================================
# EXTRACT TEXT FROM PDF
# ============================================================

def extract_resume_text(uploaded_file):

    reader = PyPDF2.PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ============================================================
# SKILL DATABASE
# ============================================================

SKILLS = [
    # Programming
    "Python",
    "Java",
    "C++",
    "C#",
    "JavaScript",
    "TypeScript",
    "C",

    # AI / ML
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "NLP",
    "Computer Vision",
    "Generative AI",
    "GenAI",
    "Large Language Models",
    "LLM",
    "RAG",

    # ML Libraries
    "Scikit-learn",
    "TensorFlow",
    "PyTorch",
    "Keras",
    "Pandas",
    "NumPy",

    # Web
    "HTML",
    "CSS",
    "React",
    "Node.js",
    "Django",
    "Flask",
    "FastAPI",

    # Database
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "SQLite",

    # Cloud
    "AWS",
    "Azure",
    "Google Cloud",
    "GCP",

    # Tools
    "Git",
    "GitHub",
    "Docker",
    "Kubernetes",

    # AI Frameworks
    "LangChain",
    "LlamaIndex",
    "Hugging Face",

    # Data
    "Data Science",
    "Data Analysis",
    "Power BI",
    "Tableau",

    # Other
    "REST API",
    "API",
    "OOP",
    "Data Structures",
    "Algorithms"
]


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(text):

    text = text.lower()

    # Normalize common variations
    replacements = {
        "scikit learn": "scikit-learn",
        "scikit learn": "scikit-learn",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning",
        "artificial-intelligence": "artificial intelligence",
        "natural language processing": "natural language processing",
        "large language model": "large language models",
        "generative-ai": "generative ai",
        "node js": "node.js",
        "power-bi": "power bi"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# ============================================================
# EXTRACT SKILLS
# ============================================================

def extract_skills(text):

    if not text:
        return []

    normalized_text = normalize_text(text)

    found_skills = []

    for skill in SKILLS:

        skill_lower = skill.lower()

        # Special handling for one-letter skill C
        if skill == "C":

            pattern = r"(?<![a-z])c(?![a-z])"

        else:

            escaped_skill = re.escape(
                skill_lower
            )

            pattern = (
                r"(?<![a-z0-9])"
                + escaped_skill
                + r"(?![a-z0-9])"
            )

        if re.search(
            pattern,
            normalized_text
        ):

            found_skills.append(skill)

    return found_skills