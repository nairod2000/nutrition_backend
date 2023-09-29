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