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

# ==============================================================================
# เมนูระบบงานหลัก (ส่วนที่ 1 ถึง 4)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. แผนกฝ่ายผลิต (PD)
# ------------------------------------------------------------------------------
if st.session_state.current_page == "pd":
    st.subheader("ส่วนงานแผนกฝ่ายผลิต (Production Department - PD)")
    # ... (ใส่โค้ดแสดงผลหรือฟอร์มของฝั่ง PD เดิมของคุณตรงนี้ได้เลยครับ) ...


# ------------------------------------------------------------------------------
# 2. แผนกควบคุมคุณภาพ (QC)
# ------------------------------------------------------------------------------
elif st.session_state.current_page == "qc":
    st.subheader("ส่วนงานฝ่ายควบคุมคุณภาพ (Quality Control - QC): ตรวจสอบเกณฑ์เกรดสเปกสินค้า")
    qc_pending_list = df[df['QC_Status'] == 'Pending QC']

    if qc_pending_list.empty:
        st.info("ไม่มีรายการสินค้าค้างตรวจสเปก")
    else:
        st.write("### รายการสินค้าค้างตรวจสเปก")
        qc_name = st.text_input("ชื่อเจ้าหน้าที่พนักงานตรวจสอบคุณภาพ (QC):", key="fg_global_name")

        options_map_qc = {}
        for r in qc_pending_list.to_dict('records'):
            display_text = f"ใบงาน: {r['job_id']} | รหัสสินค้า: {r['product_id']} | จำนวน: {r['qty']} ชิ้น (รอบ: {r['round_time']})"
            options_map_qc[display_text] = (r['job_id'], r['refrun_id'])

        selected_qc_jobs = st.multiselect(
            "คลิกเลือกตัวงานสินค้าที่ตรวจสอบผ่านเกณฑ์พร้อมกันหลายรายการ:", 
            list(options_map_qc.keys())
        )

        st.write("---")
        
        # เช็คเงื่อนไขล่วงหน้าก่อนเปิดให้กดปุ่ม (ต้องพิมพ์ชื่อ และ เลือกรายการ)
        is_button_disabled = not (qc_name.strip() and selected_qc_jobs)

        if st.button(
            "อนุมัติมาตรฐานผ่านเกณฑ์ตามรายการที่เลือก (Approve ยกแผง)", 
            type="primary", 
            use_container_width=True,
            disabled=is_button_disabled
        ):
            # ดึงคำสั่งอัปเดตข้อมูลขึ้นมาทำงานหลังจากผ่านเงื่อนไขแล้ว
            for option in selected_qc_jobs:
                job_id, refrun_id = options_map_qc[option]
                
                # ทำการอัปเดตสถานะใน DataFrame จาก 'Pending QC' เป็น 'Pending FG'
                df.loc[(df['job_id'] == job_id) & (df['refrun_id'] == refrun_id), 'QC_Status'] = 'Approved'
                df.loc[(df['job_id'] == job_id) & (df['refrun_id'] == refrun_id), 'FG_Status'] = 'Pending FG'
                df.loc[(df['job_id'] == job_id) & (df['refrun_id'] == refrun_id), 'QC_Inspector'] = qc_name.strip()
            
            save_data(df)  # บันทึกข้อมูลลงฐานข้อมูล/ไฟล์
            st.success("อนุมัติรายการสินค้าและส่งข้อมูลต่อไปยังแผนกคลังสินค้า (FG) เรียบร้อยแล้ว!")
            st.rerun()


# ------------------------------------------------------------------------------
# 3. แผนกคลังสินค้า (FG)
# ------------------------------------------------------------------------------
elif st.session_state.current_page == "fg":
    st.subheader("ส่วนงานคลังสินค้าสำเร็จรูป (Finished Goods - FG): รับสินค้าเข้าคลัง")
    fg_pending_list = df[df['FG_Status'] == 'Pending FG']

    if fg_pending_list.empty:
        st.info("ไม่มีรายการสินค้าค้างรับเข้าคลัง")
    else:
        st.write("### รายการสินค้าค้างรับเข้าคลัง")
        fg_name = st.text_input("ชื่อเจ้าหน้าที่พนักงานคลังสินค้า (FG):", key="fg_user_name")

        options_map_fg = {}
        for r in fg_pending_list.to_dict('records'):
            display_text = f"ใบงาน: {r['job_id']} | รหัสสินค้า: {r['product_id']} | จำนวน: {r['qty']} ชิ้น (รอบ: {r['round_time']})"
            options_map_fg[display_text] = (r['job_id'], r['refrun_id'])

        selected_fg_jobs = st.multiselect(
            "คลิกเลือกตัวงานสินค้าที่ต้องการรับเข้าคลังพร้อมกันหลายรายการ:", 
            list(options_map_fg.keys())
        )

        st.write("---")
        
        # เช็คเงื่อนไขก่อนเปิดปุ่มรับเข้าคลัง (ต้องพิมพ์ชื่อ และ เลือกรายการ)
        is_fg_button_disabled = not (fg_name.strip() and selected_fg_jobs)

        if st.button(
            "ยืนยันการรับสินค้าเข้าคลังสำเร็จรูป", 
            type="primary", 
            use_container_width=True,
            disabled=is_fg_button_disabled
        ):
            for option in selected_fg_jobs:
                job_id, refrun_id = options_map_fg[option]
                
                # ทำการอัปเดตสถานะจาก 'Pending FG' เป็น 'In Stock' เพื่อเตรียมส่งต่อให้ ERP
                df.loc[(df['job_id'] == job_id) & (df['refrun_id'] == refrun_id), 'FG_Status'] = 'In Stock'
                df.loc[(df['job_id'] == job_id) & (df['refrun_id'] == refrun_id), 'ERP_Status'] = 'Pending ERP'
                df.loc[(df['job_id'] == job_id) & (df['refrun_id'] == refrun_id), 'FG_Receiver'] = fg_name.strip()
            
            save_data(df)
            st.success("รับสินค้าเข้าคลังสำเร็จรูป และเตรียมส่งข้อมูลเข้าระบบ ERP เรียบร้อยแล้ว!")
            st.rerun()


# ------------------------------------------------------------------------------
# 4. ฝ่ายบริการข้อมูลคลัง (ERP)
# ------------------------------------------------------------------------------
elif st.session_state.current_page == "erp":
    st.subheader("ส่วนงานบริการข้อมูลคลังสินค้า (ERP Integration)")
