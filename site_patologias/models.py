from django.db import models

# Create your models here.
class Admin(models.Model):
    nome = models.CharField(max_length=40)
    email = models.CharField(max_length=30)
    senha = models.CharField(max_length=256)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

