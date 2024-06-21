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

from rest_framework.throttling import SimpleRateThrottle

class MySimpleRateThrottle(SimpleRateThrottle):
    # THROTTLE_RATES = super(self).THROTTLE_RATES = "'user': '3/min'"
    rate ='3/min'
    scope = None
    
    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None  # Only authenticated users are throttled

        return f'{self.scope}_{request.user.id}'




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
    
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_friends(request, search):
    from_user = request.user
    if search == 1:pass
    serializer = Friendship.objects.all().filter(from_user=from_user,status='accepted')
    return Response(serializer.data, status=status.HTTP_201_CREATED)


from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

class UserSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = UserPagination
    

    def get(self, request,keyword):
        current_user=request.user
        self.keyword = keyword
        print(current_user,"888**")
        if keyword:
            if '@' in keyword:
                users = User.objects.filter(email__iexact=keyword).exclude(username=current_user)
            else:
                users = User.objects.filter(username__icontains=keyword).exclude(username=current_user)
        # else:
        #     users = User.objects.none()

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(users, request)

        if page is not None:
            return paginator.get_paginated_response([self.serialize_user(user) for user in page])

        return Response([self.serialize_user(user) for user in users])
        

    def serialize_user(self, user):
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }    
    

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([MySimpleRateThrottle])
def send_friend_request(request, pk):
    from_user = request.user
    to_user = User.objects.get(pk=pk)

    # Check if request already exists or exceeds rate limit (implementation left as exercise)
    # ...
    if Friendship.objects.filter(from_user=from_user, to_user=to_user):
        msg="{'error': 'Friend Request already sent'}"
        return Response(msg)
    friendship = Friendship.objects.create(from_user=from_user, to_user=to_user, status='pending')
    serializer = FriendshipSerializer(friendship)
    return Response(serializer.data, status=status.HTTP_200_OK)

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
