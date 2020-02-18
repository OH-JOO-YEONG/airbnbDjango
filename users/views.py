import os
import requests
from django.views import View
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from . import forms
from . import models

class LoginView(View):

    def get(self, request):
        form = forms.LoginForm(initial={"email": "brb1111@naver.com"})
        return render(request, "users/login.html", {
            "form": form,
        })

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse("core:home"))
        return render(request, "users/login.html", {
            "form": form,
        })

def log_out(request):
    logout(request)
    return redirect(reverse("core:home"))

class SignUpView(FormView):
    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")
    initial = {
        "first_name": "Jooyeong",
        "last_name": "Oh",
        "email": "brb111@nate.com",
        "password": "",
        "password1": ""
    }

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)

def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        # 성공메시지
    except models.User.DoesNotExist:
        # 실패메시지
        pass
    return redirect(reverse("core:home"))

def github_login(request):
    client_id = os.environ.get("GH_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(f'https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user')
    #유저가 리다이렉트되고
    #리다이렉트 된 유저는 github페이지로 가서 우리가 로그인하고 싶은 어플리케이션의 아이디와 어떤 걸 얻고싶은지 알아내는 기능

class GithubException(Exception):
    pass

def github_callback(request):
    try:
        client_id = os.environ.get("GH_ID")
        client_secret = os.environ.get("GH_SECRET")
        code = request.GET.get("code", None)
        if code is not None:
            result = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"}, #이 줄에 의해서 json 값으로 주어진다.
            )
            result_json = result.json()
            error = result_json.get("error", None) #json 에러 판별
            if error is not None:
                raise GithubException()
            else: # json이 문제가 없을 때 액세스토큰을 준다.
                access_token = result_json.get("access_token") # 액세스 토큰이 문제 없으면 github api를 요청할 수 있다.
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                profile_json = profile_request.json()
                username = profile_json.get("login", None)
                # 유저네임이 현재 profile request에에있는지 없는지 판별
                if username is not None:
                    name = profile_json.get("name")
                    email = profile_json.get("email")
                    bio = profile_json.get("bio")
                    user = models.User.objects.get(email=email)
                else:
                    raise GithubException()
        else:
            raise GithubException()

    except GithubException:
        return redirect(reverse("users:login"))