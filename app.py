"""
app.py — SocioSaas Pro | Automated Uploader Dashboard
Developer: Ghulam Hussain
Single file — no external modules needed.
Run: streamlit run app.py
"""

import streamlit as st
import sqlite3
import hashlib
import uuid
import json
import re
import pandas as pd
import time
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

ADMIN_EMAIL    = "hklhhklh5@gmail.com"
ADMIN_PASSWORD = "Ghse45*#"
DEVELOPER_NAME = "Ghulam Hussain"
WHATSAPP_NUM   = "923461785207"
DB_PATH        = "sociosaas.db"
APP_TITLE      = "SocioSaas Pro"
SHEET_ID       = "1cWzMMmuJsmYCy9L-GOyAbwSzAmAe7zD9v4a3yUdPJOA"

# Sheet column names — must match your Google Sheet headers exactly
COL_TITLE    = "Video_Title"
COL_PLATFORM = "Platform"
COL_FORMAT   = "Format"
COL_TIME     = "Upload_Time"
COL_STATUS   = "Status"
COL_HASHTAGS = "Hashtags"

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG  (must be first Streamlit call)
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
#  CSS — Luxury dark minimalist
# ══════════════════════════════════════════════════════════════════════════════

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600&family=JetBrains+Mono:wght@400;600&display=swap');

    :root {
        --black:  #080A0F;
        --card:   #0E1118;
        --card2:  #141720;
        --border: #1E2333;
        --bord2:  #2A3050;
        --cyan:   #00D4FF;
        --green:  #00FF88;
        --red:    #FF3B6B;
        --gold:   #FFB800;
        --purple: #7B2FFF;
        --text:   #E2E8F8;
        --muted:  #5A6380;
    }

    html, body, .stApp { background: var(--black) !important; font-family: 'DM Sans', sans-serif; color: var(--text); }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1180px !important; }
    [data-testid="stDecoration"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }

    /* Inputs */
    .stTextInput > div > div > input,
    .stPasswordInput > div > div > input,
    .stTextArea textarea {
        background: var(--card2) !important; border: 1px solid var(--bord2) !important;
        color: var(--text) !important; border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important; font-size: 14px !important;
    }
    .stTextInput > div > div > input:focus,
    .stPasswordInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: var(--cyan) !important; box-shadow: 0 0 0 2px rgba(0,212,255,0.15) !important;
    }
    [data-baseweb="select"] > div {
        background: var(--card2) !important; border-color: var(--bord2) !important;
        color: var(--text) !important; border-radius: 10px !important;
    }
    [data-baseweb="menu"] { background: var(--card) !important; border: 1px solid var(--bord2) !important; border-radius: 10px !important; }
    [data-baseweb="option"]:hover { background: var(--card2) !important; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--cyan), #0099CC) !important;
        color: #000 !important; border: none !important; border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
        font-size: 14px !important; padding: 10px 24px !important; transition: all 0.2s !important;
    }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 24px rgba(0,212,255,0.3) !important; }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: var(--card2) !important; border: 2px dashed var(--bord2) !important;
        border-radius: 14px !important; transition: border-color 0.2s !important;
    }
    [data-testid="stFileUploader"]:hover { border-color: var(--cyan) !important; }

    /* Metrics */
    [data-testid="stMetric"] {
        background: var(--card) !important; border: 1px solid var(--border) !important;
        border-radius: 14px !important; padding: 18px 20px !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Bebas Neue', sans-serif !important; font-size: 34px !important;
        color: var(--cyan) !important; letter-spacing: 1px !important;
    }
    [data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 12px !important; }

    /* Alerts */
    .stSuccess { background: rgba(0,255,136,0.07) !important; border-left: 3px solid var(--green) !important; border-radius: 10px !important; color: var(--text) !important; }
    .stError   { background: rgba(255,59,107,0.07) !important; border-left: 3px solid var(--red) !important;   border-radius: 10px !important; color: var(--text) !important; }
    .stWarning { background: rgba(255,184,0,0.07) !important;  border-left: 3px solid var(--gold) !important;   border-radius: 10px !important; color: var(--text) !important; }
    .stInfo    { background: rgba(0,212,255,0.07) !important;  border-left: 3px solid var(--cyan) !important;   border-radius: 10px !important; color: var(--text) !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--card) !important; border: 1px solid var(--border) !important;
        border-radius: 12px !important; padding: 4px !important; gap: 2px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--muted) !important; font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important; font-size: 13px !important;
        border-radius: 8px !important; padding: 8px 18px !important;
    }
    .stTabs [aria-selected="true"] { background: var(--cyan) !important; color: #000 !important; }

    /* Toggle */
    [data-testid="stToggle"] > label > div:first-child {
        background: var(--bord2) !important;
    }
    [data-testid="stToggle"] > label > div[data-checked="true"] {
        background: var(--cyan) !important;
    }

    /* Progress */
    .stProgress > div > div { background: var(--cyan) !important; border-radius: 4px !important; }
    .stProgress > div { background: var(--border) !important; border-radius: 4px !important; }

    hr { border-color: var(--border) !important; }

    /* ── Custom components ── */

    .card {
        background: var(--card); border: 1px solid var(--border);
        border-radius: 16px; padding: 22px; position: relative; overflow: hidden;
    }
    .card::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, var(--cyan), var(--purple), var(--red));
    }
    .card-title {
        font-family: 'Bebas Neue', sans-serif; font-size: 17px;
        letter-spacing: 2px; color: var(--text); margin-bottom: 3px;
    }
    .card-sub { font-size: 12px; color: var(--muted); margin-bottom: 18px; }

    .tag {
        display: inline-block;
        background: rgba(0,212,255,0.08); border: 1px solid rgba(0,212,255,0.2);
        color: var(--cyan); padding: 3px 10px; border-radius: 100px;
        font-size: 11px; font-family: 'JetBrains Mono', monospace; margin: 2px;
    }

    .plat-badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 12px; border-radius: 100px; font-size: 12px; font-weight: 600; margin: 3px;
    }
    .plat-tt { background: rgba(255,255,255,0.05); border: 1px solid #333; color: #fff; }
    .plat-fb { background: rgba(24,119,242,0.12);  border: 1px solid #1877F2; color: #4C9FFF; }
    .plat-yt { background: rgba(255,0,0,0.1);       border: 1px solid #FF0000; color: #FF5555; }

    .log-row {
        display: grid; grid-template-columns: 2fr 1.2fr 0.7fr 1.2fr 0.6fr;
        padding: 10px 16px; border-bottom: 1px solid var(--border);
        font-size: 13px; align-items: center;
    }
    .log-row:last-child { border-bottom: none; }
    .log-hdr {
        font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase;
        color: var(--muted); font-family: 'JetBrains Mono', monospace; font-weight: 600;
    }

    /* Login */
    .login-logo {
        font-family: 'Bebas Neue', sans-serif; font-size: 52px; letter-spacing: 5px;
        background: linear-gradient(135deg, var(--cyan), var(--purple));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; text-align: center;
    }

    /* WhatsApp float */
    .wa-float {
        position: fixed; bottom: 28px; right: 28px; z-index: 9999;
        background: #25D366; width: 54px; height: 54px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 20px rgba(37,211,102,0.5); text-decoration: none !important;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .wa-float:hover { transform: scale(1.12); box-shadow: 0 6px 28px rgba(37,211,102,0.65); }
    </style>
    """, unsafe_allow_html=True)

    # WhatsApp floating button — always visible
    st.markdown(f"""
    <a class="wa-float" href="https://wa.me/{WHATSAPP_NUM}" target="_blank" title="WhatsApp Support">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="white">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>
    </a>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DATABASE  (SQLite — users only, no external file dependency)
# ══════════════════════════════════════════════════════════════════════════════

def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_db(); c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TEXT
        )
    """)
    # Ensure admin account always exists
    admin_hash = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()
    c.execute(
        "INSERT OR IGNORE INTO users (email, password, name, created_at) VALUES (?,?,?,?)",
        (ADMIN_EMAIL, admin_hash, "Ghulam Hussain", datetime.now().isoformat())
    )
    conn.commit(); conn.close()

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def login_user(email: str, password: str):
    conn = get_db(); c = conn.cursor()
    c.execute(
        "SELECT id, email, name, created_at FROM users WHERE email=? AND password=?",
        (email.strip().lower(), hash_pw(password))
    )
    row = c.fetchone(); conn.close()
    if not row: return None
    return {"id": row[0], "email": row[1], "name": row[2], "created_at": row[3]}


# ══════════════════════════════════════════════════════════════════════════════
#  GOOGLE SHEETS  (st.connection — zero JSON files uploaded to GitHub)
# ══════════════════════════════════════════════════════════════════════════════

def _gs():
    """Returns the gsheets connection from Streamlit secrets."""
    return st.connection("gsheets", type="GSheetsConnection")

@st.cache_data(ttl=30)
def load_log() -> pd.DataFrame:
    """Reads upload log from Google Sheets, cached 30 s."""
    try:
        df = _gs().read(spreadsheet=SHEET_ID, ttl=30)
        return df.fillna("")
    except Exception:
        return pd.DataFrame(columns=[COL_TITLE, COL_PLATFORM, COL_FORMAT,
                                      COL_TIME, COL_STATUS, COL_HASHTAGS])

def append_log(title: str, platform: str, fmt: str, hashtags: str, status: str = "✅ Success") -> bool:
    """Appends one row to the Google Sheet upload log."""
    try:
        conn = _gs()
        df = conn.read(spreadsheet=SHEET_ID, ttl=0)
        new = pd.DataFrame([{
            COL_TITLE:    title,
            COL_PLATFORM: platform,
            COL_FORMAT:   fmt,
            COL_TIME:     datetime.now().strftime("%Y-%m-%d %H:%M"),
            COL_STATUS:   status,
            COL_HASHTAGS: hashtags,
        }])
        conn.update(spreadsheet=SHEET_ID, data=pd.concat([df, new], ignore_index=True))
        load_log.clear()
        return True
    except Exception as e:
        st.caption(f"Sheet log note: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
#  HASHTAG ENGINE
# ══════════════════════════════════════════════════════════════════════════════

_TAGS = {
    "music":      ["#music","#newsong","#viral","#trending","#foryou","#fyp","#hitsong","#musicvideo","#nowplaying","#banger"],
    "comedy":     ["#comedy","#funny","#lol","#memes","#humor","#viral","#foryou","#fyp","#laughing","#trending"],
    "education":  ["#education","#learn","#knowledge","#study","#howto","#tutorial","#tips","#facts","#viral","#fyp"],
    "gaming":     ["#gaming","#gamer","#gameplay","#viral","#trending","#fyp","#twitch","#xbox","#playstation","#games"],
    "motivation": ["#motivation","#success","#mindset","#hustle","#grind","#viral","#fyp","#inspire","#goals","#winning"],
    "lifestyle":  ["#lifestyle","#vlog","#daily","#life","#viral","#trending","#fyp","#aesthetic","#vibes","#explore"],
    "tech":       ["#tech","#technology","#ai","#coding","#software","#viral","#fyp","#gadgets","#innovation","#trending"],
    "business":   ["#business","#entrepreneur","#money","#success","#startup","#viral","#fyp","#marketing","#hustle","#rich"],
    "fitness":    ["#fitness","#gym","#workout","#health","#bodybuilding","#viral","#fyp","#gains","#fit","#training"],
    "food":       ["#food","#foodie","#recipe","#cooking","#yummy","#viral","#fyp","#chef","#delicious","#eat"],
    "travel":     ["#travel","#explore","#wanderlust","#adventure","#trip","#viral","#fyp","#vacation","#tourism","#world"],
    "fashion":    ["#fashion","#style","#ootd","#outfit","#trendy","#viral","#fyp","#aesthetic","#drip","#swag"],
    "general":    ["#viral","#trending","#foryou","#fyp","#explore","#reels","#shorts","#content","#share","#follow"],
}

_STOP = {"a","an","the","is","it","in","on","at","to","for","of","and","or","my","me","you","this","that","with","be","are","was","were"}

def gen_tags(title: str, category: str) -> list[str]:
    key  = category.lower() if category.lower() in _TAGS else "general"
    pool = list(_TAGS[key])
    for word in re.findall(r"[a-zA-Z0-9]+", title):
        if len(word) > 3 and word.lower() not in _STOP:
            pool.append(f"#{word.lower()}")
    seen = set(); out = []
    for t in pool:
        if t not in seen: seen.add(t); out.append(t)
    return out[:20]


# ══════════════════════════════════════════════════════════════════════════════
#  UPLOAD SIMULATOR
#  Replace simulate_upload() internals with real API calls once you have
#  approved developer credentials for TikTok / Meta / Google.
# ══════════════════════════════════════════════════════════════════════════════

_PLAT_INFO = {
    "TikTok":          {"icon": "🎵", "formats": ["mp4"]},
    "Facebook Reels":  {"icon": "📘", "formats": ["mp4"]},
    "YouTube Shorts":  {"icon": "▶️", "formats": ["mp4", "mp3"]},
}

def simulate_upload(platform: str, title: str, fmt: str, fname: str) -> dict:
    time.sleep(0.5)
    info = _PLAT_INFO.get(platform)
    if not info:
        return {"ok": False, "message": f"Unknown platform: {platform}"}
    if fmt.lower() not in info["formats"]:
        return {"ok": False, "message": f"{platform} does not support {fmt.upper()}"}
    # ── Swap this stub for your real API call ─────────────────────────────────
    # TikTok:   POST https://open-api.tiktok.com/share/video/upload/
    # Facebook: POST https://graph.facebook.com/v18.0/{page-id}/video_reels
    # YouTube:  POST https://www.googleapis.com/upload/youtube/v3/videos
    # ─────────────────────────────────────────────────────────────────────────
    return {"ok": True, "message": f"{info['icon']} **{platform}** · `{fname}` · {fmt.upper()} queued"}


def run_uploads(title: str, platforms: list, formats: list, fname: str, hashtags: str):
    jobs = [(p, f) for p in platforms for f in formats]
    bar  = st.progress(0, text="Preparing…")
    results = []
    for i, (p, f) in enumerate(jobs):
        bar.progress(i / len(jobs), text=f"Uploading to {p} ({f})…")
        r = simulate_upload(p, title, f, fname)
        append_log(title, p, f, hashtags, "✅ Success" if r["ok"] else "❌ Failed")
        results.append((p, f, r))
    bar.progress(1.0, text="Done!")
    time.sleep(0.3); bar.empty()

    ok_count = sum(1 for _, _, r in results if r["ok"])
    st.success(f"✅ **{ok_count}/{len(jobs)} uploads queued successfully**")
    for _, _, r in results:
        color = "#00FF88" if r["ok"] else "#FF3B6B"
        st.markdown(f"<div style='font-size:13px;color:{color};padding:2px 0;'>{'✓' if r['ok'] else '✗'} {r['message']}</div>", unsafe_allow_html=True)
    st.caption(f"Logged to Google Sheets · {datetime.now().strftime('%H:%M:%S')}")


# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════

def render_login():
    inject_css()
    st.markdown("<div style='min-height:8vh;'></div>", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown(f"""
        <div style='background:var(--card);border:1px solid var(--border);
                    border-radius:20px;padding:40px 36px;position:relative;overflow:hidden;'>
            <div style='position:absolute;top:0;left:0;right:0;height:3px;
                        background:linear-gradient(90deg,#00D4FF,#7B2FFF,#FF3B6B);'></div>
            <div class='login-logo'>SOCIO<span style='color:#FF3B6B;'>SAAS</span></div>
            <div style='text-align:center;color:var(--muted);font-size:12px;
                        letter-spacing:1px;margin-bottom:30px;'>AUTOMATED UPLOADER DASHBOARD</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="your@email.com",
                               key="l_email", label_visibility="collapsed")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        pw = st.text_input("Password", type="password", placeholder="Password",
                            key="l_pw", label_visibility="collapsed")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Sign In →", use_container_width=True, key="btn_signin"):
            if not email or not pw:
                st.warning("Enter email and password.")
            else:
                user = login_user(email, pw)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Incorrect email or password.")

        st.markdown(f"""
        <div style='text-align:center;margin-top:18px;font-size:12px;color:var(--muted);'>
            Need help?
            <a href='https://wa.me/{WHATSAPP_NUM}' target='_blank'
               style='color:#25D366;text-decoration:none;font-weight:600;'>
               WhatsApp Support
            </a>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def render_dashboard(user: dict):
    inject_css()

    # ── Top bar ───────────────────────────────────────────────────────────────
    initial = (user.get("name") or "A")[0].upper()
    c_logo, _, c_user = st.columns([3, 5, 2])
    with c_logo:
        st.markdown("""
        <div style='font-family:"Bebas Neue",sans-serif;font-size:24px;
                    letter-spacing:3px;padding-top:4px;'>
            SOCIO<span style='color:#FF3B6B;'>SAAS</span>
            <span style='font-size:10px;color:#5A6380;letter-spacing:1px;margin-left:6px;'>PRO</span>
        </div>
        """, unsafe_allow_html=True)
    with c_user:
        st.markdown(f"""
        <div style='display:flex;align-items:center;justify-content:flex-end;
                    gap:10px;padding-top:4px;font-size:13px;color:var(--muted);'>
            <span>{user.get('name','Admin')}</span>
            <div style='width:30px;height:30px;border-radius:50%;
                        background:linear-gradient(135deg,#00D4FF,#7B2FFF);
                        display:flex;align-items:center;justify-content:center;
                        font-size:12px;font-weight:700;color:#000;'>{initial}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Logout", key="btn_logout"):
            del st.session_state.user
            st.rerun()

    st.markdown("<hr style='margin:4px 0 24px;'>", unsafe_allow_html=True)

    # ── Metrics ───────────────────────────────────────────────────────────────
    log_df = load_log()
    total   = len(log_df)
    success = int(log_df[COL_STATUS].str.contains("✅", na=False).sum()) if total else 0
    tt_cnt  = int(log_df[COL_PLATFORM].str.contains("TikTok", na=False).sum()) if total else 0
    yt_cnt  = int(log_df[COL_PLATFORM].str.contains("YouTube", na=False).sum()) if total else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Uploads",  total)
    m2.metric("Successful",     success)
    m3.metric("TikTok Posts",   tt_cnt)
    m4.metric("YouTube Shorts", yt_cnt)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    t_upload, t_log, t_guide = st.tabs(["🚀 Upload", "📋 Upload Log", "📖 API Guide"])

    # ════════════════════════════
    #  TAB — UPLOAD
    # ════════════════════════════
    with t_upload:
        left, right = st.columns([1.05, 1], gap="large")

        with left:
            st.markdown("""
            <div class='card-title'>UPLOAD CONTENT</div>
            <div class='card-sub'>Configure format, platform targets, and upload</div>
            """, unsafe_allow_html=True)

            # Format toggles
            fc1, fc2 = st.columns(2)
            with fc1: use_mp4 = st.toggle("🎬 MP4  Video", value=True,  key="t_mp4")
            with fc2: use_mp3 = st.toggle("🎵 MP3  Audio", value=False, key="t_mp3")

            if use_mp4 and use_mp3:
                fmts = ["mp4", "mp3"]
                st.info("Both formats selected — separate jobs per format.")
            elif use_mp4:
                fmts = ["mp4"]
            elif use_mp3:
                fmts = ["mp3"]
            else:
                st.warning("Select at least one format.")
                fmts = ["mp4"]

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            # File uploader
            exts = list({"mp4","mov","avi","mkv"} | ({"mp3","wav","m4a"} if "mp3" in fmts else set()))
            media = st.file_uploader("Drop media file here", type=exts, key="media_up",
                                     help="MP4/MOV/AVI for video · MP3/WAV for audio")

            # Title
            title = st.text_input("Content Title", placeholder="Enter your title…", key="c_title")

            # Category
            cat = st.selectbox("Content Category",
                ["General","Music","Comedy","Education","Gaming","Motivation",
                 "Lifestyle","Tech","Business","Fitness","Food","Travel","Fashion"],
                key="c_cat")

            # Platform checkboxes
            st.markdown("""
            <div style='font-size:11px;color:var(--muted);letter-spacing:1.5px;
                        margin:12px 0 8px;font-family:"JetBrains Mono",monospace;'>
                SELECT PLATFORMS
            </div>
            """, unsafe_allow_html=True)
            pc1, pc2, pc3 = st.columns(3)
            with pc1: p_tt = st.checkbox("🎵 TikTok",        value=True, key="p_tt")
            with pc2: p_fb = st.checkbox("📘 Facebook Reels",value=True, key="p_fb")
            with pc3: p_yt = st.checkbox("▶️ YouTube Shorts",value=True, key="p_yt")
            plats = ([("TikTok" if p_tt else None),
                      ("Facebook Reels" if p_fb else None),
                      ("YouTube Shorts" if p_yt else None)])
            plats = [p for p in plats if p]

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            go = st.button("⚡ Upload Now", key="btn_go", use_container_width=True)

        with right:
            st.markdown("""
            <div class='card-title'>PREVIEW & HASHTAGS</div>
            <div class='card-sub'>Auto-generated viral tags from title + category</div>
            """, unsafe_allow_html=True)

            if title.strip():
                tags = gen_tags(title, cat)
                tags_str = " ".join(tags)
                tag_html = "".join(f"<span class='tag'>{t}</span>" for t in tags)
                st.markdown(f"""
                <div style='background:var(--card2);border:1px solid var(--border);
                            border-radius:12px;padding:16px;'>
                    <div style='font-size:10px;color:var(--muted);letter-spacing:1.5px;
                                margin-bottom:10px;font-family:"JetBrains Mono",monospace;'>
                        {len(tags)} HASHTAGS GENERATED
                    </div>
                    {tag_html}
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                st.markdown("""
                <div style='font-size:10px;color:var(--muted);letter-spacing:1.5px;
                            margin-bottom:8px;font-family:"JetBrains Mono",monospace;'>
                    TARGET PLATFORMS
                </div>
                """, unsafe_allow_html=True)
                cls_map = {"TikTok":"plat-tt","Facebook Reels":"plat-fb","YouTube Shorts":"plat-yt"}
                icon_map= {"TikTok":"🎵","Facebook Reels":"📘","YouTube Shorts":"▶️"}
                for p in plats:
                    st.markdown(f"<span class='plat-badge {cls_map[p]}'>{icon_map[p]} {p}</span>", unsafe_allow_html=True)

                st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                for f in fmts:
                    col = "#00D4FF" if f == "mp4" else "#FFB800"
                    st.markdown(f"""
                    <span style='background:rgba(255,255,255,0.04);border:1px solid {col};
                                 color:{col};padding:4px 14px;border-radius:6px;
                                 font-family:"JetBrains Mono",monospace;font-size:12px;
                                 font-weight:700;margin-right:6px;'>
                        {f.upper()}
                    </span>
                    """, unsafe_allow_html=True)
            else:
                tags_str = ""
                st.markdown("""
                <div style='background:var(--card2);border:2px dashed var(--border);
                            border-radius:12px;padding:48px 20px;text-align:center;
                            color:var(--muted);font-size:13px;'>
                    Enter a title on the left<br>to preview hashtags here
                </div>
                """, unsafe_allow_html=True)

        # Handle upload click
        if go:
            if not title.strip():
                st.error("Please enter a title.")
            elif not plats:
                st.error("Select at least one platform.")
            else:
                fname = media.name if media else "demo_upload"
                ht = tags_str if tags_str else " ".join(gen_tags(title, cat))
                if not media:
                    st.warning("No file attached — logging a demo entry.")
                run_uploads(title.strip(), plats, fmts, fname, ht)

    # ════════════════════════════
    #  TAB — LOG
    # ════════════════════════════
    with t_log:
        st.markdown("""
        <div class='card-title'>UPLOAD LOG</div>
        <div class='card-sub'>Every upload is automatically synced to your Google Sheet</div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Refresh", key="btn_refresh"):
            load_log.clear(); st.rerun()

        fresh = load_log()
        if fresh.empty:
            st.markdown("""
            <div style='text-align:center;padding:60px;color:var(--muted);
                        background:var(--card);border-radius:14px;
                        border:1px solid var(--border);font-size:14px;'>
                <div style='font-size:36px;margin-bottom:10px;'>📋</div>
                No uploads logged yet.
            </div>
            """, unsafe_allow_html=True)
        else:
            rows_html = ""
            for _, row in fresh.tail(60).iloc[::-1].iterrows():
                p  = str(row.get(COL_PLATFORM,""))
                ic = "🎵" if "TikTok" in p else ("📘" if "Facebook" in p else "▶️")
                s  = str(row.get(COL_STATUS,""))
                sd = "🟢" if "✅" in s else ("🔴" if "❌" in s else "🟡")
                tt = str(row.get(COL_TITLE,""))[:42]
                tm = str(row.get(COL_TIME,""))[:16]
                fm = str(row.get(COL_FORMAT,"")).upper()
                rows_html += f"""
                <div class='log-row'>
                    <span style='overflow:hidden;text-overflow:ellipsis;
                                 white-space:nowrap;' title='{tt}'>{tt}</span>
                    <span>{ic} {p}</span>
                    <span style='font-family:"JetBrains Mono",monospace;
                                 font-size:11px;color:#00D4FF;'>{fm}</span>
                    <span style='font-size:12px;color:var(--muted);'>{tm}</span>
                    <span>{sd}</span>
                </div>"""

            st.markdown(f"""
            <div style='border:1px solid var(--border);border-radius:12px;overflow:hidden;'>
                <div style='background:var(--card2);'>
                    <div class='log-row log-hdr'>
                        <span>TITLE</span><span>PLATFORM</span>
                        <span>FORMAT</span><span>TIME</span><span>STATUS</span>
                    </div>
                </div>
                <div style='background:var(--card);max-height:440px;overflow-y:auto;'>
                    {rows_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ════════════════════════════
    #  TAB — API GUIDE
    # ════════════════════════════
    with t_guide:
        st.markdown("""
        <div class='card-title'>API INTEGRATION GUIDE</div>
        <div class='card-sub'>Steps to activate real uploads — replace simulate_upload() with these calls</div>
        """, unsafe_allow_html=True)

        g1, g2, g3 = st.columns(3)
        guides = [
            ("plat-tt","🎵","TikTok",
             "1. Apply at <b>developers.tiktok.com</b><br>"
             "2. Create app → get <code>client_key</code> + <code>client_secret</code><br>"
             "3. Enable <b>Video Upload</b> scope<br>"
             "4. Add to Streamlit Secrets:<br>"
             "<code>TIKTOK_CLIENT_KEY<br>TIKTOK_CLIENT_SECRET</code><br>"
             "5. API: <code>POST /share/video/upload/</code>"),
            ("plat-fb","📘","Facebook Reels",
             "1. Go to <b>developers.facebook.com</b><br>"
             "2. Create app → add <b>Pages + Reels</b><br>"
             "3. Get <code>page_access_token</code> + <code>page_id</code><br>"
             "4. Add to Streamlit Secrets:<br>"
             "<code>FB_PAGE_ID<br>FB_ACCESS_TOKEN</code><br>"
             "5. API: <code>POST /{page-id}/video_reels</code>"),
            ("plat-yt","▶️","YouTube Shorts",
             "1. <b>console.cloud.google.com</b><br>"
             "2. Enable <b>YouTube Data API v3</b><br>"
             "3. Create OAuth2 Web credentials<br>"
             "4. Add to Streamlit Secrets:<br>"
             "<code>YT_CLIENT_ID<br>YT_CLIENT_SECRET</code><br>"
             "5. API: <code>POST /upload/youtube/v3/videos</code>"),
        ]
        for col, (badge, icon, name, body) in zip([g1,g2,g3], guides):
            with col:
                st.markdown(f"""
                <div class='card' style='height:100%;'>
                    <span class='plat-badge {badge}' style='margin-bottom:12px;
                        display:inline-flex;'>{icon} {name}</span>
                    <div style='font-size:13px;color:var(--muted);line-height:1.9;'>
                        {body}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 All upload simulation is in `simulate_upload()` inside app.py. Replace each platform branch with your real API calls. No other file changes needed.")


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    init_db()
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        render_login()
    else:
        render_dashboard(st.session_state.user)

if __name__ == "__main__":
    main()
