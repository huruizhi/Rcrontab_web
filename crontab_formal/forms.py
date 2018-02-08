from . import models
from django import forms


class ScriptBaseInfoForm(forms.ModelForm):

    class Meta:
        model = models.PyScriptBaseInfoV2
        exclude = []


class PathForm(forms.ModelForm):

    class Meta:
        model = models.Path
        exclude = []
