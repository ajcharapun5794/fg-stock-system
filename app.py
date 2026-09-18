import streamlit as pd_st # (หรือ import streamlit as st)
import pandas as pd
import os
from datetime import datetime

# ==============================================================================
# 0. ฟังก์ชันจัดการข้อมูล (LOAD & SAVE DATA)
# ==============================================================================
DB_FILE = "fg_stock_data.csv"

def load_data():
    """โหลดข้อมูลจากไฟล์ หากไม่มีจะสร้างข้อมูลเริ่มต้นให้"""
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # สร้างโครงสร้างข้อมูลตัวอย่างสำหรับการรันครั้งแรก
        data = {
            'job_id': ['JOB-0001', 'JOB-0002'],
            'refrun_id': ['REF-001', 'REF-002'],
            'product_id': ['1144144101', '2233445566'],
            'qty':,
            'round_time': ['08:00', '10:30'],
            'shift': ['A', 'B'],
            'PD_Status': ['Completed', 'Completed'],
            'QC_Status': ['Pending QC', 'Pending QC'],
            'FG_Status': ['None', 'None'],
            'ERP_Status': ['None', 'None'],
            'QC_Inspector': ['', ''],
            'FG_Receiver': ['', '']
        }
        df_init = pd.DataFrame(data)
        df_init.to_csv(DB_FILE, index=False)
        return df_init

def save_data(dataframe):
    """บันทึกข้อมูลลงไฟล์ล็อกปัจจุบัน"""
    dataframe.to_csv(DB_FILE, index=False)

# โหลดข้อมูลเข้ามาใช้งานในแอป
if 'df' not in pd_st.session_state:
    pd_st.session_state.df = load_data()

df = pd_st.session_state.df

