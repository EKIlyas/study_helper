import time

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, Div
from django import forms
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector
from django.db import models

from .models import Cart, Category


class CartForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        session_id = kwargs.pop('session_id')
        if user.is_authenticated:
            categories = Category.objects.filter(author=user)
        else:
            categories = Category.objects.filter(session_id=session_id)
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = categories

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                'question',
                'answer',
                HTML("""
                <button type="button" class="btn btn-link btn-sm" data-toggle="modal"
                        data-target="#createCategoryModal" style="padding: 0">Создать Категорию
                </button>
                """),
                'category',
                'repeat_date',
            ),
            ButtonHolder(
                Submit('submit', 'Сохранить')
            )
        )

    class Meta:
        model = Cart
        fields = ['question', 'answer', 'category', 'repeat_date']
        widgets = {
            'answer': forms.Textarea(),
            'repeat_date': forms.DateInput(
                attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'mode']

        help_texts = {
            'mode': 'Долгосрочный: 1ый повтор - +30мин, 2ой повтор - +день, 3ий повтор - +2недели, 4ый повтор - +2месяца'
        }


class SearchForm(forms.Form):
    query = forms.CharField(label='')

    @staticmethod
    def search_query(query, user=None, session_id=None):
        results = Cart.objects.annotate(search=SearchVector('category__name', 'question'), ).filter(search=query)
        results = results.filter(author=user) if user.is_authenticated else results.filter(session_id=session_id)
        return results
