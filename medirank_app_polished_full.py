# Fix: Display patient input summary and most likely diagnosis on-screen
# Add input summary and chart figures to PDF output in code

# Load the last polished app version
with open("/mnt/data/medirank_app_polished_full.py", "r") as f:
    code = f.read()

# Fix PDF section: add patient input + include chart images
fixed_code = code.replace(
    "pdf.cell(0, 8, f\"Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\"",
    "pdf.cell(0, 8, f\"Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\""
    "\\npdf.ln(3)\n"
    "pdf.set_font(\"Arial\", 'B', 12)\n"
    "pdf.cell(0, 8, \"Patient Input Summary:\", ln=True)\n"
    "pdf.set_font(\"Arial\", '', 11)\n"
    "for i, val in enumerate([fever, platelet, wbc, bleeding, fatigue, pain, nausea]):\n"
    "    label = [\"Fever\", \"Platelet\", \"WBC\", \"Bleeding\", \"Fatigue\", \"Pain\", \"Nausea\"][i]\n"
    "    pdf.cell(0, 7, f\"{label}: {val}\", ln=True)\n"
)

# Add image saving and insertion to PDF
insert_image_code = '''
# Save chart images
bar_buf = io.BytesIO()
fig_bar.savefig(bar_buf, format='png', bbox_inches='tight')
bar_buf.seek(0)
bar_img = Image.open(bar_buf)
bar_path = "_bar_chart.png"
bar_img.save(bar_path)

radar_buf = io.BytesIO()
fig_radar.savefig(radar_buf, format='png', bbox_inches='tight')
radar_buf.seek(0)
radar_img = Image.open(radar_buf)
radar_path = "_radar_chart.png"
radar_img.save(radar_path)

# Insert figures into PDF
pdf.add_page()
pdf.set_font("Arial", 'B', 12)
pdf.cell(0, 8, "Diagnosis Similarity Chart:", ln=True)
pdf.image(bar_path, x=15, y=30, w=180)
pdf.ln(95)
pdf.cell(0, 8, "Radar Chart Comparison:", ln=True)
pdf.image(radar_path, x=40, y=110, w=120)
'''

fixed_code += "\n" + insert_image_code.strip()

# Save corrected file
fixed_final_path = "/mnt/data/medirank_app_fixed_display_and_figures.py"
with open(fixed_final_path, "w") as f:
    f.write(fixed_code)

fixed_final_path
