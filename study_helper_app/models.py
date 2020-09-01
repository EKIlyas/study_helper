import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class PracticeManager(models.Manager):
    def get_queryset(self, user=None, session_id=None):
        result = super().get_queryset().filter(repeat_date__lte=timezone.now()).order_by('repeat_date')
        result = result.filter(author=user) if user else result.filter(session_id=session_id)
        return result

    def get_first(self, user=None, session_id=None):
        queryset = self.get_queryset(user=user) if user else self.get_queryset(session_id=session_id)
        if queryset:
            return queryset[0]


class Mode(models.Model):
    name = models.CharField('Название', max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Режим'
        verbose_name_plural = 'Все Режимы'


class Stage(models.Model):
    name = models.CharField('Название', max_length=20)
    interval_minute = models.IntegerField('Интервал (в минутах)', default=0)
    interval_hour = models.IntegerField('Интервал (в часах)', default=0)
    interval_day = models.IntegerField('Интервал (в днях)', default=0)
    sequence = models.IntegerField('Последовательность', unique=True)
    mode = models.ForeignKey(Mode, verbose_name='Режим', on_delete=models.RESTRICT, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Стадия'
        verbose_name_plural = 'Стадии'


class Category(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=32, blank=True, null=True)

    name = models.CharField('Категория', max_length=20)
    mode = models.ForeignKey(Mode, verbose_name='Режим', on_delete=models.RESTRICT, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Cart(models.Model):
    objects = models.Manager()
    to_practice = PracticeManager()

    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=32, blank=True, null=True)

    question = models.CharField('Вопрос', max_length=200)
    answer = models.CharField('Ответ', max_length=500)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, null=True, verbose_name='Категория')
    add_date = models.DateField('Дата Добавления', auto_now_add=True)
    repeat_date = models.DateTimeField('Дата Повторения', default=timezone.now)
    stage = models.IntegerField('Стадия', default=0)

    @staticmethod
    def next_stage(pk):
        current_cart = Cart.objects.get(id=pk)
        next_stage = Stage.objects.filter(mode__category=current_cart.category, sequence=current_cart.stage+1)
        if not next_stage:
            next_stage = Stage.objects.get(mode__category=current_cart.category, sequence=current_cart.stage)
        increment_date = datetime.timedelta(
            minutes=next_stage.interval_minute,
            hours=next_stage.interval_hour,
            days=next_stage.interval_day
        )
        current_cart.repeat_date = timezone.now() + increment_date
        current_cart.stage += 1
        current_cart.save()

    @staticmethod
    def stay_stage(pk):
        current_cart = Cart.objects.get(id=pk)
        current_cart.repeat_date = timezone.now()
        current_cart.save()

    def __str__(self):
        return self.question[:20]

    class Meta:
        verbose_name = 'Карточка'
        verbose_name_plural = 'Карточки'
