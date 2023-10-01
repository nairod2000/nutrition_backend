from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password

from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition.models import User, Unit, Nutrient, ServingSize, Item, CombinedItem, Consumed, CombinedItemElement, ItemNutrient, ItemBioactive, FavoriteItem, GoalTemplate, GoalTemplateNutrient, UserGoal, UserGoalNutrient
from nutrition.utils.nutrition_utils import calculate_calories, calculate_macronutrients

from .permissions import IsAdminUserOrReadOnly
from .serializers import ChangePasswordSerializer, UserUpdateSerializer, UserSerializer, GroupSerializer, UnitSerializer, NutrientSerializer, ServingSizeSerializer, ItemSerializer, CombinedItemSerializer, ConsumedSerializer, CombinedItemElementSerializer, ItemNutrientSerializer, ItemBioactiveSerializer, FavoriteItemSerializer, GoalTemplateSerializer, GoalTemplateNutrientSerializer, UserGoalSerializer, UserGoalNutrientSerializer

### User Management ###

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

# Create User and Authenticate (sign up and log in)
class UserCreateAndAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data.get('password')
            hashed_password = make_password(password)
            serializer.validated_data['password'] = hashed_password
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            # Return user and token in the response
            return Response({'user': UserSerializer(user).data, 'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Retrieve and update the user's own profile information
class UserUpdateView(RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
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


### Goals ###

class UserGoalGenerateView(CreateAPIView):
    serializer_class = UserGoalSerializer
    queryset = UserGoal.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Get the user associated with the token
        user = request.user

        # Determine the GoalTemplate based on user attributes (sex, is_pregnant, is_lactating, age)
        goal_template = GoalTemplate.objects.filter(
            sex=user.sex,
            isPregnant=user.is_pregnant,
            isLactating=user.is_lactating,
            ageMin__lte=user.age,
            ageMax__gte=user.age
        ).first()

        if not goal_template:
            return Response({'detail': 'No suitable GoalTemplate found for the user.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the calories for the user
        calculated_calories = calculate_calories(user)
        nutrient_distribution = calculate_macronutrients(calculated_calories, user.age)

        # Try to get an existing UserGoal with the same name
        user_goal, created = UserGoal.objects.get_or_create(
            user=user,
            name=goal_template.name,
            defaults={
                'template': goal_template,
                'calories': calculated_calories
            }
        )

        # If the UserGoal was not created (already exists), update its attributes
        if not created:
            user_goal.template = goal_template
            user_goal.calories = calculated_calories
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
        headers = self.get_success_headers(serializer.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


### Model View Sets ###

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