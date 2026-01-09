from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import os

class Departamento(models.Model):
    nome = models.CharField(max_length=400)
    descricao = models.TextField(max_length=800)
    
    def __str__(self):
        return f'{self.nome}'

class Curso(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.CharField(max_length=500)
    
    def __str__(self):
        return f'{self.nome} - {self.descricao} '


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O campo Email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    TIPOS_USUARIO = (
        ("cordenacao", "cordenacao"),
        ("dac", "dac"),
        ("presidente", "professores"),
        ("estudante", "estudante"),
        ("area_cientifica", "area_cientifica"),
        ("tutor", "tutor"),
    )

    ESTADO_USUARIO = (
        ("activo", "activo"),
        ("desativado", "desativado"),
    )

    username = None
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    imagem = models.ImageField(
        upload_to="usuarios/",
        null=True,
        blank=True
    )

    perfil = models.CharField(
        max_length=20,
        choices=TIPOS_USUARIO,
    )

    estado_user = models.CharField(
        max_length=20,
        choices=ESTADO_USUARIO,
        default="desativado"
    )
    curso = models.ForeignKey(
        Curso, on_delete=models.SET_NULL, null=True, blank=True
    )
    depart = models.ForeignKey(
        Departamento, on_delete=models.SET_NULL, null=True, blank=True
    )
    telefone = models.CharField(max_length=9)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome", "sobrenome"]

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nome} {self.sobrenome} ({self.perfil})"

        
# tfc/models.py


class Tema(models.Model):

    STATUS_TUTOR = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado pelo tutor'),
        ('rejeitado', 'Rejeitado pelo tutor'),
    )

    STATUS_COORD = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado pela coordenação'),
        ('rejeitado', 'Rejeitado pela coordenação'),
    )

    STATUS_FINAL = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    )

    estudante = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='temas',
        limit_choices_to={'perfil': 'estudante'}
    )

    titulo = models.CharField(max_length=200)
    descricao = models.TextField()

    resumo = models.FileField(upload_to='resumos/', blank=True, null=True)
    requerimento = models.FileField(upload_to='requer/', blank=True, null=True)

    tutor_indicado = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='temas_orientados',
        limit_choices_to={'perfil': 'tutor'}
    )

    status_tutor = models.CharField(
        max_length=15,
        choices=STATUS_TUTOR,
        default='pendente'
    )

    status_coordenacao = models.CharField(
        max_length=20,
        choices=STATUS_COORD,
        default='pendente'
    )

    status_final = models.CharField(
        max_length=15,
        choices=STATUS_FINAL,
        default='pendente'
    )

    data_envio = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Final aprovado apenas se tutor e coord aprovaram
        if self.status_tutor == 'aprovado' and self.status_coordenacao == 'aprovado':
            self.status_final = 'aprovado'

        # Se qualquer um rejeitar → final rejeitado
        elif self.status_tutor == 'rejeitado' and self.status_coordenacao == 'aprovado':
            self.status_final = 'aprovado'

        # Caso contrário → pendente
        else:
            self.status_final = 'pendente'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titulo} ({self.estudante.nome})"



class Recomendacao(models.Model):
    tema = models.ForeignKey(
        Tema,
        on_delete=models.CASCADE,
        related_name='recomendacoes'
    )
    tutor = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'perfil': 'tutor'},
        related_name='recomendacoes_feitas'
    )
    texto = models.TextField()
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-data_criacao']  # As primeiras recomendacoes ... 

    def __str__(self):
        return f"Recomendação de {self.tutor} para '{self.tema.titulo}'"

