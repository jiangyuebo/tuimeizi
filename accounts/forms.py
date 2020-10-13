from django import forms
from captcha.fields import CaptchaField


class UserRegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=6, max_length=12, error_messages={
        'required': '密码必须填写',
        'min_length': '密码必须大于6位',
        'max_length': '密码不能超过12位',
    })
    captcha = CaptchaField()


class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=6, max_length=12, error_messages={
        'required': '密码必须填写',
        'min_length': '密码必须大于6位',
        'max_length': '密码不能超过12位',
    })

