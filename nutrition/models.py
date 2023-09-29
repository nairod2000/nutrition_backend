from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

class User(AbstractUser):
    # Represents a user of the application.
    age = models.PositiveIntegerField(blank=True, null=True)
    weight = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True, null=True)
    is_pregnant = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name='user_set_nutrition', blank=True, verbose_name='groups')
    user_permissions = models.ManyToManyField(Permission, related_name='user_set_nutrition', blank=True, verbose_name='user permissions')

    def clean(self):
        if self.sex == 'Male' and self.is_pregnant:
            raise ValidationError("A male user cannot be pregnant.")

    def __str__(self):
        return self.username

class Unit(models.Model):
    # Represents a unit of measurement, such as a gram or fluid ounce.
    name = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name
    
class ServingSize(models.Model):
    # Represents a serving size, such as 1 pint or 100 grams.
    amount = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0.01)])
    unitId = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amount} {self.unitId}"

class Nutrient(models.Model):
    # Represents a nutrient, such as a macronutrient or a vitamin or mineral.
    name = models.CharField(max_length=50, unique=True)
    unitId = models.ForeignKey(Unit, on_delete=models.CASCADE)
    isCategory = models.BooleanField(default=False)
    parentNutrientId = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    # Represents a distinct edible item, including basic and packaged foods and supplements.
    name = models.TextField()
    barcode = models.CharField(max_length=50, null=True, blank=True)
    calories = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
<<<<<<< HEAD
    servingSizeId = models.ForeignKey(ServingSize, on_delete=models.CASCADE)
    nutrients = models.ManyToManyField(Nutrient, through='ItemNutrient', related_name='items')
    userId = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # Creator of item (if applicable)
=======
    servingSize = models.ForeignKey(ServingSize, on_delete=models.CASCADE)
    nutrients = models.ManyToManyField(Nutrient, through='ItemNutrient', related_name='items')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # Creator of item (if applicable)
>>>>>>> dev-casey
    favoritedBy = models.ManyToManyField(User, through='FavoriteItem', related_name='favorites')
    isCustom = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # If item is user-created, set isCustom to True.
<<<<<<< HEAD
        if self.userId:
=======
        if self.user:
>>>>>>> dev-casey
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
<<<<<<< HEAD
    combinedItemId = models.ForeignKey(CombinedItem, on_delete=models.CASCADE)
    itemId = models.ForeignKey(Item, on_delete=models.CASCADE)
=======
    combinedItem = models.ForeignKey(CombinedItem, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
>>>>>>> dev-casey
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
    unitId = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class FavoriteItem(models.Model):
    # Represents one of the favorite items of a user.
<<<<<<< HEAD
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    itemId = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.userId.username}'s favorite: {self.itemId.name}"

class NutritionalGoalTemplate(models.Model):
=======
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.item.name}"

class GoalTemplate(models.Model):
>>>>>>> dev-casey
    # Represents a template for a nutritional goal, such as fda recommended daily values or weight loss or gain.
    name = models.CharField(max_length=50)
    calories = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    nutrients = models.ManyToManyField(Nutrient, through='GoalTemplateNutrient', related_name='templates')

    def __str__(self):
        return self.name
    
class GoalTemplateNutrient(models.Model):
    # Links a nutrient to a nutritional goal template and specifies the recommended value for that nutrient.
<<<<<<< HEAD
    nutrientId = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    templateId = models.ForeignKey(NutritionalGoalTemplate, on_delete=models.CASCADE)
=======
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    template = models.ForeignKey(GoalTemplate, on_delete=models.CASCADE)
>>>>>>> dev-casey
    recommendedValue = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.templateId.name} - {self.nutrientId.name}"
    
class UserGoal(models.Model):
    # Represents a user's nutritional goals.
<<<<<<< HEAD
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) # Name of goal, not user
    templateId = models.ForeignKey(NutritionalGoalTemplate, on_delete=models.CASCADE)
    calories = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    nutrients = models.ManyToManyField(Nutrient, through='UserNutritionalGoalNutrient', related_name='goals')

    def __str__(self):
        return f"{self.userId.username}'s {self.name} Goal"
=======
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) # Name of goal, not user
    template = models.ForeignKey(GoalTemplate, on_delete=models.CASCADE)
    calories = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    nutrients = models.ManyToManyField(Nutrient, through='UserGoalNutrient', related_name='goals')

    def __str__(self):
        return f"{self.user.username}'s {self.name} Goal"
>>>>>>> dev-casey
    
    def save(self, *args, **kwargs):
        # Set the name field based on the selected template's name
        if not self.name:
<<<<<<< HEAD
            self.name = self.templateId.name
        super(UserNutritionalGoal, self).save(*args, **kwargs)
    
class UserNutritionalGoalNutrient(models.Model):
    # Links a nutrient to a user's nutritional goal and specifies the recommended value for that nutrient.
    nutrientId = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    goalId = models.ForeignKey(UserNutritionalGoal, on_delete=models.CASCADE)
    recommendedValue = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.goalId.userId.username}'s {self.goalId.name} Goal - {self.nutrientId.name}"
=======
            self.name = self.template.name
        super(UserGoal, self).save(*args, **kwargs)
    
class UserGoalNutrient(models.Model):
    # Links a nutrient to a user's nutritional goal and specifies the recommended value for that nutrient.
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    goal = models.ForeignKey(UserGoal, on_delete=models.CASCADE)
    recommendedValue = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.goal.user.username}'s {self.goal.name} Goal - {self.nutrient.name}"
>>>>>>> dev-casey
