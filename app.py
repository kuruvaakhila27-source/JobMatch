import re
import streamlit as st
import database

from resume_parser import extract_resume_text, extract_skills
from job_search import search_jobs
from matcher import analyze_job_match


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="JobMatch AI",
    page_icon="💼",
    layout="wide"
)

database.init_db()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_company(job):
    company = job.get("company", "")

    if isinstance(company, dict):
        return company.get("display_name", "Unknown Company")

    return company or "Unknown Company"


def get_location(job):
    location = job.get("location", "")

    if isinstance(location, dict):
        return location.get("display_name", "Unknown Location")

    return location or "Unknown Location"


def get_description(job):
    return job.get("description") or job.get("content") or ""


def get_url(job):
    return (
        job.get("redirect_url")
        or job.get("url")
        or job.get("apply_url")
        or ""
    )


def get_experience(text):
    """
    Try to detect experience requirement from job description.
    """
    text = text.lower()

    patterns = [
        r"(\d+)\s*-\s*(\d+)\s*years?",
        r"(\d+)\s*\+\s*years?",
        r"(\d+)\s*years?\s*of\s*experience",
        r"experience\s*[:\-]?\s*(\d+)\s*years?"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            numbers = [
                int(value)
                for value in match.groups()
                if value
            ]

            if len(numbers) >= 2:
                return f"{numbers[0]}-{numbers[1]} years"

            if len(numbers) == 1:
                return f"{numbers[0]}+ years"

    return "Not specified"


def get_experience_number(text):
    """
    Return approximate minimum experience required.
    """
    text = text.lower()

    patterns = [
        r"(\d+)\s*-\s*(\d+)\s*years?",
        r"(\d+)\s*\+\s*years?",
        r"(\d+)\s*years?\s*of\s*experience"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            numbers = [
                int(value)
                for value in match.groups()
                if value
            ]

            if numbers:
                return numbers[0]

    return 0


def calculate_match_score(
    resume_skills,
    job,
    target_role=""
):
    """
    More meaningful match score.

    Components:
    - Skills match: 60%
    - Job title match: 25%
    - Resume relevance: 15%
    """

    description = get_description(job)

    try:
        job_skills = extract_skills(description)
    except Exception:
        job_skills = []

    resume_set = {
        str(skill).lower().strip()
        for skill in resume_skills
    }

    job_set = {
        str(skill).lower().strip()
        for skill in job_skills
    }

    # ---------------- SKILL SCORE ----------------

    if job_set:

        matched = [
            skill
            for skill in job_skills
            if str(skill).lower().strip() in resume_set
        ]

        missing = [
            skill
            for skill in job_skills
            if str(skill).lower().strip() not in resume_set
        ]

        skill_score = (
            len(matched) / len(job_set)
        ) * 60

    else:

        matched = []

        missing = []

        skill_score = 0


    # ---------------- TITLE SCORE ----------------

    title = str(
        job.get("title", "")
    ).lower()

    target_words = [
        word.lower()
        for word in target_role.split()
        if len(word) > 2
    ]

    if target_words:

        title_matches = sum(
            1
            for word in target_words
            if word in title
        )

        title_score = min(
            (title_matches / len(target_words)) * 25,
            25
        )

    else:

        title_score = 0


    # ---------------- RESUME RELEVANCE ----------------

    description_lower = description.lower()

    resume_relevant_skills = [
        skill
        for skill in resume_skills
        if str(skill).lower() in description_lower
    ]

    if resume_skills:

        relevance_score = (
            len(resume_relevant_skills)
            / len(resume_skills)
        ) * 15

    else:

        relevance_score = 0


    total_score = round(
        skill_score
        + title_score
        + relevance_score
    )

    total_score = max(
        0,
        min(total_score, 100)
    )

    return {
        "score": total_score,
        "matched": matched,
        "missing": missing,
        "job_skills": job_skills
    }


# =========================================================
# SESSION STATE
# =========================================================

if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "jobs" not in st.session_state:
    st.session_state.jobs = []

if "analyzed_jobs" not in st.session_state:
    st.session_state.analyzed_jobs = []

if "searched" not in st.session_state:
    st.session_state.searched = False


# =========================================================
# CUSTOM UI
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }

    .job-card {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
    }

    .feature-box {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #ddd;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">💼 JobMatch AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered job search, resume matching and skill gap analysis.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("🔎 Job Search")

target_role = st.sidebar.text_input(
    "Target Job Role",
    placeholder="Example: AI Engineer"
)

location = st.sidebar.text_input(
    "Location",
    value="Hyderabad"
)

number_of_jobs = st.sidebar.slider(
    "Number of Jobs",
    5,
    20,
    10
)

search_clicked = st.sidebar.button(
    "🚀 Search Live Jobs",
    use_container_width=True
)


# =========================================================
# RESUME UPLOAD
# =========================================================

st.header("📄 Resume")

uploaded_file = st.file_uploader(
    "Upload your PDF resume",
    type=["pdf"]
)


if uploaded_file is not None:

    st.success(
        f"Resume uploaded: {uploaded_file.name} ✅"
    )

    try:

        resume_text = extract_resume_text(
            uploaded_file
        )

        resume_skills = extract_skills(
            resume_text
        )

        st.session_state.resume_text = resume_text

        st.session_state.resume_skills = resume_skills

        st.success(
            "Resume analyzed successfully! 🎉"
        )

    except Exception as error:

        st.error(
            f"Resume analysis failed: {error}"
        )


# =========================================================
# RESUME SKILLS
# =========================================================

if st.session_state.resume_skills:

    st.header("🧠 Skills Found In Your Resume")

    cols = st.columns(
        min(
            4,
            len(st.session_state.resume_skills)
        )
    )

    for index, skill in enumerate(
        st.session_state.resume_skills
    ):

        with cols[index % len(cols)]:

            st.success(
                f"✓ {skill}"
            )


# =========================================================
# SEARCH
# =========================================================

st.header("🌐 Live Job Search")

st.write(
    "Search real job listings and compare them "
    "against your resume."
)


if search_clicked:

    if uploaded_file is None:

        st.warning(
            "📄 Please upload your resume first."
        )

    elif not target_role.strip():

        st.warning(
            "Please enter a target job role."
        )

    else:

        with st.spinner(
            "Searching live jobs..."
        ):

            try:

                jobs = search_jobs(
                    target_role.strip(),
                    location.strip(),
                    number_of_jobs
                ) or []

                st.session_state.jobs = jobs

                st.session_state.searched = True

                database.save_search(
                    target_role.strip(),
                    location.strip(),
                    len(jobs)
                )

            except Exception as error:

                st.error(
                    f"Job search failed: {error}"
                )

                st.session_state.jobs = []


# =========================================================
# ANALYZE JOBS
# =========================================================

if st.session_state.jobs:

    analyzed_jobs = []

    for job in st.session_state.jobs:

        result = calculate_match_score(
            st.session_state.resume_skills,
            job,
            target_role
        )

        analyzed_jobs.append(
            {
                "job": job,
                "score": result["score"],
                "matched": result["matched"],
                "missing": result["missing"],
                "job_skills": result["job_skills"]
            }
        )

    analyzed_jobs.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    st.session_state.analyzed_jobs = analyzed_jobs


# =========================================================
# DASHBOARD
# =========================================================

if st.session_state.analyzed_jobs:

    st.header("📊 JobMatch Dashboard")

    total_jobs = len(
        st.session_state.analyzed_jobs
    )

    scores = [
        item["score"]
        for item in st.session_state.analyzed_jobs
    ]

    average_score = round(
        sum(scores) / len(scores)
    ) if scores else 0

    strong_matches = sum(
        1
        for score in scores
        if score >= 70
    )

    saved_jobs = database.get_saved_jobs()

    saved_count = len(saved_jobs)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🌐 Live Jobs",
        total_jobs
    )

    col2.metric(
        "⭐ Strong Matches",
        strong_matches
    )

    col3.metric(
        "📈 Average Match",
        f"{average_score}%"
    )

    col4.metric(
        "📌 Saved Jobs",
        saved_count
    )


# =========================================================
# JOB FILTERS
# =========================================================

if st.session_state.analyzed_jobs:

    st.header("🎯 Job Filters")

    all_companies = sorted(
        list(
            set(
                get_company(item["job"])
                for item in st.session_state.analyzed_jobs
            )
        )
    )

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:

        selected_location = st.text_input(
            "📍 Filter Location",
            value=""
        )

    with filter_col2:

        min_match = st.slider(
            "⭐ Minimum Match %",
            0,
            100,
            0
        )

    with filter_col3:

        selected_company = st.selectbox(
            "🏢 Company",
            ["All Companies"] + all_companies
        )


    filtered_jobs = []

    for item in st.session_state.analyzed_jobs:

        job = item["job"]

        job_company = get_company(job)

        job_location = get_location(job)

        description = get_description(job)

        score = item["score"]


        if selected_location:

            if selected_location.lower() not in job_location.lower():

                continue


        if score < min_match:

            continue


        if (
            selected_company != "All Companies"
            and job_company != selected_company
        ):

            continue


        filtered_jobs.append(item)


    st.info(
        f"Showing {len(filtered_jobs)} "
        f"of {len(st.session_state.analyzed_jobs)} jobs."
    )


# =========================================================
# JOB LIST
# =========================================================

if st.session_state.analyzed_jobs:

    st.header("🔥 Best Matching Jobs")

    for index, item in enumerate(
        filtered_jobs,
        start=1
    ):

        job = item["job"]

        title = job.get(
            "title",
            "Unknown Job"
        )

        company = get_company(job)

        job_location = get_location(job)

        description = get_description(job)

        url = get_url(job)

        score = item["score"]

        matched = item["matched"]

        missing = item["missing"]

        experience = get_experience(
            description
        )


        if score >= 70:

            icon = "🔥"

        elif score >= 50:

            icon = "👍"

        elif score >= 30:

            icon = "📊"

        else:

            icon = "⚠️"


        st.markdown("---")

        st.subheader(
            f"{index}. {title}"
        )

        st.write(
            f"🏢 **{company}**"
        )

        st.write(
            f"📍 **{job_location}**"
        )

        st.write(
            f"💼 **Experience:** {experience}"
        )

        st.write(
            f"{icon} **{score}% Match**"
        )


        if description:

            short_description = description[:700]

            if len(description) > 700:

                short_description += "..."

            st.write(
                short_description
            )


        if matched:

            st.success(
                "✅ Matching Skills: "
                + ", ".join(
                    map(str, matched)
                )
            )

        else:

            st.info(
                "✅ Matching Skills: "
                "No matching skills detected."
            )


        if missing:

            st.warning(
                "⚠️ Skills To Improve: "
                + ", ".join(
                    map(str, missing[:8])
                )
            )

        else:

            st.success(
                "🎉 No major skill gaps detected!"
            )


        action1, action2 = st.columns(2)


        with action1:

            if url:

                st.link_button(
                    "🚀 Apply / View Job",
                    url,
                    use_container_width=True
                )

            else:

                st.info(
                    "Application link unavailable."
                )


        with action2:

            if st.button(
                "📌 Save Job",
                key=f"save_job_{index}_{title}",
                use_container_width=True
            ):

                try:

                    database.save_job(
                        title,
                        company,
                        job_location,
                        url
                    )

                    st.success(
                        "Job saved! ✅"
                    )

                except Exception as error:

                    st.error(
                        f"Could not save job: {error}"
                    )


# =========================================================
# RESUME SKILL GAP SUMMARY
# =========================================================

if st.session_state.analyzed_jobs:

    st.markdown("---")

    st.header(
        "🧠 Resume Skill Gap Summary"
    )

    all_missing_skills = []

    for item in st.session_state.analyzed_jobs:

        all_missing_skills.extend(
            item["missing"]
        )


    skill_counts = {}

    for skill in all_missing_skills:

        clean_skill = str(
            skill
        ).strip()

        if clean_skill:

            key = clean_skill.lower()

            if key not in skill_counts:

                skill_counts[key] = {
                    "name": clean_skill,
                    "count": 0
                }

            skill_counts[key]["count"] += 1


    sorted_gaps = sorted(
        skill_counts.values(),
        key=lambda item: item["count"],
        reverse=True
    )


    if sorted_gaps:

        st.write(
            "These skills appear frequently in the "
            "jobs you searched for but are missing "
            "from your detected resume skills."
        )

        gap_cols = st.columns(
            min(4, len(sorted_gaps))
        )

        for index, skill in enumerate(
            sorted_gaps[:8]
        ):

            with gap_cols[index % len(gap_cols)]:

                st.warning(
                    f"**{skill['name']}**\n\n"
                    f"Found in {skill['count']} job(s)"
                )

    else:

        st.success(
            "🎉 Great! No major skill gaps found."
        )


# =========================================================
# SEARCH HISTORY
# =========================================================

st.markdown("---")

st.header("🕘 Search History")

try:

    history = database.get_search_history()

except Exception as error:

    history = []

    st.error(
        f"Could not load search history: {error}"
    )


if history:

    for item in history:

        st.write(
            f"🔎 **{item['role']}** "
            f"• 📍 {item['location']} "
            f"• Jobs found: {item['jobs_found']} "
            f"• {item['searched_at']}"
        )


    if st.button(
        "🗑️ Clear Search History"
    ):

        database.clear_search_history()

        st.success(
            "Search history cleared! ✅"
        )

        st.rerun()

else:

    st.info(
        "No searches recorded yet."
    )


# =========================================================
# SAVED JOBS
# =========================================================

st.markdown("---")

st.header("📌 My Saved Jobs")


try:

    saved_jobs = database.get_saved_jobs()

except Exception as error:

    saved_jobs = []

    st.error(
        f"Could not load saved jobs: {error}"
    )


if saved_jobs:

    for saved_job in saved_jobs:

        title = saved_job.get(
            "title",
            "Saved Job"
        )

        company = saved_job.get(
            "company",
            ""
        )

        saved_location = saved_job.get(
            "location",
            ""
        )

        url = saved_job.get(
            "url",
            ""
        )

        job_id = saved_job.get(
            "id"
        )


        with st.expander(
            f"💼 {title}"
        ):

            st.write(
                f"🏢 {company}"
            )

            st.write(
                f"📍 {saved_location}"
            )


            action_view, action_delete = st.columns(2)


            with action_view:

                if url:

                    st.link_button(
                        "🚀 View Job",
                        url,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "Job link unavailable."
                    )


            with action_delete:

                if st.button(
                    "🗑️ Remove",
                    key=f"delete_job_{job_id}",
                    use_container_width=True
                ):

                    try:

                        database.delete_job(
                            job_id
                        )

                        st.success(
                            "Job removed! ✅"
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Could not remove job: {error}"
                        )

else:

    st.info(
        "You haven't saved any jobs yet."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "JobMatch AI • AI Job Matching • "
    "Live Jobs • Skill Gap Analysis • "
    "Saved Jobs • Search History"
)