import time

from flask import Flask, render_template, request, jsonify, json
from datetime import datetime
from flask_moment import Moment
from googleapiclient.discovery import build

Key = "AIzaSyDJMPIX2CuoHD1U6XSHUEzxXTcUd0dBdrU"  # Replace with your API key.

BlogID = "5826046378587679340"  # Replace with your BlogId here.

Roles = ["CSGO", "Garry's Mod", "GTA 5"]  # Add your server roles here.

blog = build("blogger", "v3", developerKey=Key)

import gspread, json, requests

gc = gspread.service_account(filename='service_acoount.json')
planilha_central = gc.open_by_key('1NeWXNJnloZ4n_4DoOy3v2XPx3Q2EIFQOO_8mtU6FabA')


#gc = gspread.service_account(filename='service_acoount.json')
#sh = gc.open_by_key('1SkdGGG_ke6rE_-PACEw8EIr5PeHEPRh-t0fnp46PX88')
#worksheet = sh.worksheet("Página120")
#valor = worksheet.get('A1:D3')

app = Flask(__name__)
moment = Moment()
moment.init_app(app)
# criar a 1ª página
# route -> localhost
#template

# cria JSON
@app.route("/_relatorios")
def relatorios():
    respostas = relatoriosEst.get('B6:I')
    return jsonify(respostas)

#index
@app.route("/")
def index():
    return render_template("indexmeu.html", podio=busca_podio())

#documentos
@app.route("/documentos")
def documentos():
    return render_template("docs.html", regimento=busca_anuncio('3073735437882198575'), penal=busca_anuncio('2651698189980401399'), apostilas=busca_apostilas())

#anuncios
@app.route("/anuncios")
def anuncios():
    return render_template("anuncios.html", anuncios=anuncios_blogger())

#anuncio
@app.route("/anuncio/<id>")
def anuncio(id):
    return render_template("anuncio.html", anuncio=busca_anuncio(id))


#url variavel
@app.route("/instrutor")
def instrutores():
    instrutor = request.args.get('policial')
    if instrutor == '':
        return render_template("indexmeu.html")
    else:
        return render_template("instrutor.html", instrutor=instrutor, dados=consulta_instrutor(instrutor))

#consultar instrutor
def consulta_instrutor(id):
    usuario = requests.get(f"https://www.habbo.com.br/api/public/users?name={id}")
    todo = json.loads(usuario.content)
    grupos = requests.get(f"https://www.habbo.com.br/api/public/groups/g-hhbr-16af3c950e9e4a38a510bd220f05c634/members")
    membros = json.loads(grupos.content)
    for membro in membros:
        if membro['uniqueId'] == todo['uniqueId']:
            grupo = 'true'
            break
        else:
            grupo = 'false'
    membro = busca_lista(id)
    if not hasattr(membro, 'Cargo'):
        cargo = '-'
    else:
        cargo = membro.Cargo

    return {
        "Nome": id,
        "Habbo": {
            "Missão": todo['motto'],
            "ID": todo['uniqueId'],
            "Online": todo['online'],
            "UltimaVez": todo['lastAccessTime'],
            "Visibilidade": todo['profileVisible'],
            "Grupo": grupo
        },
        "Membro": membro,
        "Historico": busca_historico_metas(id),
        "Avaliações": busca_avaliacoes(id),
        "Projetos": busca_projetos(id),
        "Infracoes": busca_infracoes(id),
        "História": busca_historia(id),
        "Parciais": busca_parcial(id, cargo)
    }

import gspread, json, requests
from datetime import datetime

gc = gspread.service_account(filename='service_acoount.json')
planilha_central = gc.open_by_key('1NeWXNJnloZ4n_4DoOy3v2XPx3Q2EIFQOO_8mtU6FabA')
def busca_lista(nick):
    aba_lista_de_membros = planilha_central.worksheet("[x] Lista de Membros")
    lista = aba_lista_de_membros.get('AE2:AP')
    for membro in lista:
        if membro[1] == nick:
            data = datetime.strptime(membro[2], '%d/%m/%Y')
            return {
                "Cargo": membro[0],
                "Nick": membro[1],
                "Entrada": data,
                "Promoção": membro[3],
                "CAP": membro[4],
                "PromoBloq": membro[5],
                "InicioLicença": membro[6],
                "FimLicença": membro[7],
                "Ministério": membro[8],
                "AV": membro[9],
                "TAGs": membro[10],
                "Situação": membro[11]
            }


