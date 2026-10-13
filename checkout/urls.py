from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_view, name='menu'),
    path('add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('rewards/', views.rewards_login, name='rewards_login'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('confirmation/<int:order_id>/', views.confirmation_view, name='confirmation'),
    path('logout/', views.logout_view, name='logout'),
]