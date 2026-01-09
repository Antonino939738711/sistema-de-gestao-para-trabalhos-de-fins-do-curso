from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from .models import Departamento, Usuario, Curso, Tema,Recomendacao
from chat.models import Mensagem
from django.contrib.staticfiles import finders
Usuario = get_user_model()
from django.contrib.auth import authenticate, login as auth_login
from django.conf import settings

def login_view(request):
    if request.user.is_authenticated:

        # Autenticao apenas se o usuario esta activo 
        if request.user.estado_user != "activo":
            messages.error(request, "A sua conta está desativada. Contacte a coordenação.")
            return redirect("login")

        if request.user.perfil == "cordenacao" or request.user.is_superuser:
            return redirect("admink")

        if request.user.perfil == "estudante":
            return redirect("dashboard_estudante")

        if request.user.perfil == "tutor":
            return redirect("dashboard_tutor")

        if request.user.perfil == "presidente":
            return redirect("dashboard_presidencia")
        

    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("senha")

        user = authenticate(request, username=email, password=password)

        if user is not None:

            # 🔒 BLOQUEIO PRINCIPAL
            if user.estado_user != "activo":
                messages.error(
                    request,
                    "Conta desativada. Não é possível fazer login."
                )
                return render(request, "usuarios/index.html")

            auth_login(request, user)

            if user.perfil == "cordenacao" or user.is_superuser:
                return redirect("admink")

            if user.perfil == "estudante":
                return redirect("dashboard_estudante")

            if user.perfil == "tutor":
                return redirect("dashboard_tutor")
            if request.user.perfil == "presidente":
            	return redirect("dashboard_presidencia")

        else:
            messages.error(request, "Email ou senha incorretos.")

    return render(request, "usuarios/index.html")



def sair(request):
    logout(request)
    return redirect("login")

# Cadastro do Usuario
def cadastro(request):
    departamentos = Departamento.objects.all()
    cursos = Curso.objects.all()
    if request.method == "POST":
        nome_completo = request.POST.get("nome_completo")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        perfil = request.POST.get("perfil")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        departamento_id = request.POST.get("departamento")
        curso_id = request.POST.get("curso")
        partes_nome = nome_completo.strip().split(" ", 1)
        nome = partes_nome[0]
        sobrenome = partes_nome[1] if len(partes_nome) > 1 else ""

        if password1 != password2:
            messages.error(request, "As senhas não coincidem.")
            return redirect("cadastro")

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Já existe um usuário com este e-mail.")
            return redirect("cadastro")

        try:
            user = Usuario.objects.create_user(
                email=email,
                password=password1,
                nome=nome,
                sobrenome=sobrenome,
                telefone=telefone,
                perfil=perfil,
            )

            if perfil == "cordenacao" and departamento_id:
                try:
                    departamento = Departamento.objects.get(id=departamento_id)
                    user.depart = departamento
                    user.save()
                except Departamento.DoesNotExist:
                    messages.warning(request, "Departamento inválido, mas usuário criado com sucesso.")
            
            if perfil == "estudante" and curso_id:
                try:
                    curso = Curso.objects.get(id=curso_id)
                    user.curso = curso
                    user.save()
                except Curso.DoesNotExist:
                     messages.warning(request, "Curso inválido, mas usuário criado com sucesso.")

            messages.success(request, "Conta criada com sucesso!")
            return redirect("login")

        except Exception as e:
            messages.error(request, f"Erro ao criar usuário: {str(e)}")
            return redirect("cadastro")

    return render(request, "usuarios/cadastro.html", {"departamentos": departamentos , "cursos":cursos} )


# --- Funções Admin/Coordenação ---

