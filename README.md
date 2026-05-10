# ⚖️ منظومة مراجعة التشريعات
نظام احترافي لمراجعة القوانين والتشريعات من قِبَل المستشارين القانونيين.

## 🚀 خطوات الإعداد من الصفر

### 1. إنشاء مستودع GitHub جديد
- اذهب إلى github.com → New repository
- اسم المستودع: `legal-audit`
- ارفع جميع الملفات

### 2. إعداد Google Cloud
- اذهب إلى console.cloud.google.com
- أنشئ مشروعاً جديداً
- فعّل Google Sheets API و Google Drive API
- أنشئ Service Account → احصل على JSON key

### 3. إنشاء Google Sheet
- اذهب إلى sheets.google.com
- أنشئ Spreadsheet جديداً باسم: `Legal Audit System`
- شارك الـ Sheet مع بريد الـ Service Account (Editor)
- احفظ الـ Spreadsheet ID من الرابط

### 4. إعداد Streamlit Cloud
- اذهب إلى share.streamlit.io
- اربط مستودع GitHub
- في Settings → Secrets أضف:

```toml
spreadsheet_id = "YOUR_SPREADSHEET_ID"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"
```

### 5. إنشاء حساب المدير
- غيّر Main file إلى `setup_admin.py`
- شغّل التطبيق وأنشئ حساب المدير
- عُد إلى `app.py` واحذف `setup_admin.py`

### 6. ابدأ العمل
- سجّل دخول كمدير
- ارفع ملف القوانين
- أنشئ حسابات المستشارين
- وزّع القوانين عليهم

## 📁 هيكل المشروع
```
legal-audit/
├── app.py           ← التطبيق الرئيسي
├── sheets.py        ← التواصل مع Google Sheets
├── auth.py          ← تسجيل الدخول والترحيب
├── admin.py         ← لوحة الإدارة
├── setup_admin.py   ← إنشاء المدير (يُحذف بعد الاستخدام)
├── requirements.txt ← المكتبات
└── .streamlit/
    └── config.toml  ← إعدادات الثيم
```
