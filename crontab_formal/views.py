from django.shortcuts import render
from . import forms
# Create your views here.


def insert(request):
    form = forms.ScriptBaseInfo()
    if request.method == 'GET':
        return render(request, 'rcrontab_formals', {'form': forms})


