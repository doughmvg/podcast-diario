"""
BOT DE PODCAST - CLAUDIÃO NEWS
Podcast diário com personalidade, curadoria e qualidade
"""

import requests
from datetime import datetime
import json
import os
from deep_translator import GoogleTranslator
import re

# ============================================
# CONFIGURAÇÕES
# ============================================

NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '320e0a7059344e03abc65ce9f56c6c17')

# Palavras-chave para FILTRAR notícias irrelevantes
FILTROS_NEGATIVOS = [
    'loteria', 'quina', 'mega-sena', 'lotomania', 'resultado do jogo',
    'horóscopo', 'signo', 'fofoca', 'celebridade', 'BBB',
    'A Fazenda', 'reality show', 'resultado da loteria'
]

# Categorias relevantes para buscar
CATEGORIAS_RELEVANTES = [
    'economia', 'política', 'tecnologia', 'ciência', 'saúde',
    'educação', 'meio ambiente', 'segurança', 'infraestrutura'
]

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def traduzir_texto(texto):
    """Traduz texto para português brasileiro"""
    if not texto or texto.strip() == "" or len(texto) < 3:
        return ""
    
    try:
        translator = GoogleTranslator(source='auto', target='pt')
        if len(texto) > 4500:
            texto = texto[:4500]
        return translator.translate(texto)
    except Exception as e:
        print(f"⚠️ Erro ao traduzir: {e}")
        return texto

def limpar_texto(texto):
    """Remove caracteres problemáticos e limpa o texto"""
    if not texto:
        return ""
    
    # Remove [Removed], quebras de linha excessivas, etc
    texto = texto.replace('[Removed]', '').replace('[removed]', '')
    texto = texto.replace('\n', ' ').replace('\r', ' ')
    texto = re.sub(r'\s+', ' ', texto)  # Remove espaços múltiplos
    texto = texto.strip()
    
    # Remove URLs do meio do texto
    texto = re.sub(r'http[s]?://\S+', '', texto)
    
    # Remove "O post ... apareceu primeiro em ..."
    texto = re.sub(r'O post .+ apareceu primeiro em .+', '', texto, flags=re.IGNORECASE)
    
    return texto

def eh_noticia_relevante(titulo, descricao):
    """Verifica se a notícia é relevante (não é fofoca, loteria, etc)"""
    texto_completo = f"{titulo} {descricao}".lower()
    
    for filtro in FILTROS_NEGATIVOS:
        if filtro.lower() in texto_completo:
            return False
    
    return True

def formatar_data_portugues():
    """Retorna data formatada em português brasileiro"""
    hoje = datetime.now()
    
    meses = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    
    dias_semana = {
        0: 'segunda', 1: 'terça', 2: 'quarta', 3: 'quinta',
        4: 'sexta', 5: 'sábado', 6: 'domingo'
    }
    
    dia = hoje.day
    mes = meses[hoje.month]
    ano = hoje.year
    dia_semana = dias_semana[hoje.weekday()]
    
    return f"{dia} de {mes} de {ano}", dia_semana

def resumir_noticia(titulo, descricao, conteudo=""):
    """
    Cria um resumo inteligente da notícia
    Combina título, descrição e conteúdo para fazer um parágrafo coeso
    """
    # Limpar todos os textos
    titulo = limpar_texto(titulo)
    descricao = limpar_texto(descricao)
    conteudo = limpar_texto(conteudo)
    
    # Se não tem descrição, retorna só o título
    if not descricao or len(descricao) < 20:
        return titulo
    
    # Se a descrição é só repetição do título, tenta usar conteúdo
    if descricao.lower() in titulo.lower() or titulo.lower() in descricao.lower():
        if conteudo and len(conteudo) > 100:
            # Pega as primeiras 2-3 frases do conteúdo
            frases = conteudo.split('.')[:3]
            resumo = '. '.join(frases).strip()
            if len(resumo) > 50:
                return resumo + '.'
    
    # Combina título e descrição de forma natural
    if len(descricao) > 150:
        # Se a descrição é longa, usa ela
        return descricao[:300] + ('...' if len(descricao) > 300 else '')
    else:
        # Combina título com descrição
        return f"{descricao}"

