"""
Haystack の検索インデックス設定
django-haystack + Whoosh を使った全文検索インデックス
"""
from haystack import indexes
from .models import Book


class BookIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Book モデルの検索インデックス
    複数のフィールドをインデックス化して全文検索を実現
    """
    # text フィールドは全文検索に使われるメイン検索フィールド
    text = indexes.CharField(
        document=True,
        use_template=True,
        template_name='search/indexes/libraryapp/book_text.txt'
    )
    
    # 個別フィールドのインデックス（部分的な検索に対応）
    title = indexes.CharField(model_attr='title', indexed=True)
    writer = indexes.CharField(model_attr='writer', indexed=True)
    isbn = indexes.CharField(model_attr='isbn', indexed=True)
    
    # 日付フィールド（範囲検索に対応）
    publication_date = indexes.DateField(
        model_attr='publication_date',
        null=True,
        indexed=True
    )
    
    # オートコンプリート用
    title_auto = indexes.EdgeNgramField(model_attr='title')
    writer_auto = indexes.EdgeNgramField(model_attr='writer')

    def get_model(self):
        """検索対象のモデルを指定"""
        return Book

    def index_queryset(self, using=None):
        """インデックスに含むクエリセットの指定"""
        return self.get_model().objects.all()
    
    def get_updated_field(self):
        """更新可能なフィールド（オプション）"""
        return 'updated_at'  # モデルに updated_at フィールドがあれば指定
