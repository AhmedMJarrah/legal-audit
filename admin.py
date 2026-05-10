"""
admin.py — Admin Panel
"""
import streamlit as st
import pandas as pd
import io
from pathlib import Path
from sheets import (
    get_spreadsheet, upload_laws, upload_entities,
    load_laws, load_users, invalidate_laws, invalidate_users,
    create_user, delete_user, update_password,
    assign_laws_to_user, get_progress, get_full_df,
    get_entity_names, get_parent_ministries,
)


def admin_panel():
    sp = st.session_state.spreadsheet

    st.markdown("""
    <div class="hero">
      <div style="font-size:2.2rem;margin-bottom:0.3rem">🛡️</div>
      <h1>لوحة الإدارة</h1>
      <p>رفع الملفات · توزيع القوانين · متابعة التقدم · إدارة المستخدمين</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📂 رفع الملف",
        "⚖️ توزيع القوانين",
        "📊 التقدم",
        "👥 المستخدمون",
        "📥 التنزيل",
    ])

    # ── Tab 1: Upload ──────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### 📂 رفع ملف القوانين")
        st.info("بعد الرفع، يمكنك توزيع القوانين على المستشارين من تبويب **توزيع القوانين**.")

        laws_file = st.file_uploader(
            "ملف القوانين (Excel أو CSV)",
            type=["xlsx","xls","csv"],
            label_visibility="collapsed",
        )

        if laws_file:
            try:
                ext = Path(laws_file.name).suffix.lower()
                df  = pd.read_csv(laws_file, encoding="utf-8-sig") if ext==".csv" \
                      else pd.read_excel(laws_file)

                required = {"leg_name"}
                if not required.issubset(set(df.columns)):
                    st.error("❌ الملف يجب أن يحتوي على عمود leg_name على الأقل")
                else:
                    st.markdown(f"""
                    <div style="background:var(--green-lt);border:1px solid var(--green-border);
                                border-radius:10px;padding:1rem 1.5rem;margin-bottom:1rem">
                      <b style="color:var(--green)">✅ تم قراءة الملف بنجاح</b><br>
                      <span style="font-size:0.88rem;color:var(--text2)">
                        {len(df)} سجل · {df['leg_name'].nunique()} قانون فريد
                      </span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.dataframe(df.head(5), use_container_width=True, hide_index=True)

                    # Extract entities & parents from file if they exist
                    entities = []
                    parents  = []
                    if "entity_audited" in df.columns:
                        entities = sorted(df["entity_audited"].dropna().unique().tolist())
                    if "parent_ministry" in df.columns:
                        parents = sorted(df["parent_ministry"].dropna().unique().tolist())

                    st.warning(f"⚠️ رفع الملف سيحذف البيانات الحالية. هل أنت متأكد؟")
                    if st.button("✅ رفع الملف الآن", type="primary", use_container_width=True):
                        with st.spinner("جارٍ الرفع..."):
                            n = upload_laws(sp, df)
                            if entities or parents:
                                upload_entities(sp, entities, parents)
                        st.success(f"✅ تم رفع {n} قانون!")
                        st.balloons()
            except Exception as e:
                st.error(f"خطأ: {e}")

    # ── Tab 2: Assign Laws ─────────────────────────────────────────────────────
    with tab2:
        st.markdown("### ⚖️ توزيع القوانين على المستشارين")

        # Load laws and users
        with st.spinner("جارٍ التحميل..."):
            records = load_laws()
            users   = load_users()

        if not records:
            st.warning("لا يوجد قوانين مرفوعة بعد. ارفع الملف أولاً.")
        else:
            # Get unique laws in order
            seen_laws, ordered_laws = {}, []
            for r in records:
                law = r.get("leg_name","")
                if law not in seen_laws:
                    seen_laws[law] = len(ordered_laws)
                    ordered_laws.append(law)

            total_laws = len(ordered_laws)
            consultants = {u: info for u, info in users.items() if info["role"] != "admin"}

            st.markdown(f"**إجمالي القوانين:** {total_laws} · **المستشارون:** {len(consultants)}")

            # Show current assignment summary
            if consultants:
                st.markdown("#### الوضع الحالي")
                for uname, info in consultants.items():
                    af = info.get("assigned_from","")
                    at = info.get("assigned_to_row","")
                    my_laws = [r for r in records if str(r.get("assigned_to","")).strip()==uname]
                    reviewed = sum(1 for r in my_laws if r.get("audit_status","")!="لم يُراجع")
                    pct = int(reviewed/len(my_laws)*100) if my_laws else 0
                    st.markdown(f"""
                    <div style="background:var(--card);border:1px solid var(--border);
                                border-radius:10px;padding:0.8rem 1.2rem;margin-bottom:0.5rem;
                                display:flex;justify-content:space-between;align-items:center">
                      <span style="font-weight:700">👤 {uname}</span>
                      <span style="font-size:0.85rem;color:var(--text2)">
                        قوانين {af}–{at} &nbsp;·&nbsp; {len(my_laws)} قانون &nbsp;·&nbsp;
                        <span style="color:{'#16a34a' if pct==100 else 'var(--accent)'}">
                          {reviewed} مراجَع ({pct}%)
                        </span>
                      </span>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### تعيين قوانين لمستشار")

            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                target_user = st.selectbox(
                    "اختر المستشار",
                    options=list(consultants.keys()) if consultants else ["لا يوجد مستشارون"],
                    key="assign_user"
                )
            with c2:
                from_law = st.number_input("من القانون رقم", min_value=1,
                                           max_value=total_laws, value=1, key="from_law")
            with c3:
                to_law = st.number_input("إلى القانون رقم", min_value=1,
                                         max_value=total_laws, value=min(200, total_laws),
                                         key="to_law")

            if from_law <= to_law:
                count = to_law - from_law + 1
                # Show preview of first and last law
                preview_first = ordered_laws[from_law-1][:60] + "..."
                preview_last  = ordered_laws[to_law-1][:60]   + "..."
                st.markdown(f"""
                <div style="background:var(--accentlt);border:1px solid #c7d7fb;
                            border-radius:10px;padding:1rem 1.2rem;font-size:0.88rem">
                  <b>معاينة:</b> {count} قانون<br>
                  <span style="color:var(--text2)">أول قانون: {preview_first}</span><br>
                  <span style="color:var(--text2)">آخر قانون: {preview_last}</span>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"✅ تعيين {count} قانون لـ {target_user}",
                             type="primary", use_container_width=True, key="do_assign"):
                    with st.spinner("جارٍ التعيين..."):
                        n = assign_laws_to_user(sp, target_user, from_law-1, to_law-1)
                    st.success(f"✅ تم تعيين {n} قانون لـ {target_user}")
                    st.rerun()
            else:
                st.error("رقم البداية يجب أن يكون أصغر من رقم النهاية")

    # ── Tab 3: Progress ────────────────────────────────────────────────────────
    with tab3:
        st.markdown("### 📊 تقدم المراجعة")
        if st.button("🔄 تحديث", key="ref_prog"):
            st.cache_data.clear(); st.rerun()

        progress = get_progress()
        if not progress:
            st.info("لا يوجد بيانات بعد.")
        else:
            # Overall stats
            total_r  = sum(p["total"]    for p in progress)
            total_rv = sum(p["reviewed"] for p in progress)
            opct     = int(total_rv / total_r * 100) if total_r else 0

            c1,c2,c3,c4 = st.columns(4)
            for col,(num,lbl,color) in zip([c1,c2,c3,c4],[
                (len(progress), "المستشارون",    "var(--stat-num-laws)"),
                (total_r,       "إجمالي القوانين","var(--stat-num-rows)"),
                (total_rv,      "تمت مراجعتها",  "var(--stat-num-ok)"),
                (f"{opct}%",    "نسبة الإنجاز",  "var(--stat-num-pct)"),
            ]):
                with col:
                    st.markdown(f"""<div class="stat-card">
                        <div class="stat-num" style="color:{color}">{num}</div>
                        <div class="stat-lbl">{lbl}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

            for p in progress:
                pct   = p["pct"]
                color = "#16a34a" if pct==100 else "#2563eb"
                last  = p["last_active"][:16].replace("T"," ") if p["last_active"] else "لم يبدأ بعد"
                st.markdown(f"""
                <div class="progress-wrap" style="margin-bottom:0.8rem">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                      <span style="font-weight:700;font-size:1rem">👤 {p["username"]}</span>
                      <span style="font-size:0.78rem;color:var(--text3);margin-right:8px">
                        قوانين {p.get("assigned_from","")}–{p.get("assigned_to_row","")}
                      </span>
                    </div>
                    <span style="font-size:0.8rem;color:var(--text3)">آخر نشاط: {last}</span>
                  </div>
                  <div style="font-size:0.85rem;color:var(--text2);margin:5px 0 7px 0;
                              display:flex;gap:1.5rem">
                    <span>{p["reviewed"]}/{p["total"]} قانون</span>
                    <span style="color:#2563eb">🌐 جميع الجهات: {p["jamea"]}</span>
                    <span style="color:#7c3aed">🏢 جهة معينة: {p["moayyan"]}</span>
                    <span style="color:{color};font-weight:700">{pct}%</span>
                  </div>
                  <div class="progress-bar-outer">
                    <div class="progress-bar-inner" style="width:{pct}%;background:{color}"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 4: Users ───────────────────────────────────────────────────────────
    with tab4:
        col_new, col_list = st.columns([1, 1])

        with col_new:
            st.markdown("#### ➕ إنشاء مستشار")
            nu = st.text_input("اسم المستخدم", key="nu", placeholder="مثال: consultant1")
            np = st.text_input("كلمة المرور",  key="np", type="password")
            nr = st.selectbox("الصلاحية", ["consultant","admin"], key="nr")
            if st.button("✅ إنشاء", use_container_width=True, type="primary", key="create_user"):
                if nu and np:
                    with st.spinner("جارٍ الإنشاء..."):
                        ok, msg = create_user(sp, nu.strip(), np, nr)
                    st.success(msg) if ok else st.error(msg)
                    if ok: st.cache_data.clear(); st.rerun()
                else:
                    st.warning("الرجاء تعبئة جميع الحقول")

        with col_list:
            st.markdown("#### 👥 المستخدمون الحاليون")
            invalidate_users()
            users = load_users()
            for uname, info in users.items():
                icon = "🛡️" if info["role"]=="admin" else "👤"
                with st.expander(f"{icon} {uname}"):
                    st.markdown(f"**الصلاحية:** {info['role']}")
                    np2 = st.text_input("كلمة مرور جديدة", type="password",
                                        key=f"np2_{uname}", placeholder="اتركه فارغاً للإبقاء")
                    if st.button("💾 تحديث كلمة المرور", key=f"upd_{uname}"):
                        if np2:
                            update_password(sp, uname, np2)
                            st.success("تم التحديث ✅")
                    if uname != st.session_state.username:
                        if st.button(f"🗑️ حذف {uname}", key=f"del_{uname}"):
                            delete_user(sp, uname)
                            st.success(f"تم حذف {uname}")
                            st.rerun()
                    else:
                        st.caption("لا يمكنك حذف حسابك الخاص")

    # ── Tab 5: Download ────────────────────────────────────────────────────────
    with tab5:
        st.markdown("### 📥 تنزيل البيانات")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### الملف الكامل")
            if st.button("تحميل كل البيانات", use_container_width=True, key="dl_all"):
                with st.spinner("جارٍ التحميل..."):
                    df = get_full_df()
                if df.empty:
                    st.warning("لا يوجد بيانات.")
                else:
                    buf = io.BytesIO()
                    df.to_excel(buf, index=False)
                    buf.seek(0)
                    st.download_button(
                        "⬇️ تنزيل Excel",
                        data=buf,
                        file_name="legal_audit_complete.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary",
                    )

        with c2:
            st.markdown("#### ملف مستشار محدد")
            users      = load_users()
            consultant_list = [u for u,i in users.items() if i["role"]!="admin"]
            sel_user   = st.selectbox("اختر المستشار", consultant_list, key="dl_user")
            if st.button("تحميل بياناته", use_container_width=True, key="dl_user_btn"):
                with st.spinner("جارٍ التحميل..."):
                    all_records = load_laws()
                    user_records = [r for r in all_records
                                    if str(r.get("assigned_to","")).strip()==sel_user]
                df_u = pd.DataFrame(user_records)
                if df_u.empty:
                    st.warning("لا يوجد بيانات لهذا المستشار.")
                else:
                    buf = io.BytesIO()
                    df_u.to_excel(buf, index=False)
                    buf.seek(0)
                    st.download_button(
                        f"⬇️ تنزيل ملف {sel_user}",
                        data=buf,
                        file_name=f"audit_{sel_user}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary",
                    )
