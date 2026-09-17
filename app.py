import streamlit as st
import pandas as pd
from datetime import datetime

# ====================================================
# ⚙️ CONFIGURATION: ใส่รหัสเชื่อมต่อ Google Sheets ของคุณ
# ====================================================
GOOGLE_SHEET_ID = "1Q14RlHndi2CjpA1SgamQAptmDKgCqtN8myuqteritg"
SHEET_NAME = "Sheet1"

GSHEET_URL = f"https://google.com{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# ====================================================
# 💾 FUNCTION: อ่านข้อมูลจากฐานข้อมูล
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
# 🖥️ STREAMLIT FRONTEND (หน้าจอระบบเว็บ)
# ====================================================
st.set_page_config(page_title="FG Stock Management System", layout="wide")
st.title("📦 ระบบสต็อก FG ป้องกันยอดดิฟ (Connected to Google Sheets)")

if 'current_db' not in st.session_state:
    st.session_state.current_db = load_data()

user_role = st.sidebar.selectbox("เลือกแผนกของคุณเพื่อเข้าใช้งาน:", ["1. ฝ่ายผลิต (PD)", "2. ควบคุมคุณภาพ (QC)", "3. คลังสินค้า (FG Receiver)", "4. แอดมินสรุปยอด (ERP Admin)"])

# ----------------------------------------------------
# 1. ฝ่ายผลิต (PD) - บันทึกงานส่งมอบ
# ----------------------------------------------------
if user_role == "1. ฝ่ายผลิต (PD)":
    st.header("🏭 หน้าจอสำหรับ ฝ่ายผลิต (PD)")
    with st.form("pd_form", clear_on_submit=True):
        pd_name = st.text_input("ชื่อพนักงานฝ่ายผลิตที่ส่งงาน:")
        
        # 🔥 แก้ไขเป็นช่องให้พิมพ์รหัส/ยิงบาร์โค้ดเองตามต้องการแล้วครับ ไม่ต้องกดเลือกแล้ว!
        sku = st.text_input("พิมพ์รหัสสินค้า หรือใช้ปืนสแกนบาร์โค้ดยิง (SKU):")
        
        pd_qty = st.number_input("จำนวนที่ผลิตและต้องการส่งมอบจริง (ชิ้น/พาเลท):", min_value=1, step=1)
        submit_pd = st.form_submit_button("🚀 ส่งงานให้ QC ตรวจสอบ")
        
        if submit_pd and pd_name and sku:
            df = st.session_state.current_db
            new_id = len(df) + 1
            job_id = f"JOB-{new_id:04d}"
            new_data = {
                'JobID': job_id, 'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'PD_Name': pd_name, 'SKU': sku, 'PD_Qty': pd_qty,
                'QC_Status': 'รอ QC ตรวจสอบ (Pending QC)', 'QC_Name': '-',
                'FG_Qty': 0, 'FG_Status': 'รอผ่าน QC', 'FG_Name': '-'
            }
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            save_data(df)
            st.success(f"บันทึกข้อมูลสำเร็จ! คิวงาน {job_id} ส่งต่อไปหน้าจอทีม QC เรียบร้อยแล้ว")
        elif submit_pd:
            st.error("กรุณากรอกข้อมูลชื่อผู้ส่งและรหัสสินค้าให้ครบถ้วน")

