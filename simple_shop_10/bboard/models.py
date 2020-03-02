from django.db import models
from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS


class AdsBoard(models.Model):
    title = models.CharField(
        max_length=50, verbose_name='Name',
        validators=[validators.RegexValidator(regex='^.{4,}$')],
        error_messages={'invalid': 'Wrong item name!'},
    )
    content = models.TextField(null=True, blank=True, verbose_name='Description')
    price = models.FloatField(null=True, blank=True, verbose_name='Price')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Published')
    rubric = models.ForeignKey('Rubric', null=True, on_delete=models.PROTECT, verbose_name='Rubric')

    def clean(self):
        errors = {}
        if not self.content:
            errors['content'] = ValidationError('Description needed')
        if self.price and self.price < 0:
            errors['price'] = ValidationError('Price must be positive')
        if errors:
            raise ValidationError(errors)

    class Meta:
        verbose_name_plural = 'Advertisements'
        verbose_name = 'Advertisement'
        ordering = ['-published']
        indexes = [
            models.Index(fields=['-published', 'title'], name='main'),
            models.Index(fields=['title', 'price', 'rubric']),
        ]

    def title_and_price(self):
        if self.price:
            return '{0} ({1:.2f})'.format(self.title, self.price)
        else:
            return self.title

    title_and_price.short_description = 'Title and Price'


class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, verbose_name='Rubric name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Rubrics'
        verbose_name = 'Rubric'
        ordering = ['name']


class AdvUser(models.Model):
    is_activated = models.BooleanField(default=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Spare(models.Model):
    name = models.CharField(max_length=30)


class Machine(models.Model):
    name = models.CharField(max_length=30)
    spares = models.ManyToManyField(Spare)
