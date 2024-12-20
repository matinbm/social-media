from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.views import View
from .forms import UserRegistrationForm, user_loginForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, views as auth_views
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from home.models import Post
from django.urls import reverse_lazy
from .models import Relation


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
        is_following = False
        user = get_object_or_404(User, pk=user_id)
        # posts = get_list_or_404(Post, user=user)
        # posts = Post.objects.filter(user=user)
        posts = user.posts.all()
        # if we use exist we have use the filter method not all method
        relations = Relation.objects.filter(from_user=request.user, to_user=user)
        if relations.exists():
            is_following = True
        return render(request, 'account/profile.html', {'user': user, 'posts': posts, 'is_following': is_following})


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'account/password_reset_form.html'
    success_url = reverse_lazy('account:password_reset_done')
    email_template_name = 'account/password_reset_email.html'


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account:password_reset_complete')


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'


class UserFollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            messages.error(request, 'You are already following', 'error')
        else:
            Relation(from_user=request.user, to_user=user).save()
            messages.success(request, 'You are now following the user', 'success')
            return redirect('account:user_profile', user_id=user.id)


class UserUnfollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(pk=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user_id)
        if relation.exists():
            relation.delete()
            messages.success(request, 'You are no longer following', 'success')
        else:
            messages.error(request, 'You are already unfollowing', 'error')
            return redirect('account:user_profile', user_id=user.id)
