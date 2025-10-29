"""
BOT DE PODCAST - VERSÃO CORRIGIDA E OTIMIZADA PARA TTS
Gera podcast diário automaticamente em português brasileiro
"""

import requests
from datetime import datetime
import json
import os
from deep_translator import GoogleTranslator

# ============================================
# CONFIGURAÇÕES
# ============================================

NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '320e0a7059344e03abc65ce9f56c6c17')

# Configuração de locale para português
import locale
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except:
        pass  # Fallback manual se não conseguir configurar

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def traduzir_texto(texto):
    """Traduz texto para português brasileiro"""
    if not texto or texto.strip() == "":
        return ""
    
    try:
        translator = GoogleTranslator(source='auto', target='pt')
        # Dividir em partes menores se o texto for muito grande
        if len(texto) > 4500:
            texto = texto[:4500]
        return translator.translate(texto)
    except Exception as e:
        print(f"⚠️ Erro ao traduzir: {e}")
        return texto

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

# ============================================
# FUNÇÕES DE BUSCA DE NOTÍCIAS
# ============================================

def buscar_noticias_brasil():
    """Busca notícias do Brasil com múltiplas tentativas"""
    print("📰 Buscando notícias do Brasil...")
    
    noticias_coletadas = []
    
    # Tentativa 1: Notícias gerais do Brasil
    try:
        url = f'https://newsapi.org/v2/top-headlines?country=br&pageSize=10&apiKey={NEWSAPI_KEY}'
        resposta = requests.get(url, timeout=15)
        dados = resposta.json()
        
        if dados.get('status') == 'ok' and dados.get('articles'):
            noticias_coletadas.extend(dados['articles'])
            print(f"✅ Encontradas {len(dados['articles'])} notícias gerais do Brasil")
    except Exception as e:
        print(f"⚠️ Erro na busca geral Brasil: {e}")
    
    # Tentativa 2: Buscar por palavras-chave brasileiras
    if len(noticias_coletadas) < 3:
        palavras_chave = ['Brasil', 'Brasília', 'São Paulo', 'economia brasileira', 'governo']
        
        for palavra in palavras_chave:
            if len(noticias_coletadas) >= 5:
                break
            
            try:
                url = f'https://newsapi.org/v2/everything?q={palavra}&language=pt&sortBy=publishedAt&pageSize=3&apiKey={NEWSAPI_KEY}'
                resposta = requests.get(url, timeout=15)
                dados = resposta.json()
                
                if dados.get('status') == 'ok' and dados.get('articles'):
                    noticias_coletadas.extend(dados['articles'])
                    print(f"✅ Encontradas notícias sobre '{palavra}'")
            except Exception as e:
                print(f"⚠️ Erro buscando '{palavra}': {e}")
    
    # Remover duplicatas
    noticias_unicas = []
    titulos_vistos = set()
    
    for noticia in noticias_coletadas:
        titulo = noticia.get('title', '')
        if titulo and titulo not in titulos_vistos:
            titulos_vistos.add(titulo)
            noticias_unicas.append(noticia)
    
    print(f"✅ Total de notícias únicas do Brasil: {len(noticias_unicas)}")
    return noticias_unicas[:5]  # Retorna no máximo 5


def buscar_noticias_mundo():
    """Busca notícias internacionais e traduz para português"""
    print("🌍 Buscando notícias do mundo...")
    
    # Buscar de fontes internacionais
    url = f'https://newsapi.org/v2/top-headlines?country=us&pageSize=5&apiKey={NEWSAPI_KEY}'
    
    try:
        resposta = requests.get(url, timeout=15)
        dados = resposta.json()
        
        if dados.get('status') == 'ok' and dados.get('articles'):
            noticias = dados['articles']
            print(f"✅ Encontradas {len(noticias)} notícias internacionais")
            
            # Traduzir títulos e descrições
            print("🔄 Traduzindo notícias para português...")
            for noticia in noticias:
                if noticia.get('title'):
                    noticia['title'] = traduzir_texto(noticia['title'])
                if noticia.get('description'):
                    noticia['description'] = traduzir_texto(noticia['description'])
            
            print("✅ Notícias traduzidas")
            return noticias[:3]  # Retorna 3 notícias
        else:
            print(f"❌ Erro ao buscar notícias: {dados.get('message')}")
            return []
    except Exception as erro:
        print(f"❌ Erro de conexão: {erro}")
        return []


# ============================================
# CRIAÇÃO DO ROTEIRO OTIMIZADO PARA TTS
# ============================================