@login_required
def admink(request):
    if request.user.perfil == 'cordenacao' and request.user.depart:
        dept_nome = request.user.depart.nome
        dept_part = dept_nome.split(' ')[2:] # pega a partir da 3ª palvra Tela Preta Departamento de ------------
        dept_filtrar = ' '.join(dept_part)

        usuarios = Usuario.objects.filter(
            perfil='estudante',
            curso__nome__icontains=dept_filtrar
        )
    elif request.user.is_superuser:
        usuarios = Usuario.objects.filter(perfil='estudante')
    else:
        usuarios = Usuario.objects.filter(perfil='estudante')
    nome = request.user.nome 

    tutores = Usuario.objects.filter(perfil='tutor')
    total_tutor = tutores.count()
    total = usuarios.count()
    lista_temas_reprovados = Tema.objects.exclude(status_final='aprovado') \
                                        .select_related('estudante', 'tutor_indicado')
    total_temas = len(lista_temas_reprovados)

    return render(request, 'admin/index.html', {
        'total': total,
        'total_tutor': total_tutor,
        'nome': nome,
        'tutores': tutores,
        'total_temas':total_temas,
    })


@login_required
def lista_estudantes(request):
    # Prefetch do tema → pega apenas 1 tema por estudante (o mais recente)
    temas_prefetch = Prefetch(
        'temas',
        queryset=Tema.objects.order_by('-data_envio'),
        to_attr='tema_list'
    )

    if request.user.perfil == 'cordenacao' and request.user.depart:
        # Pega o nome do departamento, remove prefixo "Departamento de " (assumindo sempre esse padrão)
        dept_nome = request.user.depart.nome
        dept_part = dept_nome.split(' ')[2:] # pega a partir da 3ª palavra
        dept_filtrar = ' '.join(dept_part)

        estudantes = Usuario.objects.filter(
            perfil='estudante',
            curso__nome__icontains=dept_filtrar
        ).prefetch_related(temas_prefetch).order_by("nome")
    else:
        estudantes = Usuario.objects.filter(perfil='estudante') \
                                     .prefetch_related(temas_prefetch) \
                                     .order_by("nome")

    return render(request, "admin/lista_estudantes.html", {
        "estudantes": estudantes
    })


@login_required
def alterar_status_tema(request, tema_id, novo_status):
    # Permissão para Tutor ou Coordenacao
    if request.user.perfil not in ['tutor', 'cordenacao']:
        messages.error(request, "Acesso negado.")
        return redirect('lista_estudantes')

    tema = get_object_or_404(Tema, id=tema_id)

    # Validação do status
    if novo_status not in ['aprovado', 'rejeitado', 'pendente']:
        messages.error(request, "Status inválido.")
        # Redirecionamento depende do perfil para ter uma UX melhor
        if request.user.perfil == 'tutor':
            return redirect('dashboard_tutor')
        return redirect('lista_reprovados') 

    # Lógica para TUTOR (altera apenas o status dele)
    if request.user.perfil == 'tutor':
        tema.status_tutor = novo_status
        tema.save()
        messages.success(request, f"Status do tutor atualizado para: {novo_status}")
        return redirect('lista_estudantes') # Ou dashboard_tutor, dependendo da sua rota

    # Lógica para COORDENAÇÃO (altera o status de coordenação)
    if request.user.perfil == 'cordenacao':
        
        tema.status_coordenacao = novo_status
        tema.save()
        
        if novo_status == 'aprovado':
            messages.success(request, f"Status da coordenação atualizado para: {novo_status}")
        else:
            messages.error(request, f"Status da coordenação atualizado para: {novo_status}")
            
        return redirect('lista_reprovados')


@login_required
def temas_aprovados(request):
    lista_temas_aprovados = Tema.objects.filter(status_final='aprovado') \
                                        .select_related('estudante', 'tutor_indicado')

    if request.user.perfil == 'cordenacao' and request.user.depart:
        dept_nome = request.user.depart.nome
        dept_part = dept_nome.split(' ')[2:] # pega a partir da 3ª palavra
        dept_filtrar = ' '.join(dept_part)
        lista_temas_aprovados = lista_temas_aprovados.filter(
            estudante__curso__nome__icontains=dept_filtrar
        )

    return render(request, "admin/lista_aprovados.html", {
        "lista_temas_aprovados": lista_temas_aprovados
    })


