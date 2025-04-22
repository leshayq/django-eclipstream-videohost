from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
import re
from django.contrib.auth.forms import PasswordResetForm
from .tasks import send_email_async

def add_class_to_error_message(self):
    """Додає клас error, якщо є помилки у формах. """
    for field_name, field in self.fields.items():
        if self[field_name].errors:
            existing_classes = self.fields[field_name].widget.attrs.get("class", "")
            self.fields[field_name].widget.attrs["class"] = existing_classes + " error"

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input'}), label='Логін')
    email = forms.EmailField(required=True, label='Електронна пошта')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2',)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        if not re.match(r'^[a-z0-9]+$', username):
            raise forms.ValidationError("Ім'я користувача повинно містити лише букви англійського алфавіту та цифри.")
        
        if len(username) < 3:
            raise forms.ValidationError("Ім'я користувача повинно містити 3 або більше символів.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Така e-mail адреса вже зареєстрована")
        return email

    def add_error_css(self):
        add_class_to_error_message(self=self)


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Логін"
        self.fields['password'].label = "Пароль"

    def add_error_css(self):
        add_class_to_error_message(self=self)

class AsyncPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags

        subject = render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        message = render_to_string(email_template_name, context)
        html_message = None
        if html_email_template_name:
            html_message = render_to_string(html_email_template_name, context)
        else:
            html_message = None

        send_email_async.delay(subject, strip_tags(message), from_email, [to_email], html_message)