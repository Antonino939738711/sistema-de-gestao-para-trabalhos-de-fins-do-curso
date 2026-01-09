from django.contrib.auth.decorators import login_required
from .models import Mensagem
from Coordenacao.models import Usuario
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from Coordenacao.models import Usuario, Tema



@login_required
def chat_view(request, user_id):
    outro = get_object_or_404(Usuario, id=user_id)

    mensagens = Mensagem.objects.filter(
        remetente__in=[request.user, outro],
        destinatario__in=[request.user, outro],
    )

    return render(request, 'chat/chat.html', {
        'outro': outro,
        'mensagens': mensagens
    })


@login_required
def enviar_mensagem(request, user_id):
    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()
        outro = get_object_or_404(Usuario, id=user_id)

        if texto:
            Mensagem.objects.create(
                remetente=request.user,
                destinatario=outro,
                texto=texto
            )

        return JsonResponse({"status": "ok"})

# Lista de estudantes por tutores ... 
@login_required
def tutor_chat_estudantes(request):
    if request.user.perfil != 'tutor':
        return JsonResponse({"erro": "Acesso negado"}, status=403)
    estudantes = Usuario.objects.filter(
        temas__tutor_indicado=request.user
    ).distinct()

    return render(request, "chat/tutor_estudantes.html", {
        "estudantes": estudantes
    })

# Chat com estudante específico apenas o tutor x com o estudante y
@login_required
def chat_tutor(request, estudante_id):
    if request.user.perfil != 'tutor':
        return JsonResponse({"erro": "Acesso negado"}, status=403)

    aluno = get_object_or_404(Usuario, id=estudante_id)

    # Relacao Tutor x ----> Aluno Y 
    if not Tema.objects.filter(tutor_indicado=request.user, estudante=aluno).exists():
        return JsonResponse({"erro": "Acesso negado"}, status=403)

    mensagens = Mensagem.objects.filter(
        remetente__in=[request.user, aluno],
        destinatario__in=[request.user, aluno]
    ).order_by('enviado_em')

    return render(request, 'chat/chat_tutor.html', {
        'aluno': aluno,
        'mensagens': mensagens
    })
@login_required
def chat_tutor_enviar(request, estudante_id):

    if request.method == "POST" and request.user.perfil == 'tutor':
        aluno = get_object_or_404(Usuario, id=estudante_id) 

        if not Tema.objects.filter(tutor_indicado=request.user, estudante=aluno).exists():
            return JsonResponse({"erro": "Acesso negado"}, status=403)

        texto = request.POST.get("texto", "").strip()
        if texto:
            Mensagem.objects.create(
                remetente=request.user,
                destinatario=aluno,
                texto=texto
            )

        return JsonResponse({"status": "ok"})
