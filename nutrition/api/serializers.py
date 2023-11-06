from django.contrib.auth.models import Group
from rest_framework import serializers
from nutrition.models import User, Unit, Nutrient, ServingSize, Item, CombinedItem, Consumed, CombinedItemElement, ItemNutrient, ItemBioactive, FavoriteItem, GoalTemplate, GoalTemplateNutrient, UserGoal, UserGoalNutrient


# User Management Serializers

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
class UserRetrieveUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'age', 'weight', 'height', 'sex', 'is_pregnant', 'is_lactating', 'activity_level', 'diet_goal']
        extra_kwargs = {
            'username': {'required': False},
        }

# Goal Serializers
class UserGoalIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGoal
        fields = ['id']

# Nutrient Serializers

class NutrientStatusSerializer(serializers.Serializer):
    nutrient_id = serializers.IntegerField()
    nutrient_name = serializers.CharField()
    nutrient_unit = serializers.CharField(max_length=10)
    target_value = serializers.DecimalField(max_digits=7, decimal_places=2)
    total_consumed = serializers.DecimalField(max_digits=8, decimal_places=2)

# Model Serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'

class NutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrient
        fields = '__all__'

class ServingSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServingSize
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class CombinedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CombinedItem
        fields = '__all__'

class ConsumedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumed
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}

class CombinedItemElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CombinedItemElement
        fields = '__all__'

class ItemNutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemNutrient
        fields = '__all__'

class ItemBioactiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemBioactive
        fields = '__all__'

class FavoriteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteItem
        fields = '__all__'

class GoalTemplateNutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalTemplateNutrient
        fields = '__all__'

class GoalTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalTemplate
        fields = '__all__'

class UserGoalNutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGoalNutrient
        fields = '__all__'

class UserGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGoal
        fields = '__all__'

