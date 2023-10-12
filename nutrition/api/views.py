from datetime import date

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404


from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition.models import User, Unit, Nutrient, ServingSize, Item, CombinedItem, Consumed, CombinedItemElement, ItemNutrient, ItemBioactive, FavoriteItem, GoalTemplate, GoalTemplateNutrient, UserGoal, UserGoalNutrient
from nutrition.utils.nutrition_utils import calculate_calories, calculate_macronutrients, serialize_goal_nutrients

from .permissions import IsAdminUserOrReadOnly
from .serializers import ChangePasswordSerializer, UserRetrieveUpdateSerializer, UserGoalIDSerializer , UserSerializer, GroupSerializer, UnitSerializer, NutrientSerializer, ServingSizeSerializer, ItemSerializer, CombinedItemSerializer, ConsumedSerializer, CombinedItemElementSerializer, ItemNutrientSerializer, ItemBioactiveSerializer, FavoriteItemSerializer, GoalTemplateSerializer, GoalTemplateNutrientSerializer, UserGoalSerializer, UserGoalNutrientSerializer, NutrientStatusSerializer


#######################
### User Management ###
#######################

# Create User (sign up)
class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        password = serializer.validated_data.get('password')
        hashed_password = make_password(password)
        serializer.validated_data['password'] = hashed_password
        serializer.save()

# Retrieve and update the user's own profile information
class UserRetrieveUpdateView(RetrieveUpdateAPIView):
    serializer_class = UserRetrieveUpdateSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the currently authenticated user
        return self.request.user

# Change Password
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user)  # To update session after password change
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#######################
######## Goals ########
#######################

