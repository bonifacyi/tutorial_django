from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Image
from .forms import ImageCreateForm
from common.decorators import ajax_required
from actions.utils import create_action
import redis
from django.conf import settings

# Подключение к Redis.
redis_db = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB)


@login_required
def image_create(request):
    if request.method == 'POST':
        # Форма отправлена.
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # Данные формы валидны.
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            # Добавляем пользователя к созданному объекту.
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request, 'Image added successfully')
            # Перенаправляем пользователя на страницу сохраненного изображения.
            return redirect(new_item.get_absolute_url())
    else:
        # Заполняем форму данными из GET-запроса.
        form = ImageCreateForm(data=request.GET)
    return render(
        request,
        'images/image/create.html',
        {'section': 'images', 'form': form},
    )


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # Увеличиваем количество просмотров картинки на 1.
    total_views = redis_db.incr('image:{}:views'.format(image.id))
    # Увеличиваем рейтинг картинки на 1.
    # redis_db.zincrby('image_ranking', 1, image.id)
    redis_db.zadd('image_ranking', {image.id: total_views})
    context = {
        'section': 'images',
        'image': image,
        'total_views': total_views,
    }
    return render(request, 'images/image/detail.html', context)


@login_required
def image_ranking(request):
    # Получаем набор рейтинга картинок.
    image_ranking_scores = redis_db.zrange('image_ranking', 0, -1, desc=True, withscores=True)[:10]
    # Получаем отсортированный список самых популярных картинок.
    most_viewed = [Image.objects.get(id=id_) for id_, s in image_ranking_scores]
    return render(
        request,
        'images/image/ranking.html',
        {'section': 'images', 'most_viewed': most_viewed})


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'ok'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # Если переданная страница не является числом, возвращаем первую.
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # Если получили AJAX-запрос с номером страницы, большим, чем их количество,
            # возвращаем пустую страницу.
            return HttpResponse('')
        # Если номер страницы больше, чем их количество, возвращаем последнюю.
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(
            request,
            'images/image/list_ajax.html',
            {'section': 'images', 'images': images})
    return render(
        request,
        'images/image/list.html',
        {'section': 'images', 'images': images})
