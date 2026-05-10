"""
sheets.py — Google Sheets backend for Legal Audit System
"""
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import bcrypt
import time
import pandas as pd
import math

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── Fill this with your new Spreadsheet ID after creating it ──
SPREADSHEET_ID = st.secrets.get("spreadsheet_id", "YOUR_SPREADSHEET_ID")

SHEET_USERS    = "users"
SHEET_LAWS     = "laws_data"
SHEET_LOG      = "audit_log"
SHEET_ENTITIES = "entities"

USERS_HEADERS = [
    "username", "password_hash", "role",
    "created_at", "last_active", "assigned_from", "assigned_to_row"
]

LAWS_HEADERS = [
    "row_id", "year", "magazine_number", "leg_name", "leg_number",
    "status", "scope", "entity_audited", "parent_ministry",
    "audit_status", "audit_notes", "assigned_to", "last_updated"
]

ENTITIES_HEADERS = ["entity_name", "parent_ministry"]


# ─── CONNECTION ────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def get_client():
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=SCOPES
    )
    return gspread.authorize(creds)


@st.cache_resource(show_spinner=False)
def get_spreadsheet():
    sid = st.secrets.get("spreadsheet_id", "")
    return get_client().open_by_key(sid)


def ensure_sheet(spreadsheet, name: str, headers: list):
    try:
        return spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=name, rows=3000, cols=max(len(headers), 10))
        ws.append_row(headers)
        return ws


def safe_call(fn, retries=4, wait=6):
    for attempt in range(retries):
        try:
            return fn()
        except gspread.exceptions.APIError as e:
            if "429" in str(e) and attempt < retries - 1:
                time.sleep(wait * (attempt + 1))
            else:
                raise


def clean(val):
    if val is None: return ""
    if isinstance(val, float) and math.isnan(val): return ""
    return str(val)


# ─── USERS ─────────────────────────────────────────────────────────────────────

def get_users_sheet(sp):
    return ensure_sheet(sp, SHEET_USERS, USERS_HEADERS)


@st.cache_data(ttl=30, show_spinner=False)
def load_users_cached(_sid: str) -> dict:
    sp      = get_spreadsheet()
    ws      = get_users_sheet(sp)
    records = safe_call(ws.get_all_records)
    return {r["username"]: r for r in records}


def load_users() -> dict:
    sid = st.secrets.get("spreadsheet_id", "")
    return load_users_cached(sid)


def invalidate_users():
    load_users_cached.clear()


def create_user(spreadsheet, username: str, password: str,
                role: str = "consultant",
                assigned_from: int = 0, assigned_to_row: int = 0):
    users = load_users()
    if username in users:
        return False, "اسم المستخدم موجود مسبقاً"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    ws = get_users_sheet(spreadsheet)
    safe_call(lambda: ws.append_row([
        username, hashed, role,
        datetime.now().isoformat(), "",
        assigned_from, assigned_to_row
    ]))
    invalidate_users()
    return True, "تم إنشاء المستخدم بنجاح"


def delete_user(spreadsheet, username: str):
    ws      = get_users_sheet(spreadsheet)
    records = safe_call(ws.get_all_values)
    for i, row in enumerate(records):
        if row and row[0] == username:
            safe_call(lambda idx=i: ws.delete_rows(idx + 1))
            invalidate_users()
            return True
    return False


def update_user_assignment(spreadsheet, username: str,
                           assigned_from: int, assigned_to_row: int):
    ws   = get_users_sheet(spreadsheet)
    cell = safe_call(lambda: ws.find(username))
    safe_call(lambda: ws.update(f"F{cell.row}:G{cell.row}",
                                [[assigned_from, assigned_to_row]]))
    invalidate_users()


