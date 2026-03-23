import requests
import re
import re
from django.utils.dateparse import parse_date
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import transaction
from django.views.decorators.http import require_POST
from .models import Book, Lending, BookItem
from .forms import BookSearchForm
from django.core.files.base import ContentFile


def index(request):
    # .order_by('?') でランダムに並び替え、最初の1件 (.first()) を取得
    random_book = Book.objects.order_by('?').first()
    
    return render(request, 'index.html', {
        'featured_book': random_book
    })

def book_search(request):
    """Book モデルの全文検索ビュー"""
    form = BookSearchForm(request.GET or None)
    search_results = None
    query = ''
    
    if form.is_valid():
        search_results = form.search_books()
        query = form.cleaned_data.get('query', '')
        
        # ページング処理
        if search_results:
            paginator = Paginator(search_results, 10)
            page = request.GET.get('page')
            search_results = paginator.get_page(page)
            
            if query:
                messages.info(request, f'「{query}」で{paginator.count}件の本が見つかりました。')
    
    context = {
        'form': form,
        'search_results': search_results,
        'query': query,
    }
    return render(request, 'book_search.html', context)

def book_register(request):
    """APIから本を取得し、DBに登録するビュー"""
    book_data = None 
    isbn = request.GET.get('isbn')
    api_key = getattr(settings, 'GOOGLE_BOOKS_API_KEY', settings.SECRET_KEY)

    # 1. 【GET処理】検索
    if isbn:
        clean_isbn = isbn.replace('-', '').strip()
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{clean_isbn}&key={api_key}"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            if data.get("totalItems", 0) > 0:
                volume_info = data["items"][0]["volumeInfo"]
                image_links = volume_info.get("imageLinks", {})
                raw_url = image_links.get("thumbnail", "")
                book_data = {
                    'isbn': clean_isbn,
                    'title': volume_info.get("title", "タイトル不明"),
                    'writer': ", ".join(volume_info.get("authors", [])) or "著者不明",
                    'cover_url': raw_url.replace("http://", "https://") if raw_url else "",
                    'published_date': volume_info.get("publishedDate", "出版日不明")
                }
            else:
                messages.warning(request, f"ISBN: {clean_isbn} に該当する本は見つかりませんでした。")
        except Exception as e:
            messages.error(request, f"API通信エラー: {e}")

    # 2. 【POST処理】登録実行
    if request.method == 'POST':
        isbn_val = request.POST.get('isbn', '').replace('-', '').strip()
        title = request.POST.get('title', '').strip()
        writer = request.POST.get('writer', '').strip()
        publication_date_raw = request.POST.get('book-publication-date', '').strip()
        image_url = request.POST.get('image_url', '').strip()

        # 🚨 【バリデーション1】必須チェック
        if not isbn_val or not title:
            messages.error(request, "ISBNとタイトルは必須項目です。")
            return redirect(f"{request.path}?isbn={isbn_val}")

        # 🚨 【バリデーション2】重複チェック
       # 🚨 【バリデーション2】重複チェック
        if Book.objects.filter(isbn=isbn_val).exists():
            messages.warning(request, f"「{title}」はすでに登録されています！")
            # パラメータを付けずにリダイレクトすることで、初期の検索画面に戻る
            return redirect('book_register')

        # 日付補正の強化
        formatted_date = None
        if publication_date_raw and publication_date_raw != "出版日不明":
            # 数字とハイフン以外を除去
            temp_date = re.sub(r'[^0-9-]', '', publication_date_raw)
            if len(temp_date) == 4: temp_date += "-01-01"
            elif len(temp_date) == 7: temp_date += "-01"
            
            if parse_date(temp_date): # 正しい日付形式か検証
                formatted_date = temp_date

        try:
            with transaction.atomic():
                # 重複がないことが確定しているので .create で作成
                book = Book.objects.create(
                    isbn=isbn_val,
                    title=title[:200], # 文字数制限対策
                    writer=writer[:200],
                    image_url=image_url,
                    publication_date=formatted_date
                )

                # BookItem（在庫・個体）の作成
                BookItem.objects.get_or_create(book=book, defaults={'price': 0})

                messages.success(request, f'「{title}」を本棚に登録しました！')
                return redirect('index')

        except Exception as e:
            print(f"Error: {e}") # ログ出力
            messages.error(request, f"データベース登録中にエラーが発生しました。")
            return redirect(f"{request.path}?isbn={isbn_val}")

    return render(request, 'book_register.html', {'book': book_data, 'isbn': isbn})

@require_POST
def book_lenderItem(request, isbn):
    """実際に貸し出し処理を行うビュー"""
    book = get_object_or_404(Book, isbn=isbn)
    
    with transaction.atomic():
        items = BookItem.objects.filter(book=book)
        
        if not items.exists():
            from django.http import HttpResponse
            return HttpResponse(f"エラー：BookItem（蔵書個体）が登録されていません。ISBN:{isbn}")

        target_item = None
        for item in items:
            is_lending = Lending.objects.filter(
                book_item=item, 
                returned_date__isnull=True
            ).exists()
            
            if not is_lending:
                target_item = item
                break

        if not target_item:
            from django.http import HttpResponse
            return HttpResponse("エラー：全ての個体が貸出中と判断されました。")

        due_date_str = request.POST.get('due_date')

        try:
            lending = Lending.objects.create(
                user=request.user if request.user.is_authenticated else None,
                book_item=target_item,
                status='lending',
                lending_date=timezone.now(),
                due_date=due_date_str if due_date_str else None
            )
            return redirect('checkout_thanks', lending_id=lending.id)
            
        except Exception as e:
            from django.http import HttpResponse
            return HttpResponse(f"保存失敗：{e}") 


def checkout_thanks(request, lending_id):
    """貸出完了画面"""
    lending = get_object_or_404(Lending, id=lending_id)
    book = lending.book_item.book
    location = getattr(lending.book_item, 'location', '999階 自動販売機前 25番棚')

    return render(request, 'checkout_thanks.html', {
        'lending': lending,
        'book': book,
        'location': location
    })