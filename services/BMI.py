def get_bmi_details(weight, height):
    bmi = weight / (height ** 2)
    if bmi < 18.5: return bmi, "Underweight", "🔵"
    if bmi <= 24.9: return bmi, "Healthy Weight", "🟢"
    if bmi <= 29.9: return bmi, "Overweight", "🟡"
    return bmi, "Obese", "🔴"

def get_recommendations(sleep, activity, diet):
    recommendations = []
    
    if sleep < 6:
        recommendations.append({"text": "Improve sleep (aim for 7-9 hours)", "icon": "😴"})
    if activity < 3:
        recommendations.append({"text": "Increase activity (try 30 mins walking)", "icon": "🏃‍♂️"})
    if diet < 3:
        recommendations.append({"text": "Adjust diet (add more greens/protein)", "icon": "🥗"})
        
    if not recommendations:
        recommendations.append({"text": "Maintain your excellent lifestyle!", "icon": "🌟"})
        
    return recommendations