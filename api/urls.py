from django.urls import path
from . import  views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register("books", views.BookViewSet, basename="post")

urlpatterns = router.urls

urlpatterns += [
    path('users/', views.AllUserList.as_view(),name='users'),
]