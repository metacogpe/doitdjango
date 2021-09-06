from time import sleep
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag, Comment
from django.contrib.auth.models import User
# Create your tests here.


class TestView(TestCase):
    def setUp(self):  # 테스트하기 전에 DB비우기를 먼저하고 기본 데이터 채우기를 시행
        self.client = Client()
        self.user_trump = User.objects.create_user(
            username='trump',
            password='somepassword'
        )
        self.user_obama = User.objects.create_user(
            username='obama',
            password='somepassword'
        )
        self.user_obama.is_staff = True
        self.user_obama.save()

        self.category_programming = Category.objects.create(
            name='programming', slug='programming'
        )
        self.category_music = Category.objects.create(
            name='music', slug='music'
        )

        self.tag_python_kor = Tag.objects.create(
            name='파이썬 공부', slug='파이썬-공부'
        )
        self.tag_python = Tag.objects.create(
            name='python', slug='python'
        )
        self.tag_hello = Tag.objects.create(
            name='hello', slug='hello'
        )

        # post_list_test()에 있던 post_list를 이동
        self.post_001 = Post.objects.create(
            title='첫 번째 포스트 입니다.',
            content='Hello, World. We are the world.',
            category=self.category_programming,
            author=self.user_trump
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트 입니다.',
            content='저는 쌀국수를 좋아합니다.',
            category=self.category_music,
            author=self.user_obama
        )
        self.post_003 = Post.objects.create(
            title='세 번째 포스트 입니다.',
            content='Category가 없을 수도 있죠.',
            author=self.user_obama
        )
        # post3에 2개의 tag
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)

        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_obama,
            content='첫 번째 댓글입니다.'

        )

    def navbar_test(self, soup):  # 내부에서 사용하기 위해 생성 : test_post_list()함수 와 test_post_detail()함수에서 사용
        # 1.4 네비게이션 바가 있다.
        navbar = soup.nav
        # 1.5 Blog, About me 라는 문구가 navabar에 있다.
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

        logo_btn = navbar.find('a', text='Do it Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def category_card_test(self, soup):     # 내부 함수이므로 test_ 로 시작하지 않고, soup을 받아서 찾는 형태로 테스트
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)       # Categories 문구 존재 확인
        self.assertIn(
            f'{self.category_programming} ({self.category_programming.post_set.count()})',
            categories_card.text
        )  # programming 카테고리의 포스트 갯수 확인
        self.assertIn(
            f'{self.category_music} ({self.category_music.post_set.count()})',
            categories_card.text
        )  # music 카테고리의 포스트 갯수 확인
        self.assertIn(
            f'미분류 ({Post.objects.filter(category=None).count()})',
            categories_card.text
        )

    def test_post_list_with_posts(self):   # 기존 test_post_list(self) 함수 이름 변경 -> post가 없는 상황에 대한 테스트
        self.assertEqual(Post.objects.count(), 3)   # 게시물이 3개 존재

        # 1.1 포스트 목록 페이지(post list)를 연다.
        response = self.client.get('/blog/')
        # 1.2 정상적으로 페이지가 로드된다.
        self.assertEqual(response.status_code, 200)
        # 1.3 페이지의 타이틀에 Blog라는 문구가 있다.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn('Blog', soup.title.text)

        # 1.4 네비게이션 바가 있다.
        self.navbar_test(soup)  # navbar_test(self, soup) 함수를 호출하여 수행

        # category card 테스트
        self.category_card_test(soup)

        # 아래의 post_001과 post_002를 def setUp(self) 으로 이동
        # 3.1 만약 게시물이 2개 있다면,
        # post_001 = Post.objects.create(
        #     title='첫 번째 포스트 입니다.',
        #     content='Hello, World. We are the world.',
        #     author=self.user_trump
        # )
        # post_002 = Post.objects.create(
        #     title='두 번째 포스트 입니다.',
        #     content='저는 쌀국수를 좋아합니다.',
        #     author=self.user_obama
        # )

        self.assertEqual(Post.objects.count(),3)

        # 3.2 포스트 목록 페이지를 새로 고침했을 때,
        # response = self.client.get('/blog/')
        # soup = BeautifulSoup(response.content, 'html.parser')

        # 3.3 메인 영역에 포스트 2개의 타이틀이 존재한다.
        main_area = soup.find('div', id='main-area')
        # 3.4 "아직 게시물이 없습니다." 라는 문구가 없어야 한다.
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        # post_001_card, post_002_card 추가 이전
        # self.assertIn(self.post_001.title, main_area.text)
        # self.assertIn(self.post_002.title, main_area.text)
        # post_001_card 추가 이후
        post_001_card = main_area.find('div', id='post-1')   # html에서 id가 'post-1'인 것이 있어야 함
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)  # card 영역에 카테고리 이름이 존재하는지 테스트
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')   # html에서 id가 'post-2'인 것이 있어야 함
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text) # card 영역에 카테고리 이름이 존재하는지 테스트
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')   # html에서 id가 'post-3'인 것이 있어야 함
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text) # card 영역에 카테고리 미분류 존재하는지 테스트
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

         # post에  author 유무 테스트
        self.assertIn(self.post_001.author.username.upper(), main_area.text)
        self.assertIn(self.post_002.author.username.upper(), main_area.text)

    def test_post_list_without_posts(self):  # post가 없는 상황에 대한 테스트
        Post.objects.all().delete() # 3개로 시작한 post 모두 지우기 : post 없는 테스트 용도
        # 이동 : 2.1 게시물이 하나도 없을 때,
        self.assertEqual(Post.objects.count(), 0)

        # 복사 : 1.1 포스트 목록 페이지(post list)를 연다.
        response = self.client.get('/blog/')
        # 복사 : 1.2 정상적으로 페이지가 로드된다.
        self.assertEqual(response.status_code, 200)
        # 복사 : 1.3 페이지의 타이틀에 Blog라는 문구가 있다.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)  # 추가 : navbar_test(soup) 활용
        self.assertIn('Blog', soup.title.text)

        # 이동 : 2.2 메인 영역에 "아직 게시물이 없습니다." 라는 문구가 나온다.
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):
        # 1.1 포스트가 하나 있다.
        # post_001 = Post.objects.create(
        #     title='첫 번째 포스트입니다.',
        #     content='Hello, World. We are the world.',
        #
        # )
        # post_002 = Post.objects.create(
        #     title='첫 번째 포스트입니다.',
        #     content='Hello, World. We are the world.',
        # )
        self.assertEqual(Post.objects.count(), 3)
        # 1.2 그 포스트의 url은 '/blog/1/' 이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 2. 첫 번째 포스트의 상세 페이지 테스트
        # 2.1 첫 번째 포스트의 url로 접근하면 정상적으로 response가 온다.(status code : 200)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # 2.2 포스트 목록 페이지와 똑같은 내비게이션 바가 있다.
        self.navbar_test(soup)  # navbar_test(self, soup) 함수를 호출하여 수행
        self.category_card_test(soup)

        # 2.3 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 들어 있다.
        self.assertIn(self.post_001.title, soup.title.text)

        # 2.4 첫 번째 포스트의 제목이 포스트 영역에 있다. (포스트 영역은 main-area임)
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)            # tile 존재 확인
        self.assertIn(self.post_001.category.name, post_area.text)    # category name 존재 확인

        # 2.5 첫 번째 포스트의 작성자가 포스트 영역에 있다.(아직 구현하지 않음)
        # 2.6 첫 번째 포스트의 내용(content)이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)

        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)

    def test_comment_form(self):
        # setUp 에서 설정한 comment 우선 확인
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.post_001.comment_set.count(), 1)

        # 로그인 하지 않은 상태
        response = self.client.get(self.post_001.get_absolute_url())  # 페이지 열기
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertIn('Log in and leave a comment', comment_area.text)
        self.assertFalse(comment_area.find('form', id='comment-form')) # 미로그인인이므로 코멘트 폼이 없어야 함 assertFalse

        # 로그인 한 상태
        self.client.login(username='obama', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())  # 페이지 열기
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('Log in and leave a comment', comment_area.text)  # 해당 버튼이 보이지 않아야 함 assertNotIn
        # self.assertTrue(comment_area.find('form', id='comment-form'))      # 로그인 상태에서는 코멘트 폼이 있어야 함 assertTrue
        # comment form test 필요
        comment_form = comment_area.find('form', id='comment-form')
        self.assertTrue(comment_form.find('textarea', id="id_content"))
        response = self.client.post(
            self.post_001.get_absolute_url() + 'new_comment/',
            {
                'content': '오바마의 댓글입니다.',
            },
            follow=True  # DB에 저장하는 작업을 마치고 redirect page 로 따라가기
        )
        self.assertEqual(response.status_code, 200)
        # comment 가 추가 되었으므로 갯수가 2인지 확인
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

        new_comment = Comment.objects.last()
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(new_comment.post.title, soup.title.text)

        comment_area = soup.find('div', id='comment-area')
        new_comment_div = comment_area.find('div', id=f'comment-{new_comment.pk}')
        self.assertIn('obama', new_comment_div.text)
        self.assertIn('오바마의 댓글입니다.', new_comment_div.text)

    def test_comment_update(self):
        comment_by_trump = Comment.objects.create(
            post=self.post_001,
            author=self.user_trump,
            content='트럼프의 댓글입니다.'
        )
        # 로그인이 아닌 상태 : 아래 2개의 댓글이 보이지 않아야 함
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-update-btn'))
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))

        # obama 로 로그인한 상태
        self.client.login(username='obama', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_area = soup.find('div', id='comment-area')
        self.assertTrue(comment_area.find('a', id='comment-1-update-btn'))   # comment 수정 버튼이 보여야 함
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))  # comment 수정 버튼이 보이지 않아야 함
        # 수정 버튼에 edit 문구가 있어야 하고, 링크 연결하기 위한 정의한 경로 확인
        comment_001_update_btn = comment_area.find('a', id='comment-1-update-btn')
        self.assertIn('edit', comment_001_update_btn.text)
        self.assertEqual(comment_001_update_btn.attrs['href'], '/blog/update_comment/1/') # comment 수정 경로
        # comment 수정 페이지가 열리는지 테스트
        response = self.client.get('/blog/update_comment/1/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 수정 페이지에 대한 확인 : title, form, textarea, textarea.text
        self.assertEqual('Edit Comment - Blog', soup.title.text)
        update_comment_form = soup.find('form', id='comment-form')
        content_textarea = update_comment_form.find('textarea', id='id_content')
        self.assertIn(self.comment_001.content, content_textarea.text)
        # 수정 후 submit 클릭 전에 sleep 부여
        sleep(2)
        # 수정 이후 submit 클릭 동작 테스트
        response = self.client.post(
            '/blog/update_comment/1/',
            {
                'content': '오바마의 댓글을 수정합니다.',
            },
            follow=True
        )
        # 수정한 내용이 확인됨을 테스트
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_001_div = soup.find('div', id='comment-1')
        self.assertIn('오바마의 댓글을 수정합니다.', comment_001_div.text)
        self.assertIn('Updated : ', comment_001_div.text)

    def test_comment_delete(self):
        # 댓글 하나 더 만들기
        comment_by_trump = Comment.objects.create(
            post=self.post_001,
            author=self.user_trump,
            content='트럼프의 댓글입니다.'
        )
        self.assertEqual(Comment.objects.count(), 2)            # 댓글이 2개임을 테스트 (obama, trump)
        self.assertEqual(self.post_001.comment_set.count(), 2)  # 댓글 2개 모두 post_001 에 속함

        # 테스트할 comment 페이지 열기
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # login 하지 않은 경우 테스트
        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', 'comment-1-delete-btn'))
        self.assertFalse(comment_area.find('a', 'comment-2-delete-btn'))
        # trump로 login 한  경우 테스트
        self.client.login(username='trump', password='somepassword')  # login
        response = self.client.get(self.post_001.get_absolute_url())  # 페이지 열기
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn'))
        self.assertTrue(comment_area.find('a', id='comment-2-delete-btn'))
        # delete 버튼 보이기 테스트
        comment_002_delete_modal_btn = comment_area.find('a', id='comment-2-delete-btn')
        self.assertIn('delete', comment_002_delete_modal_btn.text)
        # modal 테스트
        self.assertEqual(
                comment_002_delete_modal_btn.attrs['data-target'],
                '#deleteCommentModal-2'
            )
        delete_comment_modal_002 = soup.find('div', id='deleteCommentModal-2')
        self.assertIn('Are You Sure?', delete_comment_modal_002.text)  # 팝업 모달 확인
        really_delete_btn_002 = delete_comment_modal_002.find('a')     # delete 버튼 확인
        self.assertIn('Delete', really_delete_btn_002.text)
        self.assertEqual(really_delete_btn_002.attrs['href'], '/blog/delete_comment/2/')          # 연결 링크 속성 확인
        # delete 버튼 클릭 시 url 연결
        response = self.client.get('/blog/delete_comment/2/', follow=True)  # 삭제 후 원래 페이지로 돌아가기 follow=Ture
        self.assertEqual(response.status_code, 200)           # 잘 열리는지
        soup = BeautifulSoup(response.content, 'html.parser') # soup 으로 봐서
        self.assertIn(self.post_001.title, soup.title.text)   # 지우고서 보이는 페이지가 해당 페이지가 맞는지 title 로 확인
        comment_area = soup.find('div', id='comment-area')    # comment-area 가 잘 보이는지 확인
        # 지우기를 한 댓글은 보이면 안됨 : 트럼프의 댓글
        self.assertNotIn('트럼프의 댓글입니다.', comment_area.text) # comment-area 의 text 로 트럽프 댓글이 보이지 않아야 함
        # 1개의 댓글은 지웠으므로, 댓글이 1개만 남았는지 테스트

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())   # 해당 url로 진입
        self.assertEqual(response.status_code, 200)                              # 목적 url 응답 200 OK 확인

        soup = BeautifulSoup(response.content, 'html.parser')                    # html을 soup 으로 담기
        self.navbar_test(soup)                                                   # navbar를 test(soup) : soup을 입력해서 상단의 navabr 존재 테스트
        self.category_card_test(soup)                                            # category_card 를 테스트 : 오른쪽의 category 카드 존재하는지 테스트

        main_area = soup.find('div', id='main-area')                     # main-area 되어 있는 부분 가져오기
        self.assertIn(self.category_programming.name, main_area.h1.text) # 첫 번째 나오는 h1에 category 명이 programming 인지 테스트
        self.assertIn(self.category_programming.name, main_area.text)    # programming 이 카테고리명으로 존재 테스트
        self.assertIn(self.post_001.title, main_area.text)               # programming 카테고리인 post_001에가 노출 되는지 확인 테스트
        self.assertNotIn(self.post_002.title, main_area.text)            # programming 카테고리가 아닌 post_002는 미노출 되는지 확인 테스트
        self.assertNotIn(self.post_003.title, main_area.text)            # programming 카테고리가 아닌 post_002는 미노출 되는지 확인 테스트

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())   # tag_hello 의  절대 경로 읽기
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)         # navbar 는 똑깥이 존재해야 함
        self.category_card_test(soup)  # category_card 는 똑같이 존재해야 함

        self.assertIn(self.tag_hello.name, soup.h1.text)  # h1에 해당 tag 가 존재해야 함(post_001에 hello tag 존재)
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text) # main-area 에 tag_hello name 의 text 가 존재해야 함

        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post_without_login(self):
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

    # def test_create_post(self):
    def test_create_post_with_login(self):
        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/blog/create_post/')
        # self.assertEqual(response.status_code, 200)  # 이 줄은 아래의 코드로 변경 : staff에게만 작성 권한 제공 때문
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='obama', password='somepassword')  # obama가 staff이고, 작성권한 있어 테스트에 추가
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)  # staff은 create_post 페이지를 열 수 있음

        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create a New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content': 'Post Form 페이지를 만듭시다.',
                'tags_str': 'new tag; 한글 태그, python'
            }
        )

        last_post = Post.objects.last()  # 맨 마지막 post
        self.assertEqual(last_post.title, 'Post Form 만들기')
        self.assertEqual(last_post.author.username, 'obama')
        self.assertEqual(last_post.content, 'Post Form 페이지를 만듭시다.')

        self.assertEqual(last_post.tags.count(), 3) # 마지막 post 에는 new tag, 한글 태크, python 으로 표현됨됨
        self.assertTrue(Tag.objects.get(name='new tag'))  # new tag 존재 확인
        self.assertTrue(Tag.objects.get(name='한글 태그'))  # 한글 태그 존재 확인
        self.assertTrue(Tag.objects.get(name='python'))   # python 태그 존재 확인
        self.assertEqual(Tag.objects.count(), 5)          # 당초 태그 3개에서 2개가 더해져서 5개임

    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인 하지 않은 상태에서 접근하는 경우
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인은 했지만, 작성자가 아닌 경우
        self.client.login(username='trump', password='somepassword')  # trump가 로그인
        self.assertNotEqual(self.post_003.author, self.user_trump)      # post_003의 작성자가 trump 가 아니어야 함
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)                # 작성자가 아닌 경우 응답 실패가 나와야 함

        # 작성자(obama)가 접근하는 경우
        self.client.login(username='obama', password='somepassword')  # obama가 로그인
        self.assertEqual(self.post_003.author, self.user_obama)  # post_003의 작성자가 obama 이어야 함
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)              # 작성자가 맞는 경우 응답 성공이 되어야 함

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual('Edit Post - Blog', soup.title.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn("파이썬 공부;python", tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트를 수정했습니다.',
                'content': '안녕 세계? 우리는 하나!',
                'category': self.category_music.pk,
                'tags_str': "파이썬 공부; 한글 태그, some tag"  # update 동작시 tag 가 기존에서 변경되도록 구성
            },
            follow=True  # 수정된 페이지를 보여 줌
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트를 수정했습니다.', main_area.text)
        self.assertIn('안녕 세계? 우리는 하나!', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)

        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('python', main_area.text)

    def test_search(self):  # title 과 tag 기준으로 검색
        # title 에 검색어 파이썬이 포함되는 경우를 포함
        post_about_python = Post.objects.create(
            title='파이썬에 대한 포스트입니다.',
            content='Hello World, We are the world',
            author=self.user_trump
        )

        response = self.client.get('/blog/search/파이썬/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')


        self.assertIn('Search: 파이썬 (2)', main_area.text)
        self.assertNotIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertIn(self.post_003.title, main_area.text)
        self.assertIn(post_about_python.title, main_area.text)