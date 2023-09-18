from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password

from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from nutrition.models import Unit, Nutrient, ServingSize, Item, CombinedItem, Consumed, CombinedItemElement, ItemNutrient, ItemBioactive, NutritionalGoalTemplate, GoalTemplateNutrient, UserNutritionalGoal

from .permissions import IsAdminUserOrReadOnly
from .serializers import ChangePasswordSerializer, UserUpdateSerializer, UserSerializer, GroupSerializer, UnitSerializer, NutrientSerializer, ServingSizeSerializer, ItemSerializer, CombinedItemSerializer, ConsumedSerializer, CombinedItemElementSerializer, ItemNutrientSerializer, ItemBioactiveSerializer, NutritionalGoalTemplateSerializer, GoalTemplateNutrientSerializer, UserNutritionalGoalSerializer

### User Management ###

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

# Create User (sign up)
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    def perform_create(self, serializer):
        password = serializer.validated_data.get('password')
        hashed_password = make_password(password)
        serializer.validated_data['password'] = hashed_password
        serializer.save()

# Retrieve and update the user's own profile information
class UserUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the currently authenticated user
        return self.request.user

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

class NutritionalGoalTemplateViewSet(viewsets.ModelViewSet):
    queryset = NutritionalGoalTemplate.objects.all()
    serializer_class = NutritionalGoalTemplateSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class GoalTemplateNutrientViewSet(viewsets.ModelViewSet):
    queryset = GoalTemplateNutrient.objects.all()
    serializer_class = GoalTemplateNutrientSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class UserNutritionalGoalViewSet(viewsets.ModelViewSet):
    queryset = UserNutritionalGoal.objects.all()
    serializer_class = UserNutritionalGoalSerializer
    permission_classes = [IsAuthenticated]