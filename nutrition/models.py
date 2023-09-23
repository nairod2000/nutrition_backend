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
    servingSizeId = models.ForeignKey(ServingSize, on_delete=models.CASCADE)
    nutrients = models.ManyToManyField(Nutrient, through='ItemNutrient', related_name='items')
    userId = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # Creator of item (if applicable)
    favoritedBy = models.ManyToManyField(User, through='FavoriteItem', related_name='favorites')
    isCustom = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # If item is user-created, set isCustom to True.
        if self.userId:
            self.isCustom = True
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class CombinedItem(models.Model):
    # Represents a user-defined combination of items, such as a recipe or a meal.
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Consumed(models.Model):
    # Represents a user's consumption of an item or combined item.
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    itemId = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    combinedItemId = models.ForeignKey(CombinedItem, on_delete=models.CASCADE, null=True, blank=True)
    consumedAt = models.DateTimeField(auto_now_add=True)
    portion = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def clean(self):
        # Ensure that at least one of itemId or combinedItemId is populated.
        if not self.itemId and not self.combinedItemId:
            raise ValidationError("At least one of itemId or combinedItemId must be populated.")
        
        # Ensure that only one of itemId or combinedItemId is populated.
        if self.itemId and self.combinedItemId:
            raise ValidationError("Only one of itemId or combinedItemId should be populated.")
        
    def __str__(self):
        if self.itemId:
            return f"Consumed: {self.itemId.name} by User: {self.userId.username}"
        elif self.combinedItemId:
            return f"Consumed: {self.combinedItemId.name} by User: {self.userId.username}"
    
class CombinedItemElement(models.Model):
    # Represents an item that is part of a combined item.
    combinedItemId = models.ForeignKey(CombinedItem, on_delete=models.CASCADE)
    itemId = models.ForeignKey(Item, on_delete=models.CASCADE)
    portion = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"Element: {self.itemId.name} in Combined Item: {self.combinedItemId.name}"

class ItemNutrient(models.Model):
    # Links an item to a nutrient and specifies the amount of that nutrient in the item.
    itemId = models.ForeignKey(Item, on_delete=models.CASCADE)
    nutrientId = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.itemId.name} - {self.nutrientId.name}"


class ItemBioactive(models.Model):
    # Represents a bioactive compound in an item.
    itemId = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    unitId = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class FavoriteItem(models.Model):
    # Represents one of the favorite items of a user.
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    itemId = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.userId.username}'s favorite: {self.itemId.name}"

class NutritionalGoalTemplate(models.Model):
    # Represents a template for a nutritional goal, such as fda recommended daily values or weight loss or gain.
    name = models.CharField(max_length=50)
    calories = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    nutrients = models.ManyToManyField(Nutrient, through='GoalTemplateNutrient', related_name='templates')

    def __str__(self):
        return self.name
    
class GoalTemplateNutrient(models.Model):
    # Links a nutrient to a nutritional goal template and specifies the recommended value for that nutrient.
    nutrientId = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    templateId = models.ForeignKey(NutritionalGoalTemplate, on_delete=models.CASCADE)
    recommendedValue = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.templateId.name} - {self.nutrientId.name}"
    
class UserNutritionalGoal(models.Model):
    # Represents a user's nutritional goals.
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) # Name of goal, not user
    templateId = models.ForeignKey(NutritionalGoalTemplate, on_delete=models.CASCADE)
    calories = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    nutrients = models.ManyToManyField(Nutrient, through='UserNutritionalGoalNutrient', related_name='goals')

    def __str__(self):
        return f"{self.userId.username}'s {self.name} Goal"
    
    def save(self, *args, **kwargs):
        # Set the name field based on the selected template's name
        if not self.name:
            self.name = self.templateId.name
        super(UserNutritionalGoal, self).save(*args, **kwargs)
    
class UserNutritionalGoalNutrient(models.Model):
    # Links a nutrient to a user's nutritional goal and specifies the recommended value for that nutrient.
    nutrientId = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    goalId = models.ForeignKey(UserNutritionalGoal, on_delete=models.CASCADE)
    recommendedValue = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.goalId.userId.username}'s {self.goalId.name} Goal - {self.nutrientId.name}"