# ============================================
# BUSCA DE NOTÍCIAS COM CURADORIA
# ============================================

def buscar_noticias_brasil_curadas():
    """Busca notícias do Brasil com curadoria de qualidade"""
    print("📰 Buscando notícias do Brasil com curadoria...")
    
    noticias_coletadas = []
    
    # Busca 1: Notícias gerais top headlines
    try:
        url = f'https://newsapi.org/v2/top-headlines?country=br&pageSize=15&apiKey={NEWSAPI_KEY}'
        resposta = requests.get(url, timeout=15)
        dados = resposta.json()
        
        if dados.get('status') == 'ok' and dados.get('articles'):
            noticias_coletadas.extend(dados['articles'])
            print(f"✅ Encontradas {len(dados['articles'])} notícias gerais")
    except Exception as e:
        print(f"⚠️ Erro na busca geral: {e}")
    
    # Busca 2: Por categorias relevantes
    for categoria in ['business', 'technology', 'health', 'science']:
        if len(noticias_coletadas) >= 20:
            break
        
        try:
            url = f'https://newsapi.org/v2/top-headlines?country=br&category={categoria}&pageSize=5&apiKey={NEWSAPI_KEY}'
            resposta = requests.get(url, timeout=15)
            dados = resposta.json()
            
            if dados.get('status') == 'ok' and dados.get('articles'):
                noticias_coletadas.extend(dados['articles'])
                print(f"✅ Notícias de {categoria}")
        except:
            pass
    
    # CURADORIA: Filtrar notícias relevantes
    noticias_relevantes = []
    titulos_vistos = set()
    
    for noticia in noticias_coletadas:
        titulo = noticia.get('title', '')
        descricao = noticia.get('description', '')
        
        # Pular se já vimos esse título
        if titulo in titulos_vistos or not titulo:
            continue
        
        # Pular se não é relevante
        if not eh_noticia_relevante(titulo, descricao):
            print(f"❌ Filtrada: {titulo[:50]}...")
            continue
        
        titulos_vistos.add(titulo)
        noticias_relevantes.append(noticia)
        
        if len(noticias_relevantes) >= 5:
            break
    
    print(f"✅ {len(noticias_relevantes)} notícias relevantes do Brasil selecionadas")
    return noticias_relevantes

def buscar_noticias_mundo_curadas():
    """Busca e traduz notícias internacionais relevantes"""
    print("🌍 Buscando notícias do mundo...")
    
    noticias = []
    
    # Buscar de múltiplas fontes internacionais
    paises = ['us', 'gb']  # EUA e Reino Unido
    
    for pais in paises:
        if len(noticias) >= 5:
            break
        
        try:
            url = f'https://newsapi.org/v2/top-headlines?country={pais}&pageSize=5&apiKey={NEWSAPI_KEY}'
            resposta = requests.get(url, timeout=15)
            dados = resposta.json()
            
            if dados.get('status') == 'ok' and dados.get('articles'):
                noticias.extend(dados['articles'])
        except:
            pass
    
    # Filtrar e traduzir
    noticias_curadas = []
    titulos_vistos = set()
    
    print("🔄 Traduzindo e curando notícias internacionais...")
    
    for noticia in noticias:
        if len(noticias_curadas) >= 3:
            break
        
        titulo_original = noticia.get('title', '')
        descricao_original = noticia.get('description', '')
        
        if not titulo_original or titulo_original in titulos_vistos:
            continue
        
        # Traduzir
        titulo_traduzido = traduzir_texto(titulo_original)
        descricao_traduzida = traduzir_texto(descricao_original) if descricao_original else ""
        
        # Verificar relevância após tradução
        if not eh_noticia_relevante(titulo_traduzido, descricao_traduzida):
            continue
        
        noticia['title'] = titulo_traduzido
        noticia['description'] = descricao_traduzida
        
        titulos_vistos.add(titulo_traduzido)
        noticias_curadas.append(noticia)
    
    print(f"✅ {len(noticias_curadas)} notícias internacionais selecionadas")
    return noticias_curadas

