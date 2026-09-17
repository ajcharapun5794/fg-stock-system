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
        'JobID', 'Timestamp', 'PD_Name', 'SKU', 'PD_Qty', 'QC_Status', 'QC_Name', 'FG_Qty', 'FG_Status', 'FG_Name'
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

# คำนวณจำนวนงานค้างของแต่ละแผนก
count_qc = len(df_current[df_current['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)'])
count_fg = len(df_current[df_current['FG_Status'] == 'รอคลังรับเข้า (Pending FG)'])

if 'current_page' not in st.session_state:
    st.session_state.current_page = "PD"

# ====================================================
# NEW SIDEBAR PORTAL: การันตีเปลี่ยนสีปุ่มเมนู 4 แทบด้านซ้าย
# ====================================================
st.sidebar.markdown("## เมนูระบบงานหลัก")

# 1. แทบฝ่ายผลิต (PD)
st.sidebar.info("🟢 1. แผนกฝ่ายผลิต (PD)")
if st.sidebar.button("👉 เปิดหน้าบันทึกส่งมอบงาน", key="btn_nav_pd", use_container_width=True):
    st.session_state.current_page = "PD"
    st.rerun()

st.sidebar.write("")

# 2. แทบฝ่ายควบคุมคุณภาพ (QC)
if count_qc > 0:
    st.sidebar.error(f"🔴 2. แผนกควบคุมคุณภาพ (QC) \n(ค้าง {count_qc} รายการ)")
else:
    st.sidebar.info("🟢 2. แผนกควบคุมคุณภาพ (QC) \n(ไม่มีงานค้าง)")
    
if st.sidebar.button("👉 เปิดหน้าตรวจสอบสเปกสินค้า", key="btn_nav_qc", use_container_width=True):
    st.session_state.current_page = "QC"
    st.rerun()

st.sidebar.write("")

# 3. แทบฝ่ายคลังสินค้า (FG)
if count_fg > 0:
    st.sidebar.error(f"🔴 3. แผนกคลังสินค้าสำเร็จรูป (FG) \n(ค้าง {count_fg} รายการ)")
else:
    st.sidebar.info("🟢 3. แผนกคลังสินค้าสำเร็จรูป (FG) \n(ไม่มีงานค้าง)")
    
if st.sidebar.button("👉 เปิดหน้าตรวจนับยอดรับสินค้า", key="btn_nav_fg", use_container_width=True):
    st.session_state.current_page = "FG"
    st.rerun()

st.sidebar.write("")

# 4. แทบฝ่ายแอดมิน ERP
st.sidebar.success("📊 4. ฝ่ายบริหารข้อมูลคลัง (ERP)")
if st.sidebar.button("👉 เปิดรายงานสรุปยอดลง ERP", key="btn_nav_erp", use_container_width=True):
    st.session_state.current_page = "ERP"
    st.rerun()

# ====================================================
# WORKFLOW PAGES INTERFACE (เนื้อหาฝั่งขวา)
# ====================================================

# ----------------------------------------------------
# 1. หน้าจอส่วนงาน: ฝ่ายผลิต (PD)
# ----------------------------------------------------
if st.session_state.current_page == "PD":
    st.subheader("⚙️ ส่วนงานฝ่ายผลิต (Production - PD): บันทึกส่งมอบงานสินค้า")
    pd_name = st.text_input("ชื่อพนักงานฝ่ายผลิตผู้บันทึกข้อมูล:")
    
    st.markdown("#### ตารางรายการรหัสสินค้าที่ต้องการนำส่ง")
    if 'temp_items' not in st.session_state:
        st.session_state.temp_items = []

    with st.container(border=True):
        # 🔥 แก้ไขจุดบั๊กในภาพเรียบร้อย: ดึงค่ากลับมาเป็นรูปแบบกล่องอาร์เรย์ (List) รองรับระบบเวอร์ชันใหม่
        cols = st.columns(3)
        with cols[0]:
            input_sku = st.text_input("ระบุรหัสสินค้า หรือใช้ปืนสแกนบาร์โค้ดยิง (SKU):", key="input_sku")
        with cols[1]:
            input_qty = st.number_input("จำนวนสินค้าที่นำส่งมอบจริง:", min_value=1, step=1, key="input_qty")
        with cols[2]:
            st.write("") 
            st.write("") 
            if st.button("➕ เพิ่มเข้าตาราง", use_container_width=True):
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
        if st.button("🚀 ยืนยันการนำส่งข้อมูลทั้งหมดให้ฝ่ายควบคุมคุณภาพ (QC)", type="primary", use_container_width=True):
            if pd_name.strip() == "":
                st.error("กรุณาระบุชื่อพนักงานฝ่ายผลิตผู้บันทึกข้อมูลก่อนกดยืนยัน")
            else:
                df = st.session_state.current_db
                timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                for item in st.session_state.temp_items:
                    new_id = len(df) + 1
                    job_id = f"JOB-{new_id:04d}"
                    new_data = {
                        'JobID': job_id, 'Timestamp': timestamp_now,
                        'PD_Name': pd_name, 'SKU': item['SKU'], 'PD_Qty': item['Qty'],
                        'QC_Status': 'รอ QC ตรวจสอบ (Pending QC)', 'QC_Name': '-',
                        'FG_Qty': 0, 'FG_Status': 'รอผ่าน QC', 'FG_Name': '-'
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
            title_text = f"📋 คิวงาน: {row['JobID']} | รหัสสินค้า: {row['SKU']} | จำนวน: {row['PD_Qty']:,} ชิ้น"
            with st.expander(title_text):
                st.write(f"### รหัสสินค้า (SKU): **{row['SKU']}**")
                st.write(f"### ปริมาณแจ้งส่งมอบจากแผนกผลิต: **{row['PD_Qty']:,} ชิ้น**")
                st.write(f"เจ้าหน้าที่แผนกผลิตผู้ส่งของ: {row['PD_Name']} | เวลาบันทึกระบบ: {row['Timestamp']}")
                
                qc_name = st.text_input("ชื่อเจ้าหน้าที่พนักงานตรวจสอบคุณภาพ (QC):", key=f"qc_name_{row['JobID']}")
                col_qc_btns = st.columns(2)
                
                with col_qc_btns[0]:
                    if st.button("✅ อนุมัติมาตรฐานผ่านเกณฑ์ (Approve)", key=f"qc_app_{row['JobID']}", use_container_width=True):
                        if qc_name.strip() != "":
                            df.at[idx, 'QC_Status'] = 'สเปกผ่านแล้ว (Approved)'
                            df.at[idx, 'QC_Name'] = qc_name
                            df.at[idx, 'FG_Status'] = 'รอคลังรับเข้า (Pending FG)'
                            save_data(df)
                            st.rerun()
                        else:
                            st.error("กรุณาระบุชื่อพนักงาน QC ก่อนทำการกดยืนยันข้อมูล")
                        
                with col_qc_btns[1]:
                    if st.button("❌ ปฏิเสธเกณฑ์/ตีกลับงานเสีย (Reject/NG)", key=f"qc_rej_{row['JobID']}", use_container_width=True):
                        if qc_name.strip() != "":
                            df.at[idx, 'QC_Status'] = 'ตีกลับ/สเปกไม่ผ่าน (NG)'
                            df.at[idx, 'QC_Name'] = qc_name
                            df.at[idx, 'FG_Status'] = 'ยกเลิก (QC ไม่ผ่าน)'
                            save_data(df)
                            st.rerun()
                        else:
                            st.error("กรุณาระบุชื่อพนักงาน QC ก่อนทำการกดยืนยันข้อมูล")

# ----------------------------------------------------
# 3. หน้าจอส่วนงาน: คลังสินค้าสำเร็จรูป (FG)
# ----------------------------------------------------
elif st.session_state.current_page == "FG":
    st.subheader("📥 ส่วนงานฝ่ายคลังสินค้าสำเร็จรูป (Finished Goods - FG): ตรวจนับสต็อกรับจริง")
    
    df = st.session_state.current_db
    fg_pending_indices = df[df['FG_Status'] == 'รอคลังรับเข้า (Pending FG)'].index.tolist()
    
    if not fg_pending_indices:
        st.info("ไม่มีรายการสินค้าค้างรับเข้าคลังสินค้าสำเร็จรูปในระบบขณะนี้")
    else:
        for idx in fg_pending_indices:
            row = df.loc[idx]
            title_text = f"📦 คิวงาน: {row['JobID']} | รหัสสินค้า: {row['SKU']} | ยอดในใบส่ง: {row['PD_Qty']:,} ชิ้น"
            with st.expander(title_text):
                st.write(f"### รหัสสินค้า (SKU): **{row['SKU']}**")
                st.write(f"### ปริมาณนำส่งตามเกณฑ์ระบบ: **{row['PD_Qty']:,} ชิ้น**")
