from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Usuario
from django.core.files.storage import FileSystemStorage
import os
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import json
from .models import Barbearia, Usuario,Agendamento



def pag_principal(request):
    return render(request, 'principal.html')

def Home(request):
    if not request.session.get('logado'):
        return redirect('loginatalho')
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        
        #verificação de tipo de usuario
        if usuario.tipo == 'barbearia':
            return redirect('barbeiroatalho')
        
        context = {
            'usuario': usuario,
            'foto_url': usuario.foto_perfil.url if usuario.foto_perfil else None
        }
        return render(request, 'home.html', context)
    except Usuario.DoesNotExist:
        return redirect('loginatalho')

def logout(request):
    request.session.flush()  # Limpa toda a sessão
    return redirect('loginatalho')

def perfil(request):
    if request.method == 'POST' and request.FILES.get('foto_perfil'):
        # Salva a foto no sistema de arquivos
        foto = request.FILES['foto_perfil']
        fs = FileSystemStorage()
        filename = fs.save(f'perfil/{request.user.id}_{foto.name}', foto)
        
        # Atualiza a foto no perfil do usuário
        usuario = request.user
        usuario.foto_perfil = filename
        usuario.save()
        
        # Retorna a URL da imagem para atualizar via JS
        return JsonResponse({'foto_url': fs.url(filename)})
    
    return render(request, 'perfil.html')

def barbearia(request):
    if not request.session.get('logado'):
        return redirect('loginatalho')
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        barbearias = Barbearia.objects.filter(ativa=True)
        
        context = {
            'barbearias': barbearias,
            'foto_url': usuario.foto_perfil.url if usuario.foto_perfil else None
        }
        return render(request, 'barbearias.html', context)
    except Usuario.DoesNotExist:
        return redirect('loginatalho')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        try:
            usuario = Usuario.objects.get(email=email)
            if usuario.verificar_senha(senha):
                request.session['usuario_id'] = usuario.id
                request.session['logado'] = True  # Sinaliza que está logado
                return redirect('Homeatalho')
            else:
                messages.error(request, "Senha incorreta")
        except Usuario.DoesNotExist:
            messages.error(request, "E-mail não cadastrado")
    
    return render(request, 'login.html')

def cadastro(request):
    erros = {'cadastro': None, 'login': None}
    
    if request.method == 'POST':
        if 'cadastrar' in request.POST:
            email = request.POST.get('email')
            senha = request.POST.get('senha')
            
            # Validação de email existente
            if Usuario.objects.filter(email=email).exists():
                erros['cadastro'] = "Este e-mail já está cadastrado"
            # Validação de senha com mínimo de 8 caracteres
            elif len(senha) < 8:
                erros['cadastro'] = "A senha deve ter no mínimo 8 caracteres"
            else:
                novo_usuario = Usuario(
                    email=email,
                    senha=request.POST.get('senha'),
                    nome=request.POST.get('nome'),
                    sobrenome=request.POST.get('sobrenome'),
                    tipo=request.POST.get('tipo', 'cliente')
                )
                novo_usuario.save()
                request.session['cadastro_sucesso'] = True
                return redirect('loginatalho')
    
    return render(request, 'cadastro.html', erros)

def limpar_sessao_sucesso(request):
    if 'cadastro_sucesso' in request.session:
        del request.session['cadastro_sucesso']
    return JsonResponse({'status': 'ok'})

def perfil(request):
    if not request.session.get('logado'):
        return redirect('loginatalho')
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
    except Usuario.DoesNotExist:
        return redirect('loginatalho')
    
    context = {
        'usuario': usuario,
        'foto_url': usuario.foto_perfil.url if usuario.foto_perfil else None
    }
    return render(request, 'perfil.html', context)

