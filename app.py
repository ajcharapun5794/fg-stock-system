import streamlit as st
import pandas as pd
from datetime import datetime

# ====================================================
# CONFIGURATION: Google Sheets Connection
# ====================================================
GOOGLE_SHEET_ID = "1Q14RlHndi2CjpA1SgamQAptmDKgCqtN8myuqteritg"
SHEET_NAME = "Sheet1"
GSHEET_URL = f"https://google.com{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# ====================================================
# DATABASE FUNCTIONS
# ====================================================
if 'mock_db' not in st.session_state:
    st.session_state.mock_db = pd.DataFrame(columns=[
        'JobID', 'Timestamp', 'PD_Shift', 'PD_Name', 'SKU', 'PD_Qty', 'QC_Status', 'QC_Name', 'FG_Qty', 'FG_Status', 'FG_Name'
    ])

def load_data():
    return st.session_state.mock_db

def save_data(df):
    st.session_state.current_db = df
    st.session_state.mock_db = df

# ====================================================
# SYSTEM CORE SETUP
# ====================================================
st.set_page_config(page_title="Finished Goods Management Portal", layout="wide")

st.markdown("# ระบบบริหารจัดการคลังสินค้าสำเร็จรูปและตรวจสอบคุณภาพ")
st.markdown("ระบบบันทึก ตรวจสอบ และเชื่อมโยงข้อมูลปริมาณสินค้าคลังสำเร็จรูป (Finished Goods - FG)")
st.write("---")

if 'current_db' not in st.session_state:
    st.session_state.current_db = load_data()

df_current = st.session_state.current_db

