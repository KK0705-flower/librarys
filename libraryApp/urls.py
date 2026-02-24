from django.urls import path
from . import views

urlpatterns = [
    # ここに今後、スキャン画面などのパスを書いていきます
    path('book_register/', views.book_register, name='book_entry'),
]