def criar_roteiro_tts(noticias_brasil, noticias_mundo):
    """
    Cria roteiro OTIMIZADO PARA TEXT-TO-SPEECH
    Remove símbolos, notações e comentários que não devem ser lidos
    """
    print("✍️ Criando roteiro otimizado para TTS...")
    
    data_formatada, dia_semana = formatar_data_portugues()
    
    saudacoes = {
        'segunda': 'Começando a semana bem informado!',
        'terça': 'Terça-feira e a gente continua ligado!',
        'quarta': 'Metade da semana, hora de se atualizar!',
        'quinta': 'Quintou! E as notícias não param!',
        'sexta': 'Sextou! Mas antes, vamos às notícias!',
        'sábado': 'Final de semana, mas a informação não para!',
        'domingo': 'Domingão com aquele update maroto!'
    }
    
    # ===========================================
    # ROTEIRO LIMPO (para TTS ler)
    # ===========================================
    
    roteiro_tts = f"""Eaí, beleza? {saudacoes[dia_semana]}

Hoje é {dia_semana} feira, {data_formatada}, e eu trouxe pra você um resumo rápido e descontraído do que está rolando no Brasil e no mundo.

Pega seu café, senta confortável, e bora lá!

"""
    
    # NOTÍCIAS DO BRASIL
    if noticias_brasil and len(noticias_brasil) > 0:
        roteiro_tts += "Vamos começar aqui de casa, com as notícias do Brasil.\n\n"
        
        transicoes_br = [
            "Primeira parada: ",
            "Agora olha só isso: ",
            "Outra que chamou atenção: ",
            "E tem mais: ",
            "Pra fechar o Brasil: "
        ]
        
        for i, noticia in enumerate(noticias_brasil[:5]):
            titulo = noticia.get('title', '').replace('[Removed]', '').strip()
            descricao = noticia.get('description', '').replace('[Removed]', '').strip()
            fonte = noticia.get('source', {}).get('name', 'Fonte desconhecida')
            
            if not titulo or titulo == "":
                continue
            
            # Limpar título e descrição de caracteres problemáticos
            titulo = titulo.replace('\n', ' ').replace('\r', ' ')
            descricao = descricao.replace('\n', ' ').replace('\r', ' ')
            
            roteiro_tts += f"{transicoes_br[i]}{titulo}.\n\n"
            
            if descricao and len(descricao) > 10:
                roteiro_tts += f"{descricao}\n\n"
            
            roteiro_tts += f"Informação do {fonte}.\n\n"
    else:
        roteiro_tts += "Infelizmente não conseguimos buscar notícias do Brasil no momento, mas vamos direto para as internacionais.\n\n"
    
    # TRANSIÇÃO PARA MUNDO
    roteiro_tts += "Agora vamos dar uma espiada no que está rolando lá fora.\n\n"
    
    # NOTÍCIAS DO MUNDO
    if noticias_mundo and len(noticias_mundo) > 0:
        transicoes_mundo = [
            "Do outro lado do Atlântico: ",
            "Enquanto isso no mundo: ",
            "E pra fechar as internacionais: "
        ]
        
        for i, noticia in enumerate(noticias_mundo[:3]):
            titulo = noticia.get('title', '').replace('[Removed]', '').strip()
            descricao = noticia.get('description', '').replace('[Removed]', '').strip()
            fonte = noticia.get('source', {}).get('name', 'Fonte desconhecida')
            
            if not titulo or titulo == "":
                continue
            
            titulo = titulo.replace('\n', ' ').replace('\r', ' ')
            descricao = descricao.replace('\n', ' ').replace('\r', ' ')
            
            roteiro_tts += f"{transicoes_mundo[i]}{titulo}.\n\n"
            
            if descricao and len(descricao) > 10:
                roteiro_tts += f"{descricao}\n\n"
            
            roteiro_tts += f"Fonte: {fonte}.\n\n"
    else:
        roteiro_tts += "Também não conseguimos notícias internacionais no momento. Tente novamente mais tarde.\n\n"
    
    # ENCERRAMENTO
    roteiro_tts += f"""E é isso, galera! Foram mais alguns minutos bem investidos pra você não ficar por fora de nada.

Se você curtiu, compartilha com aquela pessoa que vive dizendo que não tem tempo de ler notícia. Manda no grupo da família, espalha o conhecimento!

Amanhã eu volto com mais notícias fresquinhas. Até lá, se cuida e fica bem!

Valeu e até amanhã!
"""
    
    return roteiro_tts


