from nutrition.models import UserGoalNutrient

WEIGHT_CONSTANT = 4.536
HEIGHT_CONSTANT = 15.88
AGE_CONSTANT = 5
MALE_BMR_CONSTANT = 5
FEMALE_BMR_CONSTANT = -161

ACTIVITY_MULTIPLIERS = {
    'Sedentary': 1.2,
    'Lightly Active': 1.375,
    'Moderately Active': 1.55,
    'Very Active': 1.725,
    'Extremely Active': 1.9,
}

# Calculate BMR using Mifflin-St Jeor Equation
def calculate_bmr(user):
    bmr = (WEIGHT_CONSTANT * user.weight) + (HEIGHT_CONSTANT * user.height) - (AGE_CONSTANT * user.age)
    if user.sex == 'Male':
        bmr += MALE_BMR_CONSTANT
    else:
        bmr += FEMALE_BMR_CONSTANT
    return bmr

# Calculate TDEE and adjust for goals, pregnancy, and lactation
def calculate_calories(user):
    bmr = calculate_bmr(user)
    activity_level_multiplier = ACTIVITY_MULTIPLIERS.get(user.activity_level, 1.2)
    tdee = bmr * activity_level_multiplier

    if user.is_pregnant:
        # Add an extra 300-500 calories per day during pregnancy
        tdee += 300  # We could adjust this value based on specific recommendations

    if user.is_lactating:
        # Add an extra 500 calories per day during lactation
        tdee += 500  # We could adjust this value based on specific recommendations

    if user.diet_goal == 'Lose Weight':
        calculated_calories = tdee - 500  # Create a caloric deficit of 500 calories/day
    elif user.diet_goal == 'Gain Weight':
        calculated_calories = tdee + 500  # Create a caloric surplus of 500 calories/day
    else:
        calculated_calories = tdee  # Maintain current weight

    return calculated_calories

# Calculate the amounts of macronutrients (Carbohydrate, Fat, Protein) a user should consume per day
def calculate_macronutrients(calories, age):
    # FDA recommended percentages for different age groups
    fda_percentages = {
        'Age_1-3': {'Fat': 0.35, 'Carbohydrate': 0.525, 'Protein': 0.125},
        'Age_4-18': {'Fat': 0.275, 'Carbohydrate': 0.525, 'Protein': 0.2},
        'Adults': {'Fat': 0.225, 'Carbohydrate': 0.525, 'Protein': 0.25},
    }

    # Calorie values per gram for each macronutrient
    calorie_per_gram = {'Fat': 9, 'Carbohydrate': 4, 'Protein': 4}

    # Determine the age group based on the provided 'age' parameter
    age_group = ''
    if 1 <= age <= 3:
        age_group = 'Age_1-3'
    elif 4 <= age <= 18:
        age_group = 'Age_4-18'
    else:
        age_group = 'Adults'

    # Calculate nutrient distribution based on FDA percentages and calorie values
    nutrient_distribution = {}
    for nutrient, percentage in fda_percentages[age_group].items():
        calorie_value = (percentage * calories) / calorie_per_gram[nutrient]
        nutrient_distribution[nutrient] = calorie_value

    return nutrient_distribution

def serialize_goal_nutrients(goal):
    goal_nutrients = UserGoalNutrient.objects.filter(goal=goal)
    goal_nutrients_data = []

    for goal_nutrient in goal_nutrients:
        nutrient_data = {
            "id": goal_nutrient.id,
            "nutrient": {
                "id": goal_nutrient.nutrient.id,
                "name": goal_nutrient.nutrient.name,
                "unit": goal_nutrient.nutrient.unit.abbreviation,
            },
            "targetValue": goal_nutrient.targetValue,
        }
        goal_nutrients_data.append(nutrient_data)

    return goal_nutrients_data