# คำนวณจำนวนงานค้างเพื่ออัปเดตสถานะป้ายไฟแจ้งเตือนสีเขียว/สีแดงด้านซ้าย
count_qc = len(df_current[df_current['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)'])
count_fg = len(df_current[df_current['FG_Status'] == 'รอคลังรับเข้า (Pending FG)'])

# ====================================================
# SIDEBAR PORTAL: ระบบเลือกแผนกงานหลัก (แถบไฟสี เขียว/แดง ดีไซน์เดิมที่พี่ชอบ)
# ====================================================
st.sidebar.markdown("## เมนูระบบงานหลัก")

txt_qc_status = f"🚨 มีงานค้าง {count_qc} รายการ" if count_qc > 0 else "🟢 เคลียร์หมด ไม่มีงานค้าง"
color_qc_bg = "#FFEBEE" if count_qc > 0 else "#E8F5E9"
color_qc_txt = "#B71C1C" if count_qc > 0 else "#1B5E20"
color_qc_border = "#EF9A9A" if count_qc > 0 else "#A5D6A7"

txt_fg_status = f"🚨 มีงานค้าง {count_fg} รายการ" if count_fg > 0 else "🟢 เคลียร์หมด ไม่มีงานค้าง"
color_fg_bg = "#FFEBEE" if count_fg > 0 else "#E8F5E9"
color_fg_txt = "#B71C1C" if count_fg > 0 else "#1B5E20"
color_fg_border = "#EF9A9A" if count_fg > 0 else "#A5D6A7"

st.sidebar.markdown(f"""
    <style>
    .nav-badge {{ padding: 10px; border-radius: 6px; font-weight: bold; text-align: center; margin-top: 12px; margin-bottom: 4px; font-size: 13px; }}
    .c-green {{ background-color: #E8F5E9; color: #1B5E20; border: 1px solid #A5D6A7; }}
    .c-blue {{ background-color: #E3F2FD; color: #0D47A1; border: 1px solid #90CAF9; }}
    .c-qc-dynamic {{ background-color: {color_qc_bg}; color: {color_qc_txt}; border: 1px solid {color_qc_border}; }}
    .c-fg_dynamic {{ background-color: {color_fg_bg}; color: {color_fg_txt}; border: 1px solid {color_fg_border}; }}
    div[data-testid="stSidebarUserContent"] button {{ font-weight: bold !important; font-size: 14px !important; margin-bottom: 10px !important; }}
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="nav-badge c-green">1. แผนกฝ่ายผลิต (PD) <br><small>🟢 สถานะปกติ</small></div>', unsafe_allow_html=True)
nav_pd = st.sidebar.button("👉 เปิดหน้าจอ ฝ่ายผลิต", key="go_pd", use_container_width=True)

st.sidebar.markdown(f'<div class="nav-badge c-qc-dynamic">2. แผนกควบคุมคุณภาพ (QC) <br><small>{txt_qc_status}</small></div>', unsafe_allow_html=True)
nav_qc = st.sidebar.button("👉 เปิดหน้าจอ ตรวจสเปก QC", key="go_qc", use_container_width=True)

st.sidebar.markdown(f'<div class="nav-badge c-fg_dynamic">3. แผนกคลังสินค้า (FG) <br><small>{txt_fg_status}</small></div>', unsafe_allow_html=True)
nav_fg = st.sidebar.button("👉 เปิดหน้าจอ ตรวจนับของ FG", key="go_fg", use_container_width=True)

st.sidebar.markdown('<div class="nav-badge c-blue">4. ฝ่ายบริหารข้อมูลคลัง (ERP) <br><small>📊 สรุปยอดข้อมูลรวม</small></div>', unsafe_allow_html=True)
nav_erp = st.sidebar.button("👉 เปิดรายงานสรุปยอดลง ERP", key="go_erp", use_container_width=True)

if 'current_page' not in st.session_state:
    st.session_state.current_page = "PD"

if nav_pd: st.session_state.current_page = "PD"; st.rerun()
if nav_qc: st.session_state.current_page = "QC"; st.rerun()
if nav_fg: st.session_state.current_page = "FG"; st.rerun()
if nav_erp: st.session_state.current_page = "ERP"; st.rerun()

# ====================================================
# WORKFLOW PAGES INTERFACE (เนื้อหาฝั่งขวา)
# ====================================================

# ----------------------------------------------------
# 1. แผนกฝ่ายผลิต (PD) - บันทึก ชื่อ, รอบเวลา, รหัสสินค้า, จำนวน (สะสมหลายโค้ดได้)
# ----------------------------------------------------
if st.session_state.current_page == "PD":
    st.subheader("⚙️ ส่วนงานฝ่ายผลิต (Production - PD): บันทึกส่งมอบงานสินค้า")
    pd_name = st.text_input("ชื่อพนักงานฝ่ายผลิตผู้บันทึกข้อมูล:")
    pd_shift = st.text_input("ระบุรอบเวลาการส่งงาน / กะการทำงาน (เช่น รอบ 10:00 น. หรือ กะเช้า):")
    st.markdown("#### ตารางรายการรหัสสินค้าที่ต้องการนำส่ง")
    
    if 'temp_items' not in st.session_state:
        st.session_state.temp_items = []

    with st.container(border=True):
        input_sku = st.text_input("ระบุรหัสสินค้า หรือใช้ปืนสแกนบาร์โค้ดยิง (SKU):", key="input_sku")
        input_qty = st.number_input("จำนวนสินค้าที่นำส่งมอบจริง (ชิ้น):", min_value=1, step=1, key="input_qty")
        st.write("") 
        if st.button("➕ เพิ่มเข้าตารางรายการ", use_container_width=True):
            if input_sku.strip() != "":
                st.session_state.temp_items.append({'SKU': input_sku.strip(), 'Qty': input_qty})
                st.rerun()
            else:
                st.error("กรุณาระบุรหัสสินค้า")

    if st.session_state.temp_items:
        df_temp = pd.DataFrame(st.session_state.temp_items)
        df_temp_idx = df_temp.copy()
        df_temp_idx.insert(0, 'เลือกเพื่อลบ', False)
        
        st.write("**รายการที่เตรียมส่งมอบรอบนี้:**")
        edited_temp = st.data_editor(df_temp_idx, hide_index=True, use_container_width=True, disabled=['SKU', 'Qty'])
        
        col_pd_del, col_pd_send = st.columns(2)
        with col_pd_del:
            if st.button("🗑️ ล้างรายการส่งมอบที่เลือก", use_container_width=True):
                keep_indices = edited_temp[edited_temp['เลือกเพื่อลบ'] == False].index.tolist()
                st.session_state.temp_items = [st.session_state.temp_items[i] for i in keep_indices]
                st.success("ลบรายการที่เลือกเรียบร้อย")
                st.rerun()
                
        with col_pd_send:
            if st.button("🚀 ยืนยันการนำส่งข้อมูลทั้งหมดให้ระบบ", type="primary", use_container_width=True):
                if pd_name.strip() == "" or pd_shift.strip() == "":
                    st.error("กรุณาระบุชื่อพนักงานและรอบเวลาการส่งงานให้ครบถ้วน")
                else:
                    df = st.session_state.current_db
                    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    for item in st.session_state.temp_items:
                        new_id = len(df) + 1
                        job_id = f"JOB-{new_id:04d}"
                        new_data = {
                            'JobID': job_id, 'Timestamp': timestamp_now, 'PD_Shift': pd_shift,
                            'PD_Name': pd_name, 'SKU': item['SKU'], 'PD_Qty': item['Qty'],
                            'QC_Status': 'รอ QC ตรวจสอบ (Pending QC)', 'QC_Name': '-',
                            'FG_Qty': 0, 'FG_Status': 'รอคลังรับเข้า (Pending FG)', 'FG_Name': '-'
                        }
                        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                    
                    save_data(df)
                    st.session_state.temp_items = []
                    st.success("บันทึกข้อมูลส่งมอบเข้าสู่คิวงานเรียบร้อยแล้ว!")
                    st.rerun()
    else:
        st.info("คำแนะนำ: ยังไม่มีรายการสินค้าในตารางชั่วคราว กรุณาระบุรหัสสินค้าด้านบนเพื่อดำเนินการเพิ่มข้อมูล")

# ----------------------------------------------------
# 2. แผนกควบคุมคุณภาพ (QC) - เลือกหลายโค้ด ผ่านยกแผงในปุ่มเดียว
# ----------------------------------------------------
elif st.session_state.current_page == "QC":
    st.subheader("🔍 ส่วนงานฝ่ายควบคุมคุณภาพ (Quality Control - QC): ตรวจสอบเกณฑ์เกรดสเปกสินค้า")
    df = st.session_state.current_db
    qc_pending_list = df[df['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)']
    
    if qc_pending_list.empty:
        st.info("ไม่มีรายการสินค้าค้างตรวจสอบคุณภาพในระบบขณะนี้")
    else:
        st.write("### 📋 รายการสินค้าค้างตรวจสเปก")
        qc_name = st.text_input("ชื่อเจ้าหน้าที่พนักงานตรวจสอบคุณภาพ (QC):", key="qc_global_name")
        
        options_map_qc = {}
        for _, r in qc_pending_list.iterrows():
            display_text = f"คิวงาน: {r['JobID']} | รหัสสินค้า: {r['SKU']} | จำนวน: {r['PD_Qty']:,} ชิ้น (รอบ: {r['PD_Shift']})"
            options_map_qc[display_text] = r['JobID']
            
        selected_qc_jobs = st.multiselect("คลิกเลือกคิวงานสินค้าที่ตรวจสอบผ่านเกณฑ์พร้อมกันหลายรายการ:", list(options_map_qc.keys()))
        
        st.write("---")
        col_qc_act1, col_qc_act2 = st.columns(2)
        with col_qc_act1:
            if st.button("✅ อนุมัติมาตรฐานผ่านเกณฑ์ทุกรายการที่เลือก (Approve ยกแผง)", type="primary", use_container_width=True):
                if qc_name.strip() == "":
                    st.error("กรุณาระบุชื่อพนักงาน QC ก่อนทำการกดยืนยันข้อมูล")
                elif not selected_qc_jobs:
                    st.error("กรุณาคลิกเลือกรายการคิวงานสินค้าที่ต้องการอนุมัติอย่างน้อย 1 รายการ")
                else:
                    for option in selected_qc_jobs:
                        job_id_extracted = options_map_qc[option] 
                        
#----------------------------------------------------
# 3. แผนกคลังสินค้าสำเร็จรูป (FG) - เลือกหลายโค้ด อนุมัติรับงานยกแผงปุ่มเดียวส่งต่อด่าน 4 ได้จริง 100%
# ----------------------------------------------------
elif st.session_state.current_page == "FG":
    st.subheader("📥 ส่วนงานฝ่ายคลังสินค้าสำเร็จรูป (Finished Goods - FG): ตรวจนับสต็อกรับจริง")
    df = st.session_state.current_db
    fg_pending_list = df[df['FG_Status'] == 'รอคลังรับเข้า (Pending FG)']
    
    if fg_pending_list.empty:
        st.info("ไม่มีรายการสินค้าค้างรับเข้าคลังสินค้าสำเร็จรูปในระบบขณะนี้")
    else:
        st.write("### 📦 รายการสินค้าค้างนับรับเข้าสต็อก")
        fg_name = st.text_input("ชื่อพนักงานคลังสินค้าผู้ตรวจนับของจริง:", key="fg_global_name")
        
        options_map_fg = {}
        for _, r in fg_pending_list.iterrows():
            display_text = f"📦 คิวงาน: {r['JobID']} | รหัสสินค้า: {r['SKU']} | ยอดแจ้งส่ง: {r['PD_Qty']:,} ชิ้น (รอบ: {r['PD_Shift']}) | QC ผู้ตรวจ: {r['QC_Name']}"
            options_map_fg[display_text] = r['JobID']
            
        selected_fg_jobs = st.multiselect("คลิกเลือกคิวงานสินค้าที่ต้องการรับเข้าสต็อกคลังพร้อมกันหลายรายการ:", list(options_map_fg.keys()))
        
        st.write("---")
        # ปุ่มหลัก: บันทึกรับของเข้าคลังแบบยกแผงปุ่มเดียวผ่านฉลุย ยอดวิ่งไปหน้าแอดมินส่วนที่ 4 ทันที
        if st.button("💾 ยืนยันบันทึกรับสินค้าเข้าสต็อกทุกรายการที่เลือก (Approve ยกแผง)", type="primary", use_container_width=True):
            if fg_name.strip() == "":
                st.error("กรุณาระบุชื่อพนักงานคลังสินค้าผู้ตรวจนับของจริงก่อนกดยืนยัน")
            elif not selected_fg_jobs:
                st.error("กรุณาคลิกเลือกรายการคิวงานสินค้าที่ต้องการรับเข้าสต็อกอย่างน้อย 1 รายการ")
            else:
                for option in selected_fg_jobs:
                    job_id_extracted = options_map_fg[option]
                    idx = df[df['JobID'] == job_id_extracted].index
                    # ใช้คำสั่งระบุพิกัดตรงตัว .loc เพื่อให้ระบบคัดลอกค่าจำนวนเซฟทับและผลักข้อมูลไปส่วนที่ 4 ได้ทันที ไม่พังแถบชมพู
                    df.loc[idx, 'FG_Qty'] = df.loc[idx, 'PD_Qty'].values
                    df.loc[idx, 'FG_Name'] = fg_name
                    df.loc[idx, 'FG_Status'] = 'รับเข้าคลังสำเร็จ (Completed)'
                save_data(df)
                st.success(f"คลังสินค้า FG บันทึกรับเข้าสต็อกสำเร็จ {len(selected_fg_jobs)} รายการ! ยอดถูกจัดส่งไปหน้าตารางสรุปผลแอดมิน ERP แล้ว")
                st.rerun()
                
        if st.button("🗑️ ลบคิวงานคลัง FG ที่เลือกออกจากระบบ", use_container_width=True):
            if not selected_fg_jobs:
                st.error("กรุณาเลือกรายการคิวงานที่ต้องการลบก่อนกดปุ่ม")
            else:
                for option in selected_fg_jobs:
                    job_id_extracted = options_map_fg[option]
                    df = df[df['JobID'] != job_id_extracted]
                save_data(df)
                st.success("ลบรายการคิวงานที่เลือกออกจากระบบสำเร็จแล้ว!")
                st.rerun()

# ----------------------------------------------------
# 4. ฝ่ายบริหารข้อมูลคลัง (ERP Admin) - ยอดรับจริงหน้างาน 100% พร้อมปุ่มโหลดไฟล์ลง ERP
# ----------------------------------------------------
elif st.session_state.current_page == "ERP":
    st.header("หน้าจอส่วนงาน: ฝ่ายบริหารข้อมูลคลังสินค้า (ERP Administrator)")
    st.subheader("รายงานสรุปตรวจสอบยอดรับจริงหน้างาน 100% เพื่อนำข้อมูลคีย์ลงระบบ ERP")
    
    df = st.session_state.current_db
    df_erp_display = df.copy()
    df_erp_display.insert(0, 'เลือกเพื่อลบ', False)
    
    edited_erp_df = st.data_editor(
        df_erp_display[['เลือกเพื่อลบ', 'JobID', 'Timestamp', 'PD_Shift', 'PD_Name', 'SKU', 'PD_Qty', 'QC_Status', 'QC_Name', 'FG_Qty', 'FG_Status', 'FG_Name']],
        hide_index=True,
        use_container_width=True,
        disabled=['JobID', 'Timestamp', 'PD_Shift', 'PD_Name', 'SKU', 'PD_Qty', 'QC_Status', 'QC_Name', 'FG_Qty', 'FG_Status', 'FG_Name']
    )
    
    st.write("---")
    col_admin1, col_admin2 = st.columns(2)
    with col_admin1:
        completed_jobs = df[df['FG_Status'] == 'รับเข้าคลังสำเร็จ (Completed)']
        if not completed_jobs.empty:
            csv = completed_jobs.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์รายงานยอดรับจริง (.CSV) สำหรับนำข้อมูลอัปโหลดเข้า ERP ของบริษัททันที",
                data=csv,
                file_name="Finished_Goods_Verified_Report.csv",
                mime='text/csv',
                use_container_width=True
            )
            
    with col_admin2:
        if st.button("🚨 ลบข้อมูลประวัติที่เลือกออกจากฐานข้อมูลถาวร", use_container_width=True):
            selected_del_jobs = edited_erp_df[edited_erp_df['เลือกเพื่อลบ'] == True]['JobID'].tolist()
            if not selected_del_jobs:
                st.error("กรุณาติ๊กถูกหน้าคิวงานที่ต้องการลบในตารางสรุปผลก่อนกดปุ่ม")
            else:
                for job in selected_del_jobs:
                    df = df[df['JobID'] != job]
                save_data(df)
                st.success(f"ลบข้อมูลคิวงานออกจากระบบถาวรเรียบร้อยแล้วจำนวน {len(selected_del_jobs)} รายการ!")
                st.rerun()
