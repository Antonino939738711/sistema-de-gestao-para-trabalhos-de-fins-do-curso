from django.db import models
from django.conf import settings

Usuario = settings.AUTH_USER_MODEL

class Mensagem(models.Model):
    remetente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    destinatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensagens_recebidas')
    texto = models.TextField()
    enviado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['enviado_em']

    def __str__(self):
        return f"{self.remetente} → {self.destinatario}"
