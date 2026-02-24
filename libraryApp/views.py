from django.shortcuts import render, redirect 
from .models import Book
from .forms import BookForm
import re
import requests
from django.contrib import messages

def book_isbn(request):
    """スキャン画面を表示する"""
    return render(request, 'book_isbn.html')

def book_register(request):
    """書籍情報の取得と登録を行う"""
    # 1. 保存処理 (POST)
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "蔵書を登録しました！")
            return redirect('book_isbn') 
        else:
            messages.error(request, "入力内容に不備があります。")
    
    # 2. 検索・表示処理 (GET)
    else:
        isbn = request.GET.get('isbn', '').replace('-', '').strip()
        book_data = {'isbn': isbn, 'title': '', ' writer': ''}

        if isbn:
            # APIリクエスト
            url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            try:
                response = requests.get(url, timeout=5)
                data = response.json()

                if "items" in data:
                    volume_info = data["items"][0]["volumeInfo"]
                    book_data['title'] = volume_info.get("title", "")
                    writer = volume_info.get("writer", [])
                    book_data['writer'] = ", ".join(writer) if  writer else ""
                    messages.success(request, f"「{book_data['title']}」が見つかりました。")
                else:
                    messages.warning(request, "Google Booksにデータが見つかりませんでした。")
            except Exception as e:
                messages.error(request, f"APIエラーが発生しました: {e}")

        # 取得したデータ（または空のデータ）をフォームの初期値にする
        form = BookForm(initial=book_data)
        # 画像URLをテンプレートで使いやすいように個別で渡す
        return render(request, 'book_register.html', {
            'form': form, 
            'cover_url': book_data.get('cover_url')
        })


    return render(request, 'book_register.html', {'form': form})