import os
import requests
from django.views import View
from django.views.generic import FormView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.files.base import ContentFile
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
    messages.info(request, f"See you later {request.user.first_name}")
    logout(request)
    return redirect(reverse("core:home"))

class SignUpView(FormView):
    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")

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
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"}, #이 줄에 의해서 json 값으로 주어진다.
            )
            token_json = token_request.json()
            error = token_json.get("error", None) #json 에러 판별
            if error is not None:
                raise GithubException("Can't get access token")
            else: # json이 문제가 없을 때 액세스토큰을 준다.
                access_token = token_json.get("access_token") # 액세스 토큰이 문제 없으면 github api를 요청할 수 있다.
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                profile_json = profile_request.json()
                username = profile_json.get("login", None)
                # 유저네임이 현재 profile request에 있는지 없는지 판별
                if username is not None:
                    name = profile_json.get("name")
                    email = profile_json.get("email")
                    bio = profile_json.get("bio")
                    try:
                        user = models.User.objects.get(email=email) #깃허브의 이메일로 유저를 가져오고 유저가 있다면
                        if user.login_method != models.User.LOGIN_GITHUB: # 유저를 찾았다면 로그인 메서드를 확인 후 깃허브가 아니였다면
                            raise GithubException(f"Please login in with: {user.login_method}")
                    except models.User.DoesNotExist: # 깃허브의 이메일로 유저를 가져오지 못했다면
                        user = models.User.objects.create(
                            email=email,
                            first_name=name,
                            bio=bio,
                            username=email,
                            login_method=models.User.LOGIN_GITHUB,
                            email_verified=True,
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    messages.success(request, f"Welcome back {user.first_name}")
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException("Can't get your profile")
        else:
            raise GithubException("Can't get code")

    except GithubException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))

def kakao_login(request):
    client_id = os.environ.get("KAKAO_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code")

class KakaoException(Exception):
    pass

def kakao_callback(request):
    try:
        code = request.GET.get("code", None)
        client_id = os.environ.get("KAKAO_ID")
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
        token_request = requests.get(f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}')
        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException("Cat't get authorization code")
        access_token = token_json.get("access_token")
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={'Authorization': f'Bearer {access_token}'},
        )
        profile_json = profile_request.json()
        kakao_account = profile_json.get("kakao_account")
        email = kakao_account.get("email", None)
        if email is None:
            raise KakaoException("Please also give me your email")
        profile = kakao_account.get("profile")
        nickname = profile.get("nickname")
        profile_image = profile.get('profile_image_url', None)
        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                raise KakaoException(f"Please log in with: {user.login_method}")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email=email,
                username=email,
                first_name=nickname,
                login_method=models.User.LOGIN_KAKAO,
                email_verified=True,
            )
            user.set_unusable_password()
            user.save()
            if profile_image is not None:
                photo_request = requests.get(profile_image)
                # photo_request.content()는 json도 아닌 text도 아닌 0 과 1로 이루어진 bullshit파일
                user.avatar.save(f"{nickname}-avatar", ContentFile(photo_request.content)) # ContentFile 메서드로 해주면 bullshit파일을 파일로 바꿔줌 % django에서 bullshit파일을 처리하는 방법
        login(request, user)
        messages.success(request, f"Welcome back {user.first_name}")
        return redirect(reverse("core:home"))
    except KakaoException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))

class UserProfileView(DetailView):

    model = models.User
    context_object_name = 'user_obj'

