from django.contrib import admin
from .models import NewsArticle, ArticleImage, Video, VideoAttendance, UserStory, EventAlbum, AlbumPhoto


class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 2
    fields = ('image', 'caption')


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'views_count', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ArticleImageInline]
    search_fields = ('title', 'content')
    list_editable = ('is_published',)
    date_hierarchy = 'created_at'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_live', 'is_recorded', 'requires_login', 'views_count', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_live', 'requires_login', 'is_recorded')
    search_fields = ('title', 'description')
    list_editable = ('is_live', 'requires_login')


@admin.register(VideoAttendance)
class VideoAttendanceAdmin(admin.ModelAdmin):
    list_display = ('video', 'user', 'watched_at')
    list_filter = ('video', 'watched_at')
    date_hierarchy = 'watched_at'


@admin.register(UserStory)
class UserStoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_alias', 'has_user_consent', 'is_published', 'created_at')
    list_filter = ('is_published', 'has_user_consent')
    list_editable = ('is_published',)
    search_fields = ('title', 'content', 'author_alias')
    date_hierarchy = 'created_at'


# ─── Event Album / Gallery Admin ─────────────────────────────────────────────

class AlbumPhotoInline(admin.TabularInline):
    model = AlbumPhoto
    extra = 3
    fields = ('image', 'caption', 'order')
    ordering = ('order',)


@admin.register(EventAlbum)
class EventAlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'photo_count', 'is_published', 'created_at')
    list_filter = ('is_published', 'event_date')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    inlines = [AlbumPhotoInline]
    search_fields = ('title', 'description')
    date_hierarchy = 'event_date'


@admin.register(AlbumPhoto)
class AlbumPhotoAdmin(admin.ModelAdmin):
    list_display = ('album', 'caption', 'order', 'uploaded_at')
    list_filter = ('album',)
    search_fields = ('caption', 'album__title')
