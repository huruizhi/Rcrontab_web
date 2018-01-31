from . import models
from django import forms


class ScriptBaseInfo(forms.ModelForm):

    class Meta:
        model = models.PyScriptBaseInfoV2
        exclude = []


class Path(forms.ModelForm):

    class Meta:
        model = models.Path
        exclude = []
