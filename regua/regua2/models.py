from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class Usuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('cliente', 'Cliente'),
        ('barbearia', 'Barbearia'),
    ]
    
    email = models.EmailField(max_length=255, unique=True)
    senha = models.CharField(max_length=128)
    nome = models.CharField(max_length=30)
    sobrenome = models.CharField(max_length=30)
    tipo = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES, default='cliente')
    telefone = models.CharField(max_length=15, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='perfil/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.senha = make_password(self.senha)
        super().save(*args, **kwargs)
    
    def verificar_senha(self, senha):
        return check_password(senha, self.senha)
    
    def __str__(self):
        return f"{self.nome} {self.sobrenome} ({self.get_tipo_display()})"

class Barbearia(models.Model):
    STATUS_BARBEARIA_CHOICES = [
        ('aberto', 'Aberto'),
        ('fechado', 'Fechado'),
    ]
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='barbearia')
    nome_barbearia = models.CharField(max_length=100)
    telefone_comercial = models.CharField(max_length=15, blank=True, null=True)
    foto_logo = models.ImageField(upload_to='barbearias/logos/', blank=True, null=True)
    
    # Dados de localização
    endereco = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    
    # Status da barbearia (aberto/fechado)
    status_barbearia = models.CharField(
        max_length=10,
        choices=STATUS_BARBEARIA_CHOICES,
        default='aberto'
    )
    
    data_cadastro = models.DateTimeField(default=timezone.now)
    ativa = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome_barbearia

    
class Agendamento(models.Model):
    barbearia = models.ForeignKey(Barbearia, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)
    horario = models.TimeField(auto_now_add=True)
    confirmado = models.BooleanField(default=False)
    realizado = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    horario_estimado = models.TimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.cliente.nome} - {self.barbearia.nome_barbearia} - {self.data} {self.horario}" 
