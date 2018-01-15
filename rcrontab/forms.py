from django import forms
from rcrontab import models, user_validator


class EditExec(forms.ModelForm):

    class Meta:
        model = models.PyScriptBaseInfoNew
        exclude = []

    def clean_is_jk(self):
        data = self.cleaned_data['is_jk']
        if data not in (0, 1):
            raise forms.ValidationError('The value of this field must be 0 or 1!')
        else:
            return data

    def clean_exec_time(self):
        data = self.cleaned_data['exec_time']
        try:
            hour = int(data.split(":")[0])
            minute = int(data.split(":")[1])
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return data
            else:
                raise forms.ValidationError('The value of this field must be a time type like 00:01')
        except:
            raise forms.ValidationError('The value of this field must be a time type like 00:01')


class EditForm(forms.Form):
    exclude_a = user_validator.CodeAValidator()
    select = {(0, 'aaa'), (1, 'bbb')}
    sid = forms.IntegerField()
    name = forms.CharField(label='你的名字', max_length=5, initial='input your name', validators=(exclude_a,))
    deploy_server = forms.ChoiceField(choices=select)
    message = forms.CharField(widget=forms.Textarea, required=False)
    sender = forms.EmailField(error_messages={"required": "123123", })
    cc_myself = forms.BooleanField(required=False)
    date = forms.DateTimeField()
    time = forms.TimeField()
    url = forms.URLField()

    def clean_sid(self):
        sid_new = self.cleaned_data['sid']
        if sid_new > 50:
            raise forms.ValidationError(message='sid must less than %(value)s!',
                                        code='ValueError', params={'value': 50, })


    # field.py
    # required -- Boolean that specifies whether the field is required.
    #             True by default.
    # widget -- A Widget class, or instance of a Widget class, that should
    #           be used for this Field when displaying it. Each Field has a
    #           default Widget that it'll use if you don't specify this. In
    #           most cases, the default widget is TextInput.
    # label -- A verbose name for this field, for use in displaying this
    #          field in a form. By default, Django will use a "pretty"
    #          version of the form field name, if the Field is part of a
    #          Form.
    # initial -- A value to use in this Field's initial display. This value
    #            is *not* used as a fallback if data isn't given.
    # help_text -- An optional string to use as "help text" for this Field.
    # error_messages -- An optional dictionary to override the default
    #                   messages that the field will raise.
    # show_hidden_initial -- Boolean that specifies if it is needed to render a
    #                        hidden widget with initial value after widget.
    # validators -- List of additional validators to use
    # localize -- Boolean that specifies if the field should be localized.
    # disabled -- Boolean that specifies whether the field is disabled, that
    #             is its widget is shown in the form but not editable.
    # label_suffix -- Suffix to be added to the label. Overrides
    #                 form's label_suffix.


