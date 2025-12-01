from django import forms
from .models import BancoModel
from django.contrib.auth.hashers import make_password

class BancoForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput())  # Campo de senha com máscara
    
    class Meta:
        model = BancoModel
        fields = ['email', 'senha', 'nome', 'sobrenome']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.senha = make_password(self.cleaned_data['senha'])  # Hash da senha
        if commit:
            user.save()
        return user