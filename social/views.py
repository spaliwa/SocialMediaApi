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
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

class MySimpleRateThrottle(SimpleRateThrottle):
    
    rate ='3/min'
    scope = None
    
    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None  

        return f'{self.scope}_{request.user.id}'

class MyObtainTokenPairView(TokenObtainPairView):
    '''
        Generate Login Token
    '''
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    '''
        Register User
    '''
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer 

class UserView(viewsets.ViewSet):


    def list(self, request):
        '''
        List All Users
        '''
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        serialized_data = serializer.data
        response_data = {}
        response_data = {f"user_{i+1}": user_data for i, user_data in enumerate(serialized_data)}
    
        return Response(response_data)
    

class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

class UserSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = UserPagination
    
    # def get(self, request,keyword):
    def get(self, request):
        '''
        Search Users
        '''
        keyword = request.GET.get('keyword', '')
        current_user=request.user
        self.keyword = keyword
        if keyword:
            if '@' in keyword:
                users = User.objects.filter(email__iexact=keyword).exclude(username=current_user)
            else:
                users = User.objects.filter(username__icontains=keyword).exclude(username=current_user)
        if not users:
            return Response("{'No results found'}")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(users, request)
       
        if page is not None:
            return paginator.get_paginated_response(self.serialize_user(user) for user in page)
    
        return Response(self.serialize_user(user) for user in users)
    
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
    '''
        Send Friend Request to other Users
    '''
    from_user = request.user
    to_user = User.objects.get(pk=pk)

    if Friendship.objects.filter(from_user=from_user, to_user=to_user):
        msg="{'error': 'Friend Request already sent'}"
        return Response(msg)
    friendship = Friendship.objects.create(from_user=from_user, to_user=to_user, status='pending')
    serializer = FriendshipSerializer(friendship)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def accept_friend_request(request, pk):
    '''
        Accept Friend Request of other Users
    '''
    try:
        friendship = Friendship.objects.get(pk=pk)
    except:
        return Response({'error': 'wrong request'}, status=status.HTTP_404_NOT_FOUND)
    if friendship.to_user != request.user:
        return Response({'error': 'You cannot accept a request you did not receive.'}, status=status.HTTP_403_FORBIDDEN)
    if friendship.status == 'accepted':
        return Response({'request': f'Already friend with {friendship.from_user.username}'}, status=status.HTTP_200_OK)
    friendship.status = 'accepted'
    friendship.save()
    msg=f"Accpeted request of {friendship.from_user.username}"
    return Response({'request': f'Accpeted request of {friendship.from_user.username}'}, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def reject_friend_request(request, pk):
    '''
        reject Friend Request of other Users
    '''

    try:
        friendship = Friendship.objects.get(pk=pk)
    except:
        return Response({'error': 'wrong request'}, status=status.HTTP_404_NOT_FOUND)
    
    if friendship.to_user != request.user:
        return Response({'error': 'You cannot reject a request you did not receive.'}, status=status.HTTP_403_FORBIDDEN)
    if friendship.status == 'accepted':
        return Response({'request': f'Friend with {friendship.from_user.username}'}, status=status.HTTP_200_OK)
    
    friendship.status = 'rejected'
    friendship.save()
    return Response({'request': f'Rejected request of {friendship.from_user.username}'},status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_friends(request):
    '''
        List All Friends of User
    '''
    user = request.user
    friends = Friendship.objects.filter(from_user=user, status='accepted') | Friendship.objects.filter(to_user=user, status='accepted')
    friends = friends.select_related('from_user', 'to_user')  
    if not friends:
            return Response("{'data':'No results found'}")
    serializer = FriendshipSerializer(friends, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_pending_friend_requests(request):
    '''
        List Pending Friend Request of other Users
    '''
    user = request.user
    requests = Friendship.objects.filter(to_user=user, status='pending')
    if not requests:
            return Response("No results found")
    serializer = FriendshipSerializer(requests, many=True)
    serialized_data = serializer.data
    
    return Response(serializer.data[0], status=status.HTTP_200_OK)
