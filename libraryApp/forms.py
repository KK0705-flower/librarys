from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['isbn', 'title', 'writer']  # ここを writer に変更！
        # フォームの見た目を整えるためのウィジェット設定（任意）
        widgets = {
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'id': 'manual-isbn'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'writer': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # --- ISBNのバリデーション ---
    def clean_isbn(self):
        # 送信されたデータからハイフンや空白を取り除く
        isbn = self.cleaned_data.get('isbn').replace('-', '').replace(' ', '')

        # 数字のみかチェック
        if not isbn.isdigit():
            raise forms.ValidationError("ISBNは数字のみで入力してください。")

        # 桁数チェック（10桁または13桁）
        if len(isbn) not in [10, 13]:
            raise forms.ValidationError(f"ISBNの桁数が正しくありません（現在は{len(isbn)}桁です）。")

        # 日本の書籍の開始番号チェック（任意）
        if len(isbn) == 13 and not (isbn.startswith('978') or isbn.startswith('979')):
            raise forms.ValidationError("日本の書籍ISBN（978または979開始）を入力してください。")

        return isbn

    # --- タイトルのバリデーション ---
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or title.strip() == "":
            raise forms.ValidationError("タイトルは必須入力です。")
        return title