from django.urls import path
from django.contrib import admin
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register', views.register_user),
    path('login', views.login_user, name='login_user'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('clicks', views.click_events, name='click_events'),
    path('data/upload', views.upload_data),
    path('notifications/logs', views.notification_logs),
]
