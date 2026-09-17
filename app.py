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
def load_data():
    try:
        df = pd.read_csv(GSHEET_URL)
        return df
    except:
        if 'mock_db' not in st.session_state:
            st.session_state.mock_db = pd.DataFrame(columns=[
                'JobID', 'Timestamp', 'PD_Name', 'SKU', 'PD_Qty', 'QC_Status', 'QC_Name', 'FG_Qty', 'FG_Status', 'FG_Name'
            ])
        return st.session_state.mock_db

def save_data(df):
    st.session_state.current_db = df
    st.session_state.mock_db = df

# ====================================================
# SYSTEM CORE SETUP
# ====================================================
st.set_page_config(page_title="FG Stock Management System", layout="wide")
st.title("ระบบบริหารจัดการคลังสินค้าสำเร็จรูปและตรวจสอบคุณภาพ")
st.write("ระบบบันทึก ตรวจสอบ และเชื่อมโยงข้อมูลปริมาณสินค้าคลังสำเร็จรูป (FG)")

if 'current_db' not in st.session_state:
    st.session_state.current_db = load_data()

df_current = st.session_state.current_db

# คำนวณจำนวนงานค้างของแต่ละแผนกให้แม่นยำ
count_qc = len(df_current[df_current['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)'])
count_fg = len(df_current[df_current['FG_Status'] == 'รอคลังรับเข้า (Pending FG)'])

if 'current_page' not in st.session_state:
    st.session_state.current_page = "PD"

# ====================================================
# DYNAMIC COLOR SIDEBAR (ระบบเปลี่ยนสีปุ่มเมนูตามสถานะงานค้าง)
# ====================================================
st.sidebar.markdown("### เมนูระบบงานหลัก")

bg_pd = "#E8F5E9"  
bg_qc = "#FFEBEE" if count_qc > 0 else "#E8F5E9"  
bg_fg = "#FFEBEE" if count_fg > 0 else "#E8F5E9"  
bg_erp = "#E3F2FD" 

st.markdown(f"""
    <style>
    div.stButton > button:first-child {{ font-weight: bold; border-radius: 6px; }}
    .st-emotion-cache-164746f > div:nth-child(2) button {{ background-color: {bg_pd} !important; color: #1B5E20 !important; }}
    .st-emotion-cache-164746f > div:nth-child(3) button {{ background-color: {bg_qc} !important; color: {"#B71C1C" if count_qc > 0 else "#1B5E20"} !important; border: 1px solid {"#EF9A9A" if count_qc > 0 else "#A5D6A7"} !important; }}
    .st-emotion-cache-164746f > div:nth-child(4) button {{ background-color: {bg_fg} !important; color: {"#B71C1C" if count_fg > 0 else "#1B5E20"} !important; border: 1px solid {"#EF9A9A" if count_fg > 0 else "#A5D6A7"} !important; }}
    .st-emotion-cache-164746f > div:nth-child(5) button {{ background-color: {bg_erp} !important; color: #0D47A1 !important; }}
    </style>
""", unsafe_allow_html=True)

if st.sidebar.button("1. ฝ่ายผลิต (PD) - ส่งมอบสินค้า", use_container_width=True):
    st.session_state.current_page = "PD"
    st.rerun()

label_qc = f"2. ฝ่ายควบคุมคุณภาพ (QC) - ตรวจสเปก (ค้าง {count_qc})" if count_qc > 0 else "2. ฝ่ายควบคุมคุณภาพ (QC) - ไม่มีงานค้าง"
if st.sidebar.button(label_qc, use_container_width=True):
    st.session_state.current_page = "QC"
    st.rerun()

label_fg = f"3. ฝ่ายคลังสินค้า (FG) - ตรวจนับยอด (ค้าง {count_fg})" if count_fg > 0 else "3. ฝ่ายคลังสินค้า (FG) - ไม่มีงานค้าง"
if st.sidebar.button(label_fg, use_container_width=True):
    st.session_state.current_page = "FG"
    st.rerun()

if st.sidebar.button("4. ฝ่ายบริหารข้อมูลคลังสินค้า (ERP Admin)", use_container_width=True):
    st.session_state.current_page = "ERP"
    st.rerun()

# ====================================================
# WORKFLOW PAGES INTERFACE 
# ====================================================

# ----------------------------------------------------
# 1. ฝ่ายผลิต (PD)
# ----------------------------------------------------
if st.session_state.current_page == "PD":
    st.header("หน้าจอส่วนงาน: ฝ่ายผลิต (Production - PD)")
    st.subheader("บันทึกการนำส่งมอบสินค้าประจำวัน")
    
    pd_name = st.text_input("ชื่อพนักงานฝ่ายผลิตผู้บันทึกข้อมูล:", key="pd_operator_name")
    st.markdown("#### ตารางสรุปรายการสินค้าที่ต้องการส่งมอบในรอบนี้")
    
    if 'temp_items' not in st.session_state:
        st.session_state.temp_items = []

    with st.container(border=True):
        col_sku, col_qty, col_btn = st.columns(3)
        with col_sku:
            input_sku = st.text_input("ระบุรหัสสินค้า หรือสแกนบาร์โค้ด (SKU):", key="input_sku")
        with col_qty:
            input_qty = st.number_input("จำนวนที่ต้องการส่งมอบ (ชิ้น):", min_value=1, step=1, key="input_qty")
        with col_btn:
            st.write("") 
            st.write("") 
            if st.button("เพิ่มรายการลงตาราง", use_container_width=True):
                if input_sku.strip() != "":
                    st.session_state.temp_items.append({'SKU': input_sku.strip(), 'Qty': input_qty})
                    st.rerun()
                else:
                    st.error("กรุณาระบุรหัสสินค้าให้ถูกต้อง")

    if st.session_state.temp_items:
        df_temp = pd.DataFrame(st.session_state.temp_items)
        st.write("**รายการเตรียมจัดส่งขณะนี้:**")
        
        df_display = df_temp.copy()
        df_display['SKU'] = df_display['SKU'].apply(lambda x: f"**{x}**")
        df_display['Qty'] = df_display['Qty'].apply(lambda x: f"**{x:,} ชิ้น**")
        st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        st.write("")
        if st.button("ล้างรายการในตารางทั้งหมด", use_container_width=True):
            st.session_state.temp_items = []
            st.rerun()
            
        st.write("---")
        if st.button("ยืนยันการนำส่งข้อมูลทั้งหมดให้ฝ่ายควบคุมคุณภาพ (QC)", type="primary", use_container_width=True):
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
                st.success("บันทึกข้อมูลและส่งต่อเข้าคิวงานสำเร็จ")
                st.rerun()
    else:
        st.info("คำแนะนำ: ยังไม่มีรายการสินค้าในตารางชั่วคราว กรุณาระบุรหัสสินค้าด้านบนเพื่อดำเนินการเพิ่มข้อมูล")

# ----------------------------------------------------
# 2. ควบคุมคุณภาพ (QC)
# ----------------------------------------------------
elif st.session_state.current_page == "QC":
    st.header("หน้าจอส่วนงาน: ฝ่ายควบคุมคุณภาพ (Quality Control - QC)")
    st.subheader("รายการสินค้าค้างตรวจสอบเกณฑ์มาตรฐานคุณภาพสินค้า")
    
    if st.button("🔄 ดึงข้อมูลคิวงานล่าสุด"):
        st.session_state.current_db = load_data()
        st.rerun()
        
    df = st.session_state.current_db
    qc_pending_indices = df[df['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)'].index.tolist()
    
    if not qc_pending_indices:
        st.info("ไม่มีรายการสินค้าค้างตรวจสอบคุณภาพในระบบขณะนี้")
    else:
        for idx in qc_pending_indices:
            row = df.loc[idx]
            title_text = f"📋 คิวงาน: {row['JobID']} | รหัสสินค้า: {row['SKU']} | จำนวนจากฝ่ายผลิต: {row['PD_Qty']:,} ชิ้น"
            with st.expander(title_text):
                st.markdown(f"### รหัสสินค้า (SKU): `{row['SKU']}`")
                st.markdown(f"### จำนวนจากฝ่ายผลิต: **{row['PD_Qty']:,} ชิ้น**")
                st.write(f"ผู้บันทึกนำส่ง: {row['PD_Name']} | เวลาบันทึกข้อมูล: {row['Timestamp']}")
                
                qc_name = st.text_input("ชื่อพนักงานตรวจสอบคุณภาพ (QC):", key=f"qc_name_{row['JobID']}")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("อนุมัติมาตรฐานผ่านเกณฑ์ (Approve)", key=f"qc_app_{row['JobID']}"):
                        if qc_name.strip() != "":
                            df.at[idx, 'QC_Status'] = 'สเปกผ่านแล้ว (Approved)'
                            df.at[idx, 'QC_Name'] = qc_name
                            df.at[idx, 'FG_Status'] = 'รอคลังรับเข้า (Pending FG)'
                            save_data(df)
                            st.rerun()
                        else:
                            st.error("กรุณาระบุชื่อพนักงานตรวจสอบคุณภาพ (QC) ก่อนกดยืนยัน")
                        
                with col2:
                    if st.button("ปฏิเสธมาตรฐาน/ตีกลับงานเสีย (Reject/NG)", key=f"qc_rej_{row['JobID']}"):
                        if qc_name.strip() != "":
                            df.at[idx, 'QC_Status'] = 'ตีกลับ/สเปกไม่ผ่าน (NG)'
                            df.at[idx, 'QC_Name'] = qc_name
                            df.at[idx, 'FG_Status'] = 'ยกเลิก (QC ไม่ผ่าน)'
                            save_data(df)
                            st.rerun()
                        else:
                            st.error("กรุณาระบุชื่อพนักงานตรวจสอบคุณภาพ (QC) ก่อนกดยืนยัน")

# ----------------------------------------------------
# 3. คลังสินค้า (FG Receiver) - ซ่อมตรรกะการดึงแถวสำเร็จเรียบร้อย
