import streamlit as st
import plotly.graph_objects as go
import random

def show():
    st.markdown("""
        <style>
        .prediction-box {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
            background-color: #f0f9ff;
            border-left: 6px solid #1f77b4;
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("🧬 Genetic Test Recommendation")

