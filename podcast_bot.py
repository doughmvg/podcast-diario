"""
BOT DE PODCAST - CONFIGURADO E PRONTO
Gera podcast diário automaticamente
"""

import requests
from datetime import datetime
import json
import os

# ============================================
# CONFIGURAÇÕES
# ============================================

# API Key já configurada (você pode trocar depois por segurança)
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '320e0a7059344e03abc65ce9f56c6c17')

# ============================================
# FUNÇÕES DO BOT
# ============================================

def buscar_noticias_brasil():
    """Busca as principais notícias do Brasil"""
    print("📰 Buscando notícias do Brasil...")
    
    url = f'https://newsapi.org/v2/top-headlines?country=br&pageSize=5&apiKey={NEWSAPI_KEY}'
    
    try:
        resposta = requests.get(url, timeout=10)
        dados = resposta.json()
        
        if dados.get('status') == 'ok':
            print(f"✅ {len(dados['articles'])} notícias do Brasil encontradas")
            return dados['articles']
        else:
            print(f"❌ Erro ao buscar notícias: {dados.get('message')}")
            return []
    except Exception as erro:
        print(f"❌ Erro de conexão: {erro}")
        return []


def buscar_noticias_mundo():
    """Busca as principais notícias do mundo"""
    print("🌍 Buscando notícias do mundo...")
    
    url = f'https://newsapi.org/v2/top-headlines?country=us&pageSize=3&apiKey={NEWSAPI_KEY}'
    
    try:
        resposta = requests.get(url, timeout=10)
        dados = resposta.json()
        
        if dados.get('status') == 'ok':
            print(f"✅ {len(dados['articles'])} notícias do mundo encontradas")
            return dados['articles']
        else:
            print(f"❌ Erro ao buscar notícias: {dados.get('message')}")
            return []
    except Exception as erro:
        print(f"❌ Erro de conexão: {erro}")
        return []


def criar_roteiro(noticias_brasil, noticias_mundo):
    """Cria o roteiro do podcast em tom casual"""
    print("✍️ Criando roteiro do podcast...")
    
    hoje = datetime.now()
    data_formatada = hoje.strftime('%d de %B de %Y')
    
    dias_semana = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo']
    dia_semana = dias_semana[hoje.weekday()]
    
    saudacoes = {
        'segunda': 'Começando a semana bem informado!',
        'terça': 'Terça-feira e a gente continua ligado!',
        'quarta': 'Metade da semana, hora de atualizar!',
        'quinta': 'Quintou! E as notícias não param!',
        'sexta': 'Sextou! Mas antes, vamos às notícias!',
        'sábado': 'Final de semana, mas a informação não para!',
        'domingo': 'Domingão com aquele update maroto!'
    }
    
    # Montando o roteiro
    roteiro = f"""🎙️ PODCAST DE NOTÍCIAS DIÁRIAS
Data: {data_formatada}

═══════════════════════════════════════════
INTRODUÇÃO
═══════════════════════════════════════════

Eaí, beleza? {saudacoes[dia_semana]}

Hoje é {dia_semana}-feira, {data_formatada}, e eu trouxe pra você um resumo 
rápido e descontraído do que está rolando no Brasil e no mundo.

Pega seu café, senta confortável, e bora lá!


═══════════════════════════════════════════
🇧🇷 NOTÍCIAS DO BRASIL
═══════════════════════════════════════════

Vamos começar aqui de casa:

"""
    
    transicoes_br = [
        "Primeira parada: ",
        "Agora olha só isso: ",
        "Outra que chamou atenção: ",
        "E tem mais: ",
        "Pra fechar o Brasil: "
    ]
    
    # Adiciona notícias do Brasil
    for i, noticia in enumerate(noticias_brasil[:5]):
        titulo = noticia.get('title', 'Sem título')
        descricao = noticia.get('description', '')
        fonte = noticia.get('source', {}).get('name', 'Fonte desconhecida')
        
        roteiro += f"{transicoes_br[i]}{titulo}\n\n"
        
        if descricao:
            roteiro += f"{descricao}\n\n"
        
        roteiro += f"Informação do {fonte}.\n\n"
        roteiro += "─" * 50 + "\n\n"
    
    # Transição para notícias do mundo
    roteiro += """
═══════════════════════════════════════════
🌎 NOTÍCIAS DO MUNDO
═══════════════════════════════════════════

Agora vamos dar uma espiada no que está rolando lá fora:

"""
    
    transicoes_mundo = [
        "Do outro lado do Atlântico: ",
        "Enquanto isso no mundo: ",
        "E pra fechar as internacionais: "
    ]
    
    # Adiciona notícias do mundo
    for i, noticia in enumerate(noticias_mundo[:3]):
        titulo = noticia.get('title', 'Sem título')
        descricao = noticia.get('description', '')
        fonte = noticia.get('source', {}).get('name', 'Fonte desconhecida')
        
        roteiro += f"{transicoes_mundo[i]}{titulo}\n\n"
        
        if descricao:
            roteiro += f"{descricao}\n\n"
        
        roteiro += f"Fonte: {fonte}.\n\n"
        roteiro += "─" * 50 + "\n\n"
    
    # Encerramento
    roteiro += f"""
═══════════════════════════════════════════
ENCERRAMENTO
═══════════════════════════════════════════

E é isso, galera! Foram mais alguns minutos bem investidos pra você 
não ficar por fora de nada.

Se você curtiu, compartilha com aquela pessoa que vive dizendo que 
não tem tempo de ler notícia. Manda no grupo da família, espalha o 
conhecimento!

Amanhã eu volto com mais notícias fresquinhas. Até lá, se cuida e 
fica bem!

Valeu e até amanhã! 👋


═══════════════════════════════════════════
📊 ESTATÍSTICAS DO EPISÓDIO
═══════════════════════════════════════════

Total de notícias: {len(noticias_brasil) + len(noticias_mundo)}
Notícias do Brasil: {len(noticias_brasil)}
Notícias do Mundo: {len(noticias_mundo)}
Data de geração: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

Podcast gerado automaticamente por Bot de Notícias Diárias
"""
    
    return roteiro


