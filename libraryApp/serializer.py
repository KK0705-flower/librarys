import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    # タイトルと著者名を「部分一致（contains）」で検索できるようにする
    title = django_filters.CharFilter(lookup_expr='icontains', label='タイトル')
    author = django_filters.CharFilter(lookup_expr='icontains', label='著者名')
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn'] # 完全一致で良ければここに追加する