def upload_foto_perfil(request):
    if request.method == 'POST' and request.FILES.get('foto_perfil'):
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
            
            # Remove a foto antiga se existir (agora usando Cloudinary)
            if usuario.foto_perfil:
                # O Cloudinary gerencia automaticamente o armazenamento,
                # então não precisamos nos preocupar em excluir arquivos físicos
                pass
            
            # Salva a nova foto diretamente no modelo
            foto = request.FILES['foto_perfil']
            usuario.foto_perfil = foto
            usuario.save()
            
            return JsonResponse({
                'status': 'success', 
                'foto_url': usuario.foto_perfil.url
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error'}, status=400)

def atualizar_perfil(request):
    if request.method == 'POST':
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
            
            # Atualiza os campos
            usuario.nome = request.POST.get('nome', usuario.nome)
            usuario.sobrenome = request.POST.get('sobrenome', usuario.sobrenome)
            usuario.email = request.POST.get('email', usuario.email)
            usuario.telefone = request.POST.get('telefone', usuario.telefone)
            usuario.cpf = request.POST.get('cpf', usuario.cpf)
            
            # Atualiza senha se foi fornecida
            nova_senha = request.POST.get('senha')
            if nova_senha:
                usuario.senha = make_password(nova_senha)
            
            usuario.save()
            
            # Redirecionamento específico para barbeiros
            if usuario.tipo == 'barbearia':
                return redirect('barbeiroatalho')
            else:
                return redirect('Homeatalho')
                
        except Exception as e:
            messages.error(request, f'Erro ao atualizar perfil: {str(e)}')
            if usuario.tipo == 'barbearia':  # Corrigido: use 'usuario' em vez de 'request.user'
                return redirect('perfil_barbeiroatalho')  # Use o nome correto da URL
            else:
                return redirect('perfilatalho')
    
    return redirect('loginatalho')

def deletar_conta(request):
    if request.method == 'POST':
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
            
            # Com Cloudinary, não precisamos excluir arquivos manualmente
            # O Cloudinary gerencia automaticamente o armazenamento
            
            usuario.delete()
            request.session.flush()
            return redirect('pag_inicial_atalho')
        
        except Exception as e:
            messages.error(request, f'Erro ao excluir conta: {str(e)}')
            return redirect('perfilatalho')
    
    return redirect('perfilatalho')

def barbeiro_pag(request):
    if not request.session.get('logado'):
        return redirect('loginatalho')
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        
        # Verificação de tipo de usuario
        if usuario.tipo != 'barbearia':
            return redirect('Homeatalho')
        
        context = {
            'usuario': usuario,
            'foto_url': usuario.foto_perfil.url if usuario.foto_perfil else None
        }
        return render(request, "pagina_barbeiro.html", context)
    except Usuario.DoesNotExist:
        return redirect('loginatalho')

def cadastro_barbearia(request):
    # Verifica se o usuário está logado
    if not request.session.get('logado'):
        return redirect('loginatalho')
    
    try:
        
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        
        
        if hasattr(usuario, 'barbearia'):
            messages.warning(request, 'Você já possui uma barbearia cadastrada!')
            return redirect('barbeiroatalho')
            
    except (Usuario.DoesNotExist, KeyError):
        messages.error(request, "Sessão inválida. Faça login novamente.")
        return redirect('loginatalho')

    if request.method == 'POST':
        try:
            # Cria a barbearia associada ao usuário existente
            barbearia = Barbearia.objects.create(
                usuario=usuario,  # Associa ao usuário logado
                nome_barbearia=request.POST['nome_barbearia'],
                telefone_comercial=request.POST['telefone_comercial'],
                endereco=request.POST['endereco'],
                cidade=request.POST['cidade'],
                estado=request.POST['estado'],
                foto_logo=request.FILES.get('logo-upload'),
                status_barbearia=request.POST.get('status_barbearia', 'aberto')
            )

            # Atualiza o tipo do usuário para barbearia
            if usuario.tipo != 'barbearia':
                usuario.tipo = 'barbearia'
                usuario.save()

            messages.success(request, 'Barbearia cadastrada com sucesso!')
            return redirect('barbeiroatalho')

        except Exception as e:
            print(f"Erro ao cadastrar barbearia: {str(e)}")
            messages.error(request, f'Erro ao cadastrar barbearia: {str(e)}')
    
    # Contexto para o template
    context = {
        'usuario': usuario,
        'nome_completo': f"{usuario.nome} {usuario.sobrenome}",
        'email': usuario.email,
        'telefone': usuario.telefone
    }
    
    return render(request, 'cadastro_barbearia.html', context)

def editar_horarios(request):
    if not request.session.get('logado'):
        return redirect('loginatalho')
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        barbearia = Barbearia.objects.get(usuario=usuario)
        
        if request.method == 'POST':
            horarios = {}
            for dia in ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']:
                horarios[dia] = {
                    'abertura': request.POST.get(f'{dia}_abertura', ''),
                    'fechamento': request.POST.get(f'{dia}_fechamento', '')
                }
            barbearia.horarios_funcionamento = horarios
            barbearia.save()
            return redirect('barbeiroatalho')
        
        context = {
            'barbearia': barbearia,
            'horarios': barbearia.horarios_funcionamento
        }
        return render(request, 'editar_horarios.html', context)
    
    except (Usuario.DoesNotExist, Barbearia.DoesNotExist):
        return redirect('loginatalho')
    
def minha_barbearia(request):
    if not request.session.get('logado'):
        return redirect('loginatalho')
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        barbearia = Barbearia.objects.get(usuario=usuario)
    except (Usuario.DoesNotExist, KeyError):
        messages.error(request, "Sessão inválida. Faça login novamente.")
        return redirect('loginatalho')
    except Barbearia.DoesNotExist:
        messages.warning(request, "Você ainda não possui uma barbearia cadastrada.")
        return redirect('cadastro_barbatalho')

    if request.method == 'POST':
        if 'excluir_barbearia' in request.POST:
            barbearia.delete()
            messages.success(request, "Barbearia excluída com sucesso!")
            return redirect('barbeiroatalho')
        
        try:
            
            barbearia.nome_barbearia = request.POST['nome_barbearia']
            barbearia.telefone_comercial = request.POST['telefone_comercial']
            barbearia.endereco = request.POST['endereco']
            barbearia.cidade = request.POST['cidade']
            barbearia.estado = request.POST['estado']
            
            
            barbearia.status_barbearia = request.POST.get('status_barbearia', 'aberto')
            
            if 'logo-upload' in request.FILES:
                barbearia.foto_logo = request.FILES['logo-upload']
            
            barbearia.save()
            messages.success(request, 'Barbearia atualizada com sucesso!')
            return redirect('barbeiroatalho')

        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {str(e)}')

    context = {
        'barbearia': barbearia,
        'usuario': usuario,
    }
    
    return render(request, 'minha_barbearia.html', context)

def perfil_barb(request):
    if not request.session.get('logado'):
        return redirect('loginatalho')
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        context = {
            'usuario': usuario,
            'foto_url': usuario.foto_perfil.url if usuario.foto_perfil else None
        }
        return render(request, 'perfil_barb.html', context)
    except Usuario.DoesNotExist:
        return redirect('loginatalho')

def buscar_horarios(request):
    barbearia_id = request.GET.get('barbearia_id')
    data_str = request.GET.get('data')
    
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        dia_semana = data.strftime('%A').lower()
        
        barbearia = Barbearia.objects.get(id=barbearia_id)
        horarios = barbearia.horarios_funcionamento.get(dia_semana, {})
        
        if horarios.get('fechado', True):
            return JsonResponse({'horarios': []})
        
        horarios_disponiveis = []
        abertura = datetime.strptime(horarios['abertura'], '%H:%M').time()
        fechamento = datetime.strptime(horarios['fechamento'], '%H:%M').time()
        
        current = datetime.combine(data, abertura)
        end = datetime.combine(data, fechamento)
        
        while current < end:
            horarios_disponiveis.append(current.strftime('%H:%M'))
            current += timedelta(minutes=30)
        
        return JsonResponse({'horarios': horarios_disponiveis})
    except Exception as e:
        return JsonResponse({'horarios': [], 'error': str(e)})

@csrf_exempt
def criar_agendamento(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            barbearia = Barbearia.objects.get(id=data['barbearia_id'])
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
            
            # FORÇAR UTC explicitamente
            from django.utils import timezone
            agora_utc = timezone.now()  # Já é UTC quando USE_TZ = True
            
            # Criar agendamento com horário UTC
            agendamento = Agendamento.objects.create(
                barbearia=barbearia,
                cliente=usuario,
                data_criacao=agora_utc,
                horario=agora_utc.time()  # Adiciona o horário UTC
            )
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Agendamento realizado com sucesso!',
                'agendamento_id': agendamento.id,
                'data_criacao': agora_utc.isoformat(),  # Para debug
                'horario': agora_utc.time().isoformat()  # Para debug
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'})

def meus_agendamentos(request):
    if not request.session.get('logado'):
        return redirect('loginatalho')
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        
        meus_agendamentos = Agendamento.objects.filter(
            cliente=usuario,
            confirmado=False  
        )
        
        if not meus_agendamentos.exists():
            messages.warning(request, 'Você não está na fila de nenhuma barbearia. Entre em uma!')
            return redirect('barbeariaatalho')
        
       
        barbearias_ids = meus_agendamentos.values_list('barbearia', flat=True).distinct()
        
       
        agendamentos = Agendamento.objects.filter(
            barbearia__in=barbearias_ids,
            confirmado=False  
        ).order_by('data', 'horario')
        
       
        for agendamento in agendamentos:
            agendamento.eh_meu = (agendamento.cliente.id == usuario.id)
        
        context = {
            'agendamentos': agendamentos,
            'foto_url': usuario.foto_perfil.url if usuario.foto_perfil else None,
            'barbearias': Barbearia.objects.filter(id__in=barbearias_ids)
        }
        return render(request, 'agendamento_cliente.html', context)
        
    except Usuario.DoesNotExist:
        return redirect('loginatalho')
    
@csrf_exempt
def cancelar_agendamento(request, agendamento_id):
    if request.method == 'POST':
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
            agendamento = Agendamento.objects.get(id=agendamento_id, cliente=usuario)
            agendamento.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Agendamento cancelado com sucesso!'
            })
        except Agendamento.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Agendamento não encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido'
    }, status=405)

