import streamlit as st
import requests
import os
import pandas as pd

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(
    page_title="HireFast — AI Recruitment",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_css():
    st.markdown("""
    <style>
    /* ── Background ── */
    body,
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg,#dbeafe,#e0f2fe,#f0f9ff) !important;
    }
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stMain"] {
        background: transparent !important;
    }
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] { display: none !important; }

    .main .block-container {
        background: transparent !important;
        max-width: 960px;
        margin: auto;
        padding: 2rem 1.5rem;
    }
    .stTextInput input[type="password"] {
    font-size: 18px !important;
    letter-spacing: 3px !important;
    min-height: 48px !important;
}

.stTextInput input[type="password"]::placeholder {
    font-size: 18px !important;
    letter-spacing: 3px !important;
}

    /* ── Text ── */
    h1, h2, h3 { color: #111827 !important; }
    p, span, div { color: #1f2937 !important; }
    label {
        color: #1f2937 !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] { background-color: #111827 !important; }
    section[data-testid="stSidebar"] * { color: #f9fafb !important; }
    section[data-testid="stSidebar"] hr { border-color: #374151 !important; }

    /* ── Inputs ── */
    input, textarea, select,
    .stTextInput input,
    .stTextArea textarea {
        background: rgba(255,255,255,0.7) !important;
        color: #111827 !important;
        caret-color: #111827 !important;
        border: 1px solid rgba(255,255,255,0.5) !important;
        border-radius: 10px !important;
    }
    input::placeholder, textarea::placeholder { color: #6b7280 !important; }
    [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.7) !important;
        color: #111827 !important;
        border: 1px solid rgba(255,255,255,0.5) !important;
        border-radius: 10px !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg,#2563eb,#3b82f6) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.4rem !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.4) !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
    }
    .stButton > button p { color: #ffffff !important; }
    .stButton > button:hover {
        background: linear-gradient(135deg,#1d4ed8,#2563eb) !important;
        box-shadow: 0 6px 20px rgba(37,99,235,0.5) !important;
        transform: translateY(-2px) !important;
    }
    .stButton > button:active { transform: translateY(0px) !important; }
    .stButton > button:disabled {
        opacity: 0.6 !important;
        transform: none !important;
    }

    /* ── Metrics, uploader, tables, alerts ── */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.5) !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
        border-radius: 12px !important;
        padding: 1rem 1.25rem !important;
    }
    [data-testid="stMetricValue"] { color: #111827 !important; font-weight: 700 !important; }
    [data-testid="stFileUploadDropzone"] {
        background: rgba(240,249,255,0.6) !important;
        border: 2px dashed #93c5fd !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploadDropzone"] * { color: #1e40af !important; }
    [data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden !important; }
    .stAlert { border-radius: 10px !important; }
    hr { border-color: rgba(255,255,255,0.4) !important; margin: 1.25rem 0 !important; }
    [data-testid="stCaptionContainer"] { color: #6b7280 !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #93c5fd; border-radius: 3px; }

    /* ── Glass cards (login / register / forgot password) ── */
    .st-key-login_card,
    .st-key-register_card,
    .st-key-forgot_card {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.15) !important;
    padding: 1.5rem !important;
}
    </style>
    """, unsafe_allow_html=True)


def section_header(title, subtitle=None):
    sub = f'<p style="color:#6b7280;margin:4px 0 0;font-size:0.9rem;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom:1.25rem;">
        <h1 style="color:#111827;margin:0;font-size:1.6rem;font-weight:700;">{title}</h1>
        {sub}
    </div>""", unsafe_allow_html=True)


def badge(text, color):
    palette = {
        "green":  ("#d1fae5", "#065f46"),
        "blue":   ("#dbeafe", "#1e40af"),
        "yellow": ("#fef3c7", "#92400e"),
        "red":    ("#fee2e2", "#991b1b"),
        "gray":   ("#f3f4f6", "#374151"),
    }
    bg, fg = palette.get(color, palette["gray"])
    return (f'<span style="background:{bg};color:{fg};padding:3px 10px;'
            f'border-radius:999px;font-size:0.78rem;font-weight:600;">{text}</span>')


def brand_header(size=34, tagline="Hire smarter. Screen faster. Build better teams.", top="3rem"):
    st.markdown(f"""
    <div style="text-align:center;padding:{top} 0 1.5rem;background:transparent;">
        <div style="font-size:{size}px;font-weight:800;color:#111827;
                    letter-spacing:-1px;line-height:1;margin-bottom:0.5rem;">
             HireFast
        </div>
        <p style="font-size:15px;color:#4b5563;margin:0;">{tagline}</p>
    </div>""", unsafe_allow_html=True)


def _job_card(job):
    """Job card showing title, company, sector, skills."""
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.55);backdrop-filter:blur(10px);
                border:1px solid rgba(255,255,255,0.4);border-radius:14px;
                padding:1.1rem 1.25rem;margin-bottom:0.75rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.07);">
        <p style="font-weight:700;font-size:1rem;color:#111827;margin:0 0 2px;">
            {job['title']}</p>
        <p style="color:#2563eb;font-size:0.85rem;font-weight:500;margin:0 0 4px;">
            {job.get('company_name', '')}</p>
        <p style="color:#6b7280;font-size:0.82rem;margin:0 0 6px;">
            {job['sector']} &nbsp;·&nbsp; {job['education_required']}
            &nbsp;·&nbsp; {job['experience_required']}</p>
        <p style="color:#374151;font-size:0.82rem;margin:0 0 8px;">
            <span style="color:#2563eb;font-weight:500;">Skills:</span>
            {job['skills_required']}</p>
        <p style="color:#4b5563;font-size:0.85rem;margin:0;
                  border-top:1px solid rgba(0,0,0,0.06);padding-top:8px;">
            {job['description'][:160]}…</p>
    </div>""", unsafe_allow_html=True)


