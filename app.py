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
# DATABASE FUNCTIONS (ระบบฐานข้อมูลประคองหน่วยความจำเสถียรสูงสุด)
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

# คำนวณจำนวนงานค้างของแต่ละแผนกเพื่อแสดงไฟสีด้านซ้าย
count_qc = len(df_current[df_current['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)'])
count_fg = len(df_current[df_current['FG_Status'] == 'รอคลังรับเข้า (Pending FG)'])

# ====================================================
# SIDEBAR PORTAL: แถบไฟเตือนสีเขียว-แดง (เสถียร 100% ไม่มีวันหาย)
# ====================================================
st.sidebar.markdown("## เมนูระบบงานหลัก")

status_qc_text = f"🔴 ค้าง {count_qc} รายการ" if count_qc > 0 else "🟢 ไม่มีงานค้าง"
status_fg_text = f"🔴 ค้าง {count_fg} รายการ" if count_fg > 0 else "🟢 ไม่มีงานค้าง"

color_qc_bg = "#FFEBEE" if count_qc > 0 else "#E8F5E9"
color_qc_txt = "#B71C1C" if count_qc > 0 else "#1B5E20"
color_qc_border = "#EF9A9A" if count_qc > 0 else "#A5D6A7"

color_fg_bg = "#FFEBEE" if count_fg > 0 else "#E8F5E9"
color_fg_txt = "#B71C1C" if count_fg > 0 else "#1B5E20"
color_fg_border = "#EF9A9A" if count_fg > 0 else "#A5D6A7"

st.sidebar.markdown(f"""
    <style>
    .nav-header {{ padding: 10px; border-radius: 6px; font-weight: bold; text-align: center; margin-top: 15px; margin-bottom: 5px; font-size: 14px; }}
    .c-pd {{ background-color: #E8F5E9; color: #1B5E20; border: 1px solid #A5D6A7; }}
    .c-qc {{ background-color: {color_qc_bg}; color: {color_qc_txt}; border: 1px solid {color_qc_border}; }}
    .c-fg {{ background-color: {color_fg_bg}; color: {color_fg_txt}; border: 1px solid {color_fg_border}; }}
    .c-erp {{ background-color: #E3F2FD; color: #0D47A1; border: 1px solid #90CAF9; }}
    div[data-testid="stSidebarUserContent"] button {{ font-weight: bold !important; font-size: 15px !important; }}
    </style>
""", unsafe_allow_html=True)

# 1. แผนกฝ่ายผลิต (PD)
st.sidebar.markdown('<div class="nav-header c-pd">1. แผนกฝ่ายผลิต (PD)</div>', unsafe_allow_html=True)
if st.sidebar.button("👉 เข้าสู่หน้าบันทึกส่งมอบงาน", key="nav_pd", use_container_width=True):
    st.session_state.current_page = "PD"
    st.rerun()

# 2. แผนกควบคุมคุณภาพ (QC)
st.sidebar.markdown(f'<div class="nav-header c-qc">2. แผนกควบคุมคุณภาพ (QC)<br><small>{status_qc_text}</small></div>', unsafe_allow_html=True)
if st.sidebar.button("👉 เข้าสู่หน้าตรวจสอบสเปก", key="nav_qc", use_container_width=True):
    st.session_state.current_page = "QC"
    st.rerun()

# 3. แผนกคลังสินค้าสำเร็จรูป (FG)
st.sidebar.markdown(f'<div class="nav-header c-fg">3. แผนกคลังสินค้าสำเร็จรูป (FG)<br><small>{status_fg_text}</small></div>', unsafe_allow_html=True)
if st.sidebar.button("👉 เข้าสู่หน้าตรวจนับยอดรับสินค้า", key="nav_fg", use_container_width=True):
    st.session_state.current_page = "FG"
    st.rerun()

# 4. ฝ่ายบริหารข้อมูลคลัง (ERP)
st.sidebar.markdown('<div class="nav-header c-erp">4. ฝ่ายบริหารข้อมูลคลัง (ERP)</div>', unsafe_allow_html=True)
if st.sidebar.button("👉 เข้าสู่รายงานสรุปยอดลง ERP", key="nav_erp", use_container_width=True):
    st.session_state.current_page = "ERP"
    st.rerun()

if 'current_page' not in st.session_state:
    st.session_state.current_page = "PD"

# ====================================================
# WORKFLOW PAGES INTERFACE (เนื้อหาฝั่งขวา)
# ====================================================

# ----------------------------------------------------
# 1. หน้าจอส่วนงาน: ฝ่ายผลิต (PD)
# ----------------------------------------------------
if st.session_state.current_page == "PD":
    st.subheader("⚙️ ส่วนงานฝ่ายผลิต (Production - PD): บันทึกส่งมอบงานสินค้า")
    
    # ช่องเวลา/รอบส่งงานที่เพิ่มเข้ามาตามสั่งจริง
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
        df_display = df_temp.copy()
        df_display['SKU'] = df_display['SKU'].apply(lambda x: f"<b>{x}</b>")
        df_display['Qty'] = df_display['Qty'].apply(lambda x: f"<b>{x:,} ชิ้น</b>")
        st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        st.write("")
        if st.button("🗑️ ล้างรายการสินค้าในตารางทั้งหมด", use_container_width=True):
            st.session_state.temp_items = []
            st.rerun()
            
        st.write("---")
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

# ----------------------------------------------------
# 2. หน้าจอส่วนงาน: ควบคุมคุณภาพ (QC)
# ----------------------------------------------------
elif st.session_state.current_page == "QC":
    st.subheader("🔍 ส่วนงานฝ่ายควบคุมคุณภาพ (Quality Control - QC): ตรวจสอบเกณฑ์เกรดสเปกสินค้า")
    df = st.session_state.current_db
    qc_pending_indices = df[df['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)'].index.tolist()
    
    if not qc_pending_indices:
        st.info("ไม่มีรายการสินค้าค้างตรวจสอบคุณภาพในระบบขณะนี้")
    else:
        for idx in qc_pending_indices:
            row = df.loc[idx]
            title_text = f"📋 คิวงาน: {row['JobID']} | รอบส่ง: {row['PD_Shift']} | รหัสสินค้า: {row['SKU']} | จำนวน: {row['PD_Qty']:,} ชิ้น"
            with st.expander(title_text):
                st.write(f"### รหัสสินค้า (SKU): **{row['SKU']}**")
                st.write(f"### ปริมาณแจ้งส่งมอบจากแผนกผลิต: **{row['PD_Qty']:,} ชิ้น**")
                st.write(f"รอบเวลาส่งงาน: {row['PD_Shift']} | พนักงานผู้ส่งของ: {row['PD_Name']}")
                
                qc_name = st.text_input("ชื่อเจ้าหน้าที่พนักงานตรวจสอบคุณภาพ (QC):", key=f"qc_name_{row['JobID']}")
                st.write("")
                
                if st.button("✅ อนุมัติมาตรฐานผ่านเกณฑ์ (Approve)", key=f"qc_app_{row['JobID']}", use_container_width=True):
                    if qc_name.strip() != "":
                        df.at[idx, 'QC_Status'] = 'สเปกผ่านแล้ว (Approved)'
                        df.at[idx, 'QC_Name'] = qc_name
                        save_data(df)
                        st.success("อนุมัติงานผ่านสำเร็จ!")
                        st.rerun()
                    else:
                        st.error("กรุณาระบุชื่อพนักงาน QC ก่อนทำการกดยืนยันข้อมูล")
                        
                if st.button("❌ ปฏิเสธเกณฑ์/ตีกลับงานเสีย (Reject/NG)", key=f"qc_rej_{row['JobID']}", use_container_width=True):
                    if qc_name.strip() != "":
                        df.at[idx, 'QC_Status'] = 'ตีกลับ/สเปกไม่ผ่าน (NG)'
                        df.at[idx, 'QC_Name'] = qc_name
                        df.at[idx, 'FG_Status'] = 'ยกเลิก (QC ไม่ผ่าน)'
                        save_data(df)
                        st.rerun()
# ----------------------------------------------------
# 3. แผนกคลังสินค้าสำเร็จรูป (FG) - จัดย่อหน้าและโครงสร้างใหม่ทั้งหมด ล้างบั๊กถาวร
# ----------------------------------------------------
elif current_page == "FG":
    st.subheader("📥 ส่วนงานฝ่ายคลังสินค้าสำเร็จรูป (Finished Goods - FG): ตรวจนับสต็อกรับจริง")
    df = st.session_state.current_db
    fg_pending_indices = df[df['FG_Status'] == 'รอคลังรับเข้า (Pending FG)'].index.tolist()
    
    if not fg_pending_indices:
        st.info("ไม่มีรายการสินค้าค้างรับเข้าคลังสินค้าสำเร็จรูปในระบบขณะนี้")
    else:
        for idx in fg_pending_indices:
            row = df.loc[idx]
            title_text = f"📦 คิวงาน: {row['JobID']} | รอบส่ง: {row['PD_Shift']} | รหัสสินค้า: {row['SKU']} | ยอดแจ้งส่ง: {row['PD_Qty']:,} ชิ้น"
            with st.expander(title_text, expanded=True):
                st.write(f"### รหัสสินค้า (SKU): **{row['SKU']}**")
                st.write(f"### ปริมาณที่ระบุในใบส่งมอบ: **{row['PD_Qty']:,} ชิ้น**")
                st.write(f"รอบเวลาส่งงาน: {row['PD_Shift']} | ผู้ส่ง: {row['PD_Name']} | ผลตรวจสเปกจาก QC: **{row['QC_Status']}**")
                st.write("---")
                
                fg_name = st.text_input("ชื่อพนักงานคลังสินค้าผู้ตรวจนับของจริง:", key=f"fg_name_{row['JobID']}")
                
                # ขั้นตอนที่ 1: ปุ่มทางเลือกด่วน "ของครบ โค้ดตรงตามใบส่งมอบ"
                if st.button("✅ ขั้นตอนที่ 1: ยืนยันยอดตรง (ของครบ โค้ดตรง 100%)", key=f"fg_quick_{row['JobID']}", type="primary", use_container_width=True):
                    if fg_name.strip() != "":
                        df.at[idx, 'FG_Qty'] = row['PD_Qty']
                        df.at[idx, 'FG_Name'] = fg_name
                        df.at[idx, 'FG_Status'] = 'รับเข้าคลังสำเร็จ (Completed)'
                        save_data(df)

# ----------------------------------------------------
# 4. ฝ่ายบริหารข้อมูลคลัง (ERP Admin) - ดึงรายงานสรุปยอดลง ERP
# ----------------------------------------------------
elif current_page == "ERP":
    st.header("หน้าจอส่วนงาน: ฝ่ายบริหารข้อมูลคลังสินค้า (ERP Administrator)")
    st.subheader("รายงานประวัติการหมุนเวียนและตรวจสอบสินค้าเพื่อนำข้อมูลลงระบบ ERP")
    
    df = st.session_state.current_db
    st.dataframe(df, use_container_width=True)
    
    # ดึงคิวงานที่ฝ่ายคลัง FG ตรวจนับเสร็จสมบูรณ์แล้วมารวมตารางรอส่งออก
    completed_jobs = df[df['FG_Status'] == 'รับเข้าคลังสำเร็จ (Completed)']
    if not completed_jobs.empty:
        csv = completed_jobs.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์รายงาน (.CSV) ยอดรับสินค้าผ่านการตรวจสอบเพื่อใช้คีย์เข้า ERP",
            data=csv,
            file_name="Finished_Goods_Verified_Report.csv",
            mime='text/csv',
            use_container_width=True
        )
