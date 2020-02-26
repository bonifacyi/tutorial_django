from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import AdsBoard, Rubric


def index(request):
    ads = AdsBoard.objects.all()
    rubrics = Rubric.objects.all()
    context = {
        'ads': ads,
        'rubrics': rubrics,
    }
    return render(request, 'bboard/index.html', context)


def by_rubric(request, rubric_id):
    ads = AdsBoard.objects.filter(rubric=rubric_id)
    rubrics = Rubric.objects.all()
    current_rubric = Rubric.objects.get(pk=rubric_id)
    context = {
        'ads': ads,
        'rubrics': rubrics,
        'current_rubric': current_rubric,
    }
    return render(request, 'bboard/by_rubric.html', context)