for _k, _v in {
    "token":             None,
    "user":              None,
    "page":              "login",
    "applying_to":       None,
    "job_posting":       False,
    "demo_reset_token":  None,
    "flash":             None,
    "flash_login":       None,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def hdrs():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_post(ep, json=None, data=None, files=None):
    try:
        h = hdrs() if st.session_state.token else {}
        return requests.post(f"{API_BASE}{ep}", json=json, data=data, files=files, headers=h)
    except requests.ConnectionError:
        st.error("Cannot connect to backend — make sure FastAPI is running on port 8000.")
        return None


def api_get(ep, params=None):
    try:
        h = hdrs() if st.session_state.token else {}
        return requests.get(f"{API_BASE}{ep}", params=params, headers=h)
    except requests.ConnectionError:
        st.error("Cannot connect to backend.")
        return None


def api_put(ep):
    try:
        return requests.put(f"{API_BASE}{ep}", headers=hdrs())
    except requests.ConnectionError:
        st.error("Cannot connect to backend.")
        return None


def logout():
    for k in ("token", "user", "applying_to", "flash"):
        st.session_state[k] = None
    st.session_state.page        = "login"
    st.session_state.job_posting = False
    st.rerun()


def show_login():
    brand_header()

    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        if st.session_state.get("flash_login"):
            st.success(st.session_state.pop("flash_login"))

        with st.container(border=True):
            role     = st.radio("Sign in as", ["HR", "Candidate"], horizontal=True, key="login_role")
            email    = st.text_input("Email address", placeholder="you@company.com", key="li_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="li_pw")

            if st.button("Sign in →", use_container_width=True, type="primary"):
                if not email.strip() or not password.strip():
                    st.warning("Please enter your email and password.")
                else:
                    resp = api_post("/login", json={"email": email.strip(), "password": password})
                    if resp and resp.status_code == 200:
                        data = resp.json()
                        if data["role"] != role:
                            st.error(f"This account is registered as **{data['role']}**, not {role}.")
                        else:
                            st.session_state.token = data["access_token"]
                            st.session_state.user  = data
                            st.session_state.page  = "dashboard"
                            st.rerun()
                    elif resp:
                        st.error(resp.json().get("detail", "Login failed."))

            if st.button("Forgot password?", use_container_width=True):
                st.session_state.page = "forgot"
                st.rerun()

            st.markdown(
                '<p style="text-align:center;color:#6b7280;font-size:0.85rem;margin:0.75rem 0 0;">'
                "Don't have an account?</p>",
                unsafe_allow_html=True
            )
            if st.button("Create a new account", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()


def show_register():
    brand_header(size=30, tagline="Create your account", top="2.5rem")

    _, col, _ = st.columns([1, 1.5, 1])
    with col:
       with st.container(border=True):
            role = st.radio("Registering as", ["HR", "Candidate"], horizontal=True, key="reg_role")
            name = st.text_input("Full name", placeholder="Ananya Rao", key="reg_name")

            company_name = ""
            if role == "HR":
                company_name = st.text_input("Company name", placeholder="e.g. Acme Corp", key="reg_company")

            email = st.text_input("Email address", placeholder="you@email.com", key="reg_email")
            c1, c2 = st.columns(2)
            with c1:
                password = st.text_input("Password", type="password", placeholder="••••••••", key="reg_pw")
            with c2:
                confirm = st.text_input("Confirm", type="password", placeholder="••••••••", key="reg_confirm")

            if st.button("Register →", use_container_width=True, type="primary"):
                if not name.strip() or not email.strip() or not password.strip() or not confirm.strip():
                    st.warning("Please fill in all fields.")
                elif role == "HR" and not company_name.strip():
                    st.warning("Company name is required for HR accounts.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                else:
                    resp = api_post("/register", json={
                        "name":         name.strip(),
                        "email":        email.strip(),
                        "password":     password,
                        "role":         role,
                        "company_name": company_name.strip() if role == "HR" else None
                    })
                    if resp and resp.status_code == 200:
                        st.session_state.flash_login = f"Account created! Please sign in as {role}."
                        st.session_state.page = "login"
                        st.rerun()
                    elif resp:
                        st.error(resp.json().get("detail", "Registration failed."))

            if st.button("← Back to sign in", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()


def show_forgot_password():
    brand_header(size=30, tagline="Reset your password", top="2.5rem")

    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        with st.container(border=True):
            email = st.text_input("Registered email", placeholder="you@email.com", key="fp_email")

            if st.button("Send reset code", use_container_width=True, type="primary"):
                if not email.strip():
                    st.warning("Please enter your email.")
                else:
                    with st.spinner("Generating reset code…"):
                        resp = api_post("/forgot_password", json={"email": email.strip()})
                    if resp and resp.status_code == 200:
                        data = resp.json()
                        if data.get("demo_mode"):
                            st.session_state.demo_reset_token = data["reset_token"]
                            st.info("Demo mode: email not configured. Code shown below.")
                        else:
                            st.success("Reset code sent to your email.")
                    elif resp:
                        st.error(resp.json().get("detail", "Request failed."))

            if st.session_state.get("demo_reset_token"):
                st.code(st.session_state.demo_reset_token, language=None)

            st.markdown("---")
            token  = st.text_input("Reset code", placeholder="Paste the code", key="fp_token")
            new_pw = st.text_input("New password", type="password", key="fp_new")
            conf   = st.text_input("Confirm new password", type="password", key="fp_conf")

            if st.button("Reset password", use_container_width=True, type="primary"):
                if not token.strip() or not new_pw or not conf:
                    st.warning("Please fill in all fields.")
                elif new_pw != conf:
                    st.error("Passwords do not match.")
                else:
                    with st.spinner("Resetting password…"):
                        resp = api_post("/reset_password",
                                        json={"token": token.strip(), "new_password": new_pw})
                    if resp and resp.status_code == 200:
                        st.session_state.demo_reset_token = None
                        st.session_state.flash_login = "Password reset successful. Please sign in."
                        st.session_state.page = "login"
                        st.rerun()
                    elif resp:
                        st.error(resp.json().get("detail", "Reset failed."))

            if st.button("← Back to sign in", use_container_width=True):
                st.session_state.demo_reset_token = None
                st.session_state.page = "login"
                st.rerun()


HR_PAGES = [
    "📊  Overview",
    "➕  Post new job",
    "👥  View applicants",
    "🤖  AI screening",
    "🔍  Filter candidates",
]


def hr_dashboard():
    user = st.session_state.user
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:0.5rem 0 1rem;text-align:center;">
            <div style="font-size:1.8rem;margin-bottom:0.4rem;">🚀</div>
            <p style="font-weight:700;font-size:1rem;color:#f1f5f9;margin:0;">{user['name']}</p>
            <p style="font-size:0.78rem;color:#94a3b8;margin:2px 0 0;">
                {user.get('company_name', 'HR')} · HireFast</p>
        </div>""", unsafe_allow_html=True)
        st.divider()
        page = st.radio("Menu", HR_PAGES, label_visibility="collapsed")
        st.divider()
        if st.button("Sign out", use_container_width=True):
            logout()

    {
        HR_PAGES[0]: hr_overview,
        HR_PAGES[1]: hr_post_job,
        HR_PAGES[2]: hr_applicants,
        HR_PAGES[3]: hr_ai_screening,
        HR_PAGES[4]: hr_filter,
    }[page]()


def hr_overview():
    user = st.session_state.user
    section_header(f"Welcome, {user['name']}", user.get("company_name", ""))

    resp = api_get("/my_jobs")                      # only THIS HR's jobs
    jobs = resp.json() if resp and resp.status_code == 200 else []

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("My job postings",  len(jobs))
    c2.metric("Total applicants", "—")
    c3.metric("Shortlisted",      "—")
    c4.metric("AI screened",      "—")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown(
        '<h3 style="color:#111827;font-weight:600;margin-bottom:0.75rem;">My recent postings</h3>',
        unsafe_allow_html=True
    )
    if not jobs:
        st.info("You haven't posted any jobs yet. Use **Post new job** to get started.")
        return
    for job in jobs[:6]:
        _job_card(job)


def hr_post_job():
    section_header("Post a new job", "Company name is auto-linked from your profile")

    sectors  = ["IT", "Healthcare", "Finance", "Marketing", "Education", "Manufacturing", "Legal"]
    edu_opts = ["High School", "Diploma", "B.Sc", "B.Tech", "B.Com", "MBA", "M.Tech", "PhD", "Any"]

    if st.session_state.get("flash"):
        st.success(st.session_state.pop("flash"))

    company = st.session_state.user.get("company_name", "")
    st.markdown(f"""
    <div style="background:rgba(219,234,254,0.7);border:1px solid #bfdbfe;
                border-radius:10px;padding:0.75rem 1rem;margin-bottom:1rem;">
        <p style="color:#1e40af;font-size:0.875rem;margin:0;">
            Posting as: <b>{company}</b>
        </p>
    </div>""", unsafe_allow_html=True)

    title       = st.text_input("Job title", placeholder="e.g. Senior Python Developer", key="job_title")
    description = st.text_area("Job description", height=130,
                               placeholder="Describe the role, responsibilities, and requirements...",
                               key="job_desc")
    c1, c2 = st.columns(2)
    c1.selectbox("Sector", sectors, key="job_sector")
    c2.selectbox("Education required", edu_opts, key="job_edu")
    c3, c4 = st.columns(2)
    experience = c3.text_input("Experience required", placeholder="e.g. 3 years", key="job_exp")
    skills     = c4.text_input("Required skills (comma-separated)",
                               placeholder="Python, SQL, FastAPI", key="job_skills")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    clicked = st.button(
        "Posting…" if st.session_state.job_posting else "Post job →",
        type="primary",
        disabled=st.session_state.job_posting
    )

    if clicked and not st.session_state.job_posting:
        if not title.strip() or not description.strip() or not experience.strip() or not skills.strip():
            st.warning("Please fill in all fields.")
        else:
            st.session_state.job_posting = True
            st.rerun()

    if st.session_state.job_posting:
        with st.spinner("Posting job…"):
            resp = api_post("/create_job", json={
                "title":               st.session_state.get("job_title", ""),
                "description":         st.session_state.get("job_desc", ""),
                "sector":              st.session_state.get("job_sector", "IT"),
                "education_required":  st.session_state.get("job_edu", "Any"),
                "experience_required": st.session_state.get("job_exp", ""),
                "skills_required":     st.session_state.get("job_skills", ""),
            })
        st.session_state.job_posting = False        

        if resp and resp.status_code == 200:
            for k in ["job_title", "job_desc", "job_exp", "job_skills"]:
                st.session_state.pop(k, None)       # clear form
            st.session_state.flash = "Job posted successfully"
            st.rerun()
        elif resp:
            st.error(resp.json().get("detail", "Failed to post job."))  
        else:
            st.error("No response from server.")


def hr_applicants():
    section_header("View applicants", "Candidates who applied to your jobs")

    resp = api_get("/my_jobs")
    if not resp or resp.status_code != 200:
        st.error("Could not load your jobs.")
        return
    jobs = resp.json()
    if not jobs:
        st.info("You haven't posted any jobs yet.")
        return

    opts     = {f"[{j['job_id']}] {j['title']}": j["job_id"] for j in jobs}
    selected = st.selectbox("Select your job", list(opts.keys()))
    job_id   = opts[selected]

    resp2 = api_get(f"/job_applicants/{job_id}")
    if not resp2 or resp2.status_code != 200:
        st.error("Could not load applicants.")
        return

    data           = resp2.json()
    applicants     = data.get("applicants", [])
    screening_done = data.get("screening_done", False)

    col1, col2 = st.columns([3, 1])
    col1.markdown(
        f'<p style="color:#6b7280;font-size:0.85rem;margin:0.25rem 0 1rem;">'
        f'{data["total_applicants"]} applicant(s) · {data["company_name"]}</p>',
        unsafe_allow_html=True
    )
    if screening_done:
        col2.success("AI screening done ✓")
    else:
        col2.warning("Not screened yet")

    if not applicants:
        st.info("No applicants for this job yet.")
        return

    status_map = {
        "applied":     ("Applied",     "yellow"),
        "shortlisted": ("Shortlisted", "green"),
        "rejected":    ("Rejected",    "red"),
    }
    for app in applicants:
        label, color = status_map.get(app["status"], (app["status"], "gray"))
        score_str = (
            f"AI Match: <b>{app['ai_score']}%</b>"
            if app.get("ai_score") is not None
            else '<span style="color:#f59e0b;">Run AI screening to score</span>'
        )
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.55);backdrop-filter:blur(10px);
                    border:1px solid rgba(255,255,255,0.4);border-radius:14px;
                    padding:1rem 1.25rem;margin-bottom:0.5rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <p style="font-weight:600;font-size:0.95rem;color:#111827;margin:0;">
                        {app['candidate_name']}</p>
                    <p style="color:#6b7280;font-size:0.82rem;margin:3px 0 0;">
                        {app['candidate_email']} &nbsp;·&nbsp; {score_str}</p>
                </div>
                {badge(label, color)}
            </div>
        </div>""", unsafe_allow_html=True)

        _, c2, c3 = st.columns([3, 1, 1])
        with c2:
            if st.button("✅ Shortlist", key=f"sl_{app['application_id']}"):
                r = api_put(f"/shortlist/{app['application_id']}")
                if r and r.status_code == 200:
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Failed."))
        with c3:
            if st.button("❌ Reject", key=f"rj_{app['application_id']}"):
                r = api_put(f"/reject/{app['application_id']}")
                if r and r.status_code == 200:
                    st.rerun()
                elif r:
                    st.error(r.json().get("detail", "Failed."))


def hr_ai_screening():
    section_header("AI resume screening", "Rank candidates for your jobs")

    resp = api_get("/my_jobs")
    if not resp or resp.status_code != 200:
        st.error("Could not load your jobs.")
        return
    jobs = resp.json()
    if not jobs:
        st.info("You haven't posted any jobs yet.")
        return

    opts     = {f"[{j['job_id']}] {j['title']}": j["job_id"] for j in jobs}
    selected = st.selectbox("Select your job to screen", list(opts.keys()))
    job_id   = opts[selected]

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if st.button("🚀 Run AI screening", type="primary"):
        with st.spinner("Extracting resumes, generating embeddings, scoring candidates…"):
            resp2 = api_post(f"/run_screening/{job_id}")

        if not resp2 or resp2.status_code != 200:
            st.error(resp2.json().get("detail", "Screening failed.") if resp2 else "Connection error.")
            return

        result   = resp2.json()
        rankings = result.get("rankings", [])
        errors   = result.get("errors", [])

        if not rankings and not errors:
            st.info(result.get("message", "No applicants to screen yet."))
            return

        st.success(
            f"✅ Screened **{result.get('total_screened', 0)}** candidate(s) "
            f"for **{result.get('job_title', '')}**"
        )

        if errors:
            with st.expander(f"⚠️ {len(errors)} error(s)"):
                for e in errors:
                    st.write(f"- **{e['candidate']}**: {e['error']}")

        if rankings:
            st.markdown(
                '<h3 style="color:#111827;font-weight:600;margin:1.25rem 0 0.75rem;">'
                'Ranked candidates</h3>',
                unsafe_allow_html=True
            )
            for c in rankings:
                score     = c["match_score"]
                bar_color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.55);backdrop-filter:blur(10px);
                            border:1px solid rgba(255,255,255,0.4);border-radius:14px;
                            padding:1rem 1.25rem;margin-bottom:0.6rem;
                            box-shadow:0 2px 8px rgba(0,0,0,0.07);">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div style="display:flex;align-items:center;gap:1rem;">
                            <span style="background:#f3f4f6;color:#374151;width:32px;height:32px;
                                         border-radius:50%;display:inline-flex;align-items:center;
                                         justify-content:center;font-weight:700;font-size:0.85rem;">
                                #{c['rank']}</span>
                            <div>
                                <p style="font-weight:600;color:#111827;margin:0;">{c['candidate_name']}</p>
                                <p style="color:#6b7280;font-size:0.82rem;margin:2px 0 0;">{c['candidate_email']}</p>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <p style="font-weight:700;font-size:1.1rem;color:{bar_color};margin:0;">{score}%</p>
                            <div style="width:100px;height:5px;background:#f3f4f6;border-radius:3px;margin-top:5px;">
                                <div style="width:{score}%;height:100%;background:{bar_color};border-radius:3px;"></div>
                            </div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            st.caption("Go to View applicants to shortlist or reject candidates.")
            df = pd.DataFrame(rankings)[["rank", "candidate_name", "candidate_email", "match_score", "status"]]
            df.columns = ["Rank", "Name", "Email", "Score (%)", "Status"]
            st.dataframe(df, use_container_width=True)


def hr_filter():
    section_header("Filter candidates", "Narrow by education, sector, skills or experience")

    c1, c2, c3, c4 = st.columns(4)
    education  = c1.text_input("Education",  placeholder="B.Tech")
    sector     = c2.text_input("Sector",     placeholder="IT")
    skill      = c3.text_input("Skill",      placeholder="Python")
    experience = c4.text_input("Experience", placeholder="2 years")

    if st.button("Apply filters", type="primary"):
        params = {k: v for k, v in {
            "education": education, "sector": sector,
            "skill": skill, "experience": experience
        }.items() if v}
        resp = api_get("/filter_candidates", params=params)
        if not resp or resp.status_code != 200:
            st.error("Filter failed.")
            return
        data = resp.json()
        st.markdown(
            f'<p style="color:#6b7280;font-size:0.85rem;margin-bottom:0.75rem;">'
            f'{data["count"]} candidate(s) found</p>',
            unsafe_allow_html=True
        )
        if data["candidates"]:
            df = pd.DataFrame(data["candidates"])
            st.dataframe(
                df[["candidate_name", "candidate_email", "job_title", "company_name",
                    "sector", "education_required", "skills_required",
                    "application_status", "ai_score"]],
                use_container_width=True
            )
        else:
            st.info("No candidates match the selected filters.")


# ══════════════════════════════════════════════════════════════════════
# CANDIDATE DASHBOARD
# ══════════════════════════════════════════════════════════════════════
CAND_PAGES = [
    "💼  Browse jobs",
    "📋  My applications",
]


def candidate_dashboard():
    user = st.session_state.user
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:0.5rem 0 1rem;text-align:center;">
            <div style="font-size:1.8rem;margin-bottom:0.4rem;">👤</div>
            <p style="font-weight:700;font-size:1rem;color:#f1f5f9;margin:0;">{user['name']}</p>
            <p style="font-size:0.78rem;color:#94a3b8;margin:2px 0 0;">Candidate · HireFast</p>
        </div>""", unsafe_allow_html=True)
        st.divider()
        page = st.radio("Menu", CAND_PAGES, label_visibility="collapsed")
        st.divider()
        if st.button("Sign out", use_container_width=True):
            logout()

    {
        CAND_PAGES[0]: cand_browse_jobs,
        CAND_PAGES[1]: cand_my_applications,
    }[page]()


def cand_browse_jobs():
    if st.session_state.applying_to:
        cand_apply_form()
        return

    section_header("Browse jobs", "Find your next opportunity")

    if st.session_state.get("flash"):
        st.success(st.session_state.pop("flash"))

    resp = api_get("/jobs")
    if not resp or resp.status_code != 200:
        st.error("Could not load jobs.")
        return
    jobs = resp.json()
    if not jobs:
        st.info("No openings available at the moment.")
        return

    search = st.text_input("🔍 Search by title, company or sector",
                           placeholder="Python, Google, Healthcare…")
    filtered = [
        j for j in jobs if not search or
        search.lower() in j["title"].lower() or
        search.lower() in j.get("company_name", "").lower() or
        search.lower() in j["sector"].lower()
    ]

    st.markdown(
        f'<p style="color:#6b7280;font-size:0.85rem;margin:0.5rem 0 1rem;">'
        f'{len(filtered)} opening(s) found</p>',
        unsafe_allow_html=True
    )

    for job in filtered:
        _job_card(job)
        if st.button("Apply now →", key=f"ap_{job['job_id']}", type="primary"):
            st.session_state.applying_to = job
            st.rerun()


def cand_apply_form():
    job = st.session_state.applying_to

    section_header(
        f"You're applying for {job['title']} at {job.get('company_name', '')}",
        "Review the job details, then upload your resume"
    )
    
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.55);backdrop-filter:blur(10px);
                border:1px solid rgba(255,255,255,0.4);border-radius:14px;
                padding:1.25rem 1.5rem;margin-bottom:1rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.07);">
        <p style="font-size:1rem;font-weight:700;color:#111827;margin:0 0 2px;">
            {job['title']}</p>
        <p style="color:#2563eb;font-size:0.9rem;font-weight:500;margin:0 0 10px;">
            {job.get('company_name', '')}</p>
        <p style="color:#374151;font-size:0.85rem;margin:0 0 4px;">
            <b>Sector:</b> {job['sector']} &nbsp;·&nbsp;
            <b>Education:</b> {job['education_required']} &nbsp;·&nbsp;
            <b>Experience:</b> {job['experience_required']}</p>
        <p style="color:#374151;font-size:0.85rem;margin:0 0 10px;">
            <b>Skills required:</b> {job['skills_required']}</p>
        <p style="color:#4b5563;font-size:0.85rem;margin:0;
                  border-top:1px solid rgba(0,0,0,0.06);padding-top:10px;">
            {job['description']}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(
        '<p style="font-weight:600;color:#111827;font-size:0.9rem;margin-bottom:0.4rem;">'
        'Upload your resume</p>',
        unsafe_allow_html=True
    )
    uploaded = st.file_uploader("PDF or DOCX only", type=["pdf", "docx"],
                                label_visibility="collapsed")

    col1, col2 = st.columns(2)
    with col1:
        submit_clicked = st.button("Submit →", use_container_width=True, type="primary")
    with col2:
        back_clicked = st.button("← Back to jobs", use_container_width=True)

    if back_clicked:
        st.session_state.applying_to = None
        st.rerun()

    if submit_clicked:
        if not uploaded:
            st.warning("Please upload your resume before submitting.")
        else:
            with st.spinner("Submitting application…"):
                files = {"resume": (uploaded.name, uploaded.getvalue(), "application/octet-stream")}
                try:
                    resp = requests.post(
                        f"{API_BASE}/apply_job",
                        data={"job_id": job["job_id"]},
                        files=files,
                        headers=hdrs()
                    )
                except requests.ConnectionError:
                    st.error("Cannot connect to backend.")
                    return

            if resp.status_code == 200:
                st.session_state.flash = "Application submitted successfully!"
                st.session_state.applying_to = None
                st.rerun()
            else:
                # e.g. "You have already applied" — stay on this page so it's visible
                st.error(resp.json().get("detail", "Submission failed."))


def cand_my_applications():
    section_header("My applications", "Track your application status")

    resp = api_get("/my_applications")
    if not resp or resp.status_code != 200:
        st.error("Could not load applications.")
        return

    apps = resp.json().get("applications", [])
    if not apps:
        st.info("You haven't applied to any jobs yet. Browse jobs to get started.")
        return

    status_map = {
        "applied":     ("Applied",     "yellow"),
        "shortlisted": ("Shortlisted", "green"),
        "rejected":    ("Rejected",    "red"),
    }

    for app in apps:
        label, color = status_map.get(app["status"], (app["status"], "gray"))
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.55);backdrop-filter:blur(10px);
                    border:1px solid rgba(255,255,255,0.4);border-radius:14px;
                    padding:1rem 1.25rem;margin-bottom:0.65rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <p style="font-weight:600;font-size:0.95rem;color:#111827;margin:0;">
                        {app['job_title']}</p>
                    <p style="color:#2563eb;font-size:0.82rem;font-weight:500;margin:2px 0 0;">
                        {app.get('company_name', '')}</p>
                    <p style="color:#6b7280;font-size:0.82rem;margin:2px 0 0;">
                        {app['sector']} &nbsp;·&nbsp; Applied {app['applied_at'][:10]}</p>
                </div>
                {badge(label, color)}
            </div>
        </div>""", unsafe_allow_html=True)


def main():
    inject_css()

    if st.session_state.token and st.session_state.user:
        role = st.session_state.user.get("role")
        if role == "HR":
            hr_dashboard()
        elif role == "Candidate":
            candidate_dashboard()
        else:
            logout()
        return

    if st.session_state.page == "register":
        show_register()
    elif st.session_state.page == "forgot":
        show_forgot_password()
    else:
        show_login()


if __name__ == "__main__":
    main()