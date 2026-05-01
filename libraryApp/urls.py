from django.urls import path
from . import views
urlpatterns = [
  path('top/', views.index, name='index'),
  path('book_search/', views.book_search, name='book_search'),
  path('book_register/', views.book_register, name='book_register'),
  path('checkout/<str:isbn>/', views.book_lenderItem, name='book_lenderItem'),
  path('register/success/', views.book_success, name='book_success'), 
  path('checkout/thanks/<int:lending_id>/', views.checkout_thanks, name='checkout_thanks'),
  path('my-books/', views.my_borrowed_books, name='my_borrowed_books'),
  path('book_readme/', views.book_readme, name='book_readme'),
  path('return/<int:lending_id>/', views.return_book, name='return_book'),
]