def agendamentos_barbeiro(request):
    if not request.session.get('logado'):
        return redirect('loginatalho')
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        
        # Verifica se o usuário tem uma barbearia cadastrada
        try:
            barbearia = Barbearia.objects.get(usuario=usuario)
        except Barbearia.DoesNotExist:
            messages.warning(request, 'Para ver os agendamentos dos seus clientes você precisa ter uma barbearia cadastrada!')
            return redirect('cadastro_barbatalho')
        
        agendamentos = Agendamento.objects.filter(barbearia=barbearia).order_by('-data', '-horario')
        
        context = {
            'agendamentos': agendamentos,
            'foto_url': usuario.foto_perfil.url if usuario.foto_perfil else None
        }
        return render(request, 'agendamento_barb.html', context)
        
    except Usuario.DoesNotExist:
        return redirect('loginatalho')

@csrf_exempt
def confirmar_agendamento(request, agendamento_id):
    if request.method == 'POST':
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
            barbearia = Barbearia.objects.get(usuario=usuario)
            agendamento = Agendamento.objects.get(
                id=agendamento_id, 
                barbearia=barbearia,
                confirmado=False  # Só confirma se ainda não estiver confirmado
            )
            
            agendamento.confirmado = True
            agendamento.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Agendamento confirmado com sucesso!'
            })
        except Agendamento.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Agendamento não encontrado ou já confirmado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido'
    }, status=405)

