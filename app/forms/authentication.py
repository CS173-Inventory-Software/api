from django import forms

class RequestCodePostForm(forms.Form):
    email = forms.EmailField()