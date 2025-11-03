"""
BOT DE PODCAST - CLAUDIÃO NEWS
Podcast diário com personalidade, curadoria e qualidade
VERSÃO COM GERAÇÃO DE ÁUDIO (gTTS)
"""

import requests
from datetime import datetime
import json
import os
from deep_translator import GoogleTranslator
import re
from gtts import gTTS
import time

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
    
    texto = texto.replace('[Removed]', '').replace('[removed]', '')
    texto = texto.replace('\n', ' ').replace('\r', ' ')
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()
    texto = re.sub(r'http[s]?://\S+', '', texto)
    texto = re.sub(r'O post .+ apareceu primeiro em .+', '', texto, flags=re.IGNORECASE)
    
    return texto

def eh_noticia_relevante(titulo, descricao):
    """Verifica se a notícia é relevante"""
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
    """Cria um resumo inteligente da notícia"""
    titulo = limpar_texto(titulo)
    descricao = limpar_texto(descricao)
    conteudo = limpar_texto(conteudo)
    
    if not descricao or len(descricao) < 20:
        return titulo
    
    if descricao.lower() in titulo.lower() or titulo.lower() in descricao.lower():
        if conteudo and len(conteudo) > 100:
            frases = conteudo.split('.')[:3]
            resumo = '. '.join(frases).strip()
            if len(resumo) > 50:
                return resumo + '.'
    
    if len(descricao) > 150:
        return descricao[:300] + ('...' if len(descricao) > 300 else '')
    else:
        return f"{descricao}"

# ============================================
# BUSCA DE NOTÍCIAS
# ============================================

def buscar_noticias_brasil_curadas():
    """Busca notícias do Brasil"""
    print("📰 Buscando notícias do Brasil com curadoria...")
    
    noticias_coletadas = []
    
    try:
        url = f'https://newsapi.org/v2/top-headlines?country=br&pageSize=20&apiKey={NEWSAPI_KEY}'
        resposta = requests.get(url, timeout=15)
        dados = resposta.json()
        
        if dados.get('status') == 'ok' and dados.get('articles'):
            noticias_coletadas.extend(dados['articles'])
            print(f"✅ Headlines BR: {len(dados['articles'])} notícias")
    except Exception as e:
        print(f"⚠️ Erro na busca: {e}")
    
    noticias_relevantes = []
    titulos_vistos = set()
    
    for noticia in noticias_coletadas:
        titulo = noticia.get('title', '')
        descricao = noticia.get('description', '')
        
        if titulo in titulos_vistos or not titulo:
            continue
        
        if not eh_noticia_relevante(titulo, descricao):
            continue
        
        titulos_vistos.add(titulo)
        noticias_relevantes.append(noticia)
        
        if len(noticias_relevantes) >= 5:
            break
    
    print(f"✅ {len(noticias_relevantes)} notícias relevantes do Brasil")
    return noticias_relevantes

def buscar_noticias_mundo_curadas():
    """Busca e traduz notícias internacionais"""
    print("🌍 Buscando notícias do mundo...")
    
    noticias = []
    paises = ['us', 'gb']
    
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
    
    noticias_curadas = []
    titulos_vistos = set()
    
    print("🔄 Traduzindo notícias internacionais...")
    
    for noticia in noticias:
        if len(noticias_curadas) >= 3:
            break
        
        titulo_original = noticia.get('title', '')
        descricao_original = noticia.get('description', '')
        
        if not titulo_original or titulo_original in titulos_vistos:
            continue
        
        titulo_traduzido = traduzir_texto(titulo_original)
        descricao_traduzida = traduzir_texto(descricao_original) if descricao_original else ""
        
        if not eh_noticia_relevante(titulo_traduzido, descricao_traduzida):
            continue
        
        noticia['title'] = titulo_traduzido
        noticia['description'] = descricao_traduzida
        
        titulos_vistos.add(titulo_traduzido)
        noticias_curadas.append(noticia)
    
    print(f"✅ {len(noticias_curadas)} notícias internacionais")
    return noticias_curadas

# ============================================
# CRIAÇÃO DO ROTEIRO
# ============================================

