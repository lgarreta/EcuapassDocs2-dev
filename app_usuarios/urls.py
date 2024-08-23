from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views

# Custom login view
from .views import CustomLoginView, get_country_for_username

urlpatterns = [
    path('registration/', views.registration, name='registration'),
    #path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout-post.html'), name='logout'),

    path('', views.user_list, name='usuarios'),
    path('listar/', views.user_list, name='listar'),
    path('crear/', views.UserCreate.as_view(), name='crear'),
    path('actualizar/<pk>', views.UserUpdate.as_view(), name='actualizar'),
    path('eliminar/<pk>', views.UserDelete.as_view(), name='eliminar'),
	path('get-country/', get_country_for_username, name='get_country_for_username'),
]
