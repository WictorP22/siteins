import time

from flask import Flask, render_template, request, jsonify, json
import gspread, json, requests
from datetime import datetime
from flask_moment import Moment
from lista_membros import *
from blogger import *



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

#colocar site no ar
if __name__ == "__main__":
    app.run(debug=True)