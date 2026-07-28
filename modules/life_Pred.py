import streamlit as st
from services.life_Style_Predictor import train_and_load_model, predict_lifestyle, recommendation_map

@st.cache_resource
def load_resources():
    return train_and_load_model()

def show():
    st.set_page_config(page_title="Lightweight Health AI")
    model, scaler = load_resources()

    st.title("⚡ Fast Lifestyle Advisor")
    st.caption("Powered by Scikit-Learn (No heavy TensorFlow download required)")

    with st.form("user_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 18, 100, 30)
            gender = st.selectbox("Gender", ["M", "F"])
            weight = st.number_input("Weight (kg)", 40, 150, 70)
        with col2:
            height = st.number_input("Height (m)", 1.2, 2.2, 1.7)
            sleep = st.slider("Sleep Hours", 0.0, 12.0, 7.0)
            activity = st.slider("Activity (1-5)", 1, 5, 3)
        
        diet = st.slider("Diet Score (1-5)", 1, 5, 3)
        submitted = st.form_submit_button("Analyze", use_container_width=True)

    if submitted:
        res = predict_lifestyle(age, gender, weight, height, activity, sleep, diet, model, scaler)
        
        st.subheader("Results")
        if not res["recommendations"]:
            st.success("Everything looks great!")
        else:
            for r in res["recommendations"]:
                st.warning(r)

        with st.expander("Confidence Metrics"):
            cols = st.columns(4)
            for i, label in enumerate(recommendation_map):
                p = res["probabilities"][i]
                cols[i].metric(label, f"{p*100:.0f}%")
                cols[i].progress(float(p))

if __name__ == "__main__":
    show()