# ----------------------------------------------------
# 2. ควบคุมคุณภาพ (QC) - ตรวจสอบสเปกสินค้า
# ----------------------------------------------------
elif user_role == "2. ควบคุมคุณภาพ (QC)":
    st.header("🔍 หน้าจอสำหรับ ตรวจสอบคุณภาพ (QC)")
    df = st.session_state.current_db
    qc_pending = df[df['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)']
    
    if qc_pending.empty:
        st.info("🎉 ไม่มีงานค้างตรวจคุณภาพในขณะนี้")
    else:
        for idx, row in qc_pending.iterrows():
            with st.expander(f"📌 คิวงาน: {row['JobID']} | สินค้า: {row['SKU']} | จำนวน: {row['PD_Qty']} ชิ้น"):
                qc_name = st.text_input("ชื่อพนักงาน QC ผู้ตรวจ:", key=f"qc_name_{row['JobID']}")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ สเปกผ่าน (Approve)", key=f"qc_app_{row['JobID']}") and qc_name:
                        df.at[idx, 'QC_Status'] = 'สเปกผ่านแล้ว (Approved)'
                        df.at[idx, 'QC_Name'] = qc_name
                        df.at[idx, 'FG_Status'] = 'รอคลังรับเข้า (Pending FG)'
                        save_data(df)
                        st.success("อนุมัติสเปกผ่านสำเร็จ! ส่งงานต่อให้คลัง FG")
                        st.rerun()
                        
                with col2:
                    if st.button("❌ สเปกไม่ผ่าน (Reject/NG)", key=f"qc_rej_{row['JobID']}") and qc_name:
                        df.at[idx, 'QC_Status'] = '❌ ตีกลับ/สเปกไม่ผ่าน (NG)'
                        df.at[idx, 'QC_Name'] = qc_name
                        df.at[idx, 'FG_Status'] = '❌ ยกเลิก (QC ไม่ผ่าน)'
                        save_data(df)
                        st.error("ปฏิเสธงานเสียสำเร็จ ยอดจะถูกตีกลับทันที")
                        st.rerun()

# ----------------------------------------------------
# 3. คลังสินค้า (FG Receiver) - ตรวจนับของจริง
# ----------------------------------------------------
elif user_role == "3. คลังสินค้า (FG Receiver)":
    st.header("📥 หน้าจอสำหรับ คนรับงานคลังสินค้า (FG Receiver)")
    df = st.session_state.current_db
    fg_pending = df[df['FG_Status'] == 'รอคลังรับเข้า (Pending FG)']
    
    if fg_pending.empty:
        st.info("👍 ไม่มีสินค้าค้างรับเข้าคลังในขณะนี้")
    else:
        for idx, row in fg_pending.iterrows():
            with st.expander(f"📦 คิวงาน: {row['JobID']} | สินค้า: {row['SKU']} | ยอดในใบส่ง: {row['PD_Qty']} ชิ้น"):
                fg_name = st.text_input("ชื่อพนักงานคลังผู้นับของจริง:", key=f"fg_name_{row['JobID']}")
                actual_qty = st.number_input("ป้อนจำนวนที่นับได้จริงหน้างาน:", min_value=0, step=1, value=int(row['PD_Qty']), key=f"fg_qty_{row['JobID']}")
                
                diff = actual_qty - row['PD_Qty']
                if diff == 0:
                    st.success("🟢 ยอดนับจริง ตรงกับยอดในระบบ")
                elif diff > 0:
                    st.warning(f"⚠️ งานเกินมา +{diff} ชิ้น (กรุณาแยกของเกินไว้ที่ Holding Area)")
                else:
                    st.error(f"🚨 งานขาดไป {diff} ชิ้น")
                
                if st.button("💾 บันทึกการรับเข้าสต็อก FG", key=f"fg_save_{row['JobID']}") and fg_name:
                    df.at[idx, 'FG_Qty'] = actual_qty
                    df.at[idx, 'FG_Name'] = fg_name
                    df.at[idx, 'FG_Status'] = 'รับเข้าคลังสำเร็จ (Completed)'
                    save_data(df)
                    st.success("บันทึกการรับของเข้าคลังเสร็จสิ้น ยอดพร้อมส่งเข้า ERP")
                    st.rerun()

# ----------------------------------------------------
# 4. แอดมินสรุปยอด (ERP Admin) - ดึงยอดชัวร์ไปลง ERP
# ----------------------------------------------------
elif user_role == "4. แอดมินสรุปยอด (ERP Admin)":
    st.header("📊 หน้าจอสำหรับตัวคุณ (Stock FG / ERP Admin)")
    df = st.session_state.current_db
    st.dataframe(df, use_container_width=True)
    
    completed_jobs = df[df['FG_Status'] == 'รับเข้าคลังสำเร็จ (Completed)']
    if not completed_jobs.empty:
        csv = completed_jobs.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์สำหรับคีย์เข้า ERP (ยอดชัวร์ 100%)",
            data=csv,
            file_name="Ready_to_ERP.csv",
            mime='text/csv',
        )
