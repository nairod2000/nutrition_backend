from nutrition.models import UserGoalNutrient

ACTIVITY_MULTIPLIERS = {
    'Sedentary': 1.2,
    'Lightly Active': 1.375,
    'Moderately Active': 1.55,
    'Very Active': 1.725,
    'Extremely Active': 1.9,
}

# Calculate BMR using Mifflin-St Jeor Equation
def calculateBMR(user):
    bmr = (4.536 * user.weight) + (15.88 * user.height) - (5 * user.age)
    if user.sex == 'Male':
        bmr += 5
    else:
        bmr += -161
    return bmr

# Calculate calories; this is based on total daily enerty expenditure adjusted for doet goals, pregnancy, and lactation
def calculateCalories(user):
    bmr = calculateBMR(user)
    tdee = bmr * ACTIVITY_MULTIPLIERS.get(user.activity_level, 1.2)

    if user.is_pregnant:
        # Add extra calories during pregnancy
        tdee += 300  # This is just an estimate, it should be based on more research

    if user.is_lactating:
        # Add extra calories if breastfeeding
        tdee += 500  # This is just an estimate, it should be based on more research

    if user.diet_goal == 'Lose Weight':
        calories = tdee - 500
    elif user.diet_goal == 'Gain Weight':
        calories = tdee + 500
    else:
        calories = tdee

    return calories

# Calculate macronutrent targets based on a calorie target
def calculateMacronutrients(calories, age):
    # Calorie values per gram for each macronutrient based on approximate Atwater factors
    caloriesPerGram = {'Fat': 9, 'Carbohydrate': 4, 'Protein': 4}

    # FDA macronutrent calorie distribution percentages based on age
    if 1 <= age <= 3:
        percents = {'Fat': 0.35, 'Carbohydrate': 0.525, 'Protein': 0.125}
    elif 4 <= age <= 18:
        percents = {'Fat': 0.275, 'Carbohydrate': 0.525, 'Protein': 0.2}
    else:
        percents = {'Fat': 0.225, 'Carbohydrate': 0.525, 'Protein': 0.25}

    # Calculate nutrient distribution based on FDA percentages and calorie values
    calorieDistribution = {}
    for nutrient, percent in percents.items():
        calorieValue = (percent * calories) / caloriesPerGram[nutrient]
        calorieDistribution[nutrient] = calorieValue

    return calorieDistribution

# Format nutrient data for use in the frontend
def serializeNutrients(goal):
    goalNutrients = UserGoalNutrient.objects.filter(goal=goal)
    goalNutrientsList = []

    for goalNutrient in goalNutrients:
        nutrientData = {
            "id": goalNutrient.id,
            "nutrient": {
                "id": goalNutrient.nutrient.id,
                "name": goalNutrient.nutrient.name,
                "unit": goalNutrient.nutrient.unit.abbreviation,
            },
            "targetValue": goalNutrient.targetValue,
        }
        goalNutrientsList.append(nutrientData)

    return goalNutrientsList