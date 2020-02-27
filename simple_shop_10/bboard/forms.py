from django.forms import ModelForm

from .models import AdsBoard


class AdsForm(ModelForm):
    class Meta:
        model = AdsBoard
        fields = ('title', 'content', 'price', 'rubric')
