from services.nutrition_db import NUTRITION_DB
import random


def get_conditions():
    return list(NUTRITION_DB.keys())


def get_data(condition):
    return NUTRITION_DB.get(condition, {})

def filter_by_budget(condition, budget):
    data = get_data(condition)
    daily_budget = budget / 30

    expensive = []
    for item in data["expensive"]:
        temp = item.copy()
        temp["affordable"] = temp["price"] <= daily_budget
        expensive.append(temp)

    return expensive, data["budget"]


def compute_value_score(item, focus):
    if focus not in item or item["price"] == 0:
        return 0
    return item[focus] / item["price"]

def rank_budget_foods(condition):
    data = get_data(condition)
    focus = data["nutrient_focus"]

    ranked = sorted(
        data["budget"],
        key=lambda x: compute_value_score(x, focus),
        reverse=True
    )
    return ranked


def calculate_savings(condition):
    data = get_data(condition)
    base_price = data["expensive"][0]["price"]

    savings = sum(max(0, base_price - i["price"]) for i in data["budget"])
    return savings


def generate_meal_plan(condition):
    data = get_data(condition)
    foods = data["budget"]

    meals = ["Breakfast", "Lunch", "Snack", "Dinner"]

    plan = []
    for meal in meals:
        item = random.choice(foods)
        plan.append((meal, item["name"]))

    return plan


# 🔹 AI-style recommendation
def generate_recommendation(condition, budget):
    if budget < 5000:
        return "Use lentils, eggs, and vegetables daily. Avoid expensive imports."
    elif budget < 10000:
        return "Mix local foods with occasional meat or fish."
    else:
        return "You can afford a balanced premium diet. Maintain variety."


# 🔹 Detect best alternative
def best_swap(condition):
    ranked = rank_budget_foods(condition)
    if ranked:
        return ranked[0]["name"]
    return "No suggestion"