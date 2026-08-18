import re


# ============================================================
# SKILL ALIASES
# ============================================================

SKILL_ALIASES = {
    "Python": {"python"},
    "Java": {"java"},
    "C": {"c"},
    "C++": {"c++", "cpp"},
    "C#": {"c#", "csharp"},

    "Artificial Intelligence": {
        "artificial intelligence",
        "ai",
    },

    "Machine Learning": {
        "machine learning",
        "ml",
    },

    "Deep Learning": {
        "deep learning",
    },

    "Generative AI": {
        "generative ai",
        "genai",
    },

    "NLP": {
        "nlp",
        "natural language processing",
    },

    "LLM": {
        "llm",
        "llms",
        "large language model",
        "large language models",
    },

    "RAG": {
        "rag",
        "retrieval augmented generation",
        "retrieval-augmented generation",
    },

    "LangChain": {
        "langchain",
    },

    "Pandas": {
        "pandas",
    },

    "NumPy": {
        "numpy",
    },

    "Scikit-learn": {
        "scikit-learn",
        "scikit learn",
        "sklearn",
    },

    "TensorFlow": {
        "tensorflow",
    },

    "PyTorch": {
        "pytorch",
    },

    "SQL": {
        "sql",
    },

    "MySQL": {
        "mysql",
    },

    "PostgreSQL": {
        "postgresql",
        "postgres",
    },

    "MongoDB": {
        "mongodb",
        "mongo db",
    },

    "Git": {
        "git",
    },

    "GitHub": {
        "github",
    },

    "Docker": {
        "docker",
    },

    "AWS": {
        "aws",
        "amazon web services",
    },

    "Azure": {
        "azure",
        "microsoft azure",
    },

    "GCP": {
        "gcp",
        "google cloud",
        "google cloud platform",
    },

    "Django": {
        "django",
    },

    "Flask": {
        "flask",
    },

    "FastAPI": {
        "fastapi",
        "fast api",
    },

    "React": {
        "react",
        "react.js",
    },

    "JavaScript": {
        "javascript",
        "js",
    },

    "TypeScript": {
        "typescript",
        "ts",
    },

    "Power BI": {
        "power bi",
        "power-bi",
    },

    "Tableau": {
        "tableau",
    },
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    replacements = {
        "scikit learn": "scikit-learn",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning",
        "artificial-intelligence": "artificial intelligence",
        "generative-ai": "generative ai",
        "natural-language-processing": "natural language processing",
        "large-language-model": "large language model",
        "large-language-models": "large language models",
        "google-cloud-platform": "google cloud platform",
        "power-bi": "power bi",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# ============================================================
# CHECK WHETHER A SKILL EXISTS
# ============================================================

def skill_found(text, skill):

    text = normalize_text(text)

    skill = skill.strip()

    aliases = SKILL_ALIASES.get(
        skill,
        {skill.lower()}
    )

    for alias in aliases:

        alias = normalize_text(alias)

        # Special handling for C
        if alias == "c":

            pattern = r"(?<![a-z0-9])c(?![a-z0-9])"

        else:

            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(alias)
                + r"(?![a-z0-9])"
            )

        if re.search(pattern, text):

            return True

    return False


# ============================================================
# FIND MATCHING SKILLS
# ============================================================

def find_matching_skills(
    resume_skills,
    required_skills
):

    matched = []
    missing = []

    for required_skill in required_skills:

        found = False

        # Direct/alias comparison
        for resume_skill in resume_skills:

            if skill_found(
                resume_skill,
                required_skill
            ):

                found = True
                break

            # Reverse alias comparison
            resume_aliases = SKILL_ALIASES.get(
                resume_skill,
                {resume_skill.lower()}
            )

            required_aliases = SKILL_ALIASES.get(
                required_skill,
                {required_skill.lower()}
            )

            if (
                resume_aliases
                & required_aliases
            ):

                found = True
                break

        if found:

            matched.append(
                required_skill
            )

        else:

            missing.append(
                required_skill
            )

    # Remove duplicates
    matched = list(
        dict.fromkeys(matched)
    )

    missing = list(
        dict.fromkeys(missing)
    )

    return matched, missing


# ============================================================
# BASIC SKILL MATCH
# ============================================================

def calculate_match(
    resume_skills,
    required_skills
):

    if not required_skills:

        return 0, [], []

    matched, missing = find_matching_skills(
        resume_skills,
        required_skills
    )

    score = round(
        (
            len(matched)
            / len(required_skills)
        ) * 100
    )

    return score, matched, missing


# ============================================================
# EXPERIENCE DETECTION
# ============================================================

def extract_required_experience(
    title,
    description
):

    text = normalize_text(
        title + " " + description
    )

    patterns = [

        # 5-8 years
        r"(\d+)\s*[-–]\s*(\d+)\s*years",

        # 5+ years
        r"(\d+)\s*\+\s*years",

        # 5 years of experience
        r"(\d+)\s*years\s+of\s+experience",

        # experience: 5 years
        r"experience\s*[:\-]?\s*(\d+)\s*years",

        # minimum 5 years
        r"minimum\s+of\s+(\d+)\s*years",

        # at least 5 years
        r"at\s+least\s+(\d+)\s*years",
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text
        )

        if matches:

            match = matches[0]

            try:

                if isinstance(
                    match,
                    tuple
                ):

                    return int(
                        match[0]
                    )

                return int(match)

            except:

                pass

    return 0


# ============================================================
# SENIORITY DETECTION
# ============================================================

def detect_seniority(title):

    title = normalize_text(title)

    senior_keywords = [

        "senior",

        "principal",

        "lead",

        "staff",

        "architect",

        "manager",

        "director",

        "head",

    ]

    for keyword in senior_keywords:

        if keyword in title:

            return True

    return False


# ============================================================
# FINAL REALISTIC MATCH
# ============================================================

def calculate_final_match(
    skill_score,
    title="",
    description="",
    candidate_experience=0
):

    required_experience = (
        extract_required_experience(
            title,
            description
        )
    )

    is_senior = detect_seniority(
        title
    )

    final_score = skill_score

    # --------------------------------------------------------
    # EXPERIENCE PENALTY
    # --------------------------------------------------------

    if required_experience > 0:

        if candidate_experience < required_experience:

            difference = (
                required_experience
                - candidate_experience
            )

            # Small experience gap
            if difference <= 1:

                final_score *= 0.90

            # Medium gap
            elif difference <= 3:

                final_score *= 0.70

            # Large gap
            else:

                final_score *= 0.50

    # --------------------------------------------------------
    # SENIORITY PENALTY
    # --------------------------------------------------------

    if is_senior:

        title_lower = title.lower()

        # Principal / Director / Architect
        if any(
            keyword in title_lower
            for keyword in [
                "principal",
                "director",
                "architect"
            ]
        ):

            final_score = min(
                final_score,
                35
            )

        # Senior / Lead / Staff
        elif any(
            keyword in title_lower
            for keyword in [
                "senior",
                "lead",
                "staff"
            ]
        ):

            final_score = min(
                final_score,
                50
            )

        else:

            final_score = min(
                final_score,
                60
            )

    return round(
        max(
            0,
            min(
                final_score,
                100
            )
        )
    )


# ============================================================
# COMPLETE JOB MATCH
# ============================================================

def analyze_job_match(
    resume_skills,
    required_skills,
    title="",
    description="",
    candidate_experience=0
):

    skill_score, matched, missing = (
        calculate_match(
            resume_skills,
            required_skills
        )
    )

    final_score = calculate_final_match(
        skill_score=skill_score,
        title=title,
        description=description,
        candidate_experience=candidate_experience
    )

    required_experience = (
        extract_required_experience(
            title,
            description
        )
    )

    is_senior = detect_seniority(
        title
    )

    return {
        "score": final_score,
        "skill_score": skill_score,
        "matched": matched,
        "missing": missing,
        "required_experience":
            required_experience,
        "is_senior":
            is_senior
    }