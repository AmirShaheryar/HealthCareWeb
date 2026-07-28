import streamlit as st
from services.BMI import get_bmi_details, get_recommendations

def show():
    st.set_page_config(page_title="Simple Health Tracker", layout="wide")
    
    st.title("🏃‍♂️ Simple Health Advisor")
    st.write("A rule-based tool to check your daily lifestyle habits.")
    st.markdown("---")

    # Sidebar for Physical Metrics
    with st.sidebar:
        st.header("👤 Physical Data")
        weight = st.number_input("Weight (kg)", 40.0, 160.0, 70.0)
        height = st.number_input("Height (m)", 1.2, 2.3, 1.75)
        
        bmi, status, emoji = get_bmi_details(weight, height)
        st.metric("Your BMI", f"{bmi:.1f}")
        st.subheader(f"{emoji} {status}")

    st.subheader("🗓️ Your Daily Habits")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sleep = st.slider("Sleep Hours", 0, 12, 7)
    with col2:
        activity = st.slider("Activity Level (1-5)", 1, 5, 3)
    with col3:
        diet = st.slider("Diet Quality (1-5)", 1, 5, 3)

    st.markdown("---")

    # Action Button
    if st.button("Get Advice", use_container_width=True, type="primary"):
        advice_list = get_recommendations(sleep, activity, diet)
        
        st.subheader("📋 Our Advice")
        for item in advice_list:
            if "Maintain" in item["text"]:
                st.success(f"{item['icon']} {item['text']}")
            else:
                st.warning(f"{item['icon']} {item['text']}")

if __name__ == "__main__":
    show()