def verify_password(spreadsheet, username: str, password: str):
    users = load_users()
    if username not in users:
        return False, None
    u = users[username]
    if bcrypt.checkpw(password.encode(), u["password_hash"].encode()):
        try:
            ws   = get_users_sheet(spreadsheet)
            cell = safe_call(lambda: ws.find(username))
            safe_call(lambda: ws.update_cell(cell.row, 5, datetime.now().isoformat()))
            invalidate_users()
        except Exception:
            pass
        return True, u
    return False, None


def update_password(spreadsheet, username: str, new_password: str):
    ws     = get_users_sheet(spreadsheet)
    cell   = safe_call(lambda: ws.find(username))
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    safe_call(lambda: ws.update_cell(cell.row, 2, hashed))
    invalidate_users()


# ─── LAWS DATA ─────────────────────────────────────────────────────────────────

def upload_laws(spreadsheet, df: pd.DataFrame):
    """Upload laws file as master data. Clears existing data."""
    ws = ensure_sheet(spreadsheet, SHEET_LAWS, LAWS_HEADERS)
    safe_call(ws.clear)

    rows = [LAWS_HEADERS]
    for i, (_, r) in enumerate(df.iterrows()):
        rows.append([
            i,
            clean(r.get("year", "")),
            clean(r.get("magazine_number", "")),
            clean(r.get("leg_name", "")),
            clean(r.get("leg_number", "")),
            clean(r.get("status", "ساري")),
            "",   # scope
            "",   # entity_audited
            "",   # parent_ministry
            "لم يُراجع",  # audit_status
            "",   # audit_notes
            "",   # assigned_to (username)
            "",   # last_updated
        ])

    # Write in chunks
    for i in range(0, len(rows), 200):
        safe_call(lambda s=i: ws.append_rows(rows[s:s + 200]))

    invalidate_laws()
    return len(rows) - 1


@st.cache_data(ttl=60, show_spinner=False)
def load_laws_cached(_sid: str):
    sp  = get_spreadsheet()
    ws  = ensure_sheet(sp, SHEET_LAWS, LAWS_HEADERS)
    return safe_call(ws.get_all_records)


def load_laws():
    sid = st.secrets.get("spreadsheet_id", "")
    return load_laws_cached(sid)


def invalidate_laws():
    load_laws_cached.clear()


def load_user_laws(username: str) -> list:
    """Return laws assigned to this user."""
    records = load_laws()
    return [r for r in records if str(r.get("assigned_to", "")).strip() == username]


def assign_laws_to_user(spreadsheet, username: str,
                        from_idx: int, to_idx: int):
    """
    Assign laws from_idx to to_idx (0-based, inclusive) to username.
    Updates the assigned_to column in bulk.
    """
    ws      = ensure_sheet(spreadsheet, SHEET_LAWS, LAWS_HEADERS)
    records = safe_call(ws.get_all_values)   # includes header at index 0

    updates = []
    # Find assigned_to column index (L = col 12, 1-indexed)
    assigned_col = 12  # column L

    law_counter = -1  # counts laws (unique leg_name)
    seen_laws   = {}
    all_law_order = []

    # Build ordered unique law list
    for i, rec in enumerate(records):
        if i == 0: continue  # skip header
        law = rec[3]  # leg_name column
        if law not in seen_laws:
            seen_laws[law] = []
            all_law_order.append(law)
        seen_laws[law].append(i)

    # Laws from_idx to to_idx
    target_laws = set(all_law_order[from_idx:to_idx + 1])

    for i, rec in enumerate(records):
        if i == 0: continue
        law = rec[3]
        if law in target_laws:
            updates.append({
                "range": f"L{i + 1}",
                "values": [[username]]
            })

    # Batch update in chunks
    chunk = 500
    for c in range(0, len(updates), chunk):
        safe_call(lambda s=c: ws.batch_update(updates[s:s + chunk]))
        time.sleep(1)

    # Update user's assignment range
    update_user_assignment(spreadsheet, username, from_idx, to_idx)
    invalidate_laws()
    return len(target_laws)


