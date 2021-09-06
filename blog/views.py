from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Category, Tag, Comment
from .forms import CommentForm

# from django.views.generic import ListView  # 리스트 형태의 뷰제공


class PostList(ListView):
    model = Post
    ordering = '-pk'
    paginate_by = 5
    # template_name = 'blog/post_list.html'  # post_list.html을 기본 설정으로 사용하도록 장고가 설계

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context


class PostDetail(DetailView):
    model = Post

# CBV 방식의 구현을 위해 주석 처리
# def index(request):
#     posts = Post.objects.all().order_by('-pk')
#
#     return render(
#         request,
#         'blog/post_list.html',
#         {
#             'posts': posts,
#         }
#     )

# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)
#
#     return render(
#         request,
#         'blog/single_page.html',
#         {
#             'post': post,
#         }
#     )

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] =CommentForm
        return context


class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):  # 테스트를 통과한 유저만 Post 생성하도록 체크하는 함수
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):  # override : form 입력 내용이 유효한지 확인하는 함수
        current_user = self.request.user    # 요청한 사용자
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user   # form.instance : PostCreate view에서 폼으로 채워진 인스턴스
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()  # tag 의 양쪽 공백 제거
                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t) # 만들거나 원래 있던 걸 그대로 가져오기
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)  # 만든 post에 tag를 추가
            return response
        else:
            return redirect('/blog/')  # login 사용자가 아닌 경우 redirect


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']
    template_name = 'blog/post_update_form.html'

    def dispatch(self, request, *args, **kwargs):  # 요청에 대해 get 또는 post방식 여부를 식별하는 역할, 권한있는 user인지 확인
        if request.user.is_authenticated and request.user == self.get_object().author:  # 하나의 post 가져오기 get_object()
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():  # 가져온 post 에 tag 가 있으면
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)     # 가져온 tag 를 리스트에 담기
            context['tags_str_default'] = ';'.join(tags_str_list)
        return context

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()  # object(post) 에 있는 tag 지우기 : tag 와 post 간의 연결을 끊어주기

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()  # tag 의 양쪽 공백 제거
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)
        return response


def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)          # slug와 같은 카테고리 가져오기
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category
        }
    )


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()  # post 와 연관된 tag 모두를 render 로 보내기

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'tag': tag
        }
    )


def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)  # DB에 저장 보류 : 아래의 채울 내용 때문
                comment.post = post
                comment.author = request.user
                comment.save()                             # 필요 내용이 채워졌으므로 DB에 저장
                return redirect(comment.get_absolute_url())
            return redirect(post.get_absolute_url())  # POST 가 아니거나 Form 이 valid 하지 않는 경우 post 로 redirect
    else:
        raise PermissionError


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):  # 요청에 대해 get 또는 post 방식 여부를 식별하는 역할, 권한있는 user 인지 확인
        if request.user.is_authenticated and request.user == self.get_object().author:  # 하나의 post 가져오기 get_object()
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post

    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied

class PostSearch(PostList):  # 클래스형에서는 pk인자를 받을 수 없음
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q']  # 클래스형에서는 pk인자를 받을 수 없으나, kwargs 를 활용해서 가능
        post_list = Post.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q) # 여러 필터를 걸기 위한 Q 사용 : title과 tag명 기준의 필터
        ).distinct()  # 중복 방지(title 때 한 번 tag 때 또 한 번 방지)
        return post_list

    def get_context_data(self, **kwargs):
        context = super(PostSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'
        return context

