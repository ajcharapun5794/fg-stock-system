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
        'Select', 'JobID', 'Timestamp', 'PD_Shift', 'PD_Name', 'SKU', 'PD_Qty', 'QC_Status', 'QC_Name', 'FG_Qty', 'FG_Status', 'FG_Name'
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
# SIDEBAR PORTAL: แถบไฟสีแจ้งเตือนเมนูข้าง
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
# WORKFLOW PAGES INTERFACE
# ====================================================

# ----------------------------------------------------
# 1. แผนกฝ่ายผลิต (PD)
# ----------------------------------------------------
if current_page == "PD":
    st.subheader("⚙️ ส่วนงานฝ่ายผลิต (Production - PD): บันทึกส่งมอบงานสินค้า")
    
    # เพิ่มช่องเวลา/รอบส่งงานตามสั่ง
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
                        'Select': False, 'JobID': job_id, 'Timestamp': timestamp_now,
                        'PD_Shift': pd_shift, 'PD_Name': pd_name, 'SKU': item['SKU'], 'PD_Qty': item['Qty'],
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
# 2. แผนกควบคุมคุณภาพ (QC) - ปรับเป็นตารางอนุมัติพร้อมกันได้หลายโค้ด
# ----------------------------------------------------
elif current_page == "QC":
    st.subheader("🔍 ส่วนงานฝ่ายควบคุมคุณภาพ (Quality Control - QC): ตรวจสอบเกณฑ์เกรดสเปกสินค้า")
    df = st.session_state.current_db
    
    # ดึงงานค้างเฉพาะของ QC
    df_qc = df[df['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)']
    
    if df_qc.empty:
        st.info("ไม่มีรายการสินค้าค้างตรวจสอบคุณภาพในระบบขณะนี้")
    else:
        st.write("### 📋 รายการสินค้าค้างตรวจสเปก")
        st.caption("ติ๊กถูกหน้าช่องรายการที่ต้องการ จากนั้นพิมพ์ชื่อผู้ตรวจแล้วกดปุ่มอนุมัติพร้อมกันด้านล่าง")
        
        qc_name = st.text_input("ชื่อเจ้าหน้าที่พนักงานตรวจสอบคุณภาพ (QC):", key="qc_global_name")
        
        # แสดงตารางแบบโต้ตอบ ติ๊กเลือกได้หลายช่องพร้อมกัน (Data Editor)
        edited_df_qc = st.data_editor(
            df_qc[['Select', 'JobID', 'Timestamp', 'PD_Shift', 'PD_Name', 'SKU', 'PD_Qty']],
            hide_index=True,
            use_container_width=True,
            disabled=['JobID', 'Timestamp', 'PD_Shift', 'PD_Name', 'SKU', 'PD_Qty']
        )
        
        st.write("---")
        col_qc1, col_qc2 = st.columns(2)
        
        with col_qc1:
            if st.button("✅ อนุมัติมาตรฐานผ่านเกณฑ์ทุกรายการที่เลือก (Approve)", type="primary", use_container_width=True):
                if qc_name.strip() == "":
                    st.error("กรุณาระบุชื่อพนักงาน QC ก่อนทำการกดยืนยันข้อมูล")
                else:
                    selected_jobs = edited_df_qc[edited_df_qc['Select'] == True]['JobID'].tolist()
                    if not selected_jobs:
                        st.error("กรุณาติ๊กเลือกรายการสินค้าในตารางอย่างน้อย 1 รายการ")
                    else:
                        for job in selected_jobs:
                            idx = df[df['JobID'] == job].index[0]
                            df.at[idx, 'QC_Status'] = 'สเปกผ่านแล้ว (Approved)'
                            df.at[idx, 'QC_Name'] = qc_name
                            df.at[idx, 'FG_Status'] = 'รอคลังรับเข้า (Pending FG)'
                        save_data(df)
                        st.success(f"อนุมัติผ่านเกณฑ์สำเร็จ {len(selected_jobs)} รายการ!")
                        st.rerun()
                        
        with col_qc2:
            if st.button("❌ ตีกลับงานเสียทุกรายการที่เลือก (Reject/NG)", use_container_width=True):
                if qc_name.strip() == "":
                    st.error("กรุณาระบุชื่อพนักงาน QC ก่อนทำการกดยืนยันข้อมูล")
                else:
                    selected_jobs = edited_df_qc[edited_df_qc['Select'] == True]['JobID'].tolist()
                    if not selected_jobs:
                        st.error("กรุณาติ๊กเลือกรายการสินค้าในตารางอย่างน้อย 1 รายการ")
                    else:
                        for job in selected_jobs:
                            idx = df[df['JobID'] == job].index[0]
                            df.at[idx, 'QC_Status'] = 'ตีกลับ/สเปกไม่ผ่าน (NG)'
                            df.at[idx, 'QC_Name'] = qc_name
                            df.at[idx, 'FG_Status'] = 'ยกเลิก (QC ไม่ผ่าน)'
                        save_data(df)
                        st.error(f"ตีกลับงานเสียสำเร็จ {len(selected_jobs)} รายการ!")
                        st.rerun()

# ----------------------------------------------------
# 3. แผนกคลังสินค้าสำเร็จรูป (FG) - ปรับเป็นตารางอนุมัติพร้อมกันได้หลายโค้ด
# ----------------------------------------------------
elif current_page == "FG":
    st.subheader("📥 ส่วนงานฝ่ายคลังสินค้าสำเร็จรูป (Finished Goods - FG): ตรวจนับสต็อกรับจริง")
    df = st.session_state.current_db
    
    # ดึงงานค้างเฉพาะของ FG
    df_fg = df[df['FG_Status'] == 'รอคลังรับเข้า (Pending FG)']
    
    if df_fg.empty:
        st.info("ไม่มีรายการสินค้าค้างรับเข้าคลังสินค้าสำเร็จรูปในระบบขณะนี้")
    else:
        st.write("### 📦 รายการสินค้าค้างนับรับเข้าสต็อก")
        st.caption("ตรวจสอบยอดหน้างานจริง หากของครบถ้วนให้ติ๊กถูกหน้าช่อง แล้วกดปุ่มยืนยันรับเข้าคลังพร้อมกันได้เลย")
