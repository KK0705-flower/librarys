from django.urls import path
from . import views

urlpatterns = [
     path('top/', views.index, name='index'),
    path('book_search/', views.book_search, name='book_search'),
    path('book_register/', views.book_register, name='book_register'),
  path('checkout/<str:isbn>/', views.book_lenderItem, name='book_lenderItem'),
  path('checkout/thanks/<int:lending_id>/', views.checkout_thanks, name='checkout_thanks'),
]