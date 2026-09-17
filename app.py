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
        return pd.DataFrame(columns=[
            'JobID', 'Timestamp', 'PD_Name', 'SKU', 'PD_Qty', 'QC_Status', 'QC_Name', 'FG_Qty', 'FG_Status', 'FG_Name'
        ])

def save_data(df):
    st.session_state.current_db = df

# ====================================================
# SYSTEM CORE SETUP
# ====================================================
st.set_page_config(page_title="FG Stock Management System", layout="wide")
st.title("ระบบบริหารจัดการคลังสินค้าสำเร็จรูปและตรวจสอบคุณภาพ")
st.write("ระบบบันทึก ตรวจสอบ และเชื่อมโยงข้อมูลปริมาณสินค้าคลังสำเร็จรูป (FG)")

if 'current_db' not in st.session_state:
    st.session_state.current_db = load_data()

df_current = st.session_state.current_db

# คำนวณจำนวนงานค้างเพื่อทำระบบแจ้งเตือนตัวเลขบนปุ่มเมนูข้าง
count_qc = len(df_current[df_current['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)'])
count_fg = len(df_current[df_current['FG_Status'] == 'รอคลังรับเข้า (Pending FG)'])

# 初始化 Navigation State
if 'current_page' not in st.session_state:
    st.session_state.current_page = "PD"

# ====================================================
# SIDEBAR PORTAL NAVIGATION (เรียงเมนูลงมาโดยไม่ต้องคลิกเลือก)
# ====================================================
st.sidebar.markdown("### เมนูระบบงานหลัก")

# ปุ่มที่ 1: ฝ่ายผลิต
if st.sidebar.button("1. ฝ่ายผลิต (PD) - บันทึกการส่งมอบสินค้า", use_container_width=True):
    st.session_state.current_page = "PD"
    st.status("เปลี่ยนหน้าจอสำเร็จ")

# ปุ่มที่ 2: QC + ป้ายแจ้งเตือนตัวเลขนับงานค้าง
label_qc = "2. ฝ่ายควบคุมคุณภาพ (QC) - ตรวจสอบสเปก"
if count_qc > 0:
    label_qc += f"🔴 (ค้าง {count_qc} รายการ)"
if st.sidebar.button(label_qc, use_container_width=True):
    st.session_state.current_page = "QC"
    st.status("เปลี่ยนหน้าจอสำเร็จ")

# ปุ่มที่ 3: คลังสินค้า FG + ป้ายแจ้งเตือนตัวเลขนับงานค้าง
label_fg = "3. ฝ่ายคลังสินค้า (FG Receiver) - ตรวจนับยอด"
if count_fg > 0:
    label_fg += f"🔴 (ค้าง {count_fg} รายการ)"
if st.sidebar.button(label_fg, use_container_width=True):
    st.session_state.current_page = "FG"
    st.status("เปลี่ยนหน้าจอสำเร็จ")

# ปุ่มที่ 4: แอดมินสรุปยอด
if st.sidebar.button("4. ฝ่ายบริหารข้อมูลคลังสินค้า (ERP Admin)", use_container_width=True):
    st.session_state.current_page = "ERP"
    st.status("เปลี่ยนหน้าจอสำเร็จ")

# ====================================================
# WORKFLOW PAGES INTERFACE
# ====================================================

# ----------------------------------------------------
# INTERFACE 1: ฝ่ายผลิต (PD)
# ----------------------------------------------------
if st.session_state.current_page == "PD":
    st.header("หน้าจอส่วนงาน: ฝ่ายผลิต (Production - PD)")
    st.subheader("บันทึกการนำส่งมอบสินค้าประจำวัน")
    
    pd_name = st.text_input("ชื่อพนักงานฝ่ายผลิตผู้บันทึกข้อมูล:", key="pd_operator_name")
    
    st.markdown("#### ตารางสรุปรายการสินค้าที่ต้องการส่งมอบในรอบนี้")
    st.caption("กรุณาระบุรหัสสินค้าและจำนวน จากนั้นกดเพิ่มเข้าตารางเพื่อส่งมอบพร้อมกันหลายรายการ")

    if 'temp_items' not in st.session_state:
        st.session_state.temp_items = []

    with st.container(border=True):
        col_sku, col_qty, col_btn = st.columns([5, 3, 2])
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
                else:
                    st.error("กรุณาระบุรหัสสินค้าให้ถูกต้อง")

    if st.session_state.temp_items:
        df_temp = pd.DataFrame(st.session_state.temp_items)
        st.table(df_temp)
        
        if st.button("ล้างรายการในตารางทั้งหมด", use_container_width=True):
            st.session_state.temp_items = []
            st.status("ล้างตารางข้อมูลสำเร็จ")
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
                st.success(f"บันทึกข้อมูลลงระบบคลาวด์สำเร็จ ส่งต่อข้อมูลเข้าคิวงานฝ่ายควบคุมคุณภาพ (QC) เรียบร้อยแล้ว")
                st.rerun()
    else:
        st.info("คำแนะนำ: ยังไม่มีรายการสินค้าในตารางชั่วคราว กรุณาระบุรหัสสินค้าด้านบนเพื่อดำเนินการเพิ่มข้อมูล")

# ----------------------------------------------------
# INTERFACE 2: ควบคุมคุณภาพ (QC)
# ----------------------------------------------------
elif st.session_state.current_page == "QC":
    st.header("หน้าจอส่วนงาน: ฝ่ายควบคุมคุณภาพ (Quality Control - QC)")
    st.subheader("รายการสินค้าค้างตรวจสอบเกณฑ์มาตรฐานคุณภาพสินค้า")
    
    df = st.session_state.current_db
    qc_pending = df[df['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)']
    
    if qc_pending.empty:
        st.info("ไม่มีรายการสินค้าค้างตรวจสอบคุณภาพในระบบขณะนี้")
    else:
        for idx, row in qc_pending.iterrows():
            with st.expander(f"รหัสคิวงาน: {row['JobID']} | รหัสสินค้า: {row['SKU']} | จำนวนจากฝ่ายผลิต: {row['PD_Qty']} ชิ้น"):
                st.write(f"ผู้บันทึกนำส่ง: {row['PD_Name']} | เวลาบันทึกข้อมูล: {row['Timestamp']}")
                qc_name = st.text_input("ชื่อพนักงานตรวจสอบคุณภาพ (QC):", key=f"qc_name_{row['JobID']}")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("อนุมัติมาตรฐานผ่านเกณฑ์ (Approve)", key=f"qc_app_{row['JobID']}") and qc_name:
                        df.at[idx, 'QC_Status'] = 'สเปกผ่านแล้ว (Approved)'
                        df.at[idx, 'QC_Name'] = qc_name
                        df.at[idx, 'FG_Status'] = 'รอคลังรับเข้า (Pending FG)'
                        save_data(df)
                        st.rerun()
                        
                with col2:
                    if st.button("ปฏิเสธมาตรฐาน/ตีกลับงานเสีย (Reject/NG)", key=f"qc_rej_{row['JobID']}") and qc_name:
                        df.at[idx, 'QC_Status'] = 'ตีกลับ/สเปกไม่ผ่าน (NG)'
                        df.at[idx, 'QC_Name'] = qc_name
                        df.at[idx, 'FG_Status'] = 'ยกเลิก (QC ไม่ผ่าน)'
                        save_data(df)
                        st.rerun()

# ----------------------------------------------------
# INTERFACE 3: คลังสินค้า (FG Receiver)
# ----------------------------------------------------
elif st.session_state.current_page == "FG":
    st.header("หน้าจอส่วนงาน: ฝ่ายคลังสินค้าสำเร็จรูป (Finished Goods - FG)")
    st.subheader("รายการตรวจสอบปริมาณสินค้านำเข้าคลังจริง")
    
    df = st.session_state.current_db
    fg_pending = df[df['FG_Status'] == 'รอคลังรับเข้า (Pending FG)']
    
    if fg_pending.empty:
        st.info("ไม่มีรายการสินค้าค้างรับเข้าคลังในระบบขณะนี้")
    else:
        for idx, row in fg_pending.iterrows():
            with st.expander(f"รหัสคิวงาน: {row['JobID']} | รหัสสินค้า: {row['SKU']} | ยอดแจ้งจากฝ่ายผลิต: {row['PD_Qty']} ชิ้น"):
                st.write(f"เจ้าหน้าที่ยืนยันคุณภาพสเปกสินค้า: {row['QC_Name']}")
                fg_name = st.text_input("ชื่อพนักงานคลังสินค้าผู้ตรวจนับของจริง:", key=f"fg_name_{row['JobID']}")
                actual_qty = st.number_input("ป้อนจำนวนที่ตรวจนับได้จริงหน้างาน:", min_value=0, step=1, value=int(row['PD_Qty']), key=f"fg_qty_{row['JobID']}")
                
                diff = actual_qty - row['PD_Qty']
                if diff == 0:
                    st.success("ปริมาณนับรับจริงตรงกับยอดระบบบันทึก")
                elif diff > 0:
                    st.warning(f"ตรวจสอบพบรายการสินค้าเกินระบบคิวงานจำนวน +{diff} ชิ้น (โปรดแยกสินค้าไว้ที่พื้นที่ Holding Area)")
                else:
                    st.error(f"ตรวจสอบพบรายการสินค้าขาดระบบคิวงานจำนวน {diff} ชิ้น")
                
                if st.button("บันทึกรับสินค้าเข้าคลังสำเร็จ", key=f"fg_save_{row['JobID']}") and fg_name:
                    df.at[idx, 'FG_Qty'] = actual_qty
                    df.at[idx, 'FG_Name'] = fg_name
                    df.at[idx, 'FG_Status'] = 'รับเข้าคลังสำเร็จ (Completed)'
                    save_data(df)
                    st.rerun()
