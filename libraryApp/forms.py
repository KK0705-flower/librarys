from django import forms
from django.db.models import Q
from .models import Book
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="メールアドレス", widget=forms.TextInput(attrs={'placeholder': 'メールアドレスを入力してください'}))
    password = forms.CharField(label="パスワード", widget=forms.PasswordInput(attrs={'placeholder': 'パスワードを入力してください'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not (username and password):
            return super().clean()

    
        user_exists = User.objects.filter(username=username).exists()
        if not user_exists:
            self.add_error('username', "メールアドレスが間違っています。")
            # 存在しない場合はここで終了（パスワードチェックに進まない）
            return super().clean()

        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        if user is None:
            self.add_error('password', "パスワードが間違っています。")

        return super().clean()

class BookSearchForm(forms.Form):
    """から本を検索するためのフォーム"""

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
      widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'search-checkbox-group',
            'checked': 'checked' 
        })
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
    # 検索モードの選択肢を追加
    search_mode = forms.ChoiceField(
        choices=[
            ('partial', '部分一致'),
            ('exact', '完全一致'),
        ],
        initial='partial',
        widget=forms.RadioSelect(attrs={'class': 'search-mode-radio'}),
        label='検索モード'
        )

    def search_books(self):
        if not self.is_valid():
            return Book.objects.all()    
        query = self.cleaned_data.get('query', '').strip()
    # URLにない場合は空リストではなく、全項目を入れるように明示する
        search_types = self.cleaned_data.get('search_type') or ['title', 'writer', 'isbn']
        search_mode = self.cleaned_data.get('search_mode', 'partial')

        if not query:
            return Book.objects.all()

        q_objects = Q()
        lookup_suffix = '__icontains' if search_mode == 'partial' else '__iexact'

        for s_type in search_types:
            lookup = f"{s_type}{lookup_suffix}"
            q_objects |= Q(**{lookup: query})

        return Book.objects.filter(q_objects).distinct()