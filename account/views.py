import profile

from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegistrationForm, user_loginForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from home.models import Post


class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'account/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.filter(email=cd['email'])

            User.objects.create_user(cd['username'], cd['email'], cd['password1'])
            messages.success(request, 'successful register', 'success')
            return redirect('home:home')

        return render(request, self.template_name, {'form': form})


class UserLoginView(View):
    form_class = user_loginForm
    template_name = 'account/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):

        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'successful login', 'success')
                return redirect('home:home')
            messages.error(request, 'Invalid username or password', 'warning')

        return render(request, self.template_name, {'form': form})


class UserLogoutView(LoginRequiredMixin, View):

    def get(self, request):
        logout(request)
        messages.success(request, 'successful logout', 'success')
        return redirect('home:home')


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(pk=user_id)
        posts = Post.objects.all().filter(user=user)
        return render(request, 'account/profile.html', {'user': user, 'posts': posts})
