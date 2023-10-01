MALE_BMR_CONSTANT = 88.362
FEMALE_BMR_CONSTANT = 447.593
HEIGHT_CONSTANT = 4.799
WEIGHT_CONSTANT = 13.397
AGE_CONSTANT = 5.677

ACTIVITY_MULTIPLIERS = {
    'Sedentary': 1.2,
    'Lightly Active': 1.375,
    'Moderately Active': 1.55,
    'Very Active': 1.725,
    'Extremely Active': 1.9,
}


# Calculate the number of calories a user should consume per day
def calculate_calories(user):
    if user.sex == 'Male':
        bmr = (WEIGHT_CONSTANT * user.weight) + (HEIGHT_CONSTANT * user.height) - (AGE_CONSTANT * user.age) + MALE_BMR_CONSTANT
    else:
        bmr = (WEIGHT_CONSTANT * user.weight) + (HEIGHT_CONSTANT * user.height) - (AGE_CONSTANT * user.age) + FEMALE_BMR_CONSTANT

    activity_level_multiplier = ACTIVITY_MULTIPLIERS.get(user.activity_level, 1.2)
    adjusted_calories = bmr * activity_level_multiplier

    if user.diet_goal == 'Lose Weight':
        calculated_calories = adjusted_calories - 500
    elif user.diet_goal == 'Gain Weight':
        calculated_calories = adjusted_calories + 500
    else:
        calculated_calories = adjusted_calories

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