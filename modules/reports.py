import streamlit as st
from services.report_Pdf import process_report, extract_text_from_pdf


def show():
    st.set_page_config(page_title="Medical Report AI", layout="centered")

    st.title("📄 Medical Report Simplifier AI")

    tab1, tab2 = st.tabs(["📋 Paste Report", "📁 Upload PDF"])


    with tab1:
        text = st.text_area("Paste medical report:", height=250)

        if st.button("🔍 Analyze Report"):
            if text.strip():
                result = process_report(text)

                st.markdown("### 🩺 Results")

                st.markdown("#### 📌 Findings")
                for f in result["findings"]:
                    st.markdown(f)

                st.markdown("#### 💡 Advice")
                for a in result["advice"]:
                    st.markdown(a)

                st.markdown("#### 🔬 Extracted Values")
                st.json(result["extracted"])

            else:
                st.warning("Please enter report text.")


    with tab2:
        file = st.file_uploader("Upload PDF Report", type=["pdf"])

        if file:
            st.success("PDF uploaded successfully!")

            text = extract_text_from_pdf(file)

            st.text_area("Extracted Text", text[:1000], height=200)

            result = process_report(text)

            st.markdown("### 🩺 Results")

            for f in result["findings"]:
                st.markdown(f)

            for a in result["advice"]:
                st.markdown(a)