@login_required
def temas_reprovados(request):
    lista_temas_reprovados = Tema.objects.exclude(status_final='aprovado') \
                                        .select_related('estudante', 'tutor_indicado')

    if request.user.perfil == 'cordenacao' and request.user.depart:
        dept_nome = request.user.depart.nome
        dept_part = dept_nome.split(' ')[2:] # pega a partir da 3ª palavra
        dept_filtrar = ' '.join(dept_part)
        lista_temas_reprovados = lista_temas_reprovados.filter(
            estudante__curso__nome__icontains=dept_filtrar
        )

    return render(request, "admin/lista_reprovados.html", {
        "lista_temas_aprovados": lista_temas_reprovados
    })


def alterar_status_multiplos(request):
    # Ação de coordenador
    if request.method != "POST":
        return redirect("lista_reprovados")

    ids = request.POST.getlist("temas_selecionados")
    acao = request.POST.get("acao")

    if not ids:
        messages.error(request, "Nenhum tema selecionado.")
        return redirect("lista_reprovados")

    temas = Tema.objects.filter(id__in=ids)

    # --- APENAS PARA APROVAR ---
    if acao == "aprovar":
        # Só aprova quem o tutor já aprovou
        nao_aprovados = temas.exclude(status_tutor="aprovado")

        if nao_aprovados.exists():
            messages.error(request, "Aguarde a aprovação do tutor para alguns temas selecionados.")
            return redirect("lista_reprovados")

        temas.update(status_coordenacao="aprovado")
        messages.success(request, f"{len(temas)} tema(s) aprovado(s) pela coordenação.")
        return redirect("lista_reprovados")

    # --- PARA REJEITAR (SEM PRECISAR DO TUTOR) ---
    elif acao == "rejeitar":
        temas.update(status_coordenacao="rejeitado")
        messages.error(request, f"{len(temas)} tema(s) rejeitado(s) pela coordenação.")
        return redirect("lista_reprovados")

    messages.error(request, "Ação inválida.")
    return redirect("lista_reprovados")

# --- Funções de Estudante ---

@login_required
def dashboard_estudante(request):
    user = request.user
    temas = Tema.objects.filter(estudante=user).order_by('-data_envio')  # ordena do mais recente
    tutores = Usuario.objects.filter(perfil='tutor').order_by('nome')
    total_tutor = tutores.count()
    total_estudantes = Usuario.objects.filter(perfil='estudante').count()
    nome = user.nome # pega o nome do próprio usuário logado

    temas_estudante = Tema.objects.filter(estudante=request.user)
    recomendacoes_qs = Recomendacao.objects.filter(tema__in=temas_estudante)

    # 1. Contamos as que AINDA não foram lidas antes de mudar o estado
    total_novas = recomendacoes_qs.filter(lida=False).count()

    # 2. Agora sim, marcamos todas como lidas no banco de dados
    recomendacoes_qs.filter(lida=False).update(lida=True)

    return render(request,'Estudante/index.html',{
        'total': total_estudantes,
        'total_tutor': total_tutor,
        'nome': nome,
        'total_recomendacoes': total_novas,
        'tutores': tutores,
        'temas': temas
    })


@login_required
def criar_ou_editar_tema(request):
    if request.method != "POST":
        return redirect("dashboard_estudante")
    
    titulo = request.POST.get('titulo')
    descricao = request.POST.get('descricao')
    resumo = request.FILES.get('resumo')
    requerimento = request.FILES.get('requerimento')
    tutor_id = request.POST.get('tutor_indicado')

    if not titulo or not descricao or not tutor_id:
        messages.error(request, "Por favor, preencha todos os campos obrigatórios.")
        return redirect("dashboard_estudante")

    try:
        tutor = Usuario.objects.get(id=tutor_id)
    except Usuario.DoesNotExist:
        messages.error(request, "Tutor selecionado inválido.")
        return redirect("dashboard_estudante")
    tema_existente = Tema.objects.filter(estudante=request.user).first()

    if tema_existente:
        if tema_existente.status_coordenacao != "rejeitado":
            messages.error(request, "Não é possível criar ou modificar o tema enquanto ele não for rejeitado pela coordenação.")
            return redirect("dashboard_estudante")

        # Atualiza o tema existente
        tema_existente.titulo = titulo
        tema_existente.descricao = descricao
        if resumo:
            tema_existente.resumo = resumo
        if requerimento:
            tema_existente.requerimento = requerimento
        tema_existente.tutor_indicado = tutor

        # Reset dos status para 'pendente'
        tema_existente.status_tutor = 'pendente'
        tema_existente.status_coordenacao = 'pendente'

        tema_existente.save()
        messages.success(request, "Tema atualizado com sucesso e enviado para aprovação novamente.")
        return redirect("dashboard_estudante")
    Tema.objects.create(
        estudante=request.user,
        titulo=titulo,
        descricao=descricao,
        resumo=resumo,
        requerimento=requerimento,
        tutor_indicado=tutor,
        status_tutor='pendente',
        status_coordenacao='pendente',
        # status_final='pendente'
    )

    messages.success(request, "Tema enviado com sucesso.")
    return redirect("dashboard_estudante")

