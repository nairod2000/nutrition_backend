from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

class User(AbstractUser):
    # Represents a user of the application.
    # age is in years
    age = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(120)])
    # weight is in pounds
    weight = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(1000)])
    # height is in inches
    height = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(100)])
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True, null=True)
    is_pregnant = models.BooleanField(default=False)
    is_lactating = models.BooleanField(default=False)
    activity_level = models.CharField(max_length=20, choices=[('Sedentary', 'Sedentary'), ('Lightly Active', 'Lightly Active'), ('Moderately Active', 'Moderately Active'), ('Very Active', 'Very Active'), ('Extremely Active', 'Extremely Active')], blank=True, null=True)
    diet_goal = models.CharField(max_length=20, choices=[('Lose Weight', 'Lose Weight'), ('Maintain Weight', 'Maintain Weight'), ('Gain Weight', 'Gain Weight')], blank=True, null=True)
    groups = models.ManyToManyField(Group, related_name='user_set_nutrition', blank=True, verbose_name='groups')
    user_permissions = models.ManyToManyField(Permission, related_name='user_set_nutrition', blank=True, verbose_name='user permissions')

    def clean(self):
        if self.sex == 'Male' and (self.is_pregnant or self.is_lactating):
            raise ValidationError("A male user cannot be pregnant or lactating.")
        
        if self.is_pregnant and self.is_lactating:
            raise ValidationError("A user cannot be both pregnant and lactating.")

    def __str__(self):
        return self.username

class Unit(models.Model):
    # Represents a unit of measurement, such as a gram or fluid ounce.
    name = models.CharField(max_length=20, unique=True, null=True, blank=True)
    abbreviation = models.CharField(max_length=10, unique=True, null=True, blank=True)
    
    def clean(self):
        if not self.name and not self.abbreviation:
            raise ValidationError("Either 'name' or 'abbreviation' must be provided.")

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.abbreviation
    
class ServingSize(models.Model):
    # Represents a serving size, such as 1 pint or 100 grams.
    amount = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amount} {self.unit}"

class Nutrient(models.Model):
    # Represents a nutrient, such as a macronutrient or a vitamin or mineral.
    name = models.CharField(max_length=200, unique=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    isCategory = models.BooleanField(default=False)
    parentNutrient = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    # Represents a distinct edible item, including basic and packaged foods and supplements.
    name = models.TextField()
    barcode = models.CharField(max_length=50, null=True, blank=True)
    calories = models.PositiveIntegerField(validators=[MaxValueValidator(100000)])
    servingSize = models.ForeignKey(ServingSize, on_delete=models.CASCADE)
    nutrients = models.ManyToManyField(Nutrient, through='ItemNutrient', related_name='items')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # Creator of item (if applicable)
    favoritedBy = models.ManyToManyField(User, through='FavoriteItem', related_name='favorites')
    isCustom = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # If item is user-created, set isCustom to True.
        if self.user:
            self.isCustom = True
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class CombinedItem(models.Model):
    # Represents a user-defined combination of items, such as a recipe or a meal.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Consumed(models.Model):
    # Represents a user's consumption of an item or combined item.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    combinedItem = models.ForeignKey(CombinedItem, on_delete=models.CASCADE, null=True, blank=True)
    consumedAt = models.DateTimeField(auto_now_add=True)
    portion = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def clean(self):
        # Ensure that at least one of item or combinedItem is populated.
        if not self.item and not self.combinedItem:
            raise ValidationError("At least one of item or combinedItem must be populated.")
        
        # Ensure that only one of item or combinedItem is populated.
        if self.item and self.combinedItem:
            raise ValidationError("Only one of item or combinedItem should be populated.")
        
    def __str__(self):
        if self.item:
            return f"Consumed: {self.item.name} by User: {self.user.username}"
        elif self.combinedItem:
            return f"Consumed: {self.combinedItem.name} by User: {self.user.username}"
    
class CombinedItemElement(models.Model):
    # Represents an item that is part of a combined item.
    combinedItem = models.ForeignKey(CombinedItem, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    portion = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"Element: {self.item.name} in Combined Item: {self.combinedItem.name}"

class ItemNutrient(models.Model):
    # Links an item to a nutrient and specifies the amount of that nutrient in the item.
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.item.name} - {self.nutrient.name}"

class ItemBioactive(models.Model):
    # Represents a bioactive compound in an item.
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class FavoriteItem(models.Model):
    # Represents one of the favorite items of a user.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.item.name}"

class GoalTemplate(models.Model):
    # Represents a template for a goal, such as FDA recommended daily intake.
    name = models.CharField(max_length=100, unique=True)
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True, null=True)
    isPregnant = models.BooleanField(default=False)
    isLactating = models.BooleanField(default=False)
    ageMin = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(120)])
    ageMax = models.PositiveIntegerField(default=120, validators=[MaxValueValidator(120)])
    nutrients = models.ManyToManyField(Nutrient, through='GoalTemplateNutrient', related_name='templates')

    def __str__(self):
        return self.name
    
class GoalTemplateNutrient(models.Model):
    # Links a nutrient to a goal template and specifies the recommended value for that nutrient.
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    template = models.ForeignKey(GoalTemplate, on_delete=models.CASCADE)
    recommendedValue = models.DecimalField(default=0, max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.template.name} - {self.nutrient.name}"
    
class UserGoal(models.Model):
    # Represents a user's goals.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) # Name of goal, not user
    template = models.ForeignKey(GoalTemplate, on_delete=models.CASCADE)
    calories = models.PositiveIntegerField(validators=[MaxValueValidator(100000)])
    nutrients = models.ManyToManyField(Nutrient, through='UserGoalNutrient', related_name='goals')
    isActive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s {self.name} Goal"
    
    def save(self, *args, **kwargs):
        # Set the name field based on the selected template's name
        if not self.name:
            self.name = self.template.name

        # If a new goal is created and the user has no other goals, set it as active
        if not self.pk and not UserGoal.objects.filter(user=self.user).exists():
            self.isActive = True
        
        # If a goal is set to active, set all other goals for the user to inactive
        if self.isActive:
            UserGoal.objects.filter(user=self.user).exclude(pk=self.pk).update(isActive=False)
        
        super(UserGoal, self).save(*args, **kwargs)

    def clean(self):
        # Ensure that at least one goal is active
        if not self.isActive and not UserGoal.objects.filter(user=self.user, isActive=True).exists():
            raise ValidationError("At least one goal must be active.")
    
class UserGoalNutrient(models.Model):
    # Links a nutrient to a user's goal and specifies the target value for that nutrient.
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    goal = models.ForeignKey(UserGoal, on_delete=models.CASCADE)
    targetValue = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.goal.user.username}'s {self.goal.name} Goal - {self.nutrient.name}"