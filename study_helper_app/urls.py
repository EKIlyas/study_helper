from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.CartListView.as_view(), name='main'),
    path('create/', views.CartCreateView.as_view(), name='create_cart'),
    path('cart/update/<int:pk>/', views.CartUpdateView.as_view(), name='update_cart'),
    path('cart/delete/<int:pk>/', views.CartDeleteView.as_view(), name='delete_cart'),
    path('category/create/', views.CategoryCreateView.as_view(), name='create_category'),
    path('practice/<int:pk>/', views.PracticeView.as_view(), name='practice'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main'), name='logout'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]