def busca_historico_metas(nick):
    aba_historico_metas = planilha_central.worksheet('[x] Junta Tudo')
    metas = aba_historico_metas.get('L:U')
    retorno = []
    for meta in metas:
        if(meta[2] == nick):
            inicio = datetime.strptime(meta[0], '%d/%m/%Y')
            fim = datetime.strptime(meta[1], '%d/%m/%Y')
            retorno.append({
                "Inicio": inicio,
                "Fim": fim,
                "Professor": meta[2],
                "Meta1": meta[3],
                "Meta2": meta[4],
                "Meta3": meta[5],
                "Meta4": meta[6],
                "Meta5": meta[7],
                "Situação": meta[8],
                "Tipo": meta[9]
            })
    return retorno

def busca_avaliacoes(nick):
    aba_avaliacoes = planilha_central.worksheet('[x] Avaliações')
    avaliacoes = aba_avaliacoes.get('A:M')
    retorno = []
    for avaliacao in avaliacoes:
        if avaliacao[3] == nick:
            inicio = datetime.strptime(avaliacao[0], '%d/%m/%Y %H:%M:%S')
            fim = datetime.strptime(avaliacao[4], '%d/%m/%Y %H:%M:%S')
            retorno.append({
                "Inicio": inicio,
                "Fim": fim,
                "Avaliador": avaliacao[1],
                "Fake": avaliacao[2],
                "Instrutor": avaliacao[3],
                "Corredor": avaliacao[5],
                "Aula": avaliacao[6],
                "Teste": avaliacao[7],
                "Comandos": avaliacao[8],
                "Finalização": avaliacao[9],
                "Comentários": avaliacao[10],
                "Qualidade": avaliacao[11],
                "Anexos": avaliacao[12]
            })
    return retorno

def busca_infracoes(nick):
    aba_infracoes = planilha_central.worksheet('[x] Infrações')
    infracoes = aba_infracoes.get('J2:Q')
    retorno = []
    for infracao in infracoes:
        if infracao[2] == nick:
            data = datetime.strptime(infracao[4], '%d/%m/%Y')
            retorno.append({
                "data": data,
                "Fiscalizador": infracao[1],
                "Infrator": infracao[2],
                "Infração": infracao[3],
                "Anexo": infracao[5],
                "ID": infracao[0],
                "Gravidade": infracao[7]
            })
    return retorno

def busca_projetos(nick):
    aba_projetos = planilha_central.worksheet('[x] Projetos')
    projetos = aba_projetos.get('R2:W')
    retorno = []
    for projeto in projetos:
        if projeto[1] == nick:
            data = datetime.strptime(projeto[0], '%d/%m/%Y %H:%M:%S')
            retorno.append({
                "data": data,
                "Autor": projeto[1],
                "Modalidade": projeto[3],
                "Tema": projeto[4],
                "Veredito": projeto[5],
                "Ordem": projeto[2]
            })
    return retorno

def busca_historia(nick):
    aba_historia = planilha_central.worksheet('[x] História dos Instrutores')
    historias = aba_historia.get('B2:I')
    for historia in historias:
        if historia[0] == nick:
            return {
                "Cargo": historia[1],
                "história": historia[2],
                "Contribuições": historia[3],
                "Novatos": historia[4],
                "SubGrupos": historia[5],
                "Conquistas": historia[6],
                "Anos": historia[7]
            }

