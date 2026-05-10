"""
setup_admin.py — Run ONCE to create admin account
"""
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import bcrypt
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

st.title("⚙️ إعداد حساب المدير — تشغيل مرة واحدة فقط")

col1, col2 = st.columns(2)
with col1:
    admin_username = st.text_input("اسم المستخدم للمدير", value="admin")
with col2:
    admin_password = st.text_input("كلمة المرور", type="password")

if st.button("🚀 إنشاء حساب المدير", type="primary"):
    if not admin_username or not admin_password:
        st.error("الرجاء تعبئة جميع الحقول")
    else:
        try:
            creds  = Credentials.from_service_account_info(
                dict(st.secrets["gcp_service_account"]), scopes=SCOPES)
            client = gspread.authorize(creds)
            sp     = client.open_by_key(st.secrets["spreadsheet_id"])

            # Create users sheet if not exists
            try:
                ws = sp.worksheet("users")
            except gspread.WorksheetNotFound:
                ws = sp.add_worksheet(title="users", rows=1000, cols=10)
                ws.append_row([
                    "username","password_hash","role",
                    "created_at","last_active",
                    "assigned_from","assigned_to_row"
                ])

            # Check if admin exists
            records = ws.get_all_records()
            if any(r["username"] == admin_username for r in records):
                st.warning(f"المستخدم '{admin_username}' موجود مسبقاً!")
            else:
                hashed = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
                ws.append_row([
                    admin_username, hashed, "admin",
                    datetime.now().isoformat(), "", "", ""
                ])
                st.success(f"✅ تم إنشاء حساب المدير: {admin_username}")
                st.info("الآن احذف هذا الملف من GitHub وعُد لـ app.py")
                st.warning("⚠️ لا تنشر كلمة المرور في أي مكان!")

        except Exception as e:
            st.error(f"خطأ: {e}")
            st.exception(e)
