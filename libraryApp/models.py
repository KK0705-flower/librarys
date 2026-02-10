from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from isbn_field import ISBNField

class Book(models.Model):
    """
    作品情報 (Book)
    ISBNを主キーとして管理します。
    """
    # ER図: isbn_id (PK)
    isbn = ISBNField()
    title = models.CharField(max_length=255, verbose_name="タイトル")
    writer = models.CharField(max_length=255, verbose_name="著者")
    publication_date = models.DateField(verbose_name="出版日")
    image = models.ImageField(upload_to='book_images/', blank=True, null=True, verbose_name="表紙画像")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "作品"
        verbose_name_plural = "作品一覧"


class BookItem(models.Model):
    """
    蔵書アイテム (bookItems)
    図書館にある「物理的な本」の1冊1冊を管理します。
    """
    # ER図: isbn_id (FK) -> Bookモデルへの紐づけ
    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE, 
        related_name='items', 
        verbose_name="作品"
    )
    purchase_date = models.DateField(verbose_name="購入日")
    price = models.PositiveIntegerField(verbose_name="価格")
    edition = models.CharField(max_length=50, blank=True, null=True, verbose_name="版数")

    def __str__(self):
        return f"{self.book.title} (ID: {self.id})"

    class Meta:
        verbose_name = "蔵書個体"
        verbose_name_plural = "蔵書個体一覧"


class Lending(models.Model):
    """
    貸出情報 (lending)
    「誰が」「どの個体を」借りているかを管理します。
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        verbose_name="利用者"
    )
    book_item = models.ForeignKey(
        BookItem, 
        on_delete=models.PROTECT, 
        verbose_name="貸出個体"
    )
    STATUS_CHOICES = [
        ('lending', '貸出中'),
        ('returned', '返却済み'),
    ]
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='lending', 
        verbose_name="状態"
    )
    
    lending_date = models.DateField(default=timezone.now, verbose_name="貸出日")
    due_date = models.DateField(null=True, blank=True, verbose_name="返却予定日")
    returned_date = models.DateField(null=True, blank=True, verbose_name="返却日")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.book_item.book.title}"

    class Meta:
        verbose_name = "貸出情報"
        verbose_name_plural = "貸出情報一覧"


class Reservation(models.Model):
    """
    予約 (Reservation) - パターンA
    在庫がない場合などに、「作品」に対して予約を入れます。
    """
    # ER図: isbn_id (FK) -> 「作品(Book)」への紐づけ (重要: 個体ではない)
    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE, 
        verbose_name="予約作品"
    )
    # ER図: user_id
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="予約者"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="予約日時")
    
    # 予約の状態管理
    STATUS_CHOICES = [
        ('active', '予約中'),
        ('completed', '貸出完了'),
        ('cancelled', 'キャンセル'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active', 
        verbose_name="予約状態"
    )

    def __str__(self):
        return f"予約: {self.book.title} ({self.user.username})"

    class Meta:
        verbose_name = "予約"
        verbose_name_plural = "予約一覧"