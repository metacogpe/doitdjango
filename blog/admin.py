from django.contrib import admin
from .models import Post, Category, Tag, Comment

admin.site.register(Post)
# admin.site.register(Category)  # Slug기능 사용 전
admin.site.register(Comment)


# Slug 기능 사용
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
