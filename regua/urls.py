# principal/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from regua2.views import pag_principal, Home, perfil, barbearia, cadastro, login, limpar_sessao_sucesso,buscar_meu_horario_estimado, logout, atualizar_perfil, deletar_conta, upload_foto_perfil, barbeiro_pag, cadastro_barbearia, minha_barbearia, perfil_barb, criar_agendamento, buscar_horarios, meus_agendamentos, cancelar_agendamento
from regua2.views import agendamentos_barbeiro, suporte, esqueci_senha, alterar_tema, alterar_tamanho_fonte, resetar_acessibilidade,  confirmar_agendamento, cancelar_agendamento_barbeiro, verificar_status_barbearia, salvar_horario_estimado, verificar_agendamento_ativo, cancelar_agendamento_barbeiro
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', pag_principal, name='pag_inicial_atalho'),
    path('Home/', Home, name='Homeatalho'),
    path('suporte/', suporte, name='suporteatalho'),
    path('esqueci_senha/', esqueci_senha, name='esquecisenhaatalho'),
    path('perfil/', perfil, name='perfilatalho'),
    path('perfil_barb/', perfil_barb, name='perfil_barbeiroatalho'),
    path('barbearias/', barbearia, name='barbeariaatalho'),
    path('cadastro/', cadastro, name='autenticar'),
    path('login/', login, name='loginatalho'),
    path('limpar-sessao-sucesso/', limpar_sessao_sucesso, name='limpar_sessao'),
    path('logout/', logout, name='logout'),
    path('atualizar-perfil/', atualizar_perfil, name='atualizar_perfil'),
    path('deletar-conta/', deletar_conta, name='deletar_conta'),
    path('upload-foto-perfil/', upload_foto_perfil, name='upload_foto_perfil'),
    path('pag_barb', barbeiro_pag, name='barbeiroatalho'),
    path('cadastro_barb', cadastro_barbearia, name='cadastro_barbatalho'),
    path("minha_barb", minha_barbearia, name="minha_barbatalho"),
    path('criar-agendamento/', criar_agendamento, name='criar_agendamento'),
    path('agendamento_cliente', meus_agendamentos, name="agendamento_clienteatalho"),
    path('cancelar-agendamento/<int:agendamento_id>/', cancelar_agendamento, name='cancelar_agendamento'),
    path('agendamentos-barbeiro/', agendamentos_barbeiro, name='agendamentos_barbeiro'),
    path('confirmar-agendamento/<int:agendamento_id>/', confirmar_agendamento, name='confirmar_agendamento'),
    path('cancelar-agendamento-barbeiro/<int:agendamento_id>/', cancelar_agendamento_barbeiro, name='cancelar_agendamento_barbeiro'),
    path('verificar-status-barbearia/<int:barbearia_id>/', verificar_status_barbearia, name='verificar_status_barbearia'),
    path('verificar-agendamento-ativo/', verificar_agendamento_ativo, name='verificar_agendamento_ativo'),
    path('cancelar-agendamento-barbeiro/<int:agendamento_id>/', cancelar_agendamento_barbeiro, name='cancelar_agendamento_barbeiro'),
    path('salvar-horario-estimado/<int:agendamento_id>/', salvar_horario_estimado, name='salvar_horario_estimado'),
    path('buscar-meu-horario-estimado/', buscar_meu_horario_estimado, name='buscar_meu_horario_estimado'),
    path('alterar-tema/', alterar_tema, name='alterar_tema'),
    path('alterar-tamanho-fonte/', alterar_tamanho_fonte, name='alterar_tamanho_fonte'),
    path('resetar-acessibilidade/', resetar_acessibilidade, name='resetar_acessibilidade'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

