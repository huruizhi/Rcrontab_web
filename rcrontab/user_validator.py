from django.core.exceptions import ValidationError


class CodeAValidator:
    message = 'The string include A！'
    code = 'invalid'

    def __init__(self,  message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        if 'a' in value or 'A' in value:
            raise ValidationError(self.message, code=self.code)