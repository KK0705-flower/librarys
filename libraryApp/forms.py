from django import forms
from django.db.models import Q
from .models import Book

class BookSearchForm(forms.Form):
    """本棚から本を検索するためのフォーム"""

    # ChoiceField -> MultipleChoiceField に変更
    search_type = forms.MultipleChoiceField(
        choices=[
            ('title', 'タイトル'),
            ('writer', '著者'),
            ('isbn', 'ISBN'),
        ],
        required=False,
        # 最初はすべてにチェックが入っている状態にする
        initial=['title', 'writer', 'isbn'],
        label='検索キーワード',
        # CheckboxSelectMultiple に変更
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'search-checkbox-group'})
    )

    query = forms.CharField(
        max_length=255, 
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ここに入力してください...',
            'autocomplete': 'off'
        })
    )

    def search_books(self):
        """フォームの入力内容に基づいてクエリセットをフィルタリングする"""
        if not self.is_valid():
            return Book.objects.all() # バリデーション失敗時は全件出すか、none()にする

        query = self.cleaned_data.get('query', '').strip()
        search_types = self.cleaned_data.get('search_type', [])
        
        # 基本のクエリセット
        results = Book.objects.all()

        # キーワードがある場合のみ絞り込み
        if query:
            q_objects = Q()
            
            # 選択されたタイプ（リスト）をループして OR 条件を作成
            if 'title' in search_types:
                q_objects |= Q(title__icontains=query)
            if 'writer' in search_types:
                q_objects |= Q(writer__icontains=query)
            if 'isbn' in search_types:
                q_objects |= Q(isbn__icontains=query)
            
            # もしチェックボックスが一つも選ばれていなければ、デフォルトで全項目から検索
            if not q_objects:
                q_objects = Q(title__icontains=query) | Q(writer__icontains=query) | Q(isbn__icontains=query)

            results = results.filter(q_objects)
        
        return results.distinct() # 重複を防ぐために distinct() を推奨