def criar_roteiro_claudiao(noticias_brasil, noticias_mundo):
    """Cria roteiro com personalidade do Claudião"""
    print("✍️ Criando roteiro do Claudião...")
    
    data_formatada, dia_semana = formatar_data_portugues()
    
    intros = [
        "E aí, meu povo! Bom dia, boa tarde ou boa noite, aqui é o Claudião!",
        "Salve, salve! Aqui é o Claudião dando as caras!",
        "Olá, olá! Claudinho na área!",
        "Fala galera! O Claudão chegou!",
    ]
    
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
            
            resumo = resumir_noticia(titulo, descricao)
            
            if not resumo or len(resumo) < 20:
                continue
            
            roteiro += f"{transicoes[i]}"
            roteiro += f"Segundo informações {'d' if fonte[0].lower() in 'aeiou' else 'd'}o {fonte}, "
            roteiro += f"{resumo}"
            roteiro += "\n\n"
    
    # TRANSIÇÃO
    if noticias_brasil and len(noticias_brasil) > 0:
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
            
            roteiro += f"{transicoes_mundo[i]}"
            roteiro += f"Segundo {'a' if fonte[0].lower() in 'aeiou' else 'o'} {fonte}, "
            roteiro += f"{resumo}"
            roteiro += "\n\n"
    
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
    """Cria versão visual formatada"""
    data_formatada, dia_semana = formatar_data_portugues()
    
    roteiro_visual = f"""╔══════════════════════════════════════════════════════════════╗
║              🎙️  CLAUDIÃO NEWS - PODCAST DIÁRIO            ║
║                    {data_formatada}                   ║
╚══════════════════════════════════════════════════════════════╝

{roteiro_tts}

════════════════════════════════════════════════════════════════
📰 FONTES E LINKS DAS NOTÍCIAS
════════════════════════════════════════════════════════════════

🇧🇷 BRASIL:
"""
    
    if noticias_brasil:
        for i, noticia in enumerate(noticias_brasil[:5], 1):
            titulo = noticia.get('title', 'Sem título')
            url = noticia.get('url', '')
            fonte = noticia.get('source', {}).get('name', '')
            
            roteiro_visual += f"\n{i}. {titulo}\n"
            roteiro_visual += f"   📰 {fonte}\n"
            roteiro_visual += f"   🔗 {url}\n"
    
    roteiro_visual += "\n🌍 MUNDO:\n"
    
    if noticias_mundo:
        for i, noticia in enumerate(noticias_mundo[:3], 1):
            titulo = noticia.get('title', 'Sem título')
            url = noticia.get('url', '')
            fonte = noticia.get('source', {}).get('name', '')
            
            roteiro_visual += f"\n{i}. {titulo}\n"
            roteiro_visual += f"   📰 {fonte}\n"
            roteiro_visual += f"   🔗 {url}\n"
    
    roteiro_visual += f"""
════════════════════════════════════════════════════════════════
📊 ESTATÍSTICAS
════════════════════════════════════════════════════════════════

Total: {len(noticias_brasil) + len(noticias_mundo)} notícias
Brasil: {len(noticias_brasil)} | Mundo: {len(noticias_mundo)}
Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
"""
    
    return roteiro_visual

# ============================================
# GERAÇÃO DE ÁUDIO (NOVO!)
# ============================================

def preparar_texto_para_tts(texto):
    """
    Prepara o texto para melhorar a pronúncia do gTTS
    """
    print("🔧 Preparando texto para TTS...")
    
    # Substituições para melhorar pronúncia
    texto = texto.replace('EUA', 'Estados Unidos')
    texto = texto.replace('UE', 'União Europeia')
    texto = texto.replace('ONU', 'Organização das Nações Unidas')
    texto = texto.replace('PIB', 'P I B')
    texto = texto.replace('CEO', 'C E O')
    texto = texto.replace('IA', 'inteligência artificial')
    texto = texto.replace('AI', 'inteligência artificial')
    
    # Adicionar pausas naturais
    texto = texto.replace('.\n\n', '. \n\n')  # Pausa entre parágrafos
    texto = texto.replace(': ', ':, ')  # Pausa após dois pontos
    
    return texto

def gerar_audio_gtts(texto, nome_arquivo):
    """
    Gera arquivo de áudio MP3 usando gTTS
    
    Args:
        texto: Texto a ser convertido em áudio
        nome_arquivo: Nome do arquivo MP3 (ex: 'podcast_2025-10-30.mp3')
    
    Returns:
        Caminho do arquivo gerado ou None se falhar
    """
    print(f"\n🔊 Gerando áudio com gTTS...")
    print(f"   Tamanho do texto: {len(texto)} caracteres")
    print(f"   Tempo estimado: 30-60 segundos...")
    
    try:
        # Preparar texto
        texto_preparado = preparar_texto_para_tts(texto)
        
        # IMPORTANTE: Configurações do gTTS
        tts = gTTS(
            text=texto_preparado,
            lang='pt',              # Português
            slow=False,             # Velocidade normal (True = mais lento)
            lang_check=False        # Não verificar idioma (mais rápido)
        )
        
        # Salvar arquivo
        tts.save(nome_arquivo)
        
        # Verificar se foi criado
        if os.path.exists(nome_arquivo):
            tamanho_mb = os.path.getsize(nome_arquivo) / (1024 * 1024)
            print(f"   ✅ Áudio gerado: {nome_arquivo}")
            print(f"   📊 Tamanho: {tamanho_mb:.2f} MB")
            return nome_arquivo
        else:
            print(f"   ❌ Erro: Arquivo não foi criado")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro ao gerar áudio: {e}")
        return None

