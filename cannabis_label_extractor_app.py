import streamlit as st
from PIL import Image
import pytesseract
import re
import pandas as pd

st.set_page_config(page_title="Cannabis Label Extractor", layout="wide")
st.title("📦 Cannabis Product Label Extractor")
st.markdown("Upload product images and extract UID, THC %, CBD %, dates, etc.")

uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

def extract_fields(image):
    text = pytesseract.image_to_string(image)

    data = {}
    data['UID'] = re.search(r'UID[^\w]*(1A[0-9A-Z]{20,})', text or '')\
                    .group(1) if re.search(r'UID[^\w]*(1A[0-9A-Z]{20,})', text or '') else ''
    data['Packaged Date'] = re.search(r'PACKAGED[^\d]*(\d{2}/\d{2}/\d{2})', text or '')\
                    .group(1) if re.search(r'PACKAGED[^\d]*(\d{2}/\d{2}/\d{2})', text or '') else ''
    data['MFG Date'] = re.search(r'(MFG|MFD|MANUF)[^\d]*(\d{2}/\d{2}/\d{2})', text or '', re.I)\
                    .group(2) if re.search(r'(MFG|MFD|MANUF)[^\d]*(\d{2}/\d{2}/\d{2})', text or '', re.I) else data['Packaged Date']
    data['Expiration Date'] = re.search(r'(BEST BY|EXPIRATION)[^\d]*(\d{2}/\d{2}/\d{2})', text or '', re.I)\
                    .group(2) if re.search(r'(BEST BY|EXPIRATION)[^\d]*(\d{2}/\d{2}/\d{2})', text or '', re.I) else ''
    data['THC %'] = re.search(r'THC[^%\d]*([\d.]+)\s*%', text or '')\
                    .group(1) + '%' if re.search(r'THC[^%\d]*([\d.]+)\s*%', text or '') else ''
    data['CBD %'] = re.search(r'CBD[^%\d]*([\d.]+)\s*%', text or '')\
                    .group(1) + '%' if re.search(r'CBD[^%\d]*([\d.]+)\s*%', text or '') else ''
    data['Brand'] = re.search(r'\b(CBX|CANNABIOTIX)\b', text or '', re.I)\
                    .group(1).upper() if re.search(r'\b(CBX|CANNABIOTIX)\b', text or '', re.I) else ''
    data['Product Name'] = re.search(r'\bCBX\b\s*(.*)', text or '', re.I)\
                    .group(1).strip() if re.search(r'\bCBX\b\s*(.*)', text or '', re.I) else ''
    data['Weight'] = re.search(r'NET\s*WT\.?\s*[:\-]?\s*([\d.]+\s*(g|mg|oz))', text or '', re.I)\
                    .group(1) if re.search(r'NET\s*WT\.?\s*[:\-]?\s*([\d.]+\s*(g|mg|oz))', text or '', re.I) else ''
    data['Type'] = re.search(r'\b(INDICA|SATIVA|HYBRID)\b', text or '', re.I)\
                    .group(1).capitalize() if re.search(r'\b(INDICA|SATIVA|HYBRID)\b', text or '', re.I) else ''
    return data

if uploaded_files:
    results = []
    for file in uploaded_files:
        image = Image.open(file)
        result = extract_fields(image)
        result["Filename"] = file.name
        results.append(result)

    df = pd.DataFrame(results)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "cannabis_data.csv", "text/csv")
