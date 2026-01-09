from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('gestao/', views.admink, name='admink'),
    path('estudante/', views.dashboard_estudante, name='dashboard_estudante'),
    path('estudante/criar-tema/', views.criar_ou_editar_tema, name='criar_ou_editar_tema'),
    path('sair/', views.sair, name='sair'),
    path('estudantes/', views.lista_estudantes, name='lista_estudantes'),
    path('estudantes/<int:tema_id>/status/<str:novo_status>/', 
         views.alterar_status_tema, 
         name='alterar_status_tema'),
    path('aprovados/', views.temas_aprovados, name='lista_aprovados'),
    path('reprovados/', views.temas_reprovados, name='lista_reprovados'),
    path('dashboard_tutor/',views.dashboard_tutor, name='dashboard_tutor'),
    path(
        'tema/<int:tema_id>/status/<str:novo_status>/',
        views.alterar_status_tema_tutor,
        name='alterar_status_tema_tutor' 
    ),
   
   path('alterar-status-multiplos-tutor/', views.alterar_status_multiplos_tutor, name='alterar_status_multiplos_tutor'),
   path('add_estudante/',views.add_estudante,name='add_estudante'),
   path("temas/alterar-multiplos/", views.alterar_status_multiplos, name="alterar_status_multiplos"),
   path(
    "usuarios/estado-multiplo/",
    views.alterar_estado_multiplos_usuarios,
    name="alterar_estado_multiplos_usuarios"
),
   path('tema/<int:tema_id>/recomendacoes/', views.adicionar_recomendacao, name='tutor_recomendacao'),
   path('recomendacoes/', views.todas_recomendacoes, name='todas_recomendacoes'),
   path('dashboard/', views.dashboard_presidencia, name='dashboard_presidencia'),
   path('estudantes/temas/geral/', views.lista_todos_temas_geral, name='lista_geral_temas'),
   path('estudante/<int:estudante_id>/baixar-recomendacoes/', views.baixar_recomendacoes_pdf, name='baixar_recomendacoes'),
   path('tema/<int:tema_id>/adicionar-orientador/', views.adicionar_orientador, name='adicionar_orientador'),
   path("perfil/atualizar/", views.atualizar_perfil, name="atualizar_perfil"),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
