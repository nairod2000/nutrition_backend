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
        extra_kwargs = {'username': {'required': False}}

    def validate(self, data):
        age = data.get('age')
        weight = data.get('weight')
        height = data.get('height')
        sex = data.get('sex')
        is_pregnant = data.get('is_pregnant')
        is_lactating = data.get('is_lactating')
        password = data.get('password')

        if age is not None and (age < 0 or age > 120):
            raise serializers.ValidationError("Age must be between 0 and 120.")

        if weight is not None and (weight < 0 or weight > 1000):
            raise serializers.ValidationError("Weight must be between 0 and 1000.")

        if height is not None and (height < 0 or height > 100):
            raise serializers.ValidationError("Height must be between 0 and 100.")

        if sex == 'Male' and (is_pregnant or is_lactating):
            raise serializers.ValidationError("A male user cannot be pregnant or lactating.")

        if is_pregnant and is_lactating:
            raise serializers.ValidationError("Select either pregnant or lactating, not both.")

        return data

# ID Serializers

class ItemIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id']

class FavoriteItemIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteItem
        fields = ['item']

class UserGoalIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGoal
        fields = ['id']
        
# Nutrient Serializers

class NutrientStatusSerializer(serializers.Serializer):
    nutrient_id = serializers.IntegerField()
    nutrient_name = serializers.CharField()
    nutrient_unit = serializers.CharField(max_length=10)
    target_value = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_consumed = serializers.DecimalField(max_digits=8, decimal_places=2)

# Consume Serializer

class ConsumedCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumed
        fields = ['item', 'combinedItem', 'portion']

    def validate(self, data):
        portion = data.get('portion')
        item = data.get('item')
        combinedItem = data.get('combinedItem')

        if portion is not None and portion < 0:
            raise serializers.ValidationError("Portion must be greater than or equal to 0.")

        if not item and not combinedItem:
            raise serializers.ValidationError("You must provide an item or combined item.")

        if item and combinedItem:
            raise serializers.ValidationError("You may provide either an item or combined item, not both.")

        return data
    
# Item Serializers

class ItemCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    calories = serializers.DecimalField(max_digits=8, decimal_places=2)
    serving_amount = serializers.DecimalField(max_digits=8, decimal_places=2)
    serving_unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all())
    nutrients = serializers.DictField(child=serializers.DecimalField(max_digits=8, decimal_places=2))

    def validate(self, data):
        calories = data.get('calories')
        serving_amount = data.get('serving_amount')

        if calories < 0:
            raise serializers.ValidationError("Calories must be greater than or equal to 0.")

        if serving_amount < 0:
            raise serializers.ValidationError("Serving amount must be greater than or equal to 0.")
        
        

        return data

# "Regular" Model Serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, data):
        age = data.get('age')
        weight = data.get('weight')
        height = data.get('height')
        sex = data.get('sex')
        is_pregnant = data.get('is_pregnant')
        is_lactating = data.get('is_lactating')

        if age is not None and (age < 0 or age > 120):
            raise serializers.ValidationError("Age must be between 0 and 120.")

        if weight is not None and (weight < 0 or weight > 1000):
            raise serializers.ValidationError("Weight must be between 0 and 1000.")

        if height is not None and (height < 0 or height > 100):
            raise serializers.ValidationError("Height must be between 0 and 100.")

        if sex == 'Male' and (is_pregnant or is_lactating):
            raise serializers.ValidationError("A male user cannot be pregnant or lactating.")

        if is_pregnant and is_lactating:
            raise serializers.ValidationError("Select either pregnant or lactating, not both.")

        return data

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'

    def validate(self, data):
        name = data.get('name')
        abbreviation = data.get('abbreviation')

        if not name and not abbreviation:
            raise serializers.ValidationError("Either 'name' or 'abbreviation' must be provided.")

        return data

class NutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrient
        fields = '__all__'

class ServingSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServingSize
        fields = '__all__'

    def validate(self, data):
        amount = data.get('amount')

        if amount is not None and amount < 0.01:
            raise serializers.ValidationError("Amount must be at least 0.01.")

        return data

class ItemSerializer(serializers.ModelSerializer):
    isFavorite = serializers.BooleanField(read_only=True)
    class Meta:
        model = Item
        fields = ["id", "name", "barcode", "calories", "servingSize", "isCustom", "user", "nutrients", "isFavorite"]

    def validate(self, data):
        calories = data.get('calories')

        if calories is not None and (calories < 0 or calories > 100000):
            raise serializers.ValidationError("Calories must be between 0 and 100000.")

        return data

class CombinedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CombinedItem
        fields = '__all__'

class ConsumedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumed
        fields = '__all__'

    def validate(self, data):
        portion = data.get('portion')
        item = data.get('item')
        combinedItem = data.get('combinedItem')

        if portion is not None and portion < 0:
            raise serializers.ValidationError("Portion must be greater than or equal to 0.")

        if not item and not combinedItem:
            raise serializers.ValidationError("You must provide an item or combined item.")

        if item and combinedItem:
            raise serializers.ValidationError("You may provide either an item or combined item, not both.")

        return data

class CombinedItemElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CombinedItemElement
        fields = '__all__'

    def validate(self, data):
        portion = data.get('portion')

        if portion is not None and portion < 0:
            raise serializers.ValidationError("Portion must be greater than or equal to 0.")

        return data

class ItemNutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemNutrient
        fields = '__all__'

    def validate(self, data):
        amount = data.get('amount')

        if amount is not None and amount < 0:
            raise serializers.ValidationError("Amount must be greater than or equal to 0.")

        return data

class ItemBioactiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemBioactive
        fields = '__all__'

    def validate(self, data):
        amount = data.get('amount')

        if amount is not None and amount < 0:
            raise serializers.ValidationError("Amount must be greater than or equal to 0.")

        return data

class FavoriteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteItem
        fields = '__all__'

class GoalTemplateNutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalTemplateNutrient
        fields = '__all__'

    def validate(self, data):
        recommendedValue = data.get('recommendedValue')

        if recommendedValue is not None and recommendedValue < 0:
            raise serializers.ValidationError("Recommended value must be greater than or equal to 0.")

        return data

class GoalTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalTemplate
        fields = '__all__'

class UserGoalNutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGoalNutrient
        fields = '__all__'

    def validate(self, data):
        targetValue = data.get('targetValue')

        if targetValue is not None and targetValue < 0:
            raise serializers.ValidationError("Target value must be greater than or equal to 0.")

        return data

class UserGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGoal
        fields = '__all__'

    def validate(self, data):
        if not data.get('isActive') and not UserGoal.objects.filter(user=data.get('user'), isActive=True).exists():
            raise serializers.ValidationError("One goal must be set as active.")

        return data
