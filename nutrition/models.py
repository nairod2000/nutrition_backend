from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Unit(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

class FoodItem(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    barcode = models.CharField(max_length=50)
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    fats = models.IntegerField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    servingSize = models.IntegerField()

class Supplement(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    barcode = models.CharField(max_length=50)

class Vitamin(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

class Mineral(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=50)

class CombinedItem(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

class Consumed(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    foodId = models.ForeignKey(FoodItem, on_delete=models.CASCADE, null=True, blank=True)
    supplementId = models.ForeignKey(Supplement, on_delete=models.CASCADE, null=True, blank=True)
    combinedItemId = models.ForeignKey(CombinedItem, on_delete=models.CASCADE, null=True, blank=True)
    consumedAt = models.DateTimeField(auto_now_add=True)
    portion = models.IntegerField()

    def clean(self):
        # Ensure that at least one of foodId, supplementId, or combinedItemId is populated.
        if (
            not self.foodId and
            not self.supplementId and
            not self.combinedItemId
        ):
            raise ValidationError("At least one of foodId, supplementId, or combinedItemId must be populated.")

class CombinedItemElement(models.Model):
    id = models.AutoField(primary_key=True)
    combinedFoodId = models.ForeignKey(CombinedItem, on_delete=models.CASCADE)
    foodId = models.ForeignKey(FoodItem, on_delete=models.CASCADE, null=True, blank=True)
    supplementId = models.ForeignKey(Supplement, on_delete=models.CASCADE, null=True, blank=True)
    servingSize = models.IntegerField()

    def clean(self):
        # Ensure that at least one of foodId or supplementId is populated.
        if (
            not self.foodId and
            not self.supplementId
        ):
            raise ValidationError("At least one of foodId or supplementId must be populated.")

class FoodVitamin(models.Model):
    id = models.AutoField(primary_key=True)
    foodId = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    vitaminId = models.ForeignKey(Vitamin, on_delete=models.CASCADE)
    amount = models.IntegerField()

class FoodMineral(models.Model):
    id = models.AutoField(primary_key=True)
    foodId = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    mineralId = models.ForeignKey(Mineral, on_delete=models.CASCADE)
    amount = models.IntegerField()

class SupplementVitamin(models.Model):
    id = models.AutoField(primary_key=True)
    supplementId = models.ForeignKey(Supplement, on_delete=models.CASCADE)
    vitaminId = models.ForeignKey(Vitamin, on_delete=models.CASCADE)
    amount = models.IntegerField()

class SupplementMineral(models.Model):
    id = models.AutoField(primary_key=True)
    supplementId = models.ForeignKey(Supplement, on_delete=models.CASCADE)
    mineralId = models.ForeignKey(Mineral, on_delete=models.CASCADE)
    amount = models.IntegerField()

class SupplementIngredient(models.Model):
    id = models.AutoField(primary_key=True)
    supplementId = models.ForeignKey(Supplement, on_delete=models.CASCADE)
    foodId = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    amount = models.IntegerField()
    unit = models.CharField(max_length=50)