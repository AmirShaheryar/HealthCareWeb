NUTRITION_DB = {
    "Iron Deficiency / Anaemia": {
        "goal": "Increase iron, B12, and folate intake",
        "nutrient_focus": "iron",
        "expensive": [
            {"name": "Beef", "price": 1800, "iron": 2.7, "protein": 26},
            {"name": "Salmon", "price": 1200, "iron": 0.8, "protein": 20},
            {"name": "Chia Seeds", "price": 900, "iron": 7.7, "protein": 17},
        ],
        "budget": [
            {"name": "Lentils", "price": 120, "iron": 7.5, "protein": 25, "note": "Same iron as chia"},
            {"name": "Spinach", "price": 60, "iron": 2.7, "protein": 3, "note": "Same iron as beef"},
            {"name": "Chicken Liver", "price": 200, "iron": 11.0, "protein": 20, "note": "Very high iron"},
            {"name": "Eggs", "price": 180, "iron": 1.8, "protein": 13, "note": "Good B12"},
        ]
    },

    "Diabetes / Blood Sugar Control": {
        "goal": "Control blood sugar with low GI foods",
        "nutrient_focus": "gi",
        "expensive": [
            {"name": "Quinoa", "price": 1200, "gi": 53},
            {"name": "Almonds", "price": 2000, "gi": 15},
        ],
        "budget": [
            {"name": "Barley", "price": 80, "gi": 28, "note": "Very low GI"},
            {"name": "Brown Rice", "price": 150, "gi": 55, "note": "Better than white rice"},
            {"name": "Peanuts", "price": 200, "gi": 14, "note": "Same GI as almonds"},
        ]
    }
}