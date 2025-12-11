def acessibilidade_context(request):
    """Fornece configurações de acessibilidade para todos os templates"""
    config_default = {
        'tema': 'claro',
        'tamanho_fonte': 'medio'
    }
    
    # Recupera as configurações da sessão
    config_sessao = request.session.get('config_acessibilidade', {})
    
    # Garante que todos os campos existam
    config = {
        'tema': config_sessao.get('tema', config_default['tema']),
        'tamanho_fonte': config_sessao.get('tamanho_fonte', config_default['tamanho_fonte'])
    }
    
    return {
        'config_acessibilidade': config,
        'tema_atual': config['tema'],
        'tamanho_fonte_atual': config['tamanho_fonte']
    }