# --- Funções de Tutor ---

@login_required
def dashboard_tutor(request):
    if request.user.perfil != 'tutor':
        messages.error(request, "Acesso negado.")
        return redirect('login')

    # Pega todos os temas onde o tutor indicado é o usuário logado
    temas = Tema.objects.filter(tutor_indicado=request.user).order_by('-data_envio')

    return render(request, "tutor/index.html", {
        "temas": temas
    })


@login_required
def alterar_status_tema_tutor(request, tema_id, novo_status):
    if request.user.perfil not in ['tutor', 'cordenacao']: 
        messages.error(request, "Acesso negado.")
        return redirect('dashboard_tutor')

    tema = get_object_or_404(Tema, id=tema_id)
    # Tutor so pode alterar o status do seu tutorando Tela Preta ...
    if request.user.perfil == 'tutor' and tema.tutor_indicado != request.user:
        messages.error(request, "Você não pode alterar status de temas que não são seus.")
        return redirect('dashboard_tutor')

    # Validação do status, nao pode ter stutaus diferentes desse , pendente aprovado e rejeitado
    if novo_status not in ['pendente', 'aprovado', 'rejeitado']:
        messages.error(request, "Status inválido.")
        return redirect('dashboard_tutor')
    tema.status_tutor = novo_status
    tema.save()
    
    # Mensagem do Status ...
    if novo_status == 'aprovado':
        messages.success(request, f"Status do tema atualizado para: {novo_status}")
    elif novo_status == 'rejeitado':
        messages.error(request, f"Status do tema atualizado para: {novo_status}")
    else: # pendente
        messages.info(request, f"Status do tema atualizado para: {novo_status}")
        
    return redirect('dashboard_tutor')


def alterar_status_multiplos_tutor(request):
    if request.method != "POST":
        return redirect("dashboard_tutor")

    ids = request.POST.getlist("temas_selecionados")
    acao = request.POST.get("acao")

    if not ids:
        messages.error(request, "Nenhum tema selecionado.")
        return redirect("dashboard_tutor")

    temas = Tema.objects.filter(id__in=ids, tutor_indicado=request.user) 

    if acao == "aprovar":
        temas.update(status_tutor="aprovado")
        messages.success(request, f"{len(temas)} tema(s) aprovado(s).")

    elif acao == "rejeitar":
        temas.update(status_tutor="rejeitado")
        messages.error(request, f"{len(temas)} tema(s) rejeitado(s).")
    
    else:
        messages.error(request, "Ação inválida.")

    return redirect("dashboard_tutor")


def add_estudante(request):
    cursos = Curso.objects.all()
    if request.method == "POST":
        nome = request.POST["nome"]
        sobrenome = request.POST["sobrenome"]
        email = request.POST["email"]
        telefone = request.POST["telefone"]
        curso_id = request.POST["curso"]
        senha = request.POST["senha"]
        confirmar = request.POST["confirmar_senha"]

        if senha != confirmar:
            messages.error(request, "As senhas não coincidem.")
            return redirect("add_estudante")

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Este email já está registado.")
            return redirect("add_estudante")

        try:
            curso = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            messages.error(request, "Curso inválido.")
            return redirect("add_estudante")
        
        # Cria o usuário
        user = Usuario.objects.create_user(
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            telefone=telefone,
            perfil="estudante",
            curso=curso,
            estado_user="activo",
            password=senha 
        )
        

        messages.success(request, "Estudante adicionado com sucesso!")
        return redirect("add_estudante")

    return render(request, "admin/add_estudante.html", {
        "cursos": cursos,
    })