def calcular_duracao_estimada(texto):
    """
    Estima duração do áudio baseado no número de palavras
    Velocidade média: ~150 palavras por minuto
    """
    palavras = len(texto.split())
    minutos = palavras / 150
    return int(minutos), int((minutos % 1) * 60)

# ============================================
# SALVAR ARQUIVOS
# ============================================

def salvar_arquivos(roteiro_tts, roteiro_visual, noticias_brasil, noticias_mundo, arquivo_audio=None):
    """Salva todos os arquivos do podcast"""
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    print("\n💾 Salvando arquivos...")
    
    # 1. Roteiro TTS
    arquivo_tts = f'podcast_roteiro_tts_{hoje}.txt'
    with open(arquivo_tts, 'w', encoding='utf-8') as f:
        f.write(roteiro_tts)
    print(f"  ✅ Roteiro TTS: {arquivo_tts}")
    
    # 2. Transcrição visual
    arquivo_visual = f'podcast_transcricao_{hoje}.txt'
    with open(arquivo_visual, 'w', encoding='utf-8') as f:
        f.write(roteiro_visual)
    print(f"  ✅ Transcrição: {arquivo_visual}")
    
    # 3. Metadados
    arquivo_json = f'podcast_metadados_{hoje}.json'
    
    minutos, segundos = calcular_duracao_estimada(roteiro_tts)
    
    metadados = {
        'data_geracao': datetime.now().isoformat(),
        'data_podcast': hoje,
        'apresentador': 'Claudião',
        'duracao_estimada': f"{minutos}min {segundos}s",
        'tem_audio': arquivo_audio is not None,
        'arquivo_audio': arquivo_audio if arquivo_audio else None,
        'estatisticas': {
            'total_noticias': len(noticias_brasil) + len(noticias_mundo),
            'noticias_brasil': len(noticias_brasil),
            'noticias_mundo': len(noticias_mundo),
            'caracteres': len(roteiro_tts),
            'palavras': len(roteiro_tts.split())
        },
        'fontes_brasil': [n.get('source', {}).get('name') for n in noticias_brasil],
        'fontes_mundo': [n.get('source', {}).get('name') for n in noticias_mundo]
    }
    
    with open(arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(metadados, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Metadados: {arquivo_json}")
    
    return arquivo_tts, arquivo_visual, arquivo_json

# ============================================
# FUNÇÃO PRINCIPAL
# ============================================

def gerar_podcast():
    """Executa todo o pipeline"""
    
    print("\n" + "="*70)
    print("🎙️  CLAUDIÃO NEWS - GERADOR DE PODCAST COM ÁUDIO")
    print("="*70 + "\n")
    
    inicio = time.time()
    
    # 1. Buscar notícias
    noticias_brasil = buscar_noticias_brasil_curadas()
    noticias_mundo = buscar_noticias_mundo_curadas()
    
    if not noticias_brasil and not noticias_mundo:
        print("\n❌ ERRO: Não foi possível buscar notícias!\n")
        return
    
    # 2. Criar roteiros
    roteiro_tts = criar_roteiro_claudiao(noticias_brasil, noticias_mundo)
    roteiro_visual = criar_roteiro_visual(noticias_brasil, noticias_mundo, roteiro_tts)
    
    # 3. Gerar áudio
    hoje = datetime.now().strftime('%Y-%m-%d')
    nome_audio = f'podcast_audio_{hoje}.mp3'
    
    arquivo_audio = gerar_audio_gtts(roteiro_tts, nome_audio)
    
    # 4. Salvar arquivos
    arquivo_tts, arquivo_visual, arquivo_json = salvar_arquivos(
        roteiro_tts, roteiro_visual, noticias_brasil, noticias_mundo, arquivo_audio
    )
    
    # 5. Relatório final
    tempo_total = time.time() - inicio
    minutos_estimados, segundos_estimados = calcular_duracao_estimada(roteiro_tts)
    
    print("\n" + "="*70)
    print("✅ PODCAST GERADO COM SUCESSO!")
    print("="*70)
    print(f"\n📊 Estatísticas:")
    print(f"  • Total de notícias: {len(noticias_brasil) + len(noticias_mundo)}")
    print(f"  • Notícias do Brasil: {len(noticias_brasil)}")
    print(f"  • Notícias do Mundo: {len(noticias_mundo)}")
    print(f"  • Duração estimada: {minutos_estimados}min {segundos_estimados}s")
    print(f"  • Tempo de geração: {tempo_total:.1f}s")
    print(f"\n📁 Arquivos gerados:")
    print(f"  • {arquivo_tts}")
    print(f"  • {arquivo_visual}")
    print(f"  • {arquivo_json}")
    if arquivo_audio:
        print(f"  • {arquivo_audio} 🎵")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    gerar_podcast()
