import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="منظومة مراجعة التشريعات",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&family=Amiri:wght@400;700&display=swap');

/* ══ LIGHT ══ */
:root {
    --bg:#f0f4f8; --bg2:#ffffff; --bg3:#e8edf5; --card:#ffffff;
    --border:#d0d9ea; --border2:#b0bdd4;
    --accent:#2563eb; --accent2:#4f46e5; --accentlt:#eff4ff; --purple-lt:#f0edff;
    --green:#15803d; --green-lt:#f0fdf4; --green-border:#bbf7d0;
    --orange:#c2550a; --orange-lt:#fff7ed; --orange-border:#fed7aa;
    --text:#0f172a; --text2:#475569; --text3:#94a3b8;
    --law-bg:linear-gradient(135deg,#eff6ff,#f0edff);
    --law-border:#bfdbfe; --val-bg:#f1f5f9;
    --shadow:0 1px 12px rgba(15,23,42,0.08); --shadow-md:0 4px 24px rgba(15,23,42,0.12);
    --radius:14px; --progress-bg:#e2e8f0; --input-bg:#ffffff;
    --stat-num-laws:#2563eb; --stat-num-rows:#475569;
    --stat-num-pct:#4f46e5; --stat-num-ok:#15803d; --stat-num-edit:#c2550a;
}

/* ══ DARK ══ */
@media (prefers-color-scheme:dark){:root{
    --bg:#0c1117; --bg2:#131920; --bg3:#192130; --card:#111827;
    --border:#1e2d45; --border2:#2a3f5f;
    --accent:#3b82f6; --accent2:#818cf8; --accentlt:#1e2d45; --purple-lt:#1a1a35;
    --green:#22c55e; --green-lt:#052e16; --green-border:#14532d;
    --orange:#fb923c; --orange-lt:#1c0a00; --orange-border:#7c2d12;
    --text:#f1f5f9; --text2:#94a3b8; --text3:#475569;
    --law-bg:linear-gradient(135deg,#1e2d45,#1a1a35);
    --law-border:#1e3a5f; --val-bg:#192130;
    --shadow:0 1px 12px rgba(0,0,0,0.4); --shadow-md:0 4px 24px rgba(0,0,0,0.5);
    --progress-bg:#192130; --input-bg:#131920;
    --stat-num-laws:#3b82f6; --stat-num-rows:#94a3b8;
    --stat-num-pct:#818cf8; --stat-num-ok:#22c55e; --stat-num-edit:#fb923c;
}}
[data-theme="dark"]{
    --bg:#0c1117; --bg2:#131920; --bg3:#192130; --card:#111827;
    --border:#1e2d45; --border2:#2a3f5f;
    --accent:#3b82f6; --accent2:#818cf8; --accentlt:#1e2d45; --purple-lt:#1a1a35;
    --green:#22c55e; --green-lt:#052e16; --green-border:#14532d;
    --orange:#fb923c; --orange-lt:#1c0a00; --orange-border:#7c2d12;
    --text:#f1f5f9; --text2:#94a3b8; --text3:#475569;
    --law-bg:linear-gradient(135deg,#1e2d45,#1a1a35);
    --law-border:#1e3a5f; --val-bg:#192130;
    --shadow:0 1px 12px rgba(0,0,0,0.4); --shadow-md:0 4px 24px rgba(0,0,0,0.5);
    --progress-bg:#192130; --input-bg:#131920;
    --stat-num-laws:#3b82f6; --stat-num-rows:#94a3b8;
    --stat-num-pct:#818cf8; --stat-num-ok:#22c55e; --stat-num-edit:#fb923c;
}

html,body,[class*="css"]{
    font-family:'Tajawal',sans-serif !important;
    direction:rtl;
    background-color:var(--bg) !important;
    color:var(--text) !important;
}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:0 !important;max-width:100% !important;}
.main > div{padding:1.5rem 2rem 3rem 2rem !important;max-width:1000px !important;margin:0 auto !important;}

/* ── TOP BAR ── */
.top-bar{
    background:var(--card);
    border-bottom:1px solid var(--border);
    padding:0.7rem 2rem;
    display:flex;
    justify-content:space-between;
    align-items:center;
    position:sticky;top:0;z-index:100;
    box-shadow:var(--shadow);
}
.top-bar-title{font-family:'Amiri',serif;font-size:1.2rem;font-weight:700;color:var(--accent);}
.top-bar-user{font-size:0.88rem;color:var(--text2);}
.sync-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-left:6px;}
.sync-ok{background:#22c55e;}
.sync-fail{background:#ef4444;}

/* ── HERO ── */
.hero{
    background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 50%,#4338ca 100%);
    border-radius:18px;padding:1.8rem 2.5rem;margin-bottom:1.5rem;
    text-align:center;position:relative;overflow:hidden;box-shadow:var(--shadow-md);
}
.hero h1{font-family:'Amiri',serif;font-size:2rem;font-weight:700;color:#fff;margin:0 0 0.2rem 0;}
.hero p{color:rgba(255,255,255,0.75);font-size:0.9rem;margin:0;}

/* ── LAW CARD ── */
.law-card{
    background:var(--law-bg);
    border:1px solid var(--law-border);
    border-right:5px solid var(--accent);
    border-radius:var(--radius);
    padding:1.5rem 2rem;
    margin-bottom:1.2rem;
    box-shadow:var(--shadow);
}
.law-counter{
    font-size:0.75rem;font-weight:700;
    color:var(--accent);letter-spacing:1.5px;
    text-transform:uppercase;margin-bottom:0.5rem;
}
.law-title{
    font-family:'Amiri',serif;
    font-size:1.55rem;font-weight:700;
    color:#1e3a8a;line-height:1.7;
    margin-bottom:0.8rem;
}
[data-theme="dark"] .law-title, @media(prefers-color-scheme:dark){.law-title{color:#93c5fd;}}
.law-meta-row{
    display:flex;gap:1.5rem;flex-wrap:wrap;
    font-size:0.85rem;
}
.law-meta-item{
    display:flex;align-items:center;gap:6px;
    background:rgba(255,255,255,0.5);
    border:1px solid var(--border);
    border-radius:8px;padding:4px 12px;
    color:var(--text2);font-weight:500;
}
.law-meta-item b{color:var(--text);}

/* ── EDIT SECTION ── */
.edit-section{
    background:var(--card);
    border:1px solid var(--border);
    border-radius:var(--radius);
    padding:1.5rem;
    margin-bottom:1rem;
    box-shadow:var(--shadow);
}
.edit-title{
    font-size:0.8rem;font-weight:700;
    color:var(--text3);text-transform:uppercase;
    letter-spacing:1px;margin-bottom:1rem;
    border-bottom:1px solid var(--border);
    padding-bottom:8px;
}

/* ── SCOPE BUTTONS ── */
.scope-btn-row{display:flex;gap:0.8rem;margin-bottom:0.5rem;}

/* ── PROGRESS ── */
.progress-wrap{
    background:var(--card);border:1px solid var(--border);
    border-radius:var(--radius);padding:0.8rem 1.2rem;
    margin-bottom:1rem;box-shadow:var(--shadow);
}
.progress-bar-outer{background:var(--progress-bg);border-radius:99px;height:8px;overflow:hidden;margin-top:6px;}
.progress-bar-inner{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width 0.6s ease;}

/* ── STAT CARDS ── */
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:0.9rem 1rem;text-align:center;box-shadow:var(--shadow);}
.stat-num{font-size:1.8rem;font-weight:800;line-height:1.1;}
.stat-lbl{font-size:0.75rem;color:var(--text2);margin-top:3px;}

/* ── BADGE ── */
.badge{display:inline-block;padding:4px 14px;border-radius:20px;font-size:0.78rem;font-weight:700;}
.badge-new{background:var(--bg3);color:var(--text3);border:1px solid var(--border2);}
.badge-jamea{background:var(--accentlt);color:var(--accent);border:1px solid #bfdbfe;}
.badge-moayyan{background:var(--purple-lt);color:#4f46e5;border:1px solid #c4b5fd;}

/* ── DONE ── */
.done-banner{
    background:linear-gradient(135deg,var(--green-lt),var(--accentlt));
    border:1px solid var(--green-border);border-radius:var(--radius);
    padding:2rem;text-align:center;margin:1rem 0;
}
.done-banner h2{color:var(--green);font-family:'Amiri',serif;font-size:2rem;margin:0 0 0.4rem 0;}

/* ── LOGIN ── */
.login-box{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:2.2rem 2rem;box-shadow:var(--shadow-md);}

/* ── INPUTS ── */
.stButton>button{font-family:'Tajawal',sans-serif !important;font-weight:700 !important;border-radius:10px !important;padding:0.6rem 1.5rem !important;font-size:0.95rem !important;transition:all 0.2s !important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{font-family:'Tajawal',sans-serif !important;background:var(--input-bg) !important;border:1.5px solid var(--border) !important;color:var(--text) !important;border-radius:8px !important;direction:rtl !important;font-size:0.97rem !important;}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:var(--accent) !important;box-shadow:0 0 0 3px rgba(59,130,246,0.15) !important;}
.stSelectbox>div>div{background:var(--input-bg) !important;border:1.5px solid var(--border) !important;color:var(--text) !important;border-radius:8px !important;direction:rtl !important;}
.stTextInput label,.stTextArea label,.stSelectbox label,.stRadio label{color:var(--text2) !important;font-family:'Tajawal',sans-serif !important;font-size:0.87rem !important;font-weight:600 !important;}
.stRadio>div{gap:0.6rem !important;}
.stRadio>div>label{background:var(--card) !important;border:1.5px solid var(--border) !important;border-radius:10px !important;padding:0.65rem 1.2rem !important;transition:all 0.2s !important;font-size:0.95rem !important;}
.stRadio>div>label:hover{border-color:var(--accent) !important;}
hr{border-color:var(--border) !important;margin:1rem 0 !important;}
.stAlert{border-radius:var(--radius) !important;font-family:'Tajawal',sans-serif !important;}
</style>
""", unsafe_allow_html=True)

# ─── Imports ───────────────────────────────────────────────────────────────────
from auth  import require_login, logout, greeting_page
from admin import admin_panel
from sheets import (
    load_user_laws, save_law_audit, invalidate_laws,
    get_entity_names, get_parent_ministries,
)

# ─── Session Defaults ──────────────────────────────────────────────────────────
for k, v in [
    ("logged_in",False), ("username",""), ("role",""),
    ("spreadsheet",None), ("show_greeting",False),
    ("laws",None), ("cur_law",0),
    ("streak",0), ("last_sync",None), ("sync_ok",True),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Auth Gate ─────────────────────────────────────────────────────────────────
require_login()

# ─── TOP BAR ───────────────────────────────────────────────────────────────────
tb_left, tb_right = st.columns([8, 1])
with tb_left:
    sync_html = ""
    if st.session_state.get("last_sync"):
        dot = "sync-ok" if st.session_state.sync_ok else "sync-fail"
        sync_html = f'<span class="sync-dot {dot}"></span>{st.session_state.last_sync}'
    role_lbl = "مدير" if st.session_state.role=="admin" else "مستشار قانوني"
    st.markdown(f"""
    <div style="font-size:0.88rem;color:var(--text2);padding:0.3rem 0">
      ⚖️ <b style="color:var(--text)">{st.session_state.username}</b>
      &nbsp;·&nbsp; {role_lbl}
      &nbsp;&nbsp; {sync_html}
    </div>
    """, unsafe_allow_html=True)
with tb_right:
    if st.button("خروج 🚪", use_container_width=True):
        logout()

# ─── ADMIN ─────────────────────────────────────────────────────────────────────
if st.session_state.role == "admin":
    admin_panel()
    st.stop()

# ─── LOAD LAWS ─────────────────────────────────────────────────────────────────
if st.session_state.laws is None:
    with st.spinner("جارٍ تحميل قوانينك..."):
        laws = load_user_laws(st.session_state.username)
    if not laws:
        invalidate_laws()
        laws = load_user_laws(st.session_state.username)
    if not laws:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem">
          <div style="font-size:3rem;margin-bottom:1rem">⏳</div>
          <h3 style="color:var(--text)">لم يتم تعيين قوانين لك بعد</h3>
          <p style="color:var(--text2)">الرجاء التواصل مع المدير لتعيين القوانين</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 إعادة المحاولة"):
            st.rerun()
        st.stop()

    # Group by unique law (leg_name), preserving order
    seen, groups = {}, []
    for r in laws:
        n = r["leg_name"]
        if n not in seen:
            seen[n] = len(groups)
            groups.append(r)

    st.session_state.laws = groups

    # ── Resume: find first unreviewed ──
    for i, law in enumerate(groups):
        if law.get("audit_status","") == "لم يُراجع":
            st.session_state.cur_law = i
            break
    else:
        st.session_state.cur_law = len(groups) - 1

# ─── STATS ─────────────────────────────────────────────────────────────────────
laws       = st.session_state.laws
total_laws = len(laws)
reviewed   = sum(1 for l in laws if l.get("audit_status","") != "لم يُراجع")
remaining  = total_laws - reviewed
pct        = int(reviewed / total_laws * 100) if total_laws else 0

# ─── GREETING ──────────────────────────────────────────────────────────────────
if st.session_state.show_greeting:
    greeting_page(
        username = st.session_state.username,
        total    = total_laws,
        reviewed = reviewed,
    )
    st.stop()

# ─── MAIN AUDIT UI ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>⚖️ مراجعة التشريعات</h1>
  <p>راجع كل قانون وحدد نطاقه والجهة المعنية</p>
</div>
""", unsafe_allow_html=True)

# ── Progress ──
streak_html = ""
if st.session_state.streak >= 10:
    streak_html = f'<span style="color:#ea580c;font-weight:700;margin-right:8px">🔥 {st.session_state.streak} متتالية!</span>'
st.markdown(f"""
<div class="progress-wrap">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <span style="font-weight:700;font-size:0.88rem">
      {streak_html}📊 {reviewed} / {total_laws} قانون مراجَع
    </span>
    <span style="font-size:0.82rem;color:var(--text3)">{pct}% مكتمل</span>
  </div>
  <div class="progress-bar-outer">
    <div class="progress-bar-inner" style="width:{pct}%"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Done? ──
if reviewed == total_laws and total_laws > 0:
    st.markdown("""<div class="done-banner">
      <h2>🎉 أنجزت جميع قوانينك!</h2>
      <p>عمل رائع يا مستشار! تواصل مع المدير لمعرفة الخطوة التالية.</p>
    </div>""", unsafe_allow_html=True)

# ── Law Selector ──
cur_law = st.session_state.cur_law

def law_label(i, law):
    s = law.get("audit_status","")
    icon = {"لم يُراجع":"○","جميع الجهات":"🌐","جهة معينة":"🏢"}.get(s,"○")
    short = law["leg_name"][:55] + ("..." if len(law["leg_name"])>55 else "")
    return f"{icon}  {i+1}. {short}"

law_options = [law_label(i,l) for i,l in enumerate(laws)]
selected    = st.selectbox(
    "اختر القانون للمراجعة",
    options=law_options,
    index=cur_law,
    label_visibility="collapsed",
)
new_idx = law_options.index(selected)
if new_idx != cur_law:
    st.session_state.cur_law = new_idx
    st.rerun()

cur_law = st.session_state.cur_law
law     = laws[cur_law]

# ── Status Badge ──
bmap  = {"لم يُراجع":"badge-new","جميع الجهات":"badge-jamea","جهة معينة":"badge-moayyan"}
badge = bmap.get(law.get("audit_status","لم يُراجع"),"badge-new")
badge_txt = law.get("audit_status","لم يُراجع")

# ─── LAW CARD (read-only info) ─────────────────────────────────────────────────
st.markdown(f"""
<div class="law-card">
  <div class="law-counter">القانون {cur_law + 1} من {total_laws}</div>
  <div class="law-title">{law["leg_name"]}</div>
  <div class="law-meta-row">
    <div class="law-meta-item"><span>📋 رقم القانون:</span><b>{law.get("leg_number","—")}</b></div>
    <div class="law-meta-item"><span>📅 السنة:</span><b>{law.get("year","—")}</b></div>
    <div class="law-meta-item"><span>✅ الحالة:</span><b>{law.get("status","ساري")}</b></div>
    <div class="law-meta-item"><span class="badge {badge}">{badge_txt}</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── EDIT SECTION ──────────────────────────────────────────────────────────────
st.markdown('<div class="edit-section">', unsafe_allow_html=True)
st.markdown('<div class="edit-title">✏️ بيانات المراجعة — قابلة للتعديل</div>', unsafe_allow_html=True)

# ── 1. Scope ──
current_scope = law.get("scope","") or law.get("audit_status","")
if current_scope not in ["جميع الجهات","جهة معينة"]:
    current_scope = "جميع الجهات"

scope = st.radio(
    "نطاق تطبيق القانون",
    options=["جميع الجهات", "جهة معينة"],
    index=0 if current_scope != "جهة معينة" else 1,
    horizontal=True,
    key=f"scope_{cur_law}",
)

# ── 2. Entity & Parent (shown for all scopes) ──
entity_names  = get_entity_names()
parent_names  = get_parent_ministries()

c_entity, c_parent = st.columns(2)

with c_entity:
    current_entity = law.get("entity_audited","") or ""
    entity_idx     = entity_names.index(current_entity) if current_entity in entity_names else 0
    selected_entity = st.selectbox(
        "الجهة المعنية",
        options=entity_names,
        index=entity_idx,
        key=f"entity_{cur_law}",
    )
    custom_entity = ""
    if selected_entity == "أخرى":
        custom_entity = st.text_input(
            "اكتب اسم الجهة",
            value="",
            key=f"cent_{cur_law}",
            placeholder="أدخل اسم الجهة يدوياً...",
        )

with c_parent:
    current_parent = law.get("parent_ministry","") or ""
    parent_idx     = parent_names.index(current_parent) if current_parent in parent_names else 0
    selected_parent = st.selectbox(
        "الوزارة الأم",
        options=parent_names,
        index=parent_idx,
        key=f"parent_{cur_law}",
    )
    custom_parent = ""
    if selected_parent == "أخرى":
        custom_parent = st.text_input(
            "اكتب اسم الوزارة الأم",
            value="",
            key=f"cpar_{cur_law}",
            placeholder="أدخل اسم الوزارة الأم يدوياً...",
        )

# ── Notes ──
notes = st.text_area(
    "💬 ملاحظات إضافية (اختياري)",
    value=law.get("audit_notes","") or "",
    key=f"notes_{cur_law}",
    placeholder="أضف أي ملاحظة أو تعليق على هذا القانون...",
    height=80,
)

st.markdown('</div>', unsafe_allow_html=True)

# ─── SAVE & NAVIGATE ───────────────────────────────────────────────────────────
def save_and_next():
    sp = st.session_state.spreadsheet

    final_entity = custom_entity if selected_entity == "أخرى" else selected_entity
    final_parent = custom_parent if selected_parent == "أخرى" else selected_parent

    try:
        save_law_audit(
            spreadsheet     = sp,
            row_id          = law["row_id"],
            scope           = scope,
            entity_audited  = final_entity,
            parent_ministry = final_parent,
            audit_notes     = notes,
            username        = st.session_state.username,
        )
        # Update local state
        laws[cur_law]["scope"]           = scope
        laws[cur_law]["entity_audited"]  = final_entity
        laws[cur_law]["parent_ministry"] = final_parent
        laws[cur_law]["audit_notes"]     = notes
        laws[cur_law]["audit_status"]    = scope
        st.session_state.laws            = laws
        st.session_state.sync_ok         = True
        st.session_state.last_sync       = datetime.now().strftime("%H:%M:%S")
        st.session_state.streak         += 1

        # Move to next unreviewed law
        for i in range(cur_law + 1, total_laws):
            if laws[i].get("audit_status","") == "لم يُراجع":
                st.session_state.cur_law = i
                break
        else:
            if cur_law < total_laws - 1:
                st.session_state.cur_law = cur_law + 1

        st.rerun()

    except Exception as e:
        st.session_state.sync_ok   = False
        st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
        st.error(f"❌ خطأ في الحفظ: {e}")


col_prev, col_save = st.columns([2, 8])
with col_prev:
    if st.button("◀ السابق", use_container_width=True):
        if cur_law > 0:
            st.session_state.cur_law = cur_law - 1
            st.rerun()

with col_save:
    btn_label = "✅ اعتماد والانتقال للتالي"
    if scope == "جميع الجهات":
        btn_label = "🌐 اعتماد — جميع الجهات → التالي"
    else:
        btn_label = "🏢 اعتماد — جهة معينة → التالي"

    if st.button(btn_label, use_container_width=True, type="primary"):
        # Validate
        if scope == "جهة معينة":
            final_e = custom_entity if selected_entity=="أخرى" else selected_entity
            final_p = custom_parent if selected_parent=="أخرى" else selected_parent
            if not final_e.strip():
                st.error("⚠️ الرجاء اختيار أو إدخال اسم الجهة المعنية")
                st.stop()
            if not final_p.strip():
                st.error("⚠️ الرجاء اختيار أو إدخال اسم الوزارة الأم")
                st.stop()
        save_and_next()

# ── Streak celebration ──
if st.session_state.streak > 0 and st.session_state.streak % 10 == 0:
    st.success(f"🔥 ممتاز! أنجزت {st.session_state.streak} قانوناً متتالياً!")

# ─── DOWNLOAD ──────────────────────────────────────────────────────────────────
st.markdown("---")
df_dl = pd.DataFrame([{
    "اسم القانون":     l["leg_name"],
    "رقم القانون":    l.get("leg_number",""),
    "السنة":           l.get("year",""),
    "الحالة":          l.get("status",""),
    "النطاق":          l.get("scope",""),
    "الجهة المعنية":   l.get("entity_audited",""),
    "الوزارة الأم":    l.get("parent_ministry",""),
    "حالة المراجعة":  l.get("audit_status",""),
    "ملاحظات":        l.get("audit_notes",""),
} for l in laws])
buf = io.BytesIO()
df_dl.to_excel(buf, index=False)
buf.seek(0)
st.download_button(
    label="📥 تنزيل ملفي",
    data=buf,
    file_name=f"مراجعة_{st.session_state.username}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
