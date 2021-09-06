from django.urls import path
from . import views

urlpatterns = [
    path('search/<str:q>/', views.PostSearch.as_view()),
    path('delete_comment/<int:pk>/', views.delete_comment),
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view()),
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('create_post/', views.PostCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),
    path('<int:pk>/new_comment/', views.new_comment),  # new_comment 함수에서 처리
    # path('<int:pk>/', views.single_post_page), --> FBV 방식에서 사용
    path('<int:pk>/', views.PostDetail.as_view()), # --> CBV 방식에서 사용
    # path('', views.index), --> FBV 방식에서 사용
    path('', views.PostList.as_view()),  # class PostList(ListView): 클래스를 사용하겠다는 의미
]