def save_law_audit(spreadsheet, row_id: int,
                   scope: str, entity_audited: str,
                   parent_ministry: str, audit_notes: str,
                   username: str):
    """Save audit for a single law row."""
    ws      = ensure_sheet(spreadsheet, SHEET_LAWS, LAWS_HEADERS)
    records = safe_call(ws.get_all_values)

    audit_status = scope if scope else "لم يُراجع"

    for i, rec in enumerate(records):
        if i == 0: continue
        if str(rec[0]) == str(row_id):
            row_num = i + 1
            safe_call(lambda r=row_num: ws.update(
                f"G{r}:M{r}",
                [[scope, entity_audited, parent_ministry,
                  audit_status, audit_notes, username,
                  datetime.now().isoformat()]]
            ))
            invalidate_laws()

            # Log change
            try:
                log_ws = ensure_sheet(spreadsheet, SHEET_LOG,
                                      ["timestamp", "username", "row_id",
                                       "leg_name", "field", "new_value"])
                safe_call(lambda: log_ws.append_row([
                    datetime.now().isoformat(), username,
                    row_id, rec[3],
                    "audit", f"{scope}|{entity_audited}|{parent_ministry}"
                ]))
            except Exception:
                pass
            return


# ─── ENTITIES ──────────────────────────────────────────────────────────────────

def upload_entities(spreadsheet, entities: list, parents: list):
    """Save entity and parent ministry lists."""
    ws = ensure_sheet(spreadsheet, SHEET_ENTITIES, ENTITIES_HEADERS)
    safe_call(ws.clear)
    rows = [ENTITIES_HEADERS]
    # Zip entities with parents (pad with empty if different lengths)
    max_len = max(len(entities), len(parents))
    for i in range(max_len):
        e = entities[i] if i < len(entities) else ""
        p = parents[i]  if i < len(parents)  else ""
        rows.append([e, p])
    safe_call(lambda: ws.update(rows))
    load_entities_cached.clear()


@st.cache_data(ttl=300, show_spinner=False)
def load_entities_cached(_sid: str):
    sp = get_spreadsheet()
    try:
        ws = sp.worksheet(SHEET_ENTITIES)
        return safe_call(ws.get_all_records)
    except Exception:
        return []


def load_entities():
    sid = st.secrets.get("spreadsheet_id", "")
    return load_entities_cached(sid)


def get_entity_names() -> list:
    records = load_entities()
    names   = sorted(set(r["entity_name"] for r in records if r.get("entity_name")))
    return names + ["أخرى"]


def get_parent_ministries() -> list:
    records = load_entities()
    parents = sorted(set(r["parent_ministry"] for r in records if r.get("parent_ministry")))
    return parents + ["أخرى"]


# ─── PROGRESS ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def get_progress_cached(_sid: str) -> list:
    users   = load_users()
    records = load_laws()
    result  = []

    for username, info in users.items():
        if info["role"] == "admin":
            continue
        my_rows  = [r for r in records if str(r.get("assigned_to","")).strip() == username]
        total    = len(my_rows)
        reviewed = sum(1 for r in my_rows if r.get("audit_status","") != "لم يُراجع")
        jamea    = sum(1 for r in my_rows if r.get("audit_status","") == "جميع الجهات")
        moayyan  = sum(1 for r in my_rows if r.get("audit_status","") == "جهة معينة")
        pct      = int(reviewed / total * 100) if total else 0
        af       = info.get("assigned_from", "")
        at       = info.get("assigned_to_row", "")
        result.append({
            "username":      username,
            "total":         total,
            "reviewed":      reviewed,
            "jamea":         jamea,
            "moayyan":       moayyan,
            "pct":           pct,
            "last_active":   info.get("last_active", ""),
            "assigned_from": af,
            "assigned_to_row": at,
        })
    return result


def get_progress():
    sid = st.secrets.get("spreadsheet_id", "")
    return get_progress_cached(sid)


def get_full_df() -> pd.DataFrame:
    return pd.DataFrame(load_laws())