@login_required
def alterar_estado_multiplos_usuarios(request):
    if request.method == "POST":
        ids = request.POST.getlist("usuarios")
        acao = request.POST.get("acao")
        if ids and acao in ["activar", "desativar"]:
            novo_estado = "activo" if acao == "activar" else "desativado"
            Usuario.objects.filter(id__in=ids).update(estado_user=novo_estado)

    return redirect("lista_estudantes")



@login_required
def adicionar_recomendacao(request, tema_id):
    # Garantir que só tutores acessem
    if request.user.perfil != 'tutor':
        messages.error(request, "Acesso não autorizado.")
        return redirect('dashboard_tutor')

    tema = get_object_or_404(Tema, id=tema_id)

    # Pega todas as recomendações do tema Tela preta ....
    recomendacoes = tema.recomendacoes.all().order_by('-data_criacao')

    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if texto:
            Recomendacao.objects.create(
                tema=tema,
                tutor=request.user,
                texto=texto
            )
            messages.success(request, "Recomendação adicionada com sucesso.")
            return redirect('tutor_recomendacao', tema_id=tema.id)
        else:
            messages.error(request, "O campo de recomendação não pode estar vazio.")

    return render(request, 'tutor/recomendacao.html', {
        'tema': tema,
        'recomendacoes': recomendacoes
    })
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Recomendacao, Tema

@login_required
def todas_recomendacoes(request):
    temas_estudante = Tema.objects.filter(estudante=request.user)
    recomendacoes_qs = Recomendacao.objects.filter(tema__in=temas_estudante)

    # 1. Contamos as que AINDA não foram lidas antes de mudar o estado
    total_novas = recomendacoes_qs.filter(lida=False).count()

    # 2. Agora sim, marcamos todas como lidas no banco de dados
    recomendacoes_qs.filter(lida=False).update(lida=True)

    context = {
        # Ordenamos para a exibição
        'recomendacoes': recomendacoes_qs.order_by('-data_criacao'),
        # Passamos o valor que existia no momento do clique
    }
    return render(request, 'estudante/todas_recomendacoes.html', context)




def dashboard_presidencia(request):
    total_estudantes = Usuario.objects.filter(perfil="estudante").count()
    total_temas = Tema.objects.count()
    total_recomendacoes = Recomendacao.objects.count()

    ultimos_temas = Tema.objects.order_by('-id')[:5]

    context = {
        'total_estudantes': total_estudantes,
        'total_temas': total_temas,
        'total_recomendacoes': total_recomendacoes,
        'temas': ultimos_temas,
    }
    return render(request, 'admin/presidente.html', context)


def lista_todos_temas_geral(request):
    # O primeiro argumento deve ser o nome do campo ForeignKey no model Tema, que é 'estudante'
    temas = Tema.objects.select_related('estudante', 'estudante__curso').prefetch_related('recomendacoes').all()
    
    context = {
        'temas': temas
    }
    return render(request, 'Estudante/lista_geral_temas.html', context)
import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.staticfiles import finders

# ReportLab Core e Cores
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ReportLab Enums (Alinhamentos)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

# ReportLab Platypus (Componentes de layout)
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, 
    Table, TableStyle, HRFlowable, KeepTogether
)

