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
# DATABASE FUNCTIONS (ปรับปรุงให้รองรับข้อมูลจำลองนิ่งเสถียร)
# ====================================================
if 'mock_db' not in st.session_state:
    st.session_state.mock_db = pd.DataFrame(columns=[
        'JobID', 'Timestamp', 'PD_Name', 'SKU', 'PD_Qty', 'QC_Status', 'QC_Name', 'FG_Qty', 'FG_Status', 'FG_Name'
    ])

def load_data():
    # ใช้ฐานข้อมูลหน่วยความจำร่วมกันเป็นหลัก เพื่อไม่ให้โดน Google Sheet เปล่าๆ ดึงข้อมูลทับซ้อนระหว่างทดสอบ
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

# คำนวณจำนวนงานค้างของแต่ละแผนกเพื่ออัปเดตสีแทบเมนู
count_qc = len(df_current[df_current['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)'])
count_fg = len(df_current[df_current['FG_Status'] == 'รอคลังรับเข้า (Pending FG)'])

if 'current_page' not in st.session_state:
    st.session_state.current_page = "PD"

# ====================================================
# NEW SIDEBAR PORTAL: การันตีเปลี่ยนสีปุ่มเมนู 4 แทบด้านซ้าย
# ====================================================
st.sidebar.markdown("## เมนูระบบงานหลัก")

# ตรรกะเช็คว่าสีแทบด้านข้างต้องเป็นสีอะไร (ถ้ามีงานค้าง = แดงเด่น / ถ้าไม่มีงานค้าง = เขียวเคลียร์)
status_qc_color = "🔴 มีงานค้าง" if count_qc > 0 else "🟢 เคลียร์หมด"
status_fg_color = "🔴 มีงานค้าง" if count_fg > 0 else "🟢 เคลียร์หมด"

# ใช้เทคนิคเปลี่ยนปุ่มกดสไตล์ทางการให้เปลี่ยนสีพื้นหลังตามสถานะงานค้างจริง 100% ไม่หลุดตำแหน่ง
st.sidebar.markdown(
    f"""
    <style>
    .nav-box {{ padding: 12px; border-radius: 8px; margin-bottom: 10px; font-weight: bold; text-align: center; }}
    .status-green {{ background-color: #E8F5E9; color: #1B5E20; border: 1px solid #A5D6A7; }}
    .status-red {{ background-color: #FFEBEE; color: #B71C1C; border: 1px solid #EF9A9A; animation: blinker 2s linear infinite; }}
    .status-blue {{ background-color: #E3F2FD; color: #0D47A1; border: 1px solid #90CAF9; }}
    </style>
    """, unsafe_allow_html=True
)

# 1. แทบฝ่ายผลิต (PD)
st.sidebar.markdown('<div class="nav-box status-green">1. แผนกฝ่ายผลิต (PD)</div>', unsafe_allow_html=True)
if st.sidebar.button("👉 เปิดหน้าบันทึกส่งมอบงาน", key="btn_nav_pd", use_container_width=True):
    st.session_state.current_page = "PD"
    st.rerun()

# 2. แทบฝ่ายควบคุมคุณภาพ (QC)
class_qc = "status-red" if count_qc > 0 else "status-green"
st.sidebar.markdown(f'<div class="nav-box {class_qc}">2. แผนกควบคุมคุณภาพ (QC)<br><small>สถานะ: {status_qc_color} ({count_qc} รายการ)</small></div>', unsafe_allow_html=True)
if st.sidebar.button("👉 เปิดหน้าตรวจสอบสเปกสินค้า", key="btn_nav_qc", use_container_width=True):
    st.session_state.current_page = "QC"
    st.rerun()

# 3. แทบฝ่ายคลังสินค้า (FG)
class_fg = "status-red" if count_fg > 0 else "status-green"
st.sidebar.markdown(f'<div class="nav-box {class_fg}">3. แผนกคลังสินค้าสำเร็จรูป (FG)<br><small>สถานะ: {status_fg_color} ({count_fg} รายการ)</small></div>', unsafe_allow_html=True)
if st.sidebar.button("👉 เปิดหน้าตรวจนับยอดรับสินค้า", key="btn_nav_fg", use_container_width=True):
    st.session_state.current_page = "FG"
    st.rerun()

# 4. แทบฝ่ายแอดมิน ERP
st.sidebar.markdown('<div class="nav-box status-blue">4. ฝ่ายบริหารข้อมูลคลัง (ERP)</div>', unsafe_allow_html=True)
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
        col_sku, col_qty, col_btn = st.columns([2, 2, 1])
        with col_sku:
            input_sku = st.text_input("ระบุรหัสสินค้า หรือใช้ปืนสแกนบาร์โค้ดยิง (SKU):", key="input_sku")
        with col_qty:
            input_qty = st.number_input("จำนวนสินค้าที่นำส่งมอบจริง:", min_value=1, step=1, key="input_qty")
        with col_btn:
            st.write("") # ผลักระยะปุ่มให้ตรงช่อง
            st.write("") 
            if st.button("➕ เพิ่มเข้าตาราง", use_container_width=True):
                if input_sku.strip() != "":
                    st.session_state.temp_items.append({'SKU': input_sku.strip(), 'Qty': input_qty})
                    st.rerun()
                else:
                    st.error("กรุณาระบุรหัสสินค้า")

    if st.session_state.temp_items:
        df_temp = pd.DataFrame(st.session_state.temp_items)
        # แสดงผลตารางแบบตัวหนาให้อ่านง่าย
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
                # แสดงผลรหัสสินค้าและจำนวนตัวหนาขนาดใหญ่ชัดเจน
                st.markdown(f"### รหัสสินค้า (SKU): <span style='color:#0D47A1'><b>{row['SKU']}</b></span>", unsafe_allow_html=True)
                st.markdown(f"### ปริมาณแจ้งส่งมอบจากแผนกผลิต: <span style='color:#1B5E20'><b>{row['PD_Qty']:,} ชิ้น</b></span>", unsafe_allow_html=True)
                st.write(f"เจ้าหน้าที่แผนกผลิตผู้ส่งของ: {row['PD_Name']} | เวลาบันทึกระบบ: {row['Timestamp']}")
                
                qc_name = st.text_input("ชื่อเจ้าหน้าที่พนักงานตรวจสอบคุณภาพ (QC):", key=f"qc_name_{row['JobID']}")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ อนุมัติมาตรฐานผ่านเกณฑ์ (Approve)", key=f"qc_app_{row['JobID']}", use_container_width=True):
                        if qc_name.strip() != "":
                            df.at[idx, 'QC_Status'] = 'สเปกผ่านแล้ว (Approved)'
                            df.at[idx, 'QC_Name'] = qc_name
                            df.at[idx, 'FG_Status'] = 'รอคลังรับเข้า (Pending FG)'
                            save_data(df)
                            st.rerun()
                        else:
                            st.error("กรุณาระบุชื่อพนักงาน QC ก่อนทำการกดยืนยันข้อมูล")
                        
                with col2:
                    if st.button("❌ ปฏิเสธเกณฑ์/ตีกลับงานเสีย (Reject/NG)", key=f"qc_rej_{row['JobID']}", use_container_width=True):
                        if qc_name.strip() != "":
