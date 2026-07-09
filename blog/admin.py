from django.contrib import admin
from .models import BlogCategory, BlogPost

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'status', 'is_featured', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['status', 'is_featured', 'category']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'
