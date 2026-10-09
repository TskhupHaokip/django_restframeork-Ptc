from django.contrib import admin
from django.urls import path, include
from api.views import CreateUserView,UserLogoutView
from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/register/', CreateUserView.as_view(),name='register'),
    path('api/users/login/', TokenObtainPairView.as_view(),name='login'),
    path('api/users/refresh/', TokenRefreshView.as_view(),name='refresh'),
    path('api/', include('api.urls')),
    path('api/users/logout/', UserLogoutView.as_view(),name='logout'),

]
