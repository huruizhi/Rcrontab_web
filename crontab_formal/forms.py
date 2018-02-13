from . import models
from django import forms


class ScriptBaseInfoForm(forms.ModelForm):

    class Meta:
        model = models.PyScriptBaseInfoV2
        exclude = []


class ConfigFileLogForm(forms.ModelForm):

    class Meta:
        model = models.ConfigFileLog
        exclude = []