def salvar_transcricao(roteiro):
    """Salva o roteiro em arquivo de texto"""
    hoje = datetime.now().strftime('%Y-%m-%d')
    nome_arquivo = f'podcast_transcricao_{hoje}.txt'
    
    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        arquivo.write(roteiro)
    
    print(f"💾 Transcrição salva: {nome_arquivo}")
    return nome_arquivo


def salvar_metadados(noticias_brasil, noticias_mundo):
    """Salva informações sobre o podcast em JSON"""
    hoje = datetime.now().strftime('%Y-%m-%d')
    nome_arquivo = f'podcast_metadados_{hoje}.json'
    
    metadados = {
        'data_geracao': datetime.now().isoformat(),
        'data_podcast': hoje,
        'estatisticas': {
            'total_noticias': len(noticias_brasil) + len(noticias_mundo),
            'noticias_brasil': len(noticias_brasil),
            'noticias_mundo': len(noticias_mundo)
        },
        'fontes_brasil': [n.get('source', {}).get('name') for n in noticias_brasil],
        'fontes_mundo': [n.get('source', {}).get('name') for n in noticias_mundo],
        'titulos_brasil': [n.get('title') for n in noticias_brasil],
        'titulos_mundo': [n.get('title') for n in noticias_mundo]
    }
    
    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        json.dump(metadados, arquivo, indent=2, ensure_ascii=False)
    
    print(f"📊 Metadados salvos: {nome_arquivo}")
    return nome_arquivo


def gerar_podcast():
    """Função principal que executa todo o processo"""
    
    print("\n" + "═"*60)
    print("🎙️  INICIANDO GERAÇÃO DO PODCAST DIÁRIO")
    print("═"*60 + "\n")
    
    inicio = datetime.now()
    
    # 1. Buscar notícias
    noticias_brasil = buscar_noticias_brasil()
    noticias_mundo = buscar_noticias_mundo()
    
    if not noticias_brasil and not noticias_mundo:
        print("\n❌ ERRO: Não foi possível buscar notícias.")
        print("   Verifique sua conexão com a internet e a API Key.")
        return False
    
    if not noticias_brasil:
        print("⚠️ AVISO: Nenhuma notícia do Brasil encontrada.")
    
    if not noticias_mundo:
        print("⚠️ AVISO: Nenhuma notícia do mundo encontrada.")
    
    # 2. Criar roteiro
    roteiro = criar_roteiro(noticias_brasil, noticias_mundo)
    
    # 3. Salvar arquivos
    arquivo_transcricao = salvar_transcricao(roteiro)
    arquivo_metadados = salvar_metadados(noticias_brasil, noticias_mundo)
    
    fim = datetime.now()
    tempo_total = (fim - inicio).total_seconds()
    
    # 4. Resumo final
    print("\n" + "═"*60)
    print("✅ PODCAST GERADO COM SUCESSO!")
    print("═"*60)
    print(f"\n📄 Arquivos criados:")
    print(f"   ✓ {arquivo_transcricao}")
    print(f"   ✓ {arquivo_metadados}")
    print(f"\n📊 Estatísticas:")
    print(f"   • Notícias do Brasil: {len(noticias_brasil)}")
    print(f"   • Notícias do Mundo: {len(noticias_mundo)}")
    print(f"   • Total de notícias: {len(noticias_brasil) + len(noticias_mundo)}")
    print(f"   • Tempo de execução: {tempo_total:.2f} segundos")
    
    print("\n" + "═"*60)
    print("📝 PREVIEW DO ROTEIRO (primeiras linhas):")
    print("═"*60)
    linhas = roteiro.split('\n')[:25]
    print('\n'.join(linhas))
    print("\n[...]\n")
    print("💡 Abra o arquivo de transcrição para ver o roteiro completo!")
    print("═"*60 + "\n")
    
    return True


# ============================================
# EXECUTAR O BOT
# ============================================

if __name__ == "__main__":
    sucesso = gerar_podcast()
    
    if sucesso:
        print("🎉 Processo concluído com sucesso!")
    else:
        print("😢 Algo deu errado. Verifique os erros acima.")
