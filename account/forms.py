from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password, check_password

from account.models import User


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'username']
        error_messages = {
            'username': {
                'require': "请输出用户名。"
            },
            'email': {
                "require": "请输入邮箱。"
            }
        }

    password = forms.CharField(help_text="至少六位", widget=forms.PasswordInput, min_length=6, required=True,
                               error_messages={
                                   'min_length': "密码太短。",
                                   'require': "请输入密码。"
                               },
                               label="密码")
    repeat_password = forms.CharField(widget=forms.PasswordInput, required=True,
                                      error_messages={
                                          'require': "请再次输入密码。"
                                      },
                                      label="确认密码")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create(self):
        instance = self.save(commit=False)
        instance.set_password(self.cleaned_data.get('password'))
        if not User.objects.exists():
            instance.is_superuser = True
        instance.save()
        return instance

    def clean(self):
        data = super(RegisterForm, self).clean()
        if data.get('password') != data.get('repeat_password'):
            self.add_error('repeat_password', forms.ValidationError("两次输入的密码不一致。", code='invalid'))
        return data


class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super(LoginForm, self).__init__(request, *args, **kwargs)
        self.fields['username'].label = "用户名"
        self.fields['password'].label = "密码"

    remember_me = forms.BooleanField(label="记住我", required=False)

    error_messages = {
        'invalid_login': (
            "请输入正确的用户名和密码。注意区分大小写。"
        ),
        # 'inactive': "该账户已失效。",
    }

    def clean(self):
        return super().clean()


class ModifyPasswordForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput, required=True,
                                   error_messages={
                                       'require': "请输入用户名。"
                                   },
                                   label="用户名")
    old_password = forms.CharField(help_text="至少六位", widget=forms.PasswordInput, min_length=6, required=True,
                                   error_messages={
                                       'min_length': "密码太短。",
                                       'require': "请输入密码。"
                                   },
                                   label="旧密码")
    password = forms.CharField(help_text="至少六位", widget=forms.PasswordInput, min_length=6, required=True,
                               error_messages={
                                   'min_length': "密码太短。",
                                   'require': "请输入密码。"
                               },
                               label="新密码")
    repeat_password = forms.CharField(widget=forms.PasswordInput, required=True,
                                      error_messages={
                                          'require': "请再次输入密码。"
                                      },
                                      label="确认密码")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super(ModifyPasswordForm, self).clean()
        if data.get('password') != data.get('repeat_password'):
            self.add_error('repeat_password', forms.ValidationError("两次输入的密码不一致。", code='invalid'))
        try:
            user = User.objects.get(username=data.get('username'))
            old = self.cleaned_data.get('old_password')
            if check_password(old, user.password):
                new = self.cleaned_data.get('password')
                user.password = make_password(new)
                user.save(update_fields=['password'])
            else:
                self.add_error('old_password', forms.ValidationError("密码不正确。", code='invalid'))
        except:
            self.add_error('username', forms.ValidationError("用户名不存在。", code='invalid'))
        return data