def busca_parcial(nick, cargo):
    aba_metas = planilha_central.worksheet('[x] Metas')
    print(cargo)
    if ((cargo == 'Instrutor') or (cargo == 'Aprendiz')):
        metas = aba_metas.get('A2:H')
        for meta in metas:
            if meta[0] == nick:
                return {
                    "Tipo": "Instrutor",
                    "Meta1": meta[1],
                    "Meta2": meta[2],
                    "Meta3": meta[3],
                    "Meta4": meta[4],
                    "Pontos": meta[5],
                    "Situação": meta[7]
                }
    elif cargo == 'Graduador':
        metas = aba_metas.get('R2:W')
        for meta in metas:
            if meta[0] == nick:
                return {
                    "Tipo": "Graduador",
                    "Meta1": meta[1],
                    "Meta2": meta[2],
                    "Meta3": "-",
                    "Meta4": "-",
                    "Pontos": meta[3],
                    "Situação": meta[5]
                }
    elif cargo == 'Avaliador':
        metas = aba_metas.get('AF2:AK')
        for meta in metas:
            if meta[0] == nick:
                return {
                    "Tipo": "Avaliador",
                    "Meta1": meta[1],
                    "Meta2": "-",
                    "Meta3": "-",
                    "Meta4": "-",
                    "Pontos": meta[2],
                    "Situação": meta[4]
                }
    elif cargo == 'Capacitador':
        metas = aba_metas.get('AS2:AW')
        for meta in metas:
            if meta[0] == nick:
                return {
                    "Tipo": "Capacitador",
                    "Meta1": meta[1],
                    "Meta2": "-",
                    "Meta3": "-",
                    "Meta4": "-",
                    "Pontos": meta[1],
                    "Situação": meta[3]
                }
    else:
        return {
            "Tipo": 'false'
        }

def busca_apostilas():
    aba_apostilas = planilha_central.worksheet('[x] Apostilas e Dicas')
    apostilas = aba_apostilas.get('A2:D')
    retorno = []
    for apostila in apostilas:
        data = datetime.strptime(apostila[0], '%d/%m/%Y')
        retorno.append({
            "Titulo": apostila[3],
            "Link": apostila[2],
            "Autor": apostila[1],
            "Data": data
        })
    return retorno

def busca_podio():
    aba_podio = planilha_central.worksheet('[x] Pódio')
    podio = aba_podio.get('A2:H4')
    retorno = []
    for pod in podio:
        print(pod)
        retorno.append({
            "Nick": pod[0],
            "CFSd": pod[1],
            "CFC1": pod[2],
            "CFC2": pod[3],
            "CAP": pod[4],
            "Pontos": pod[5],
            "Situação": pod[7]
        })
    return retorno

from googleapiclient.discovery import build
from datetime import datetime

Key = "AIzaSyDJMPIX2CuoHD1U6XSHUEzxXTcUd0dBdrU"  # Replace with your API key.

BlogID = "5826046378587679340"  # Replace with your BlogId here.

Roles = ["CSGO", "Garry's Mod", "GTA 5"]  # Add your server roles here.

blog = build("blogger", "v3", developerKey=Key)

def anuncios_blogger():
    posts = blog.posts().list(blogId=BlogID).execute()
    retorno = []
    for post in posts['items']:
        if ((post['labels'][0] == 'anuncio') or (post['labels'][0] == 'rápido') or (post['labels'][0] == 'ata')):
            publicado = post['updated'][0:19]
            data = datetime.strptime(publicado, '%Y-%m-%dT%H:%M:%S')
            retorno.append ({
                "Id": post['id'],
                "Title": post['title'],
                "Atualização": data,
                "Corpo": post['content'],
                "Tipo": post['labels'][0]
            })
    return retorno

def busca_anuncio(id):
    posts = blog.posts().list(blogId=BlogID).execute()
    for post in posts['items']:
        if post['id'] == id:
            publicado = post['updated'][0:19]
            data = datetime.strptime(publicado, '%Y-%m-%dT%H:%M:%S')
            return {
                "Id": post['id'],
                "Title": post['title'],
                "Atualização": data,
                "Corpo": post['content'],
                "Tipo": post['labels'][0]
            }
    return retorno

#colocar site no ar
if __name__ == "__main__":
    app.run(debug=True)