def baixar_recomendacoes_pdf(request, estudante_id):
    # 1. Busca de Dados
    estudante = get_object_or_404(Usuario, id=estudante_id)
    recomendacoes = Recomendacao.objects.filter(
        tema__estudante=estudante
    ).select_related('tutor', 'tema').order_by('-data_criacao')
    
    curso_obj = getattr(estudante, 'curso', None)
    nome_curso = curso_obj.nome.upper() if curso_obj else "NÃO INFORMADO"
    nome_depto = nome_curso.split()[0] if nome_curso else "GERAL"

    # 2. Configuração do Response
    response = HttpResponse(content_type='application/pdf')
    nome_limpo = f"{estudante.nome}_{estudante.sobrenome}".replace(" ", "_")
    response['Content-Disposition'] = f'attachment; filename="Relatorio_{nome_limpo}.pdf"'

    # 3. Configuração do Documento
    doc = SimpleDocTemplate(
        response, 
        pagesize=A4, 
        rightMargin=50, leftMargin=50, topMargin=40, bottomMargin=60
    )
    elements = []

    # --- 4. DEFINIÇÃO DE ESTILOS ---
    styles = getSampleStyleSheet()
    
    # Estilo do Cabeçalho CENTRALIZADO
    style_inst_center = ParagraphStyle(
        'InstCenter', 
        fontSize=10, 
        fontName='Helvetica-Bold', 
        leading=14, 
        textColor=colors.HexColor("#1e293b"), 
        alignment=TA_CENTER
    )
    
    style_dept_center = ParagraphStyle(
        'DeptCenter', 
        fontSize=9, 
        fontName='Helvetica-Bold', 
        leading=12, 
        textColor=colors.HexColor("#64748b"), 
        alignment=TA_CENTER
    )

    style_h1 = ParagraphStyle('H1', fontSize=22, fontName='Helvetica-Bold', spaceAfter=10, textColor=colors.HexColor("#0f172a"), alignment=TA_LEFT)
    style_card_label = ParagraphStyle('CardLabel', fontSize=7, fontName='Helvetica-Bold', textColor=colors.HexColor("#94a3b8"), leading=10, spaceAfter=2)
    style_card_val = ParagraphStyle('CardVal', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor("#1e293b"), leading=12)
    style_rec_header = ParagraphStyle('RecHeader', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor("#2563eb"))
    style_rec_date = ParagraphStyle('RecDate', fontSize=8, fontName='Helvetica', textColor=colors.HexColor("#94a3b8"), alignment=TA_RIGHT)
    style_body = ParagraphStyle('Body', fontSize=10, fontName='Helvetica', leading=14, textColor=colors.HexColor("#334155"), alignment=TA_JUSTIFY)

    # --- 5. CABEÇALHO REESTRUTURADO ---
    relative_path = 'imgs/icons/finalispbie.jpg'
    logo_path = finders.find(relative_path) or os.path.join(settings.STATIC_ROOT, relative_path)
    
    try:
        logo = Image(logo_path, width=2.5*cm, height=2.5*cm)
    except:
        logo = Paragraph("<b>ISPB</b>", style_inst_center)

    # Texto do cabeçalho organizado em blocos
    header_text_content = [
        Paragraph("INSTITUTO SUPERIOR POLITÉCNICO DO BIÉ", style_inst_center),
        Paragraph(f"DEPARTAMENTO DE {nome_depto}", style_dept_center),
        Paragraph(f"CURSO DE {nome_curso}", style_dept_center),
    ]

    # Tabela de cabeçalho: Logo (Esquerda) | Texto (Centro)
    header_table = Table([[logo, header_text_content]], colWidths=[3*cm, 14*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (1,0), (1,0), -1*cm), # Ajuste para centralizar melhor o texto ignorando o offset da logo
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
    elements.append(Spacer(1, 20))

    # --- 6. IDENTIFICAÇÃO DO ESTUDANTE ---
    elements.append(Paragraph("Relatório Académico", style_h1))
    elements.append(Spacer(1, 10))
    
    temas_qs = Tema.objects.filter(estudante=estudante)
    tema_titulo = temas_qs[0].titulo if temas_qs.exists() else "TEMA NÃO DEFINIDO"

    card_data = [
        [Paragraph("ESTUDANTE", style_card_label), Paragraph("TEMA DE INVESTIGAÇÃO", style_card_label)],
        [Paragraph(f"{estudante.nome} {estudante.sobrenome}".upper(), style_card_val), 
         Paragraph(tema_titulo.upper(), style_card_val)]
    ]
    
    card_table = Table(card_data, colWidths=[6*cm, 11*cm])
    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(card_table)
    elements.append(Spacer(1, 35))

    # --- 7. HISTÓRICO DE ORIENTAÇÕES ---
    elements.append(Paragraph("HISTÓRICO DE ORIENTAÇÕES", style_card_label))
    elements.append(Spacer(1, 12))

    if not recomendacoes.exists():
        elements.append(Paragraph("Nenhum registo de orientação encontrado.", style_body))
    else:
        for rec in recomendacoes:
            data_str = rec.data_criacao.strftime('%d %b %Y • %H:%M')
            tutor_nome = rec.tutor.nome.upper() if rec.tutor else "ORIENTADOR"
            
            rec_content = [
                [Paragraph(f"● {tutor_nome}", style_rec_header), Paragraph(data_str, style_rec_date)],
                [Paragraph(rec.texto, style_body), ""]
            ]
            
            rec_table = Table(rec_content, colWidths=[12*cm, 5*cm])
            rec_table.setStyle(TableStyle([
                ('SPAN', (0,1), (1,1)),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,1), (-1,-1), 12),
                ('LINEBELOW', (0,1), (-1,1), 0.5, colors.HexColor("#f1f5f9")),
            ]))
            
            elements.append(KeepTogether(rec_table))
            elements.append(Spacer(1, 10))

    # --- 8. RODAPÉ ---
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.setStrokeColor(colors.HexColor("#f1f5f9"))
        canvas.line(50, 45, 545, 45)
        canvas.drawString(50, 30, "SGTF-ISPB | Sistema de Gestão de Trabalhos de Fim de Curso")
        canvas.drawRightString(545, 30, f"Documento Gerado Digitalmente • Pág. {doc.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    return response
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Tema, Usuario

@login_required
def adicionar_orientador(request, tema_id):
    # Garante que apenas a coordenação acesse
    if request.user.perfil != 'cordenacao':
        messages.error(request, "Acesso negado. Apenas a coordenação pode atribuir orientadores.")
        return redirect('admink')

    tema = get_object_or_404(Tema, id=tema_id)
    tutores = Usuario.objects.filter(perfil='tutor', estado_user='activo')

    if request.method == 'POST':
        tutor_id = request.POST.get('tutor')
        if tutor_id:
            tutor = get_object_or_404(Usuario, id=tutor_id)
            
            # Atribuição e Aprovação Automática
            tema.tutor_indicado = tutor
            tema.status_tutor = 'aprovado'
            tema.status_coordenacao = 'aprovado'
            # O método save() do seu model já cuidará de definir o status_final como 'aprovado'
            tema.save()
            
            messages.success(request, f"Orientador {tutor.nome} atribuído e tema aprovado com sucesso!")
            return redirect('lista_estudantes') # Ou a rota que desejar
        else:
            messages.error(request, "Por favor, selecione um orientador.")

    return render(request, 'admin/adicionar_orientador.html', {
        'tema': tema,
        'tutores': tutores
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash

@login_required
def atualizar_perfil(request):
    usuario = request.user

    if request.method == "POST":
        # Dados normais
        usuario.nome = request.POST.get("nome")
        usuario.sobrenome = request.POST.get("sobrenome")
        usuario.telefone = request.POST.get("telefone")

        if request.FILES.get("imagem"):
            usuario.imagem = request.FILES.get("imagem")

        # ---- ALTERAÇÃO DE SENHA (opcional) ----
        senha_atual = request.POST.get("senha_atual")
        nova_senha = request.POST.get("nova_senha")
        confirmar_senha = request.POST.get("confirmar_senha")

        if senha_atual or nova_senha or confirmar_senha:
            if not check_password(senha_atual, usuario.password):
                messages.error(request, "Senha actual incorreta.")
                return redirect("atualizar_perfil")

            if nova_senha != confirmar_senha:
                messages.error(request, "As novas senhas não coincidem.")
                return redirect("atualizar_perfil")

            if len(nova_senha) < 8:
                messages.error(request, "A nova senha deve ter pelo menos 8 caracteres.")
                return redirect("atualizar_perfil")

            usuario.set_password(nova_senha)
            update_session_auth_hash(request, usuario)

        usuario.save()
        messages.success(request, "Perfil atualizado com sucesso.")
        return redirect("atualizar_perfil")

    return render(request, "Estudante/atualizar_perfil.html")
