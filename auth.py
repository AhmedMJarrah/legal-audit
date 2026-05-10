"""
auth.py — Login + Greeting pages
"""
import streamlit as st
from sheets import get_spreadsheet, verify_password


# ── Motivational messages by progress ──
def get_motivation(pct: int) -> tuple:
    if pct == 0:
        return "كل إنجاز يبدأ بخطوة واحدة. أنت جاهز! 🌟", "#2563eb"
    elif pct < 25:
        return "بداية ممتازة! استمر في العطاء 💪", "#7c3aed"
    elif pct < 50:
        return "أنجزت ربع العمل! أنت على الطريق الصحيح 🔥", "#ea580c"
    elif pct < 75:
        return "أكثر من النصف! قليل ويكتمل العمل ⭐", "#16a34a"
    elif pct < 100:
        return "أوشكت على الانتهاء! الخط الأخير 🚀", "#16a34a"
    else:
        return "أنجزت جميع القوانين! عمل استثنائي 🎉", "#16a34a"


def login_page():
    """Full-page login form."""
    st.markdown("""
    <style>
    .login-wrap {
        max-width: 460px;
        margin: 6rem auto 0 auto;
        text-align: center;
    }
    .login-logo { font-size: 4rem; margin-bottom: 0.5rem; }
    .login-title {
        font-family: 'Amiri', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--text);
        margin: 0 0 0.3rem 0;
    }
    .login-sub { color: var(--text2); font-size: 0.95rem; margin: 0 0 2.5rem 0; }
    .login-box {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 2.2rem 2rem;
        box-shadow: var(--shadow-md);
        text-align: right;
    }
    </style>

    <div class="login-wrap">
      <div class="login-logo">⚖️</div>
      <div class="login-title">منظومة مراجعة التشريعات</div>
      <div class="login-sub">للمستشارين القانونيين</div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم", key="lu")
        password = st.text_input("🔒 كلمة المرور",  type="password",
                                  placeholder="أدخل كلمة المرور", key="lp")
        if st.button("دخول →", use_container_width=True, type="primary", key="login_btn"):
            if not username or not password:
                st.error("الرجاء إدخال اسم المستخدم وكلمة المرور")
                return
            with st.spinner("جارٍ التحقق..."):
                try:
                    sp = get_spreadsheet()
                    ok, info = verify_password(sp, username.strip(), password)
                    if ok:
                        st.session_state.update({
                            "logged_in":     True,
                            "username":      username.strip(),
                            "role":          info["role"],
                            "spreadsheet":   sp,
                            "show_greeting": True,
                            "groups":        None,
                            "cur_law":       0,
                            "streak":        0,
                            "last_sync":     None,
                            "sync_ok":       True,
                        })
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                except Exception as e:
                    st.error(f"خطأ في الاتصال: {e}")
        st.markdown('</div>', unsafe_allow_html=True)


def greeting_page(username: str, total: int, reviewed: int):
    """Personalized greeting with start button."""
    remaining = total - reviewed
    pct       = int(reviewed / total * 100) if total else 0
    msg, color = get_motivation(pct)

    st.markdown(f"""
    <div style="max-width:620px;margin:4rem auto;text-align:center">
      <div style="font-size:5rem;margin-bottom:0.5rem">👋</div>
      <h1 style="font-family:'Amiri',serif;font-size:3rem;margin:0 0 0.4rem 0;color:var(--text)">
        أهلاً، {username}!
      </h1>
      <p style="font-size:1.15rem;color:{color};font-weight:700;margin:0 0 2rem 0">{msg}</p>

      <div style="background:var(--card);border:1px solid var(--border);border-radius:18px;
                  padding:2rem;margin-bottom:2rem;box-shadow:var(--shadow)">
        <div style="display:flex;justify-content:space-around;margin-bottom:1.2rem">
          <div>
            <div style="font-size:2.5rem;font-weight:900;color:var(--accent)">{total}</div>
            <div style="font-size:0.82rem;color:var(--text2)">إجمالي القوانين</div>
          </div>
          <div style="width:1px;background:var(--border)"></div>
          <div>
            <div style="font-size:2.5rem;font-weight:900;color:#16a34a">{reviewed}</div>
            <div style="font-size:0.82rem;color:var(--text2)">تمت مراجعتها</div>
          </div>
          <div style="width:1px;background:var(--border)"></div>
          <div>
            <div style="font-size:2.5rem;font-weight:900;color:{color}">{remaining}</div>
            <div style="font-size:0.82rem;color:var(--text2)">متبقية</div>
          </div>
        </div>
        <div style="background:var(--progress-bg);border-radius:99px;height:12px;overflow:hidden">
          <div style="height:100%;border-radius:99px;
                      background:linear-gradient(90deg,#2563eb,{color});
                      width:{pct}%;transition:width 1s ease"></div>
        </div>
        <div style="font-size:0.85rem;color:var(--text3);margin-top:8px">{pct}% مكتمل</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        if pct == 100:
            st.success("🎉 أنجزت جميع القوانين المخصصة لك!")
            if st.button("📥 تنزيل ملفي", use_container_width=True):
                st.session_state.show_greeting = False
                st.rerun()
        else:
            if st.button("🚀 ابدأ المراجعة", use_container_width=True, type="primary"):
                st.session_state.show_greeting = False
                st.rerun()


def require_login():
    if not st.session_state.get("logged_in"):
        login_page()
        st.stop()


def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()
