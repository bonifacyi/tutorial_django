from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm


def search_template(request):
    search_form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.objects.annotate(
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.2).order_by('-rank')
            search_form = SearchForm()
    return {
        'search_form': search_form,
        'query': query,
        'results': results,
    }


def pagination(request, object_list):
    paginator = Paginator(object_list, 5)  # По 5 статьи на каждой странице.
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, возвращаем первую страницу.
        posts = paginator.page(1)
    except EmptyPage:
        # Если номер страницы больше, чем общее количество страниц, возвращаем последнюю.
        posts = paginator.page(paginator.num_pages)
    return page, posts


def post_search(request):
    search_context = search_template(request)
    return render(request, 'blog/post/search.html', search_context)


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    page, posts = pagination(request, object_list)
    context = {
        'page': page,
        'posts': posts,
        'tag': tag,
    }
    search_context = search_template(request)
    if search_context['query']:
        return render(request, 'blog/post/search.html', search_context)

    context.update(search_context)
    return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post, page_number):
    post = get_object_or_404(
        Post, slug=post, status='published',
        publish__year=year, publish__month=month, publish__day=day
    )
    # Список активных комментариев для этой статьи.
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        # Пользователь отправил комментарий.
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создаем комментарий, но пока не сохраняем в базе данных.
            new_comment = comment_form.save(commit=False)
            # Привязываем комментарий к текущей статье.
            new_comment.post = post
            # Сохраняем комментарий в базе данных.
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')).order_by('-same_tags', '-publish')[:3]

    context = {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts,
        'page_number': page_number,
    }
    search_context = search_template(request)
    if search_context['query']:
        return render(request, 'blog/post/search.html', search_context)

    context.update(search_context)
    return render(request, 'blog/post/detail.html', context)


def post_share(request, post_id):
    # Получение статьи по идентификатору.
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Форма была отправлена на сохранение.
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Все поля формы прошли валидацию.
            sent_form_data = form.cleaned_data
            # ... Отправка электронной почты.
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.\
                format(sent_form_data['name'], sent_form_data['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.\
                format(post.title, post_url, sent_form_data['name'], sent_form_data['comments'])
            send_mail(subject, message, sent_form_data['email'], [sent_form_data['to']])
            sent = True
    else:
        form = EmailPostForm()

    context = {
        'post': post,
        'form': form,
        'sent': sent,
    }
    search_context = search_template(request)
    if search_context['query']:
        return render(request, 'blog/post/search.html', search_context)

    context.update(search_context)
    return render(request, 'blog/post/share.html', context)
