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

# คำนวณจำนวนงานค้างที่แท้จริง
count_qc = len(df_current[df_current['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)'])
count_fg = len(df_current[df_current['FG_Status'] == 'รอคลังรับเข้า (Pending FG)'])

# ====================================================
# SIDEBAR PORTAL: ระบบเลือกแผนกงานหลัก (แถบไฟสี เขียว/แดง เสถียร 100%)
# ====================================================
st.sidebar.markdown("## เมนูระบบงานหลัก")

status_pd = "🟢 1. แผนกฝ่ายผลิต (PD) - ปกติ"
status_qc = f"🚨 2. แผนกควบคุมคุณภาพ (QC) - [ค้าง {count_qc} รายการ]" if count_qc > 0 else "🟢 2. แผนกควบคุมคุณภาพ (QC) - ไม่มีงานค้าง"
status_fg = f"🚨 3. แผนกคลังสินค้าสำเร็จรูป (FG) - [ค้าง {count_fg} รายการ]" if count_fg > 0 else "🟢 3. แผนกคลังสินค้าสำเร็จรูป (FG) - ไม่มีงานค้าง"
status_erp = "📊 4. ฝ่ายบริหารข้อมูลคลัง (ERP Admin)"

menu_options = [status_pd, status_qc, status_fg, status_erp]
choice = st.sidebar.radio("คลิกเลือกแผนกงานของคุณด้านล่างนี้:", menu_options)

if choice == status_pd:
    current_page = "PD"
elif choice == status_qc:
    current_page = "QC"
elif choice == status_fg:
    current_page = "FG"
else:
    current_page = "ERP"

# ====================================================
# WORKFLOW PAGES INTERFACE (เนื้อหาฝั่งขวา)
# ====================================================

# ----------------------------------------------------
# 1. แผนกฝ่ายผลิต (PD)
# ----------------------------------------------------
if current_page == "PD":
    st.subheader("⚙️ ส่วนงานฝ่ายผลิต (Production - PD): บันทึกส่งมอบงานสินค้า")
    pd_name = st.text_input("ชื่อพนักงานฝ่ายผลิตผู้บันทึกข้อมูล:")
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
# 2. แผนกควบคุมคุณภาพ (QC) - เคลียร์บั๊กคอลลัมน์ปุ่มออกเรียบร้อย
# ----------------------------------------------------
elif current_page == "QC":
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
                st.write("")
                
                # 🛠️ จุดซ่อมแซมใหญ่: ปรับปืนปุ่มเรียงแถวลงมา คลีน ๆ เสถียร 100% ล้าง Error แถบส้มออกถาวร
                if st.button("✅ อนุมัติมาตรฐานผ่านเกณฑ์ (Approve)", key=f"qc_app_{row['JobID']}", use_container_width=True):
                    if qc_name.strip() != "":
                        df.at[idx, 'QC_Status'] = 'สเปกผ่านแล้ว (Approved)'
                        df.at[idx, 'QC_Name'] = qc_name
                        save_data(df)
                        st.rerun()
                    else:
                        st.error("กรุณาระบุชื่อพนักงาน QC ก่อนทำการกดยืนยันข้อมูล")
                        
                if st.button("❌ ปฏิเสธเกณฑ์/ตีกลับงานเสีย (Reject/NG)", key=f"qc_rej_{row['JobID']}", use_container_width=True):
                    if qc_name.strip() != "":
                        df.at[idx, 'QC_Status'] = 'ตีกลับ/สเปกไม่ผ่าน (NG)'
                        df.at[idx, 'QC_Name'] = qc_name
                        save_data(df)
                        st.rerun()
                    else:
                        st.error("กรุณาระบุชื่อพนักงาน QC ก่อนทำการกดยืนยันข้อมูล")

# ----------------------------------------------------
# 3. แผนกคลังสินค้าสำเร็จรูป (FG)
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
            title_text = f"📦 คิวงาน: {row['JobID']} | รหัสสินค้า: {row['SKU']} | ยอดแจ้งส่ง: {row['PD_Qty']:,} ชิ้น"
            with st.expander(title_text, expanded=True):
                st.write(f"### รหัสสินค้า (SKU): **{row['SKU']}**")
                st.write(f"### ปริมาณที่ระบุในใบส่งมอบ: **{row['PD_Qty']:,} ชิ้น**")
                st.write(f"เจ้าหน้าที่แผนกผลิตผู้ส่งของ: {row['PD_Name']} | ผลตรวจสเปกจาก QC: **{row['QC_Status']}**")
                st.write("---")
                
                fg_name = st.text_input("ชื่อพนักงานคลังสินค้าผู้ตรวจนับของจริง:", key=f"fg_name_{row['JobID']}")
                
                # ขั้นตอนที่ 1: ปุ่มทางเลือกด่วน "ของครบ โค้ดตรงตามใบส่งมอบ"
                if st.button("✅ ขั้นตอนที่ 1: ยืนยันยอดตรง (ของครบ โค้ดตรง 100%)", key=f"fg_quick_{row['JobID']}", type="primary", use_container_width=True):
                    if fg_name.strip() != "":
                        df.at[idx, 'FG_Qty'] = row['PD_Qty']
                        df.at[idx, 'FG_Name'] = fg_name
                        df.at[idx, 'FG_Status'] = 'รับเข้าคลังสำเร็จ (Completed)'
                        save_data(df)
                        st.success("บันทึกข้อมูลของครบถ้วนเรียบร้อย!")
                        st.rerun()
                    else:
                        st.error("กรุณาระบุชื่อพนักงานคลังสินค้าผู้ตรวจนับของจริงก่อนกดยืนยัน")
