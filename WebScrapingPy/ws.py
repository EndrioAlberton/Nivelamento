import requests  
from bs4 import BeautifulSoup  # html.parser padrão do Python ou Scrapy para processamento mais robusto
import os 
import zipfile 

def baixarEZipparPdf():
    # Define a URL base da página
    url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
    print("Entrando no site", url, "...")
    
    # Simula um navegador para evitar bloqueios do servidor
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Faz a requisição com timeout de 15 segundos
    try:
        resposta = requests.get(url, headers=headers, timeout=15)
        resposta.raise_for_status()  
    except requests.RequestException as e:
        print(f"Erro ao acessar o site: {e}")  # Corrige a string de formatação
        return 
    
    # Converte o HTML em um objeto BeautifulSoup
    sopa = BeautifulSoup(resposta.text, 'html.parser')
    pdfsBaixados = []
    
    # Obtém o diretório onde o script ws.py está localizado
    pasta_script = os.path.dirname(os.path.abspath(__file__))
    
    print("Buscando PDFs...")
    # Captura links da página (<a>)
    for link in sopa.find_all('a'):
        href = link.get('href') 
        if href and '.pdf' in href:  
            nomeLink = link.text  
            hrefOriginal = href 
            
            # Filtra links com 'Anexo_I' ou 'Anexo_II'
            if 'Anexo_I' in nomeLink or 'Anexo_II' in nomeLink or 'Anexo_I' in hrefOriginal or 'Anexo_II' in hrefOriginal:
                urlPdf = requests.compat.urljoin(url, hrefOriginal) if not hrefOriginal.startswith('http') else hrefOriginal
                print("Baixando:", urlPdf)
                try:
                    pdfResposta = requests.get(urlPdf, headers=headers, timeout=10, stream=True)
                    pdfResposta.raise_for_status() 
                    
                    # Verifica se é um PDF válido
                    if 'application/pdf' not in pdfResposta.headers.get('Content-Type', ''):
                        print(f"Erro: {urlPdf} não é um PDF válido")
                        continue
                    
                    # Define o caminho completo do arquivo na pasta do script
                    nomeArquivo = os.path.join(pasta_script, urlPdf.split('/')[-1])
                    if not nomeArquivo.endswith('.pdf'):  
                        nomeArquivo += '.pdf'
                    
                    # Salva o PDF em pedaços de 8KB na pasta do script
                    with open(nomeArquivo, 'wb') as arquivo:
                        for chunk in pdfResposta.iter_content(chunk_size=8192):
                            arquivo.write(chunk)
                    
                    # Verifica se o arquivo foi salvo corretamente
                    if os.path.getsize(nomeArquivo) > 0:
                        pdfsBaixados.append(nomeArquivo)
                        print("Baixado:", nomeArquivo)
                    else:
                        print(f"Erro: {nomeArquivo} está vazio")
                        os.remove(nomeArquivo)  
                except requests.RequestException as e:
                    print(f"Erro ao baixar {urlPdf}: {e}")
                    continue  
    
    if pdfsBaixados:
        nomeZip = os.path.join(pasta_script, "anexos.zip")  
        print("Criando ZIP...")
        with zipfile.ZipFile(nomeZip, 'w') as meuZip:
            for pdf in pdfsBaixados:
                meuZip.write(pdf, os.path.basename(pdf))
        
        for pdf in pdfsBaixados:
            os.remove(pdf)
            print(f"PDF removido: {pdf}")
        
        print("Tudo salvo em:", nomeZip, "!")
    else:
        print("Nenhum anexo encontrado para baixar")

# Executa a função
baixarEZipparPdf()