@csrf_exempt
def cancelar_agendamento_barbeiro(request, agendamento_id):
    if request.method == 'POST':
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
            barbearia = Barbearia.objects.get(usuario=usuario)
            agendamento = Agendamento.objects.get(id=agendamento_id, barbearia=barbearia)
            
            agendamento.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Agendamento cancelado com sucesso!'
            })
        except Agendamento.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Agendamento não encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido'
    }, status=405)

def verificar_status_barbearia(request, barbearia_id):
    try:
        barbearia = Barbearia.objects.get(id=barbearia_id)
        return JsonResponse({
            'status': barbearia.status_barbearia,
            'nome': barbearia.nome_barbearia
        })
    except Barbearia.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Barbearia não encontrada'}, status=404)

def verificar_agendamento_ativo(request):
    if not request.session.get('logado'):
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        agendamento_ativo = Agendamento.objects.filter(
            cliente=usuario,
            confirmado=False  # Verifica agendamentos não confirmados também
        ).exists()
        
        return JsonResponse({'possui_agendamento': agendamento_ativo})
    except (Usuario.DoesNotExist, KeyError):
        return JsonResponse({'error': 'Usuário não encontrado'}, status=404)

@csrf_exempt
def cancelar_agendamento_barbeiro(request, agendamento_id):
    if request.method == 'POST':
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
            barbearia = Barbearia.objects.get(usuario=usuario)
            agendamento = Agendamento.objects.get(id=agendamento_id, barbearia=barbearia)
            
            agendamento.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Agendamento cancelado com sucesso!'
            })
        except Agendamento.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Agendamento não encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido'
    }, status=405)

