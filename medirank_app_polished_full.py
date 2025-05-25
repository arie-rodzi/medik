import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import io

st.set_page_config(page_title="MediRank – Diagnosis Support Tool", layout="wide")
st.title("🧠 MediRank – Acute Diagnosis Support Tool")

with st.form("diagnosis_form"):
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name", "John Doe")
        fever = st.number_input("Fever (°C)", 35.0, 42.0, 38.5)
        platelet = st.number_input("Platelet Count (×10⁹/L)", 10, 500, 55)
        wbc = st.number_input("WBC Count (×10⁹/L)", 0.5, 30.0, 3.0)
    with col2:
        doctor_name = st.text_input("Doctor Name", "Dr. Zahari")
        bleeding = st.selectbox("Bleeding", ["No", "Yes"])
        fatigue = st.selectbox("Fatigue", ["None", "Mild", "Moderate", "Severe"])
        pain = st.selectbox("Pain", ["None", "Mild", "Moderate", "Severe"])
        nausea = st.selectbox("Nausea", ["None", "Slight", "Frequent"])
    submitted = st.form_submit_button("🩺 Diagnose")

if submitted:
    fuzzy_map = {
        "None": 0.0, "Mild": 0.3, "Moderate": 0.6, "Severe": 0.9,
        "Slight": 0.6, "Frequent": 0.9, "Yes": 1, "No": 0
    }

    patient_vector = [
        fever,
        platelet,
        wbc,
        fuzzy_map[bleeding],
        fuzzy_map[fatigue],
        fuzzy_map[pain],
        fuzzy_map[nausea]
    ]

    diseases = {
        "Dengue DHF":    [38.5,  45,  4.0, 1.0, 0.6, 0.9, 0.9],
        "Sepsis":        [39.0, 180, 25.0, 0.0, 0.3, 0.6, 0.0],
        "Meningitis":    [39.2, 150, 12.0, 0.0, 0.6, 0.9, 0.6],
        "Leukemia":      [38.0,  90,  1.2, 1.0, 0.6, 0.9, 0.3],
        "Typhoid Fever": [38.8, 110,  5.0, 0.0, 0.6, 0.3, 0.9],
        "Malaria":       [39.5,  70,  6.5, 1.0, 0.9, 0.9, 0.9],
        "COVID-19":      [39.0, 140,  7.0, 0.0, 0.9, 0.6, 0.3],
        "Hepatitis A":   [38.0, 160,  5.5, 0.0, 0.6, 0.3, 0.9],
        "Appendicitis":  [38.2, 250, 10.0, 0.0, 0.3, 0.9, 0.6]
    }

    def euclidean_distance(v1, v2):
        return sum((a - b) ** 2 for a, b in zip(v1, v2)) ** 0.5

    distances = {k: euclidean_distance(patient_vector, v) for k, v in diseases.items()}
    max_dist = max(distances.values())
    similarities = {k: (1 - d / max_dist) * 100 for k, d in distances.items()}

    result_df = pd.DataFrame([
        {"Disease": k, "Distance": round(distances[k], 2), "Similarity (%)": round(similarities[k], 1)}
        for k in distances
    ]).sort_values(by="Similarity (%)", ascending=False)

    top_disease = result_df.iloc[0]["Disease"]

    st.subheader("📊 Diagnosis Ranking")
    st.dataframe(result_df)

    st.success(f"✅ Most likely diagnosis: **{top_disease}**")

    # Charts layout
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Similarity Chart")
        fig_bar, ax = plt.subplots(figsize=(6, 3))
        ax.barh(result_df["Disease"], result_df["Similarity (%)"], color="green")
        ax.set_xlabel("Similarity (%)")
        ax.set_title("Diagnosis Similarity Ranking")
        for i, v in enumerate(result_df["Similarity (%)"]):
            ax.text(v + 1, i, f"{v:.1f}%", va="center", fontsize=8)
        st.pyplot(fig_bar)

    with col2:
        st.markdown("### 🕸 Radar Chart Comparison")
        def normalize(vals):
            max_vals = [42, 500, 30, 1, 1, 1, 1]
            return [v / m for v, m in zip(vals, max_vals)]

        angles = np.linspace(0, 2 * np.pi, len(patient_vector), endpoint=False).tolist()
        angles += angles[:1]
        patient_norm = normalize(patient_vector) + [normalize(patient_vector)[0]]
        top_norm = normalize(diseases[top_disease]) + [normalize(diseases[top_disease])[0]]

        fig_radar, ax = plt.subplots(subplot_kw={"polar": True}, figsize=(4, 4))
        ax.plot(angles, patient_norm, label="Patient", color="blue")
        ax.fill(angles, patient_norm, alpha=0.25, color="blue")
        ax.plot(angles, top_norm, label=top_disease, color="green")
        ax.fill(angles, top_norm, alpha=0.25, color="green")
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(["Fever", "Platelet", "WBC", "Bleeding", "Fatigue", "Pain", "Nausea"], fontsize=7)
        ax.legend(loc="upper right", fontsize=7)
        st.pyplot(fig_radar)

    # PDF generation
    buffer = io.BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "MediRank Diagnosis Report", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, f"Patient: {patient_name}", ln=True)
    pdf.cell(0, 8, f"Doctor: {doctor_name}", ln=True)
    pdf.cell(0, 8, f"Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Top Diagnosis: " + top_disease, ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 6, f"The patient's symptom profile most closely matches {top_disease} based on multi-criteria Euclidean similarity ranking.")
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Full Diagnosis Ranking:", ln=True)
    pdf.set_font("Arial", '', 10)
    for i, row in result_df.iterrows():
        pdf.cell(0, 7, f"{row['Disease']}: {row['Similarity (%)']:.1f}%", ln=True)

    buffer.write(pdf.output(dest="S").encode("latin-1"))
    buffer.seek(0)

    st.download_button(
        label="📥 Download Diagnosis Report (PDF)",
        data=buffer,
        file_name=f"MediRank_Report_{patient_name.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )