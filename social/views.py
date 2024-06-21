from .serializers import MyTokenObtainPairSerializer, UserSerializer, FriendshipSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets
from django.contrib.auth.models import User
from social.models import Friendship
from .serializers import RegisterSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes,throttle_classes
# from django_ratelimit.decorators import ratelimit
# from .ratelimitdecorator import rate_limit
from rest_framework.throttling import UserRateThrottle,SimpleRateThrottle

class MySimpleRateThrottle(SimpleRateThrottle):
    THROTTLE_RATES = "'user': '3/min'"



class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer 

class UserView(viewsets.ViewSet):

    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
    

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
# @ratelimit(key='user',rate= "3/m" )
# @rate_limit(3,60)UserRateThrottle
@throttle_classes([MySimpleRateThrottle])
def send_friend_request(request, pk):
    from_user = request.user
    to_user = User.objects.get(pk=pk)

    # Check if request already exists or exceeds rate limit (implementation left as exercise)
    # ...

    friendship = Friendship.objects.create(from_user=from_user, to_user=to_user, status='pending')
    serializer = FriendshipSerializer(friendship)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def accept_friend_request(request, pk):
    friendship = Friendship.objects.get(pk=pk)
    if friendship.to_user != request.user:
        return Response({'error': 'You cannot accept a request you did not receive.'}, status=status.HTTP_403_FORBIDDEN)

    friendship.status = 'accepted'
    friendship.save()
    serializer = FriendshipSerializer(friendship)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def reject_friend_request(request, pk):
    friendship = Friendship.objects.get(pk=pk)
    if friendship.to_user != request.user:
        return Response({'error': 'You cannot reject a request you did not receive.'}, status=status.HTTP_403_FORBIDDEN)

    friendship.status = 'rejected'
    friendship.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_friends(request):
    user = request.user
    friends = Friendship.objects.filter(from_user=user, status='accepted') | Friendship.objects.filter(to_user=user, status='accepted')
    friends = friends.select_related('from_user', 'to_user')  # Optimize query
    serializer = FriendshipSerializer(friends, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_pending_friend_requests(request):
    user = request.user
    requests = Friendship.objects.filter(to_user=user, status='pending')
    print(Friendship.objects.all().values())
    serializer = FriendshipSerializer(requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
