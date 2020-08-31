from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import PermissionRequiredMixin, AccessMixin
from django.contrib.postgres.search import SearchVector, TrigramSimilarity, SearchQuery, SearchRank
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.views.generic.base import View, RedirectView

from .models import Category, Cart
from .forms import CartForm, CategoryForm, SearchForm


# Main Page
class CartListView(ListView):
    model = Cart
    template_name = 'study_helper_app/home.html'
    search_form = SearchForm

    # paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            practice_cart = Cart.to_practice.get_first(user=user)
            practice_count = Cart.to_practice.get_queryset(user=user).count()
        else:
            session_id = self.request.session.session_key
            practice_cart = Cart.to_practice.get_first(session_id=session_id)
            practice_count = Cart.to_practice.get_queryset(session_id=session_id).count()
        kwargs['category_form'] = CategoryForm
        kwargs['search_form'] = SearchForm
        kwargs['practice_count'] = practice_count
        kwargs['practice_cart'] = practice_cart.id if practice_cart else None

        return super().get_context_data(object_list=None, **kwargs)

    def get_queryset(self):
        user = self.request.user
        session_id = self.request.session.session_key
        if 'query' in self.request.GET:
            query = self.request.GET.get('query')
            results = SearchForm.search_query(query=query, user=user, session_id=session_id)
            return results
        if user.is_authenticated:
            return Cart.objects.filter(author=self.request.user)
        return Cart.objects.filter(session_id=session_id)


# Cart
class CartCRUDView(AccessMixin, View):
    model = Cart
    form_class = CartForm

    def get_context_data(self, **kwargs):
        kwargs['category_form'] = CategoryForm
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['session_id'] = self.request.session.session_key
        return kwargs


class CartCreateView(CartCRUDView, CreateView):
    template_name = 'study_helper_app/cart_create.html'
    success_url = reverse_lazy('create_cart')

    def form_valid(self, form):
        new_cart = form.save(commit=False)
        if self.request.user.is_authenticated:
            new_cart.author = self.request.user
        else:
            new_cart.session_id = self.request.session.session_key
        new_cart.save()
        return super().form_valid(form)


class CartUpdateView(CartCRUDView, UpdateView):
    template_name = 'study_helper_app/cart_create.html'
    success_url = reverse_lazy('main')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            if self.request.user != kwargs['instance'].author:
                return self.handle_no_permission()
        else:
            if self.request.session.session_key != kwargs['instance'].session_id:
                return self.handle_no_permission()
        return kwargs


class CartDeleteView(CartCRUDView, DeleteView):
    template_name = 'study_helper_app/home.html'
    success_url = reverse_lazy('main')

    def delete(self, request, *args, **kwargs):
        cart = self.get_object()
        if self.request.user.is_authenticated:
            if self.request.user != cart.author:
                return self.handle_no_permission()
        else:
            if self.request.session.session_key != cart.session_id:
                return self.handle_no_permission()

        return super().delete(request, *args, **kwargs)


# Practice
class PracticeView(AccessMixin, DetailView):
    template_name = 'study_helper_app/practice.html'
    model = Cart

    def post(self, request, *args, **kwargs):
        if request.POST.get('next_stage'):
            Cart.next_stage(kwargs.get('pk'))
        elif request.POST.get('stay_stage'):
            Cart.stay_stage(kwargs.get('pk'))

        user = self.request.user
        if user.is_authenticated:
            practice_cart = Cart.to_practice.get_first(user=user)
        else:
            practice_cart = Cart.to_practice.get_first(session_id=self.request.session.session_key)

        if practice_cart:
            return HttpResponseRedirect(reverse('practice', args=(practice_cart.id,)))

        return HttpResponseRedirect(reverse('main'))

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        user = self.request.user
        if user.is_authenticated:
            if self.request.user != cart.author or cart not in Cart.to_practice.get_queryset(user=user):
                return self.handle_no_permission()
        else:
            session_id = self.request.session.session_key
            if session_id != cart.session_id or cart not in Cart.to_practice.get_queryset(session_id=session_id):
                return self.handle_no_permission()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            kwargs['practice_count'] = Cart.to_practice.get_queryset(user=user).count()
        else:
            kwargs['practice_count'] = Cart.to_practice.get_queryset(
                session_id=self.request.session.session_key).count()
        return super().get_context_data(**kwargs)


# Category
class CategoryCreateView(CreateView):
    template_name = 'study_helper_app/home.html'
    form_class = CategoryForm
    success_url = reverse_lazy('main')

    # не уверен правильно ли так писать
    def form_valid(self, form):
        new_category = form.save(commit=False)
        if self.request.user.is_authenticated:
            new_category.author = self.request.user
        else:
            new_category.session_id = self.request.session.session_key
        new_category.save()
        return super().form_valid(form)


# Registration
class RegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        form_valid = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        auth_user = authenticate(username=username, password=password)
        login(self.request, auth_user)
        return form_valid
