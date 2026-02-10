from django.shortcuts import render
from .models import  formBook
# Create your views here.


def bookInsent(request, isbn):

    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    form = formbook()