def criar_roteiro_visual(noticias_brasil, noticias_mundo):
    """
    Cria roteiro VISUAL com formatação bonita (para você ler)
    Este NÃO será lido pelo TTS
    """
    data_formatada, dia_semana = formatar_data_portugues()
    
    roteiro_visual = f"""╔════════════════════════════════════════════════════════════╗
║           🎙️  PODCAST DE NOTÍCIAS DIÁRIAS                  ║
║                  {data_formatada}                    ║
╚════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════
📝 ROTEIRO COMPLETO (Para referência visual)
═══════════════════════════════════════════

[INTRODUÇÃO]

Eaí, beleza? {dia_semana} feira, {data_formatada}

"""
    
    # Adicionar notícias do Brasil
    if noticias_brasil:
        roteiro_visual += "\n[BLOCO 1 - NOTÍCIAS DO BRASIL]\n\n"
        for i, noticia in enumerate(noticias_brasil[:5], 1):
            titulo = noticia.get('title', 'Sem título')
            descricao = noticia.get('description', '')
            fonte = noticia.get('source', {}).get('name', 'Fonte desconhecida')
            url = noticia.get('url', '')
            
            roteiro_visual += f"Notícia BR {i}:\n"
            roteiro_visual += f"📰 {titulo}\n"
            if descricao:
                roteiro_visual += f"   {descricao}\n"
            roteiro_visual += f"   Fonte: {fonte}\n"
            roteiro_visual += f"   🔗 {url}\n\n"
    
    # Adicionar notícias do mundo
    if noticias_mundo:
        roteiro_visual += "\n[BLOCO 2 - NOTÍCIAS DO MUNDO]\n\n"
        for i, noticia in enumerate(noticias_mundo[:3], 1):
            titulo = noticia.get('title', 'Sem título')
            descricao = noticia.get('description', '')
            fonte = noticia.get('source', {}).get('name', 'Fonte desconhecida')
            url = noticia.get('url', '')
            
            roteiro_visual += f"Notícia Mundial {i}:\n"
            roteiro_visual += f"🌍 {titulo}\n"
            if descricao:
                roteiro_visual += f"   {descricao}\n"
            roteiro_visual += f"   Fonte: {fonte}\n"
            roteiro_visual += f"   🔗 {url}\n\n"
    
    roteiro_visual += """
[ENCERRAMENTO]

E é isso, galera! Até amanhã!

═══════════════════════════════════════════
📊 ESTATÍSTICAS
═══════════════════════════════════════════
"""
    
    roteiro_visual += f"""
Total de notícias: {len(noticias_brasil) + len(noticias_mundo)}
Notícias do Brasil: {len(noticias_brasil)}
Notícias do Mundo: {len(noticias_mundo)}
Data de geração: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
"""
    
    return roteiro_visual


# ============================================
# FUNÇÕES DE SALVAMENTO
# ============================================

def salvar_arquivos(roteiro_tts, roteiro_visual, noticias_brasil, noticias_mundo):
    """Salva os arquivos do podcast"""
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    # 1. Roteiro para TTS (LIMPO)
    arquivo_tts = f'podcast_roteiro_tts_{hoje}.txt'
    with open(arquivo_tts, 'w', encoding='utf-8') as f:
        f.write(roteiro_tts)
    print(f"💾 Roteiro TTS salvo: {arquivo_tts}")
    
    # 2. Roteiro visual (FORMATADO)
    arquivo_visual = f'podcast_transcricao_{hoje}.txt'
    with open(arquivo_visual, 'w', encoding='utf-8') as f:
        f.write(roteiro_visual)
    print(f"💾 Transcrição visual salva: {arquivo_visual}")
    
    # 3. Metadados JSON
    arquivo_json = f'podcast_metadados_{hoje}.json'
    metadados = {
        'data_geracao': datetime.now().isoformat(),
        'data_podcast': hoje,
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
    print(f"📊 Metadados salvos: {arquivo_json}")
    
    return arquivo_tts, arquivo_visual, arquivo_json


# ============================================
# FUNÇÃO PRINCIPAL
# ============================================

def gerar_podcast():
    """Executa todo o processo de geração do podcast"""
    
    print("\n" + "═"*60)
    print("🎙️  INICIANDO GERAÇÃO DO PODCAST DIÁRIO")
    print("═"*60 + "\n")
    
    inicio = datetime.now()
    
    # 1. Buscar notícias
    noticias_brasil = buscar_noticias_brasil()
    noticias_mundo = buscar_noticias_mundo()
    
    if not noticias_brasil and not noticias_mundo:
        print("\n❌ ERRO: Não foi possível buscar notícias.")
        return False
    
    # 2. Criar roteiros
    roteiro_tts = criar_roteiro_tts(noticias_brasil, noticias_mundo)
    roteiro_visual = criar_roteiro_visual(noticias_brasil, noticias_mundo)
    
    # 3. Salvar arquivos
    arq_tts, arq_visual, arq_json = salvar_arquivos(
        roteiro_tts, roteiro_visual, noticias_brasil, noticias_mundo
    )
    
    fim = datetime.now()
    tempo_total = (fim - inicio).total_seconds()
    
    # 4. Resumo
    print("\n" + "═"*60)
    print("✅ PODCAST GERADO COM SUCESSO!")
    print("═"*60)
    print(f"\n📄 Arquivos criados:")
    print(f"   ✓ {arq_tts} (para gerar áudio)")
    print(f"   ✓ {arq_visual} (para você ler)")
    print(f"   ✓ {arq_json} (metadados)")
    print(f"\n📊 Estatísticas:")
    print(f"   • Notícias do Brasil: {len(noticias_brasil)}")
    print(f"   • Notícias do Mundo: {len(noticias_mundo)}")
    print(f"   • Tempo de execução: {tempo_total:.2f} segundos")
    print("\n" + "═"*60 + "\n")
    
    return True


# ============================================
# EXECUTAR
# ============================================

if __name__ == "__main__":
    sucesso = gerar_podcast()
    
    if sucesso:
        print("🎉 Processo concluído!")
    else:
        print("😢 Algo deu errado.")