# views.py - Adicione esta view
@csrf_exempt
def salvar_horario_estimado(request, agendamento_id):
    if request.method == 'POST':
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
            barbearia = Barbearia.objects.get(usuario=usuario)
            agendamento = Agendamento.objects.get(
                id=agendamento_id, 
                barbearia=barbearia
            )
            
            data = json.loads(request.body)
            horario_estimado = data.get('horario_estimado')
            
            if horario_estimado:
                agendamento.horario_estimado = horario_estimado
                agendamento.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Horário estimado salvo com sucesso!',
                    'horario_estimado': horario_estimado
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Horário estimado não fornecido'
                }, status=400)
                
        except Agendamento.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Agendamento não encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido'
    }, status=405)

# Adicione também uma view para o cliente buscar seu horário estimado
@csrf_exempt
def buscar_meu_horario_estimado(request):
    if not request.session.get('logado'):
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    try:
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        
        # Busca o agendamento ativo do usuário
        agendamento = Agendamento.objects.filter(
            cliente=usuario,
            confirmado=False
        ).first()
        
        if agendamento and agendamento.horario_estimado:
            return JsonResponse({
                'possui_horario': True,
                'horario_estimado': agendamento.horario_estimado.strftime('%H:%M')
            })
        else:
            return JsonResponse({
                'possui_horario': False,
                'horario_estimado': None
            })
            
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
        
