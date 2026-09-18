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

# คำนวณจำนวนงานค้างเพื่ออัปเดตสถานะป้ายไฟแจ้งเตือนสีเขียว/สีแดง
count_qc = len(df_current[df_current['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)'])
count_fg = len(df_current[df_current['FG_Status'] == 'รอคลังรับเข้า (Pending FG)'])

# ====================================================
# SIDEBAR PORTAL: คืนสิทธิ์ระบบ 4 แถบกล่องไฟสี เขียว-แดง แจ้งเตือนเสถียร 100%
# ====================================================
st.sidebar.markdown("## เมนูระบบงานหลัก")

# กำหนดตรรกะสีและข้อความฟ้องสถานะ (มีงาน = แดงอ่อน #FFEBEE / ไม่มีงาน = เขียวอ่อน #E8F5E9)
txt_pd_status = f"🚨 มีงานค้าง {count_qc} รายการ" if count_pd > 0 else "🟢 เคลียร์หมด ไม่มีงานค้าง"
color_pd_bg = "#FFEBEE" if count_qc > 0 else "#E8F5E9"
color_pd_txt = "#B71C1C" if count_qc > 0 else "#1B5E20"
color_pd_border = "#EF9A9A" if count_qc > 0 else "#A5D6A7"

# กำหนดตรรกะสีและข้อความฟ้องสถานะ (มีงาน = แดงอ่อน #FFEBEE / ไม่มีงาน = เขียวอ่อน #E8F5E9)
txt_qc_status = f"🚨 มีงานค้าง {count_qc} รายการ" if count_qc > 0 else "🟢 เคลียร์หมด ไม่มีงานค้าง"
color_qc_bg = "#FFEBEE" if count_qc > 0 else "#E8F5E9"
color_qc_txt = "#B71C1C" if count_qc > 0 else "#1B5E20"
color_qc_border = "#EF9A9A" if count_qc > 0 else "#A5D6A7"

txt_fg_status = f"🚨 มีงานค้าง {count_fg} รายการ" if count_fg > 0 else "🟢 เคลียร์หมด ไม่มีงานค้าง"
color_fg_bg = "#FFEBEE" if count_fg > 0 else "#E8F5E9"
color_fg_txt = "#B71C1C" if count_fg > 0 else "#1B5E20"
color_fg_border = "#EF9A9A" if count_fg > 0 else "#A5D6A7"

# แทรกคำสั่ง CSS เพื่อสร้างกล่องป้ายไฟสีอย่างเป็นทางการ มั่นคง ไม่รวนข้ามบราวเซอร์
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

# แถบที่ 1: ฝ่ายผลิต (PD)
st.sidebar.markdown('<div class="nav-badge c-green">1. แผนกฝ่ายผลิต (PD) <br><small>🟢 สถานะปกติ</small></div>', unsafe_allow_html=True)
nav_pd = st.sidebar.button("👉 เปิดหน้าจอ ฝ่ายผลิต", key="go_pd", use_container_width=True)

# แถบที่ 2: ควบคุมคุณภาพ (QC)
st.sidebar.markdown(f'<div class="nav-badge c-qc-dynamic">2. แผนกควบคุมคุณภาพ (QC) <br><small>{txt_qc_status}</small></div>', unsafe_allow_html=True)
nav_qc = st.sidebar.button("👉 เปิดหน้าจอ ตรวจสเปก QC", key="go_qc", use_container_width=True)

# แถบที่ 3: คลังสินค้าสำเร็จรูป (FG)
st.sidebar.markdown(f'<div class="nav-badge c-fg_dynamic">3. แผนกคลังสินค้า (FG) <br><small>{txt_fg_status}</small></div>', unsafe_allow_html=True)
nav_fg = st.sidebar.button("👉 เปิดหน้าจอ ตรวจนับของ FG", key="go_fg", use_container_width=True)

# แถบที่ 4: แอดมินสรุปยอด ERP
st.sidebar.markdown('<div class="nav-badge c-blue">4. ฝ่ายบริหารข้อมูลคลัง (ERP) <br><small>📊 สรุปยอดข้อมูลรวม</small></div>', unsafe_allow_html=True)
nav_erp = st.sidebar.button("👉 เปิดรายงานสรุปยอดลง ERP", key="go_erp", use_container_width=True)

# ระบบสลับเปลี่ยนหน้าจอ
if 'current_page' not in st.session_state:
    st.session_state.current_page = "PD"

if nav_pd: st.session_state.current_page = "PD"; st.rerun()
if nav_qc: st.session_state.current_page = "QC"; st.rerun()
if nav_fg: st.session_state.current_page = "FG"; st.rerun()
if nav_erp: st.session_state.current_page = "ERP"; st.rerun()

# ====================================================
# WORKFLOW PAGES INTERFACE (เนื้อหาฝั่งขวา)
# ====================================================

# ##############################################################################
# # 1. แผนกฝ่ายผลิต (PD) - ฟอร์มคีย์งานปกติ + กล่องแจ้งเตือนแก้ไขงาน Reject
# ##############################################################################
if st.session_state.current_page == "PD":
    df = st.session_state.current_db.copy()
    
    # ดึงรายการเฉพาะงานที่โดน QC ตีกลับมา
    rejected_jobs = df[df['QC_Status'] == 'ถูกตีกลับจาก QC (Rejected)']
    
    # ระบบแจ้งเตือนงานโดนตีกลับ (จะแสดงผลด้านบนสุดเฉพาะตอนที่มีงานพัง)
    if not rejected_jobs.empty:
        st.error(f"🔴 แจ้งเตือนจาก QC: มีใบงานถูกตีกลับมาแก้ไขจำนวน {len(rejected_jobs)} รายการ!")
        
        job_to_fix = st.selectbox("เลือกรหัสใบงานที่โดนตีกลับเพื่อแก้ไข:", ["-- เลือกใบงาน --"] + list(rejected_jobs['JobID'].unique()))
        if job_to_fix != "-- เลือกใบงาน --":
            # 🛠️ แก้ไขบั๊กจุดที่ 118: เพิ่ม .iloc[0] เพื่อให้เจาะจงดึงเฉพาะข้อมูลแถวแรกสุดออกมาใช้งานได้ถูกต้อง
            row_data = df[df['JobID'] == job_to_fix].iloc[0]
            st.warning(f"📋 รายละเอียดเดิม -> SKU: {row_data['SKU']} | จำนวนเดิม: {row_data['PD_Qty']}")
            
            fix_sku = st.text_input("แก้ไขรหัสสินค้า (SKU):", value=row_data['SKU'], key="fix_sku_input")
            fix_qty = st.number_input("แก้ไขจำนวนผลิตจริง:", min_value=1, value=int(row_data['PD_Qty']), key="fix_qty_input")
            
            if st.button("💾 บันทึกและส่งกลับไปให้ QC ตรวจซ้ำ", type="primary", use_container_width=True):
                idx = df[df['JobID'] == job_to_fix].index
                df.loc[idx, 'SKU'] = fix_sku
                df.loc[idx, 'PD_Qty'] = fix_qty
                df.loc[idx, 'QC_Status'] = 'รอ QC ตรวจสอบ (Pending QC)'
                df.loc[idx, 'FG_Status'] = '-'
                
                save_data(df)
                st.success("แก้ไขงานสำเร็จ! ส่งกลับเข้าคิวตรวจของแผนก QC แล้ว")
                st.rerun()
        st.write("---")
        
    st.subheader("ส่วนงานฝั่งฝ่ายผลิต (Production - PD): บันทึกและแก้ไขยอดจัดส่ง")
    st.write("### 📝 บันทึกข้อมูลใบงานผลิตใหม่")
    
    col_head1, col_head2 = st.columns(2)
    with col_head1:
        pd_name = st.text_input("ชื่อพนักงานฝ่ายผลิตผู้บันทึก:", key="pd_operator_name")
    with col_head2:
        now_date = datetime.now().strftime("%Y-%m-%d")
        time_input = st.text_input("วันที่บันทึกข้อมูล:", value=now_date, key="pd_time_input")
        
    shift_input = st.text_input("ชั้น (ตอน) / กะการทำงาน:", value="08.00", key="pd_shift_input")

    st.write("---")
    st.write("#### 🛒 รายการสินค้าที่จะจัดส่ง (คีย์เพิ่มได้หลายโค้ดด้านล่างนี้)")

    if "pd_temp_items" not in st.session_state:
        st.session_state.pd_temp_items = pd.DataFrame(columns=['โค้ดสินค้า (SKU)', 'จำนวน'])

    col_add1, col_add2, col_add3 = st.columns(3)
    with col_add1:
        sku_add = st.text_input("กรอกรหัสสินค้า (SKU):", key="sku_add_input")
    with col_add2:
        qty_add = st.number_input("กรอกจำนวน:", min_value=1, value=1, key="qty_add_input")
    with col_add3:
        st.write("<div style='padding-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("➕ เพิ่มโค้ดสินค้า", use_container_width=True):
            if sku_add.strip() == "":
                st.error("กรุณากรอกรหัสโค้ดสินค้า")
            else:
                new_item = pd.DataFrame([{'โค้ดสินค้า (SKU)': sku_add, 'จำนวน': qty_add}])
                st.session_state.pd_temp_items = pd.concat([st.session_state.pd_temp_items, new_item], ignore_index=True)
                st.rerun()

    if not st.session_state.pd_temp_items.empty:
        st.write("📋 *รายการสะสมที่กำลังจะบันทึก (เลือกแถวแล้วกด Delete บนแป้นพิมพ์เพื่อลบทีละอัน หรือดับเบิ้ลคลิกแก้ไขตัวเลขได้)*")
        st.session_state.pd_temp_items = st.data_editor(
            st.session_state.pd_temp_items,
            num_rows="dynamic",
            use_container_width=True,
            key="pd_items_bucket_editor"
        )
        
        if st.button("💾 ยืนยันบันทึกข้อมูลและออกรหัส Job งานทั้งหมด", type="primary", use_container_width=True):
            if pd_name.strip() == "":
                st.error("กรุณากรอกชื่อพนักงานฝ่ายผลิตผู้บันทึกก่อนกดส่งข้อมูลครับ")
            else:
                for _, item in st.session_state.pd_temp_items.iterrows():
                    if not df.empty and 'JobID' in df.columns:
                        try:
                            last_job = df['JobID'].iloc[-1]
                            last_num = int(last_job.split('-'))
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
                
                st.session_state.pd_temp_items = pd.DataFrame(columns=['โค้ดสินค้า (SKU)', 'จำนวน'])
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