# ==============================================================================
# เมนูระบบงานหลัก (ส่วนที่ 1 ถึง 4)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. แผนกฝ่ายผลิต (PD)
# ------------------------------------------------------------------------------
if pd_st.session_state.current_page == "pd":
    pd_st.subheader("ส่วนงานแผนกฝ่ายผลิต (Production Department - PD)")
    pd_st.write("### บันทึกยอดนำส่งจากฝ่ายผลิต")
    
    with pd_st.form("pd_form"):
        job_id = pd_st.text_input("เลขที่ใบงาน (Job ID):", placeholder="เช่น JOB-0003")
        product_id = pd_st.text_input("รหัสสินค้า (Product ID):")
        qty = pd_st.number_input("จำนวนผลิตได้ (ชิ้น):", min_value=1, step=1)
        round_time = pd_st.text_input("รอบเวลา (เช่น 08:00):")
        shift = pd_st.selectbox("กะการทำงาน:", ["A", "B", "C"])
        
        submit_pd = pd_st.form_submit_button("ส่งข้อมูลไปตรวจสเปก (QC)")
        
        if submit_pd:
            if job_id and product_id:
                refrun_id = f"REF-{int(datetime.now().timestamp())}"
                new_row = {
                    'job_id': job_id, 'refrun_id': refrun_id, 'product_id': product_id,
                    'qty': qty, 'round_time': round_time, 'shift': shift,
                    'PD_Status': 'Completed', 'QC_Status': 'Pending QC',
                    'FG_Status': 'None', 'ERP_Status': 'None',
                    'QC_Inspector': '', 'FG_Receiver': ''
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                pd_st.session_state.df = df
                pd_st.success(f"บันทึกข้อมูลใบงาน {job_id} และส่งต่อไป QC เรียบร้อย!")
                pd_st.rerun()
            else:
                pd_st.error("กรุณากรอกเลขที่ใบงานและรหัสสินค้าให้ครบถ้วน")


# ------------------------------------------------------------------------------
# 2. แผนกควบคุมคุณภาพ (QC)
# ------------------------------------------------------------------------------
elif pd_st.session_state.current_page == "qc":
    pd_st.subheader("ส่วนงานฝ่ายควบคุมคุณภาพ (Quality Control - QC): ตรวจสอบเกณฑ์เกรดสเปกสินค้า")
    qc_pending_list = df[df['QC_Status'] == 'Pending QC']

    if qc_pending_list.empty:
        pd_st.info("ไม่มีรายการสินค้าค้างตรวจสเปก")
    else:
        pd_st.write("### รายการสินค้าค้างตรวจสเปก")
        qc_name = pd_st.text_input("ชื่อเจ้าหน้าที่พนักงานตรวจสอบคุณภาพ (QC):", key="fg_global_name")

        options_map_qc = {}
        for r in qc_pending_list.to_dict('records'):
            display_text = f"ใบงาน: {r['job_id']} | รหัสสินค้า: {r['product_id']} | จำนวน: {r['qty']} ชิ้น (รอบ: {r['round_time']})"
            options_map_qc[display_text] = (r['job_id'], r['refrun_id'])

        selected_qc_jobs = pd_st.multiselect(
            "คลิกเลือกตัวงานสินค้าที่ตรวจสอบผ่านเกณฑ์พร้อมกันหลายรายการ:", 
            list(options_map_qc.keys())
        )

        pd_st.write("---")
        
        is_button_disabled = not (qc_name.strip() and selected_qc_jobs)

        if pd_st.button(
            "อนุมัติมาตรฐานผ่านเกณฑ์ตามรายการที่เลือก (Approve ยกแผง)", 
            type="primary", 
            use_container_width=True,
            disabled=is_button_disabled
        ):
            for option in selected_qc_jobs:
                j_id, ref_id = options_map_qc[option]
                
                # คีย์อัปเดตสถานะข้อมูลเพื่อส่งต่อให้คลังสินค้า (FG)
                df.loc[(df['job_id'] == j_id) & (df['refrun_id'] == ref_id), 'QC_Status'] = 'Approved'
                df.loc[(df['job_id'] == j_id) & (df['refrun_id'] == ref_id), 'FG_Status'] = 'Pending FG'
                df.loc[(df['job_id'] == j_id) & (df['refrun_id'] == ref_id), 'QC_Inspector'] = qc_name.strip()
            
            save_data(df)
            pd_st.session_state.df = df
            pd_st.success("อนุมัติรายการสินค้าและส่งข้อมูลต่อไปยังแผนกคลังสินค้า (FG) เรียบร้อยแล้ว!")
            pd_st.rerun()


# ------------------------------------------------------------------------------
# 3. แผนกคลังสินค้า (FG)
# ------------------------------------------------------------------------------
elif pd_st.session_state.current_page == "fg":
    pd_st.subheader("ส่วนงานคลังสินค้าสำเร็จรูป (Finished Goods - FG): รับสินค้าเข้าคลัง")
    fg_pending_list = df[df['FG_Status'] == 'Pending FG']

    if fg_pending_list.empty:
        pd_st.info("ไม่มีรายการสินค้าค้างรับเข้าคลัง")
    else:
        pd_st.write("### รายการสินค้าค้างรับเข้าคลัง")
        fg_name = pd_st.text_input("ชื่อเจ้าหน้าที่พนักงานคลังสินค้า (FG):", key="fg_user_name")

        options_map_fg = {}
        for r in fg_pending_list.to_dict('records'):
            display_text = f"ใบงาน: {r['job_id']} | รหัสสินค้า: {r['product_id']} | จำนวน: {r['qty']} ชิ้น (รอบ: {r['round_time']})"
            options_map_fg[display_text] = (r['job_id'], r['refrun_id'])

        selected_fg_jobs = pd_st.multiselect(
            "คลิกเลือกตัวงานสินค้าที่ต้องการรับเข้าคลังพร้อมกันหลายรายการ:", 
            list(options_map_fg.keys())
        )

        pd_st.write("---")
        
        is_fg_button_disabled = not (fg_name.strip() and selected_fg_jobs)

        if pd_st.button(
            "ยืนยันการรับสินค้าเข้าคลังสำเร็จรูป", 
            type="primary", 
            use_container_width=True,
            disabled=is_fg_button_disabled
        ):
            for option in selected_fg_jobs:
                j_id, ref_id = options_map_fg[option]
                
                # คีย์อัปเดตสถานะเข้าคลัง และเตรียมส่งตัดข้อมูลระบบ ERP
                df.loc[(df['job_id'] == j_id) & (df['refrun_id'] == ref_id), 'FG_Status'] = 'In Stock'
                df.loc[(df['job_id'] == j_id) & (df['refrun_id'] == ref_id), 'ERP_Status'] = 'Pending ERP'
                df.loc[(df['job_id'] == j_id) & (df['refrun_id'] == ref_id), 'FG_Receiver'] = fg_name.strip()
            
            save_data(df)
            pd_st.session_state.df = df
            pd_st.success("รับสินค้าเข้าคลังสำเร็จรูป และเตรียมส่งข้อมูลเข้าระบบ ERP เรียบร้อยแล้ว!")
            pd_st.rerun()


# ------------------------------------------------------------------------------
# 4. ฝ่ายบริการข้อมูลคลัง (ERP)
# ------------------------------------------------------------------------------
elif pd_st.session_state.current_page == "erp":
    pd_st.subheader("ส่วนงานบริการข้อมูลคลังสินค้า (ERP Integration)")
    erp_pending_list = df[df['ERP_Status'] == 'Pending ERP']
    
    if erp_pending_list.empty:
        pd_st.info("ไม่มีรายการสินค้าค้างซิงค์ระบบ ERP")
    else:
        pd_st.write("### รายการสินค้าที่พร้อมอัปเดตเข้าระบบ ERP หลัก")
        pd_st.dataframe(erp_pending_list[['job_id', 'product_id', 'qty', 'QC_Inspector', 'FG_Receiver']])
        
        if pd_st.button("ซิงค์ข้อมูลและตัดยอดเข้า ERP ทั้งหมด", type="primary"):
            df.loc[df['ERP_Status'] == 'Pending ERP', 'ERP_Status'] = 'Synced ERP'
            save_data(df)
            pd_st.session_state.df = df
            pd_st.success("ซิงค์ประวัติข้อมูลคลังสินค้าเข้าสู่ระบบ ERP สำเร็จเรียบร้อย!")
            pd_st.rerun()