# ============================================
# CRIAÇÃO DO ROTEIRO COM PERSONALIDADE
# ============================================

def criar_roteiro_claudiao(noticias_brasil, noticias_mundo):
    """
    Cria roteiro com a personalidade do Claudião
    Tom amigável, piadas quando apropriado, informal mas informativo
    """
    print("✍️ Criando roteiro do Claudião...")
    
    data_formatada, dia_semana = formatar_data_portugues()
    
    # Variações de introdução do Claudião
    intros = [
        "E aí, meu povo! Bom dia, boa tarde ou boa noite, aqui é o Claudião!",
        "Salve, salve! Aqui é o Claudião dando as caras!",
        "Olá, olá! Claudinho na área!",
        "Fala galera! O Claudão chegou!",
    ]
    
    # Chamada fixa após a intro
    chamada_fixa = f"""Eu tô aqui pra te deixar por dentro do que tá rolando nesse mundão! Então pega seu cafézinho, seu chazinho, ou aquele lanchinho da tarde, e vem comigo que eu vou te tirar da caverna da desinformação!

Hoje é {dia_semana} feira, dia {data_formatada}, e eu separei as principais notícias do Brasil e do mundo pra você. Bora lá!

"""
    
    intro_escolhida = intros[datetime.now().day % len(intros)]
    
    roteiro = intro_escolhida + "\n\n" + chamada_fixa
    
    # BLOCO BRASIL
    if noticias_brasil and len(noticias_brasil) > 0:
        roteiro += "Vamos começar aqui de casa, com o que tá pegando no Brasil.\n\n"
        
        transicoes = [
            "Primeira notícia: ",
            "Olha só essa aqui: ",
            "Agora presta atenção nessa: ",
            "Tem mais: ",
            "E pra fechar o Brasil: "
        ]
        
        for i, noticia in enumerate(noticias_brasil[:5]):
            titulo = noticia.get('title', '')
            descricao = noticia.get('description', '')
            fonte = noticia.get('source', {}).get('name', 'uma fonte confiável')
            
            # Criar resumo inteligente
            resumo = resumir_noticia(titulo, descricao)
            
            if not resumo or len(resumo) < 20:
                continue
            
            # Detectar se é notícia pesada (não fazer piada)
            palavras_serias = ['morte', 'morto', 'morreu', 'assassinato', 'tragédia', 
                              'desastre', 'acidente grave', 'vítima', 'ataque']
            eh_seria = any(palavra in resumo.lower() for palavra in palavras_serias)
            
            # Montar o texto da notícia
            roteiro += f"{transicoes[i]}"
            roteiro += f"Segundo informações {'d' if fonte[0].lower() in 'aeiou' else 'd'}o {fonte}, "
            roteiro += f"{resumo}"
            
            # Adicionar comentário do Claudião quando apropriado
            if not eh_seria and i < 2:  # Só comenta nas primeiras 2 notícias
                if 'tecnologia' in resumo.lower() or 'startup' in resumo.lower():
                    roteiro += " Olha aí, a tecnologia não para!"
                elif 'economia' in resumo.lower() or 'dinheiro' in resumo.lower():
                    roteiro += " Bora ficar de olho no bolso, hein!"
                elif 'recorde' in resumo.lower() or 'conquista' in resumo.lower():
                    roteiro += " Isso é Brasil, meu amigo!"
            
            roteiro += "\n\n"
    else:
        roteiro += "Opa, tivemos um probleminha técnico aqui e não consegui pegar as notícias do Brasil hoje. Mas relaxa que as internacionais eu trouxe!\n\n"
    
    # TRANSIÇÃO PRO MUNDO
    roteiro += "Beleza, agora vamos dar um pulinho pra fora e ver o que tá acontecendo pelo mundo.\n\n"
    
    # BLOCO MUNDO
    if noticias_mundo and len(noticias_mundo) > 0:
        transicoes_mundo = [
            "Começando pelo internacional: ",
            "Olha essa do mundo: ",
            "E pra fechar as notícias de fora: "
        ]
        
        for i, noticia in enumerate(noticias_mundo[:3]):
            titulo = noticia.get('title', '')
            descricao = noticia.get('description', '')
            fonte = noticia.get('source', {}).get('name', 'fontes internacionais')
            
            resumo = resumir_noticia(titulo, descricao)
            
            if not resumo or len(resumo) < 20:
                continue
            
            palavras_serias = ['morte', 'morto', 'guerra', 'ataque', 'tragédia', 
                              'desastre', 'furacão', 'terremoto']
            eh_seria = any(palavra in resumo.lower() for palavra in palavras_serias)
            
            roteiro += f"{transicoes_mundo[i]}"
            roteiro += f"Segundo {'a' if fonte[0].lower() in 'aeiou' else 'o'} {fonte}, "
            roteiro += f"{resumo}"
            
            if not eh_seria and i == 0:
                if 'tecnologia' in resumo.lower():
                    roteiro += " A inovação não tem fronteiras!"
                elif 'economia' in resumo.lower():
                    roteiro += " O mundo dos negócios não para!"
            
            roteiro += "\n\n"
    else:
        roteiro += "Também não consegui as internacionais hoje, que azar! Mas amanhã eu volto com tudo!\n\n"
    
    # ENCERRAMENTO
    total_noticias = len(noticias_brasil) + len(noticias_mundo)
    
    roteiro += f"""E é isso, galera! Foram mais {total_noticias} notícias pra você não ficar por fora de nada.

Muito obrigado por ter me ouvido até aqui! Se você curtiu o conteúdo, me ajuda aí: deixa suas 5 estrelinhas na avaliação, isso me ajuda demais!

E não esquece de compartilhar com aquela pessoa que vive dizendo que não tem tempo de ler notícia. Manda pro amigo alienado, pro parente que só compartilha fake news, manda no grupo da família! Vamos espalhar informação de qualidade!

Amanhã eu volto com mais notícias fresquinhas. Até lá, se cuida, fica bem, e lembra: informação é poder!

Falou, galera! Claudião assinando embaixo!
"""
    
    return roteiro

