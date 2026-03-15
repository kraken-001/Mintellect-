"""
ui_helpers.py — общие утилиты для всех страниц Mintellect.
Импортируй в каждой странице:
    from ui_helpers import inject_css, require_auth, sidebar_user_info
"""
import streamlit as st

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
<style>
/* Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@300;400;500&family=Onest:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Onest', sans-serif !important;
}

/* Hide default Streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Page header */
.mint-hero {
    padding: 0 0 24px 0;
    border-bottom: 1px solid #232736;
    margin-bottom: 28px;
}
.mint-hero h1 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2rem !important;
    color: #e8eaf0 !important;
    margin-bottom: 4px !important;
}
.mint-hero p {
    color: #8890a6;
    font-size: 13px;
    margin: 0;
}

/* Cards */
.mint-card {
    background: #13161d;
    border: 1px solid #232736;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 12px;
}

.mint-card:hover {
    border-color: #2e3347;
}

/* Lesson status rows */
.lesson-row {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 16px;
    background: #13161d;
    border-radius: 8px;
    margin-bottom: 8px;
    border: 1px solid #232736;
}

.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-current  { background: #3dffa0; box-shadow: 0 0 8px #3dffa0; }
.dot-next     { background: #e8c76a; }
.dot-previous { background: #4a5168; }
.dot-future   { background: #2e3347; }

.badge {
    font-size: 10px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-left: auto;
}

.badge-current  { background: rgba(61,255,160,.12);  color: #3dffa0; }
.badge-next     { background: rgba(232,199,106,.12); color: #e8c76a; }
.badge-previous { background: rgba(74,81,104,.15);   color: #4a5168; }
.badge-future   { background: #1a1e28;               color: #4a5168; }

/* Note cards */
.note-card {
    background: #13161d;
    border: 1px solid #232736;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
    transition: border-color .15s;
    cursor: pointer;
}
.note-card:hover { border-color: #e8c76a44; }
.note-card-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.note-card-meta  { font-size: 11px; color: #8890a6; font-family: 'DM Mono', monospace; }
.note-card-body  { font-size: 13px; color: #8890a6; margin-top: 6px;
                   overflow: hidden; display: -webkit-box;
                   -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

/* Schedule day column */
.day-box {
    background: #13161d;
    border: 1px solid #232736;
    border-radius: 10px;
    padding: 14px;
    min-height: 160px;
}
.day-box.today { border-color: #e8c76a55; }
.day-label {
    font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
    color: #8890a6; margin-bottom: 12px;
}
.sched-item {
    background: #1a1e28;
    border-left: 2px solid #7b9cff;
    border-radius: 6px;
    padding: 8px 10px;
    margin-bottom: 6px;
    font-size: 12px;
}
.sched-item-subject { font-weight: 500; }
.sched-item-time { color: #4a5168; font-family: 'DM Mono', monospace; font-size: 11px; }

/* Group cards */
.group-card {
    background: #13161d;
    border: 1px solid #232736;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 10px;
}
.group-card-name { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
.group-card-desc { font-size: 13px; color: #8890a6; }

/* Sidebar logo */
.sidebar-logo {
    font-family: 'DM Serif Display', serif;
    font-size: 24px;
    color: #e8c76a;
    padding: 8px 0 20px 0;
    letter-spacing: -0.3px;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #4a5168;
    font-size: 13px;
}
.empty-icon { font-size: 36px; margin-bottom: 10px; }

/* Metric cards */
.metric-card {
    background: #13161d;
    border: 1px solid #232736;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: #e8c76a;
    line-height: 1;
}
.metric-label { font-size: 12px; color: #8890a6; margin-top: 6px; }

/* Attachment chip */
.attach-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: #1a1e28; border: 1px solid #232736;
    border-radius: 6px; padding: 5px 12px;
    font-size: 12px; margin: 4px 4px 4px 0;
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="mint-hero">
        <h1>{title}</h1>
        {"<p>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


# ── AUTH GUARD ────────────────────────────────────────────────────────────────

def require_auth() -> tuple[str, dict]:
    """
    Returns (token, user) or redirects to login.
    Usage:
        token, user = require_auth()
    """
    token = st.session_state.get("token")
    user = st.session_state.get("user")
    if not token or not user:
        st.warning("Необходимо войти в аккаунт.")
        st.page_link("pages/1_Auth.py", label="→ Перейти к входу")
        st.stop()
    return token, user


# ── SIDEBAR ───────────────────────────────────────────────────────────────────

def sidebar_user_info():
    """Render user info + logout button in sidebar."""
    user = st.session_state.get("user")
    if not user:
        return
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🐺 Mintellect</div>',
                    unsafe_allow_html=True)
        st.markdown(f"**{user.get('nickname', '—')}**")
        st.caption(f"ID: {user.get('id', '?')}")
        st.divider()
        if st.button("Выйти", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ── HELPERS ───────────────────────────────────────────────────────────────────

DAYS = ["Понедельник", "Вторник", "Среда", "Четверг",
        "Пятница", "Суббота", "Воскресенье"]
DAYS_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

STATUS_LABELS = {
    "current":  "Сейчас",
    "next":     "Следующий",
    "previous": "Прошёл",
    "future":   "Позже",
}


def render_lesson_row(lesson: dict):
    status = lesson.get("status", "future")
    dot_class   = f"dot-{status}"
    badge_class = f"badge-{status}"
    label       = STATUS_LABELS.get(status, status)
    st.markdown(f"""
    <div class="lesson-row">
        <div class="status-dot {dot_class}"></div>
        <div>
            <div style="font-weight:500;font-size:14px">{lesson['subject']}</div>
            <div style="font-size:12px;color:#8890a6;font-family:'DM Mono',monospace">{lesson['time']}</div>
        </div>
        <span class="badge {badge_class}">{label}</span>
    </div>
    """, unsafe_allow_html=True)


def render_note_card(note: dict) -> bool:
    """Render note preview card. Returns True if clicked (via button)."""
    snippet = note.get("content", "")[:120]
    st.markdown(f"""
    <div class="note-card">
        <div class="note-card-title">{note['title']}</div>
        <div class="note-card-meta">{note.get('date','')}
            {' · ' + DAYS[note['schedule_id'] % 7] if note.get('schedule_id') else ''}
        </div>
        <div class="note-card-body">{snippet}{'…' if len(snippet) == 120 else ''}</div>
    </div>
    """, unsafe_allow_html=True)