@csrf_exempt
def alterar_tema(request):
    """Altera entre tema claro e escuro"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tema = data.get('tema', 'claro')
            
            # Recupera ou inicializa as configurações
            config = request.session.get('config_acessibilidade', {})
            config['tema'] = tema
            request.session['config_acessibilidade'] = config
            request.session.modified = True
            
            return JsonResponse({
                'status': 'success', 
                'tema': tema,
                'message': 'Tema alterado com sucesso!'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'})

@csrf_exempt
def alterar_tamanho_fonte(request):
    """Altera o tamanho da fonte"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tamanho = data.get('tamanho', 'medio')
            
            # Valida o tamanho
            tamanhos_validos = ['pequeno', 'medio', 'grande', 'muito_grande']
            if tamanho not in tamanhos_validos:
                return JsonResponse({'status': 'error', 'message': 'Tamanho inválido'})
            
            # Recupera ou inicializa as configurações
            config = request.session.get('config_acessibilidade', {})
            config['tamanho_fonte'] = tamanho
            request.session['config_acessibilidade'] = config
            request.session.modified = True
            
            return JsonResponse({
                'status': 'success', 
                'tamanho_fonte': tamanho,
                'message': 'Tamanho da fonte alterado com sucesso!'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'})

def resetar_acessibilidade(request):
    """Reseta todas as configurações de acessibilidade"""
    if 'config_acessibilidade' in request.session:
        del request.session['config_acessibilidade']
    
    return JsonResponse({'status': 'success', 'message': 'Configurações resetadas!'})

def esqueci_senha(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            acao = data.get('acao')
            
            if acao == 'solicitar_codigo':
                email = data.get('email', '').strip()
                
                # Verifica se o email existe no banco de dados
                try:
                    usuario = Usuario.objects.get(email=email)
                    
                    # Gera código de 6 dígitos
                    codigo = str(random.randint(100000, 999999))
                    
                    # Salva o código e email na sessão
                    request.session['reset_email'] = email
                    request.session['reset_codigo'] = codigo
                    request.session['reset_codigo_valido_ate'] = (
                        datetime.now() + timedelta(minutes=5)
                    ).isoformat()
                    
                    return JsonResponse({
                        'status': 'success',
                        'codigo': codigo,
                        'mensagem': 'Código de verificação gerado com sucesso'
                    })
                    
                except Usuario.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'mensagem': 'Email não cadastrado no sistema'
                    }, status=404)
            
            elif acao == 'verificar_codigo':
                email = request.session.get('reset_email')
                codigo_sessao = request.session.get('reset_codigo')
                codigo_valido_ate = request.session.get('reset_codigo_valido_ate')
                codigo_digitado = data.get('codigo', '')
                
                # Verifica se o código ainda é válido
                if codigo_valido_ate:
                    valido_ate = datetime.fromisoformat(codigo_valido_ate)
                    if datetime.now() > valido_ate:
                        return JsonResponse({
                            'status': 'error',
                            'mensagem': 'Código expirado. Solicite um novo.'
                        })
                
                # Verifica se o código está correto
                if codigo_digitado == codigo_sessao:
                    # Marca o código como verificado
                    request.session['reset_codigo_verificado'] = True
                    return JsonResponse({
                        'status': 'success',
                        'mensagem': 'Código verificado com sucesso'
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'mensagem': 'Código incorreto'
                    })
            
            elif acao == 'redefinir_senha':
                email = request.session.get('reset_email')
                senha = data.get('senha', '')
                
                # Verifica se o código foi verificado
                if not request.session.get('reset_codigo_verificado'):
                    return JsonResponse({
                        'status': 'error',
                        'mensagem': 'Código não verificado'
                    })
                
                # Valida a senha
                if len(senha) < 8:
                    return JsonResponse({
                        'status': 'error',
                        'mensagem': 'A senha deve ter no mínimo 8 caracteres'
                    })
                
                try:
                    # Busca o usuário e atualiza a senha no banco de dados
                    usuario = Usuario.objects.get(email=email)
                    usuario.senha = make_password(senha)
                    usuario.save()
                    
                    # Limpa a sessão
                    keys_to_remove = ['reset_email', 'reset_codigo', 
                                    'reset_codigo_valido_ate', 'reset_codigo_verificado']
                    for key in keys_to_remove:
                        if key in request.session:
                            del request.session[key]
                    
                    return JsonResponse({
                        'status': 'success',
                        'mensagem': 'Senha alterada com sucesso! Você já pode fazer login.'
                    })
                    
                except Usuario.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'mensagem': 'Usuário não encontrado'
                    }, status=404)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'mensagem': 'Erro ao processar a solicitação'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'mensagem': f'Erro interno: {str(e)}'
            }, status=500)
    
    return render(request, 'esqueci_senha.html')