def criar_roteiro_visual(noticias_brasil, noticias_mundo, roteiro_tts):
    """Cria versão visual formatada do roteiro"""
    data_formatada, dia_semana = formatar_data_portugues()
    
    roteiro_visual = f"""╔════════════════════════════════════════════════════════════╗
║              🎙️  CLAUDIÃO NEWS - PODCAST DIÁRIO            ║
║                    {data_formatada}                   ║
╚════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════
📝 ROTEIRO PARA LEITURA
═══════════════════════════════════════════

{roteiro_tts}

═══════════════════════════════════════════
📰 FONTES E LINKS DAS NOTÍCIAS
═══════════════════════════════════════════

🇧🇷 BRASIL:
"""
    
    if noticias_brasil:
        for i, noticia in enumerate(noticias_brasil[:5], 1):
            titulo = noticia.get('title', 'Sem título')
            url = noticia.get('url', '')
            fonte = noticia.get('source', {}).get('name', '')
            
            roteiro_visual += f"\n{i}. {titulo}\n"
            roteiro_visual += f"   📍 {fonte}\n"
            roteiro_visual += f"   🔗 {url}\n"
    
    roteiro_visual += "\n🌍 MUNDO:\n"
    
    if noticias_mundo:
        for i, noticia in enumerate(noticias_mundo[:3], 1):
            titulo = noticia.get('title', 'Sem título')
            url = noticia.get('url', '')
            fonte = noticia.get('source', {}).get('name', '')
            
            roteiro_visual += f"\n{i}. {titulo}\n"
            roteiro_visual += f"   📍 {fonte}\n"
            roteiro_visual += f"   🔗 {url}\n"
    
    roteiro_visual += f"""
═══════════════════════════════════════════
📊 ESTATÍSTICAS DO EPISÓDIO
═══════════════════════════════════════════

Total de notícias: {len(noticias_brasil) + len(noticias_mundo)}
Notícias do Brasil: {len(noticias_brasil)}
Notícias do Mundo: {len(noticias_mundo)}
Data de geração: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

Podcast gerado automaticamente pelo sistema Claudião News
"""
    
    return roteiro_visual

