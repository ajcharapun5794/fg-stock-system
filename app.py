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
 
# --- 1. คำนวณจำนวนรายการค้างของแต่ละแผนก รวมถึงงานที่โดน QC Reject ---
count_qc = len(df_current[df_current['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)'])
count_fg = len(df_current[df_current['FG_Status'] == 'รอคลังรับเข้า (Pending FG)'])
count_pd_reject = len(df_current[df_current['QC_Status'] == 'ถูกตีกลับจาก QC (Rejected)'])

st.sidebar.markdown("### เมนูระบบงานหลัก / แผนกจัดส่ง-เช็คสเปก")

# --- 2. กำหนดสีและข้อความของปุ่ม แผนกฝ่ายผลิต (PD) ---
if count_pd_reject > 0:
    txt_pd_status = f"🔴 1. แผนกฝ่ายผลิต (PD) - มีงานต้องแก้ไข ({count_pd_reject} รายการ)"
    color_pd_bg = "#FF4B4B"      
    color_pd_txt = "#FFFFFF"     
    color_pd_border = "#D32F2F"  
else:
    txt_pd_status = "🟢 1. แผนกฝ่ายผลิต (PD)"
    color_pd_bg = "#E8F5E9"
    color_pd_txt = "#2E7D32"
    color_pd_border = "#A5D6A7"

# --- 3. กำหนดสีและข้อความของปุ่ม แผนกควบคุมคุณภาพ (QC) ---
if count_qc > 0:
    txt_qc_status = f"🟠 2. แผนกควบคุมคุณภาพ (QC) - มีงานค้าง ({count_qc} รายการ)"
    color_qc_bg = "#FFF3E0"
    color_qc_txt = "#E65100"
    color_qc_border = "#FFB74D"
else:
    txt_qc_status = "🟢 2. แผนกควบคุมคุณภาพ (QC)"
    color_qc_bg = "#E8F5E9"
    color_qc_txt = "#2E7D32"
    color_qc_border = "#A5D6A7"

# --- 4. กำหนดสีและข้อความของปุ่ม แผนกคลังสินค้า (FG) ---
if count_fg > 0:
    txt_fg_status = f"💗 3. แผนกคลังสินค้า (FG) - มีงานค้าง ({count_fg} รายการ)"
    color_fg_bg = "#FCE4EC"
    color_fg_txt = "#C2185B"
    color_fg_border = "#F48FB1"
else:
    txt_fg_status = "🟢 3. แผนกคลังสินค้า (FG)"
    color_fg_bg = "#E8F5E9"
    color_fg_txt = "#2E7D32"
    color_fg_border = "#A5D6A7"

# --- 5. แทรก CSS สไตล์เพื่อควบคุมสีปุ่มแบบไดนามิกตามเงื่อนไข ---
st.sidebar.markdown(f"""
    <style>
    div[data-testid="stSidebarNav"] {{display: none;}}
    
    div.stButton > button[key="btn_pd"] {{
        background-color: {color_pd_bg} !important;
        color: {color_pd_txt} !important;
        border: 2px solid {color_pd_border} !important;
        font-weight: bold !important;
        border-radius: 8px;
        text-align: left;
        margin-bottom: 10px;
        width: 100%;
    }}
    
    div.stButton > button[key="btn_qc"] {{
        background-color: {color_qc_bg} !important;
        color: {color_qc_txt} !important;
        border: 2px solid {color_qc_border} !important;
        font-weight: bold !important;
        border-radius: 8px;
        text-align: left;
        margin-bottom: 10px;
        width: 100%;
    }}
    
    div.stButton > button[key="btn_fg"] {{
        background-color: {color_fg_bg} !important;
        color: {color_fg_txt} !important;
        border: 2px solid {color_fg_border} !important;
        font-weight: bold !important;
        border-radius: 8px;
        text-align: left;
        margin-bottom: 10px;
        width: 100%;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 6. แสดงผลปุ่มเมนูส่วนที่ 1 (PD) เข้าสู่ Sidebar จริง ---
if st.sidebar.button(txt_pd_status, key="btn_pd", use_container_width=True):
    st.session_state.current_page = "PD"
    st.rerun()
            background-color: {color_qc_bg} !important;
            color: {color_qc_txt} !important;
            border: 2px solid {color_qc_border} !important;
            font-weight: bold !important;
            border-radius: 8px;
            text-align: left;
            margin-bottom: 10px;
        }}
        
        /* สไตล์สำหรับปุ่ม FG */
        div.stButton > button[key="btn_fg"] {{
            background-color: {color_fg_bg} !important;
            color: {color_fg_txt} !important;
            border: 2px solid {color_fg_border} !important;
            font-weight: bold !important;
            border-radius: 8px;
            text-align: left;
            margin-bottom: 10px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # --- 6. แสดงผลปุ่มเมนูส่วนที่ 1 (PD) เข้าสู่ Sidebar จริง ---
    if st.sidebar.button(txt_pd_status, key="btn_pd", use_container_width=True):
        st.session_state.current_page = "PD"
        st.rerun()
            color: {color_qc_txt} !important;
            border: 2px solid {color_qc_border} !important;
            font-weight: bold !important;
            border-radius: 8px;
            text-align: left;
            margin-bottom: 10px;
        }}
        
        /* สไตล์สำหรับปุ่ม FG */
        div.stButton > button[key="btn_fg"] {{
            background-color: {color_fg_bg} !important;
            color: {color_fg_txt} !important;
            border: 2px solid {color_fg_border} !important;
            font-weight: bold !important;
            border-radius: 8px;
            text-align: left;
            margin-bottom: 10px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # --- 6. แสดงผลปุ่มเมนูส่วนที่ 1 (PD) เข้าสู่ Sidebar จริง ---
    if st.sidebar.button(txt_pd_status, key="btn_pd", use_container_width=True):
        st.session_state.current_page = "PD"
        st.rerun()
    df = st.session_state.current_db.copy()
    
    # เช็กว่ามีงานโดน QC ตีกลับมาหรือไม่
    rejected_list = df[df['QC_Status'] == 'ถูกตีกลับจาก QC (Rejected)']
    
    # ข้อกำหนด: เวลาที่แจ้งเตือนกลับไปที่ PD ให้ปรับหัวข้อหรือสไตล์แสดงผลเด่นชัดเป็นสีแดง
    if not rejected_list.empty:
        st.markdown("<h2 style='color: #FF4B4B;'>⚠️ [REJECTED] มีงานถูกตีกลับจาก QC กรุณาแก้ไขข้อมูล!</h2>", unsafe_allow_html=True)
    else:
        st.subheader("ส่วนงานฝั่งฝ่ายผลิต (Production - PD): บันทึกและแก้ไขยอดจัดส่ง")

    # ==========================================================================
    # ส่วนที่ 1.1: 🚨 ระบบจัดการและแก้ไขงานที่โดน QC ตีกลับมา (แก้ไขทั้งรหัสสินค้า และ จำนวน)
    # ==========================================================================
    if not rejected_list.empty:
        st.error(f"ตรวจพบใบงานไม่ผ่านการตรวจสอบจำนวน {len(rejected_list)} รายการ สามารถแก้ไขรหัสและจำนวนที่โดนตีกลับด้านล่างนี้:")
        
        # ใช้ st.data_editor เพื่อให้คนใช้งานสามารถกดแก้รหัส SKU และ จำนวนได้พร้อมกันในตารางเดียว
        editable_rejects = rejected_list[['JobID', 'SKU', 'PD_Qty', 'PD_Shift', 'QC_Name']].copy()
        
        st.write("💡 *ดับเบิ้ลคลิกที่ช่อง SKU หรือ PD_Qty เพื่อพิมพ์แก้ไขข้อมูลรายใบงานได้ทันที*")
        edited_reject_df = st.data_editor(
            editable_rejects,
            column_config={
                "JobID": st.column_config.TextColumn("รหัสใบงาน", disabled=True),
                "SKU": st.column_config.TextColumn("รหัสสินค้า (SKU)"),
                "PD_Qty": st.column_config.NumberColumn("จำนวนผลิตสำเร็จ", min_value=1),
                "PD_Shift": st.column_config.TextColumn("ชั้น(ตอน)", disabled=True),
                "QC_Name": st.column_config.TextColumn("QC ผู้ตีกลับ", disabled=True),
            },
            hide_index=True,
            key="pd_reject_editor"
        )
        
        if st.button("💾 บันทึกการแก้ไขงาน Reject ทั้งหมดและส่งให้ QC ตรวจใหม่", type="primary", use_container_width=True):
            for _, row in edited_reject_df.iterrows():
                idx = df[df['JobID'] == row['JobID']].index
                if not idx.empty:
                    # อัปเดตทั้ง รหัสสินค้า (โค้ด) และ จำนวนใหม่
                    df.loc[idx, 'SKU'] = row['SKU']
                    df.loc[idx, 'PD_Qty'] = row['PD_Qty']
                    # ดีดสเตตัสกลับไปให้ QC ตรวจสอบใหม่อีกครั้ง
                    df.loc[idx, 'QC_Status'] = 'รอ QC ตรวจสอบ (Pending QC)'
                    df.loc[idx, 'QC_Name'] = '-'
                    df.loc[idx, 'FG_Status'] = '-'
            
            st.session_state.current_db = df
            save_data(df)
            st.success("อัปเดตข้อมูลงานที่โดนตีกลับเข้าสู่ระบบ และส่งต่อให้ฝั่ง QC เรียบร้อยแล้ว!")
            st.rerun()
            
        st.write("---")

    # ==========================================================================
    # ส่วนที่ 1.2: 📝 ฟอร์มบันทึกงานผลิตใหม่ (คีย์พร้อมกันได้หลายโค้ด + เลือกจัดการลบทีละอันได้)
    # ==========================================================================
    st.write("### 📝 บันทึกข้อมูลใบงานผลิตใหม่")
    
    # 1. ฟิลด์ข้อมูลหลักบนหัวใบงาน (กรอกครั้งเดียว)
    col_head1, col_head2 = st.columns(2)
    with col_head1:
        pd_name = st.text_input("ชื่อพนักงานฝ่ายผลิตผู้บันทึก:", key="pd_operator_name")
    with col_head2:
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_input = st.text_input("เวลาที่บันทึกข้อมูล:", value=current_time, key="pd_time_input")
        
    shift_input = st.selectbox("ชั้น (ตอน) / กะการทำงาน:", ["08.00", "20.00", "กะเช้า", "กะดึก"], key="pd_shift_input")

    st.write("---")
    st.write("#### 🛒 รายการสินค้าที่จะจัดส่ง (คีย์เพิ่มได้หลายโค้ดด้านล่างนี้)")

    # สร้างคลังข้อมูลชั่วคราวใน Session เพื่อเก็บรายการย่อยที่คีย์รอกดบันทึกใหญ่
    if "pd_temp_items" not in st.session_state:
        st.session_state.pd_temp_items = pd.DataFrame(columns=['โค้ดสินค้า (SKU)', 'จำนวน'])

    # ช่องกรอกสำหรับแอดไอเทมทีละรายการเข้าสู่ตารางชั่วคราวก่อนบันทึก
    col_add1, col_add2, col_add3 = st.columns([5, 3, 2])
    with col_add1:
        sku_add = st.text_input("กรอกรหัสสินค้า (SKU):", key="sku_add_input")
    with col_add2:
        qty_add = st.number_input("กรอกจำนวน:", min_value=1, value=1, key="qty_add_input")
    with col_add3:
        st.write("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("➕ เพิ่มโค้ดนี้", use_container_width=True):
            if sku_add.strip() == "":
                st.error("กรุณากรอกรหัสโค้ดสินค้า")
            else:
                new_item = pd.DataFrame([{'โค้ดสินค้า (SKU)': sku_add, 'จำนวน': qty_add}])
                st.session_state.pd_temp_items = pd.concat([st.session_state.pd_temp_items, new_item], ignore_index=True)
                st.rerun()

    # แสดงตารางรายการสินค้าที่กำลังคีย์สะสมไว้ (เปิดฟังก์ชันให้แก้ไขตัวเลข และเลือกคลิกแถวแล้วกดปุ่ม Delete บนคีย์บอร์ดเพื่อลบทีละอันได้เลย)
    if not st.session_state.pd_temp_items.empty:
        st.write("📋 *รายการสะสมที่กำลังจะบันทึก (เลือกแถวแล้วกด Delete หรือพิมพ์แก้จำนวนตรงนี้ได้เลย)*")
        st.session_state.pd_temp_items = st.data_editor(
            st.session_state.pd_temp_items,
            num_rows="dynamic", # ยอมให้ผู้ใช้งานกดเลือกแถวแล้วกดปุ่มลบทีละอันได้อิสระ
            use_container_width=True,
            key="pd_items_bucket_editor"
        )
        
        # ปุ่มกดเซฟใหญ่นำทุกโค้ดในตารางเข้าฐานข้อมูลหลัก
        if st.button("💾 ยืนยันบันทึกข้อมูลและออกรหัส Job งานทั้งหมดลงตารางหลัก", type="primary", use_container_width=True):
            if pd_name.strip() == "":
                st.error("กรุณากรอกชื่อพนักงานฝ่ายผลิตผู้บันทึกก่อนกดส่งข้อมูลใหญ่ครับ")
            else:
                for _, item in st.session_state.pd_temp_items.iterrows():
                    # คำนวณรันเลข JobID ใหม่รายตัว
                    if not df.empty and 'JobID' in df.columns:
                        try:
                            last_job = df['JobID'].iloc[-1]
                            last_num = int(last_job.split('-')[1])
                            new_job_id = f"JOB-{last_num + 1:04d}"
                        except:
                            new_job_id = f"JOB-{len(df) + 1:04d}"
                    else:
                        new_job_id = "JOB-0001"
                        
                    new_row = pd.DataFrame([{
                        'JobID': new_job_id,
                        'Timestamp': time_input,
                        'PD_Shift': shift_input,
                        'PD_Name': pd_name,
                        'SKU': item['โค้ดสินค้า (SKU)'],
                        'PD_Qty': item['จำนวน'],
                        'QC_Status': 'รอ QC ตรวจสอบ (Pending QC)',
                        'QC_Name': '-',
                        'FG_Qty': 0,
                        'FG_Status': '-',
                        'FG_Name': '-'
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                
                # ล้างค่าในตะกร้าคีย์ชั่วคราวหลังเซฟใหญ่สำเร็จ
                st.session_state.pd_temp_items = pd.DataFrame(columns=['โค้ดสินค้า (SKU)', 'จำนวน'])
                st.session_state.current_db = df
                save_data(df)
                st.success("บันทึกข้อมูลสินค้าทุกรหัสเข้าสู่ระบบใหญ่สำเร็จเรียบร้อยแล้ว!")
                st.rerun()

# ##############################################################################
# # 2. แผนกควบคุมคุณภาพ (QC) - ตรวจสอบคุณภาพสินค้า (มีระบบบันทึกผ่านและตีกลับ)
# ##############################################################################
elif st.session_state.current_page == "QC":
    st.subheader("ส่วนงานฝั่งตรวจสอบคุณภาพ (Quality Control - QC): ตรวจสอบและอัปเดตสเปกสินค้า")
    df = st.session_state.current_db.copy()
    
    # ดึงรายการงานที่รอ QC ตรวจสอบ รวมถึงงานที่เคยโดน Reject (ถ้าต้องการแก้ไขสเตตัสซ้ำ)
    qc_pending_list = df[df['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)']

    if qc_pending_list.empty:
        st.info("ไม่มีรายการสินค้าค้างตรวจสอบในระบบขณะนี้")
    else:
        st.write("### รายการสินค้าค้างตรวจสเปก")
        qc_name = st.text_input("ชื่อเจ้าหน้าที่/พนักงานตรวจสอบคุณภาพ (QC):", key="qc_global_name")

        options_map_qc = {}
        for _, r in qc_pending_list.iterrows():
            display_text = f"📦 ตัวงาน: {r['JobID']} | รหัสสินค้า: {r['SKU']} | จำนวน: {r['PD_Qty']} | ชั้น (ตอน): {r['PD_Shift']}"
            options_map_qc[display_text] = r['JobID']

        selected_qc_jobs = st.multiselect("เลือกรายการรหัสสินค้าที่ต้องการจัดการระบบ:", list(options_map_qc.keys()))

        st.write("---")
        
        # จัดวางปุ่ม Approve และ ปุ่ม Reject ให้อยู่เคียงข้างกันในระนาบที่สวยงาม
        col_approve, col_reject = st.columns(2)
        
        # 🟢 ปุ่มที่ 1: อนุมัติผ่านตามปกติ (ส่งไป FG)
        with col_approve:
            if st.button("🟢 อนุมัติผ่านสเปก (ส่งให้คลัง FG)", type="primary", use_container_width=True):
                if qc_name.strip() == "":
                    st.error("กรุณาระบุชื่อพนักงาน QC ก่อนทำการกดยืนยันข้อมูล")
                elif not selected_qc_jobs:
                    st.error("กรุณาเลือกรายการสินค้าที่ต้องการอนุมัติอย่างน้อย 1 รายการ")
                else:
                    for option in selected_qc_jobs:
                        job_id_extracted = options_map_qc[option]
                        matching_rows = df[df['JobID'] == job_id_extracted].index
                        if not matching_rows.empty:
                            idx = matching_rows
                            df.loc[idx, 'QC_Status'] = 'สเปกผ่านแล้ว (Approved)'
                            df.loc[idx, 'QC_Name'] = qc_name
                            df.loc[idx, 'FG_Status'] = 'รอคลังรับเข้า (Pending FG)'
                    
                    st.session_state.current_db = df
                    save_data(df)
                    st.success("อนุมัติงาน QC สำเร็จ ข้อมูลถูกส่งต่อไปยังแผนกคลังสินค้า (FG) แล้ว!")
                    st.rerun()

        # 🔴 ปุ่มที่ 2: ปฏิเสธสเปกไม่ผ่าน (ตีกลับไปให้หน้างานผลิต PD)
        with col_reject:
            if st.button("🔴 ไม่ผ่านสเปก (Reject ตีกลับไปฝ่ายผลิต PD)", type="secondary", use_container_width=True):
                if qc_name.strip() == "":
                    st.error("กรุณาระบุชื่อพนักงาน QC ก่อนทำการสั่งปฏิเสธข้อมูล")
                elif not selected_qc_jobs:
                    st.error("กรุณาเลือกรายการสินค้าที่ต้องการตีกลับอย่างน้อย 1 รายการ")
                else:
                    for option in selected_qc_jobs:
                        job_id_extracted = options_map_qc[option]
                        matching_rows = df[df['JobID'] == job_id_extracted].index
                        if not matching_rows.empty:
                            idx = matching_rows
                            
                            # อัปเดตสถานะตีกลับ และล้างฟีลด์ฝั่งคลังออกไปเพื่อส่งกลับไปให้ต้นทาง
                            df.loc[idx, 'QC_Status'] = 'ถูกตีกลับจาก QC (Rejected)'
                            df.loc[idx, 'QC_Name'] = qc_name
                            df.loc[idx, 'FG_Status'] = 'งานถูกตีกลับไปแก้ไข'
                    
                    st.session_state.current_db = df
                    save_data(df)
                    st.warning("ทำการตีกลับรายการสินค้าที่ไม่ผ่านสเปก ส่งคืนให้ฝ่ายผลิต (PD) เรียบร้อย!")
                    st.rerun()
# ##############################################################################
# # 3. แผนกคลังสินค้าสำเร็จรูป (FG) - ตรวจนับและรับเข้าคลัง 100%
# ##############################################################################
elif st.session_state.current_page == "FG":
    st.subheader("ส่วนงานฝ่ายคลังสินค้าสำเร็จรูป (Finished Goods - FG): ตรวจนับสต็อกรับจริง")
    df = st.session_state.current_db.copy()
    fg_pending_list = df[df['FG_Status'] == 'รอคลังรับเข้า (Pending FG)']

    if fg_pending_list.empty:
        st.info("ไม่มีรายการสินค้าค้างรับเข้าคลังในระบบขณะนี้")
    else:
        st.write("### รายการสินค้าค้างรับเข้าเลือก")
        fg_name = st.text_input("ชื่อพนักงานคลังสินค้าผู้ตรวจรับ:", key="fg_global_name")

        options_map_fg = {}
        for _, r in fg_pending_list.iterrows():
            display_text = f"📦 ตัวงาน: {r['JobID']} | รหัสสินค้า: {r['SKU']} | ยอดจัดส่ง: {r['PD_Qty']} | ชั้น (ตอน): {r['PD_Shift']} | QC ผู้ตรวจ: {r['QC_Name']}"
            options_map_fg[display_text] = r['JobID']

        selected_fg_jobs = st.multiselect("เลือกงานจากรหัสสินค้าเพื่อตรวจสอบและรับเข้าพร้อมกัน:", list(options_map_fg.keys()))

        st.write("---")
        if st.button("อนุมัติรับสินค้าเข้าคลัง (Approve พร้อมกัน)", type="primary", use_container_width=True):
            if fg_name.strip() == "":
                st.error("กรุณาระบุชื่อพนักงาน FG ก่อนทำการกดยืนยันข้อมูล")
            elif not selected_fg_jobs:
                st.error("กรุณาเลือกรายการสินค้าที่ต้องการอนุมัติอย่างน้อย 1 รายการ")
            else:
                for option in selected_fg_jobs:
                    job_id_extracted = options_map_fg[option]
                    matching_rows = df[df['JobID'] == job_id_extracted].index
                    
                    if not matching_rows.empty:
                        idx = matching_rows
                        
                        # เปลี่ยนมาใช้ .loc แทน .at เพื่อรองรับ index แบบกลุ่มและป้องกัน InvalidIndexError
                        df.loc[idx, 'FG_Status'] = 'รับสินค้าเข้าคลังแล้ว (Approved)'
                        df.loc[idx, 'FG_Name'] = fg_name
                        
                        # ดึงค่าจำนวนการผลิตของงานตัวนั้นมาหยอดใส่สต็อก FG ให้เท่ากันอย่างปลอดภัย
                        df.loc[idx, 'FG_Qty'] = df.loc[idx, 'PD_Qty']
                
                st.session_state.current_db = df
                save_data(df)
                st.success("บันทึกข้อมูลและรับสินค้าเข้าคลังสำเร็จเรียบร้อยแล้ว!")
                st.rerun()

# ##############################################################################
# # 4. ฝ่ายบริหารข้อมูลคลัง (ERP) - แสดงตารางสรุป, ลบแถวข้อมูล และ Export
# # ############################################################################
elif st.session_state.current_page == "ERP":
    st.subheader("หน้าจอส่วนงาน: ฝ่ายบริหารข้อมูลคลังสินค้า (ERP Administrator)")
    st.write("### รายงานสรุปตรวจสอบยอดรับจริงหน้างาน 100% เพื่อนำข้อมูลคีย์ลงระบบ ERP")
    
    df_latest = st.session_state.current_db.copy()
    
    # แสดงตารางหลักให้ตรวจสอบบนหน้าจอ
    st.dataframe(df_latest, use_container_width=True)
    
    st.write("---")
    st.write("### 🛠️ เครื่องมือสำหรับผู้จัดการระบบ: ลบข้อมูลออกจากตาราง")
    
    if not df_latest.empty:
        # ดึงรายการ JobID ทั้งหมดมาให้เลือกลบ
        job_to_delete = st.selectbox("เลือกรหัสใบงาน (JobID) ที่ต้องการลบทิ้งถาวร:", ["-- เลือกใบงาน --"] + list(df_latest['JobID'].unique()))
        
        if st.button("❌ ยืนยันการลบใบงานนี้ออกจากระบบ", type="primary", use_container_width=True):
            if job_to_delete == "-- เลือกใบงาน --":
                st.error("กรุณาเลือกรหัสใบงาน (JobID) ที่ต้องการลบก่อนครับ")
            else:
                # ค้นหาตำแหน่งแถวของ JobID ที่เลือก
                matching_rows = df_latest[df_latest['JobID'] == job_to_delete].index
                
                if not matching_rows.empty:
                    # สั่งลบแถวข้อมูลนั้นออกจาก DataFrame ทันที (ตารางจะหายไปด้วย)
                    df_latest = df_latest.drop(matching_rows)
                    
                    # บันทึกข้อมูลที่ลบแล้วกลับเข้าระบบหลัก
                    st.session_state.current_db = df_latest
                    save_data(df_latest)
                    
                    st.success(f"ลบข้อมูลใบงาน {job_to_delete} ออกจากตารางระบบเรียบร้อยแล้ว!")
                    st.rerun()
    else:
        st.info("ไม่มีข้อมูลใบงานในระบบขณะนี้")

    st.write("---")
    
    # ส่วนดาวน์โหลดรายงานตัวล่าสุด
    save_data(df_latest)
    csv_data = df_latest.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 ดาวน์โหลดรายงานสรุปข้อมูลล่าสุด (Excel/CSV)",
        data=csv_data,
        file_name="ERP_Inventory_Report_Latest.csv",
        mime="text/csv",
        use_container_width=True,
        key="download_latest_report"
    )
