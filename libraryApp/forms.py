from django import forms
from .models import Book
from .forms import Book

class formBook(forms.Form):

    isbn = forms.CharField(label='ISBN',min_length=4,max_length=13)
    
