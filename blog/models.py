from django.db import models
from django.contrib.auth.models import User
import os

from markdownx.models import MarkdownxField
from markdownx.utils import markdown
from datetime import timedelta


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)  # slug : 이해할 수 있도록 글자로 분류 구분

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'   # slug를 이용해서 url 생성

    class Meta:
        verbose_name_plural = 'Categories'  # category 복수형 표시


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)  # slug : 이해할 수 있도록 글자로 분류 구분

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'   # slug를 이용해서 url 생성


class Post(models.Model):
    title = models.CharField(max_length=50)
    hook_text = models.CharField(max_length=100, blank=True)

    # content = models.TextField()   # Markdown 사용하기 이전 코드
    content = MarkdownxField()
    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now= True)
    # author: 추추 작성 예정
    # author = models.ForeignKey(User, on_delete=models.CASCADE) # cascade 옵션 사용 시
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'[{self.pk}] {self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):   # 사용자가 정의한 함수 : 업로드 파일명 가져오기
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):  # 사용자가 정의한 함수 : 업로드 파일의 확장자 가져오기
        return self.get_file_name().split('.')[-1]

    def get_content_markdown(self):   # 사용자 정의 함수
        return markdown(self.content)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/143/e3445497d896a175/svg/{self.author.email}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        # return self.post.get_absolute_url()  # 변경 전 : 해당 페이지 상단으로 표시
        return f'{self.post.get_absolute_url()}#comment-{self.pk}' # 변경 후 : 해당 코멘트를 표시

    def is_updated(self):
        return self.updated_at - self.created_at > timedelta(seconds=1)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/143/e3445497d896a175/svg/{self.author.email}'


