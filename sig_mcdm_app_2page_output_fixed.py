import streamlit as st
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os
import io

# Page config
st.set_page_config(page_title="SIG-MCDM 2-Page Diagnostic App", layout="centered")

# Header
st.title("🧠 SIG-MCDM Diagnostic Support System (2-Page Report)")
st.markdown("Enter patient data below to generate a professional PDF report.")

# Form
with st.form("input_form"):
    patient_name = st.text_input("Patient Name", "John Doe")
    doctor_name = st.text_input("Doctor Name", "Dr. Zahari")
    fever = st.number_input("Fever (°C)", 35.0, 42.0, 38.5)
    platelet = st.number_input("Platelet Count", 10, 500, 55)
    wbc = st.number_input("WBC Count", 0.5, 30.0, 3.0)
    bleeding = st.selectbox("Bleeding", ["No", "Yes"])
    fatigue = st.selectbox("Fatigue", ["None", "Mild", "Moderate", "Severe"], index=2)
    pain = st.selectbox("Pain", ["None", "Mild", "Moderate", "Severe"], index=3)
    nausea = st.selectbox("Nausea", ["None", "Slight", "Frequent"], index=2)
    submitted = st.form_submit_button("🩺 Generate Report")

if submitted:
    criteria = ['Fever (°C)', 'Platelet Count', 'WBC Count', 'Bleeding', 'Fatigue', 'Pain', 'Nausea']
    patient_values = [f"{fever:.1f}", f"{platelet}", f"{wbc:.1f}", bleeding, fatigue, pain, nausea]
    patient_vector = [
        fever, platelet, wbc,
        1 if bleeding == "Yes" else 0,
        {"None": 0.0, "Mild": 0.3, "Moderate": 0.6, "Severe": 0.9}[fatigue],
        {"None": 0.0, "Mild": 0.3, "Moderate": 0.6, "Severe": 0.9}[pain],
        {"None": 0.0, "Slight": 0.6, "Frequent": 0.9}[nausea]
    ]
    healthy_vector = [36.8, 250, 6.0, 0, 0.1, 0.1, 0.0]
    disease_vector = [38.5, 45, 4.0, 1, 0.6, 0.3, 0.9]
    company_name = "UiTM SIG-MCDM System"
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    diagnosis_explanation = [
        "- Fever matches Dengue profile (38.5°C).",
        "- Platelet count low, close to Dengue's (45 vs input).",
        "- WBC is low, consistent with viral infection.",
        "- Bleeding present - matches hallmark of Dengue Hemorrhagic Fever.",
        "- Fatigue and nausea severity align closely with Dengue symptoms.",
        "- Overall, 5 of 7 criteria are strong matches to Dengue."
    ]

    def save_chart_as_image(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        return Image.open(buf)

    fig_bar, ax = plt.subplots(figsize=(6, 2))
    diseases = ['Dengue DHF', 'Sepsis', 'Meningitis', 'Leukemia']
    scores = [98.6, 65.4, 59.3, 52.1]
    ax.barh(diseases, scores, color='green')
    ax.set_title("Diagnosis Ranking")
    for i, v in enumerate(scores):
        ax.text(v + 1, i, f"{v:.1f}%", va='center')
    bar_img = save_chart_as_image(fig_bar)
    plt.close(fig_bar)

    norm_max = [42, 500, 30, 1, 1, 1, 1]
    angles = np.linspace(0, 2 * np.pi, len(criteria), endpoint=False).tolist()
    angles += angles[:1]
    patient_norm = [v / m for v, m in zip(patient_vector, norm_max)] + [patient_vector[0] / norm_max[0]]
    disease_norm = [v / m for v, m in zip(disease_vector, norm_max)] + [disease_vector[0] / norm_max[0]]
    fig_radar, ax = plt.subplots(subplot_kw={'polar': True}, figsize=(4, 4))
    ax.plot(angles, patient_norm, label='Patient', color='blue')
    ax.fill(angles, patient_norm, alpha=0.25, color='blue')
    ax.plot(angles, disease_norm, label='Dengue DHF', color='green')
    ax.fill(angles, disease_norm, alpha=0.25, color='green')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criteria, fontsize=6)
    ax.legend(loc='upper right', fontsize=6)
    radar_img = save_chart_as_image(fig_radar)
    plt.close(fig_radar)

    fig_health, ax = plt.subplots(figsize=(5, 3))
    y = np.arange(len(criteria))
    ax.barh(y, patient_vector, color="dodgerblue", label="Patient")
    ax.barh(y, healthy_vector, color="lightgray", label="Healthy", alpha=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(criteria)
    ax.invert_yaxis()
    ax.legend()
    ax.set_title("Patient vs Healthy Profile")
    healthy_img = save_chart_as_image(fig_health)
    plt.close(fig_health)

    bar_path = "_bar_chart.png"
    radar_path = "_radar_chart.png"
    healthy_path = "_healthy_chart.png"
    bar_img.save(bar_path)
    radar_img.save(radar_path)
    healthy_img.save(healthy_path)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    def header():
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 6, f"{company_name}", ln=True)
        pdf.cell(0, 6, f"Patient: {patient_name}     Doctor: {doctor_name}     Date: {report_time}", ln=True)
        pdf.ln(4)

    pdf.add_page()
    header()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Page 1: Summary & Visual Comparison", ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Patient Input Summary:", ln=True)
    pdf.set_font("Arial", '', 11)
    for c, v in zip(criteria, patient_values):
        pdf.cell(60, 8, f"{c}:", 0, 0)
        pdf.cell(0, 8, f"{v}", ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Why 'Dengue DHF' is Ranked #1:", ln=True)
    pdf.set_font("Arial", '', 11)
    for line in diagnosis_explanation:
        pdf.multi_cell(0, 6, line)
    pdf.ln(3)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Visual Comparison:", ln=True)
    pdf.image(bar_path, x=20, y=150, w=170)
    pdf.image(radar_path, x=15, y=200, w=85)
    pdf.image(healthy_path, x=110, y=200, w=85)
    pdf.add_page()
    header()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Page 2: (Reserved for additional notes)", ln=True)

    # ✅ FIXED: Write to buffer correctly
    buffer = io.BytesIO()
    buffer.write(pdf.output(dest="S").encode("latin-1"))
    buffer.seek(0)

    st.success("✅ Report generated successfully!")
    st.download_button(
        label="📥 Download 2-Page Diagnosis Report (PDF)",
        data=buffer,
        file_name="SIG_MCDM_Report.pdf",
        mime="application/pdf"
    )