from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from .models import AdsBoard, Rubric
from .forms import AdsForm


class AdsCreateView(CreateView):
    template_name = 'bboard/create.html'
    form_class = AdsForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context


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
