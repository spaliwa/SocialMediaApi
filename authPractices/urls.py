from django.contrib import admin
from django.urls import path, include
# from .views import ProductViewSet, ImageViewSet
from rest_framework.routers import DefaultRouter
from social import views

from social.views import MyObtainTokenPairView, RegisterView, UserView, UserSearchView
from rest_framework_simplejwt.views import TokenRefreshView

from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView


router = DefaultRouter()
# router.register(r'product', ProductViewSet, basename='Product')
# router.register(r'image', ImageViewSet, basename='Image')

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('auth/', include('auth.urls')),
    # path('', include(router.urls)),
]


urlpatterns += [
    path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('users/',UserView.as_view({'get':'list'}),name="list_users"),
    path('friend/accept_friend_request/<int:pk>',views.accept_friend_request),
    path('friend/reject_friend_request/<int:pk>',views.reject_friend_request),
    path('friend/list_friends',views.list_friends),
    path('friend/list_pending_requests',views.list_pending_friend_requests),
    path('friend/send_friend_request/<int:pk>',views.send_friend_request),
    # path('user/List_user/<str:keyword>', UserSearchView.as_view(), name='list_user'),
    path('user/List_user/', UserSearchView.as_view(), name='list_user'),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    

]