from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

class Unit(models.Model):
    # Represents a unit of measurement, such as a gram or fluid ounce.
    name = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name
    
class ServingSize(models.Model):
    # Represents a serving size, such as 1 pint or 100 grams.
    amount = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amount} {self.unit}"

class Nutrient(models.Model):
    # Represents a nutrient, such as a macronutrient or a vitamin or mineral.
    name = models.CharField(max_length=50, unique=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    isCategory = models.BooleanField(default=False)
    parentNutrient = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def clean(self):
        if self.isCategory and self.parentNutrient:
            raise ValidationError("A category nutrient cannot have a parent nutrient.")

class Item(models.Model):
    # Represents a distinct edible item, including basic and packaged foods and supplements.
    name = models.TextField()
    barcode = models.CharField(max_length=50, null=True, blank=True)
    servingSize = models.ForeignKey(ServingSize, on_delete=models.CASCADE)
    nutrients = models.ManyToManyField(Nutrient, through='ItemNutrient', related_name='items')

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
    servingSize = models.ForeignKey(ServingSize, on_delete=models.CASCADE)

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
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class NutritionalGoalTemplate(models.Model):
    # Represents a template for a nutritional goal, such as fda recommended daily values or weight loss or gain.
    name = models.CharField(max_length=50)
    nutrients = models.ManyToManyField(Nutrient, through='GoalTemplateNutrient')

    def __str__(self):
        return self.name
    
class GoalTemplateNutrient(models.Model):
    # Links a nutrient to a nutritional goal template and specifies the recommended value for that nutrient.
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    template = models.ForeignKey(NutritionalGoalTemplate, on_delete=models.CASCADE)
    recommendedValue = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.template.name} - {self.nutrient.name}"
    
class UserNutritionalGoal(models.Model):
    # Represents a user's nutritional goals.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(NutritionalGoalTemplate, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s {self.template.name} Goals"