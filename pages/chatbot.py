import streamlit as st
import re
RESPONSES = {
    r"(headache|head ache|head pain)": (
        "For headaches, try resting in a quiet dark room, stay hydrated, and consider OTC pain relief. "
        "If severe or recurring, consult a doctor."
    ),
    r"(fever|temperature|hot|38|39)": (
        "For fever, rest and drink plenty of fluids. Take paracetamol if needed. "
        "Seek medical help if temperature exceeds 39.5°C or persists beyond 3 days."
    ),
    r"(chest pain|chest tightness|heart)": (
        "⚠️ Chest pain can be serious. If you are experiencing severe chest pain, call emergency services immediately. "
        "Do not ignore chest pain especially if it radiates to arm or jaw."
    ),
    r"(cough|cold|flu|runny nose|sneezing)": (
        "For cold/cough symptoms: rest, stay warm, drink warm fluids with honey. "
        "If symptoms worsen or you have difficulty breathing, see a doctor."
    ),
    r"(diabetes|blood sugar|glucose|insulin)": (
        "Diabetes management involves monitoring blood sugar, following a low-glycaemic diet, regular exercise, "
        "and taking prescribed medication. Regular check-ups are essential."
    ),
    r"(blood pressure|hypertension|bp)": (
        "High blood pressure can be managed through low-sodium diet, regular exercise, stress reduction, "
        "and prescribed medication. Monitor BP regularly."
    ),
    r"(stress|anxiety|mental health|worried|anxious)": (
        "Stress and anxiety are common. Try deep breathing exercises, meditation, or a short walk. "
        "Talking to a mental health professional can be very helpful."
    ),
    r"(sleep|insomnia|can't sleep|tired)": (
        "For better sleep: maintain a consistent schedule, avoid screens before bed, limit caffeine after 2PM, "
        "and create a cool dark sleep environment."
    ),
    r"(diet|nutrition|food|eat|weight|obesity)": (
        "A balanced diet includes fruits, vegetables, whole grains, lean proteins, and healthy fats. "
        "Limit processed food, sugar, and salt. Consider consulting a nutritionist."
    ),
    r"(exercise|workout|gym|fitness|walk)": (
        "The WHO recommends 150 minutes of moderate exercise per week. "
        "Even a 30-minute daily walk can significantly improve health."
    ),
    r"(appointment|doctor|hospital|consult)": (
        "You can use the Doctor Panel to request a clinical review. "
        "For emergencies, please contact your nearest hospital immediately."
    ),
    r"(hello|hi|hey|good morning|good evening)": (
        "Hello! I'm your NLP-Medora Health Assistant. How can I help you today? "
        "You can ask me about symptoms, medications, diet, or general health advice."
    ),
    r"(thank|thanks|thank you)": (
        "You're welcome! Stay healthy and take care. Remember — I'm here whenever you have health questions! 😊"
    ),
    r"(covid|coronavirus|pandemic|vaccine|vaccination)": (
        "COVID-19 vaccines are safe and effective. Symptoms include fever, cough, and fatigue. "
        "If experiencing severe symptoms, seek medical attention promptly."
    ),
}
