from django.contrib.auth.forms import UserCreationForm
from django.forms import PasswordInput
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("phone", "password1", "password2", "name", "email")
        widgets = {
            "password1": PasswordInput(attrs={
                "class": "unfold-input w-full",
                "data-unfold-password-toggle": "true",  # <— магия unfold
            }),
            "password2": PasswordInput(attrs={
                "class": "unfold-input w-full",
                "data-unfold-password-toggle": "true",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "bg-[#111827] border border-gray-700 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 w-full",
                "placeholder": field.label
            })
            field.help_text = None

        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"