class UserGoalGenerateView(CreateAPIView):
    serializer_class = UserGoalSerializer
    queryset = UserGoal.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Get the user associated with the token
        user = request.user

        # Default values for undefined User attributes
        sex = user.sex or 'Male'
        age = user.age or 30
        is_pregnant = user.is_pregnant or False
        is_lactating = user.is_lactating or False

        # Determine the GoalTemplate based on user attributes (sex, is_pregnant, is_lactating, age)
        goal_template = GoalTemplate.objects.filter(
            sex=sex,
            isPregnant=is_pregnant,
            isLactating=is_lactating,
            ageMin__lte=age,
            ageMax__gte=age
        ).first()

        if not goal_template:
            return Response({'detail': 'No suitable GoalTemplate found for the user.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the calories for the user
        # Check if any of the required fields required for calorie calculation is None or empty
        calorie_required_fields = ['age', 'weight', 'height', 'sex', 'activity_level']
        if any(getattr(user, field, None) is None or getattr(user, field) == '' for field in calorie_required_fields):
            calories = 2000
        else:
            calories = calculate_calories(user)
        
        # Calculate the macronutrient distribution for the user
        nutrient_distribution = calculate_macronutrients(calories, age)

        # Try to get an existing UserGoal with the same name
        user_goal, created = UserGoal.objects.get_or_create(
            user=user,
            name=(goal_template.name if user.sex else 'Nutritional Goal'),
            defaults={
                'template': goal_template,
                'calories': calories
            }
        )

        # If the UserGoal was not created (already exists), update its attributes
        if not created:
            user_goal.template = goal_template
            user_goal.calories = calories
            user_goal.save()

        # Copy GoalTemplateNutrients to UserGoalNutrients
        goal_template_nutrients = goal_template.goaltemplatenutrient_set.all()
        for nutrient in goal_template_nutrients:
            user_goal_nutrient, created = UserGoalNutrient.objects.get_or_create(
                goal=user_goal,
                nutrient=nutrient.nutrient,
                defaults={'targetValue': nutrient.recommendedValue}
            )

        # If the UserGoalNutrient was not created (already exists), update the targetValue
        if not created:
            user_goal_nutrient.targetValue = nutrient.recommendedValue
            user_goal_nutrient.save()


        # Create or modify UserGoalNutrients for Carbohydrate, Fat, and Protein
        for nutrient_name, target_value in nutrient_distribution.items():
            nutrient, _ = Nutrient.objects.get_or_create(name=nutrient_name)
            user_goal_nutrient, _ = UserGoalNutrient.objects.get_or_create(
                goal=user_goal,
                nutrient=nutrient,
                defaults={'targetValue': target_value}
            )
        # If the UserGoalNutrient already exists, update the targetValue
        if not user_goal_nutrient._state.adding:
            user_goal_nutrient.targetValue = target_value
            user_goal_nutrient.save()

        # Serialize the UserGoal object
        serializer = self.get_serializer(user_goal)
        response_data = serializer.data

        # Serialize and add goal nutrients to the response
        response_data["nutrients"] = serialize_goal_nutrients(user_goal)

        return Response(response_data, status=status.HTTP_201_CREATED)
        
class UserGoalRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = UserGoal.objects.all()
    serializer_class = UserGoalSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user_goal_serializer = self.get_serializer(instance).data

        # Serialize and add goal nutrients to the response
        user_goal_serializer["nutrients"] = serialize_goal_nutrients(instance)

        return Response(user_goal_serializer)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Update 'calories'
        if 'calories' in request.data:
            new_calories = request.data['calories']
            instance.calories = new_calories

            # If user age is defined, update the macronutrient distribution based on the new calories
            if instance.user.age is not None and instance.user.age != '':
                nutrient_distribution = calculate_macronutrients(new_calories, instance.user.age)
                for nutrient_name, target_value in nutrient_distribution.items():
                    nutrient, _ = Nutrient.objects.get_or_create(name=nutrient_name)
                    user_goal_nutrient, created = UserGoalNutrient.objects.get_or_create(
                        goal=instance,
                        nutrient=nutrient,
                        defaults={'targetValue': target_value}
                    )

                    # If the UserGoalNutrient was not created (already exists), update the targetValue
                    if not created:
                        user_goal_nutrient.targetValue = target_value
                        user_goal_nutrient.save()

        # Check if 'isActive' field is being updated
        if 'isActive' in request.data:
            activating = request.data['isActive']
            if activating:
                # Activate the goal and deactivate other goals for the same user
                UserGoal.objects.filter(user=instance.user).exclude(pk=instance.pk).update(isActive=False)
                instance.isActive = activating
                instance.save()
            else: # Attempting to deactivate the goal
                # Prevent deactivating the goal.
                raise ValidationError("To deactivate this goal, set another goal as active.")

        # Serialize and add goal nutrients to the response
        serialized_data = serializer.data
        serialized_data["nutrients"] = serialize_goal_nutrients(instance)

        return Response(serialized_data)

class UserGoalsListView(ListAPIView):
    serializer_class = UserGoalIDSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # Retrieve a list of the user's goals
    def get_queryset(self):
        user = self.request.user
        return user.usergoal_set.all()

class UserActiveGoalView(RetrieveAPIView):
    serializer_class = UserGoalIDSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # Retrieve the user's active goal ID
    def get_object(self):
        user = self.request.user
        active_goal = user.usergoal_set.filter(isActive=True).first()
        return active_goal


#############################
### Daily Nutrient Totals ###
#############################

class GoalNutrientStatusView(APIView):
    def get(self, request):
        user = request.user
        user_active_goal = UserGoal.objects.filter(user=user, isActive=True).first()

        if user_active_goal:
            goal_nutrients = user_active_goal.usergoalnutrient_set.all()
            
            # Get all consumed items for the user for the current date
            consumed_items = Consumed.objects.filter(
                user=user,
                consumedAt__date=date.today()
            )
            
            # Calculate total consumed calories
            total_consumed_calories = consumed_items.aggregate(
                total_consumed_calories=Sum(F('item__calories') * F('portion'))
            )['total_consumed_calories'] or 0

            # Create a list of nutrient status objects and add the calories
            nutrient_status = [
                {
                    "nutrient_id": 999,  # Arbitrary ID for calories
                    "nutrient_name": "Calories",
                    "nutrient_unit": "kcal",
                    "target_value": user_active_goal.calories,
                    "total_consumed": total_consumed_calories,
                }
            ]

            for goal_nutrient in goal_nutrients:
                # Filter consumed items containing the goal nutrient
                consumed_items_with_nutrient = consumed_items.filter(
                    item__itemnutrient__nutrient=goal_nutrient.nutrient
                )

                # Calculate total consumed nutrient
                total_consumed_nutrient = consumed_items_with_nutrient.aggregate(
                    total_consumed=Sum(F('portion') * F('item__itemnutrient__amount'))
                )['total_consumed'] or 0

                # Append the nutrient status to the list
                nutrient_status.append({
                    "nutrient_id": goal_nutrient.nutrient.id,
                    "nutrient_name": goal_nutrient.nutrient.name,
                    "nutrient_unit": goal_nutrient.nutrient.unit.abbreviation,
                    "target_value": goal_nutrient.targetValue,
                    "total_consumed": total_consumed_nutrient,
                })

            # Serialize the nutrient status
            serializer = NutrientStatusSerializer(nutrient_status, many=True)
            return Response(serializer.data)
        else:
            return Response({'message': 'No active goal found for the user.'}, status=status.HTTP_404_NOT_FOUND)


#######################
### Model View Sets ###
#######################

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class NutrientViewSet(viewsets.ModelViewSet):
    queryset = Nutrient.objects.all()
    serializer_class = NutrientSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class ServingSizeViewSet(viewsets.ModelViewSet):
    queryset = ServingSize.objects.all()
    serializer_class = ServingSizeSerializer
    permission_classes = [IsAuthenticated]

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

class CombinedItemViewSet(viewsets.ModelViewSet):
    queryset = CombinedItem.objects.all()
    serializer_class = CombinedItemSerializer
    permission_classes = [IsAuthenticated]

class ConsumedViewSet(viewsets.ModelViewSet):
    queryset = Consumed.objects.all()
    serializer_class = ConsumedSerializer
    permission_classes = [IsAuthenticated]

class CombinedItemElementViewSet(viewsets.ModelViewSet):
    queryset = CombinedItemElement.objects.all()
    serializer_class = CombinedItemElementSerializer
    permission_classes = [IsAuthenticated]

class ItemNutrientViewSet(viewsets.ModelViewSet):
    queryset = ItemNutrient.objects.all()
    serializer_class = ItemNutrientSerializer
    permission_classes = [IsAuthenticated]

class ItemBioactiveViewSet(viewsets.ModelViewSet):
    queryset = ItemBioactive.objects.all()
    serializer_class = ItemBioactiveSerializer
    permission_classes = [IsAuthenticated]

class FavoriteItemViewSet(viewsets.ModelViewSet):
    queryset = FavoriteItem.objects.all()
    serializer_class = FavoriteItemSerializer
    permission_classes = [IsAuthenticated]

class GoalTemplateViewSet(viewsets.ModelViewSet):
    queryset = GoalTemplate.objects.all()
    serializer_class = GoalTemplateSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class GoalTemplateNutrientViewSet(viewsets.ModelViewSet):
    queryset = GoalTemplateNutrient.objects.all()
    serializer_class = GoalTemplateNutrientSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class UserGoalViewSet(viewsets.ModelViewSet):
    queryset = UserGoal.objects.all()
    serializer_class = UserGoalSerializer
    permission_classes = [IsAuthenticated]

class UserGoalNutrientViewSet(viewsets.ModelViewSet):
    queryset = UserGoalNutrient.objects.all()
    serializer_class = UserGoalNutrientSerializer
    permission_classes = [IsAuthenticated]