# ============================================
# SALVAR ARQUIVOS
# ============================================

def salvar_arquivos(roteiro_tts, roteiro_visual, noticias_brasil, noticias_mundo):
    """Salva todos os arquivos do podcast"""
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    # 1. Roteiro TTS (limpo)
    arquivo_tts = f'podcast_roteiro_tts_{hoje}.txt'
    with open(arquivo_tts, 'w', encoding='utf-8') as f:
        f.write(roteiro_tts)
    print(f"💾 Roteiro TTS: {arquivo_tts}")
    
    # 2. Roteiro visual (com links)
    arquivo_visual = f'podcast_transcricao_{hoje}.txt'
    with open(arquivo_visual, 'w', encoding='utf-8') as f:
        f.write(roteiro_visual)
    print(f"💾 Transcrição: {arquivo_visual}")
    
    # 3. Metadados
    arquivo_json = f'podcast_metadados_{hoje}.json'
    metadados = {
        'data_geracao': datetime.now().isoformat(),
        'data_podcast': hoje,
        'apresentador': 'Claudião',
        'estatisticas': {
            'total_noticias': len(noticias_brasil) + len(noticias_mundo),
            'noticias_brasil': len(noticias_brasil),
            'noticias_mundo': len(noticias_mundo)
        },
        'fontes_brasil': [n.get('source', {}).get('name') for n in noticias_brasil],
        'fontes_mundo': [n.get('source', {}).get('name') for n in noticias_mundo]
    }
    
    with open(arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(metadados, f, indent=2, ensure_ascii=False)
    print(f"📊 Metadados: {arquivo_json}")
    
    return arquivo_tts, arquivo_visual, arquivo_json

# ============================================
# FUNÇÃO PRINCIPAL
# ============================================

def gerar_podcast():
    """Gera o podcast completo do Claudião"""
    
    print("\n" + "═"*60)
    print("🎙️  CLAUDIÃO NEWS - GERADOR DE PODCAST")
    print("═"*60 + "\n")
    
    inicio = datetime.now()
    
    # 1. Buscar e curar notícias
    noticias_brasil = buscar_noticias_brasil_curadas()
    noticias_mundo = buscar_noticias_mundo_curadas()
    
    if not noticias_brasil and not noticias_mundo:
        print("\n❌ Não foi possível buscar notícias.")
        return False
    
    # 2. Criar roteiros
    roteiro_tts = criar_roteiro_claudiao(noticias_brasil, noticias_mundo)
    roteiro_visual = criar_roteiro_visual(noticias_brasil, noticias_mundo, roteiro_tts)
    
    # 3. Salvar arquivos
    arq_tts, arq_visual, arq_json = salvar_arquivos(
        roteiro_tts, roteiro_visual, noticias_brasil, noticias_mundo
    )
    
    fim = datetime.now()
    tempo = (fim - inicio).total_seconds()
    
    # 4. Resumo
    print("\n" + "═"*60)
    print("✅ PODCAST DO CLAUDIÃO GERADO!")
    print("═"*60)
    print(f"\n📄 Arquivos:")
    print(f"   ✓ {arq_tts} (para gerar áudio)")
    print(f"   ✓ {arq_visual} (leitura + links)")
    print(f"   ✓ {arq_json}")
    print(f"\n📊 Stats:")
    print(f"   • Brasil: {len(noticias_brasil)} | Mundo: {len(noticias_mundo)}")
    print(f"   • Tempo: {tempo:.1f}s")
    print("\n" + "═"*60 + "\n")
    
    return True

# ============================================
# EXECUTAR
# ============================================

if __name__ == "__main__":
    sucesso = gerar_podcast()
    
    if sucesso:
        print("🎉 Claudião News no ar!")
    else:
        print("😢 Falha na geração.")
