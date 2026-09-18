import streamlit as st
import pandas as pd
import datetime
import os

# ตั้งค่าหน้าจอแอปพลิเคชัน
st.set_page_config(page_title="Finished Goods Management Portal", layout="wide")

# ชื่อไฟล์ฐานข้อมูล CSV
DB_FILE = "inventory_db.csv"

# ฟังก์ชันดึงข้อมูลจากฐานข้อมูล
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=[
            'JobID', 'Timestamp', 'PD_Shift', 'PD_Name', 'SKU', 'PD_Qty',
            'QC_Status', 'QC_Name', 'FG_Qty', 'FG_Status', 'FG_Name'
        ])

# ฟังก์ชันบันทึกข้อมูลลงฐานข้อมูล
def save_data(df):
    df.to_csv(DB_FILE, index=False)
    st.session_state.current_db = df

# โหลดข้อมูลเข้าสู่ตัวแปรระบบ (Session State)
if 'current_db' not in st.session_state:
    st.session_state.current_db = load_data()

if 'current_page' not in st.session_state:
    st.session_state.current_page = "PD"

df_current = st.session_state.current_db

# --- 1. คำนวณจำนวนรายการค้างและงานที่โดน QC Reject สำหรับแจ้งเตือน ---
count_qc = len(df_current[df_current['QC_Status'] == 'รอ QC ตรวจสอบ (Pending QC)'])
count_fg = len(df_current[df_current['FG_Status'] == 'รอคลังรับเข้า (Pending FG)'])
count_pd_reject = len(df_current[df_current['QC_Status'] == 'ถูกตีกลับจาก QC (Rejected)'])

st.sidebar.markdown("### เมนูระบบงานหลัก")

# --- 2. เปลี่ยนชื่อปุ่มเพื่อแจ้งเตือนเมื่อมีงานโดน Reject ---
if count_pd_reject > 0:
    txt_pd_status = f"🚨 1. แผนกฝ่ายผลิต (PD) - มีงานต้องแก้ไข ({count_pd_reject})"
else:
    txt_pd_status = "🟢 1. แผนกฝ่ายผลิต (PD)"

# --- 3. ปุ่มเมนู Sidebar แบบมาตรฐาน ปลอดภัย 100% ---
if st.sidebar.button(txt_pd_status, use_container_width=True):
    st.session_state.current_page = "PD"
    st.rerun()

if st.sidebar.button(f"🟢 2. แผนกควบคุมคุณภาพ (QC) ({count_qc})", use_container_width=True):
    st.session_state.current_page = "QC"
    st.rerun()

if st.sidebar.button(f"🟢 3. แผนกคลังสินค้า (FG) ({count_fg})", use_container_width=True):
    st.session_state.current_page = "FG"
    st.rerun()

if st.sidebar.button("📊 4. ฝ่ายบริหารข้อมูลคลัง (ERP)", use_container_width=True):
    st.session_state.current_page = "ERP"
    st.rerun()


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
        
    st.subheader("ส่วนงานฝั่งฝ่ายผลิต (Production - PD): บันทึกยอดจัดส่งสินค้า")
    
    # ฟอร์มคีย์งานใหม่ปกติ แสดงผลค้างไว้ตลอดเวลา ไม่หายไปไหน
    pd_name = st.text_input("ชื่อพนักงานฝ่ายผลิตผู้บันทึก:", key="pd_operator_name")
    sku_input = st.text_input("รหัสสินค้า (SKU):", key="pd_sku_input")
    qty_input = st.number_input("จำนวนผลิตสำเร็จ/ยอดจัดส่ง:", min_value=1, value=1, key="pd_qty_input")
    shift_input = st.selectbox("ชั้น (ตอน) / กะการทำงาน:", ["08.00", "20.00", "กะเช้า", "กะดึก"], key="pd_shift_input")
    
    if st.button("➕ บันทึกข้อมูลและออกรหัสใบงานใหม่", use_container_width=True):
        if pd_name.strip() == "" or sku_input.strip() == "":
            st.error("กรุณากรอกชื่อพนักงานและรหัสสินค้า (SKU) ให้ครบถ้วนก่อนกดบันทึก")
        else:
            timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
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
                'Timestamp': timestamp_str,
                'PD_Shift': shift_input,
                'PD_Name': pd_name,
                'SKU': sku_input,
                'PD_Qty': qty_input,
                'QC_Status': 'รอ QC ตรวจสอบ (Pending QC)',
                'QC_Name': '-',
                'FG_Qty': 0,
                'FG_Status': '-',
                'FG_Name': '-'
            }])
            
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success(f"บันทึกข้อมูลเรียบร้อย! ออกรหัสใบงานใหม่สำเร็จ: {new_job_id}")
            st.rerun()


# ##############################################################################
# # 2. แผนกควบคุมคุณภาพ (QC) - ตรวจสอบคุณภาพสินค้า (มีระบบอนุมัติและตีกลับ)
# ##############################################################################
elif st.session_state.current_page == "QC":
    st.subheader("ส่วนงานฝั่งตรวจสอบคุณภาพ (Quality Control - QC): ตรวจสอบและอัปเดตสเปกสินค้า")
    df = st.session_state.current_db.copy()
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
        col_approve, col_reject = st.columns(2)
        
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
                            df.loc[matching_rows, 'QC_Status'] = 'สเปกผ่านแล้ว (Approved)'
                            df.loc[matching_rows, 'QC_Name'] = qc_name
                            df.loc[matching_rows, 'FG_Status'] = 'รอคลังรับเข้า (Pending FG)'
                    save_data(df)
                    st.success("อนุมัติงาน QC สำเร็จ ข้อมูลถูกส่งต่อไปยังแผนกคลังสินค้า (FG) แล้ว!")
                    st.rerun()

        with col_reject:
            if st.button("🔴 不ผ่านสเปก (Reject ตีกลับไปฝ่ายผลิต PD)", type="secondary", use_container_width=True):
                if qc_name.strip() == "":
                    st.error("กรุณาระบุชื่อพนักงาน QC ก่อนทำการสั่งปฏิเสธข้อมูล")
                elif not selected_qc_jobs:
                    st.error("กรุณาเลือกรายการสินค้าที่ต้องการตีกลับอย่างน้อย 1 รายการ")
                else:
                    for option in selected_qc_jobs:
                        job_id_extracted = options_map_qc[option]
                        matching_rows = df[df['JobID'] == job_id_extracted].index
                        if not matching_rows.empty:
                            df.loc[matching_rows, 'QC_Status'] = 'ถูกตีกลับจาก QC (Rejected)'
                            df.loc[matching_rows, 'QC_Name'] = qc_name
                            df.loc[matching_rows, 'FG_Status'] = 'งานถูกตีกลับไปแก้ไข'
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
