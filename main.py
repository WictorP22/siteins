from flask import Flask, render_template, request, jsonify, json
import gspread, json, requests



#gc = gspread.service_account(filename='service_acoount.json')
#sh = gc.open_by_key('1SkdGGG_ke6rE_-PACEw8EIr5PeHEPRh-t0fnp46PX88')
#worksheet = sh.worksheet("Página120")
#valor = worksheet.get('A1:D3')

gc = gspread.service_account(filename='service_acoount.json')
relatorios = gc.open_by_key('1xdcuiK0IX1Z2QE1VeO_eUmtxI-wzP328pfMJwE5iKkc')
relatoriosEst = relatorios.get_worksheet(1)

lista_membros = gc.open_by_key('11ud_9VXt3bO5LngVCkJaC3mIM2op86e6RFA0JTRCp9Q')
listado = lista_membros.get_worksheet(0)


plan_metas_parcial = gc.open_by_key('12mbGProgrQnDfrkeau5UdLXtvm6KCqs0pg8T7hg6Xr4')
aba_metas_parcial = plan_metas_parcial.get_worksheet(2)

plan_historico = gc.open_by_key('1yJv5gCkXLvw3wxcTXVSkEZ474erm17RXtqIkAZxGfPA')
aba_metas = plan_historico.get_worksheet(0)

plan_avaliacoes = gc.open_by_key('1UQvOve1AdhNvpaGidXVk7BG7jogWjuVWrq2HvcoiI7Q')
aba_todas_av = plan_avaliacoes.worksheet('Completo')

plan_system = gc.open_by_key('1SkdGGG_ke6rE_-PACEw8EIr5PeHEPRh-t0fnp46PX88')
aba_projetos = plan_system.worksheet('[INS] Registros')

plan_form_historia = gc.open_by_key('1BD3yqT61GMDSTk8vVXWsBruNAqdaJe8f0hAInykMRvY')
aba_historia = plan_form_historia.get_worksheet(0)


app = Flask(__name__)

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
    return render_template("indexmeu.html")

#documentos
@app.route("/documentos")
def documentos():
    return render_template("docs.html")

#anuncios
@app.route("/anuncios")
def anuncios():
    return render_template("anuncios.html")

#url variavel
@app.route("/instrutor")
def instrutores():
    instrutor = request.args.get('policial')
    if instrutor == '':
        return render_template("indexmeu.html")
    else:
        historico = busca_historico(instrutor)
        hist = json.dumps(historico)
        av = busca_avs(instrutor)
        avs = json.dumps(av)
        projet = busca_projetos(instrutor)
        projetos = json.dumps(projet)
        return render_template("instrutor.html", instrutor=instrutor, dados=consulta_instrutor(instrutor), hist=hist, avs=avs, projetos=projetos)

#consultar instrutor
def consulta_instrutor(id):
    usuario = requests.get(f"https://www.habbo.com.br/api/public/users?name={id}")
    todo = json.loads(usuario.content)
    grupos = requests.get(f"https://www.habbo.com.br/api/public/groups/g-hhbr-16af3c950e9e4a38a510bd220f05c634/members")
    membros = json.loads(grupos.content)
    grupo = 'false'
    if busca_parcial(id) == None:
        user_parcial = ['-', '-', '-', '-', '-', '-', '-']
    else:
        user_parcial = busca_parcial(id)
    if not consulta_membros(id):
        dados_membro = [['-', '-', '-']]
    else:
        dados_membro = consulta_membros(id)
    for membro in membros:
        if membro['uniqueId'] == todo['uniqueId']:
            grupo = 'true'
    parciais = busca_historico(id)

    if not busca_historia(id):
        historico = ['-', '-', '-', '-', '-', '-', '-']
    else:
        historico = busca_historia(id)
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
        "Planilha": dados_membro,
        "Parcial": {
            "CFSd": user_parcial[1],
            "CFC1": user_parcial[2],
            "CFC2": user_parcial[3],
            "CAP": user_parcial[4],
            "Pontos": user_parcial[5]
        },
        "Historico": [parciais, len(parciais)],
        "História": {
            "Hist": historico[2],
            "Contribuições": historico[3],
            "Novatos": historico[4],
            "SubGrupos": historico[5],
            "Conquistas": historico[6]
        }
    }

#consulta listaMembros
def consulta_membros(nick):
    todos = listado.get('A2:D')
    retorno = []
    for linha in todos:
        for coluna in linha:
            if coluna == nick:
                retorno.append([linha[0], linha[1], linha[2]])
    return retorno

#busca parcial
def busca_parcial(nick):
    parciais = aba_metas_parcial.get("K3:P")
    for linha in parciais:
        for coluna in linha:
            if coluna == nick:
                return linha

#busca historico
def busca_historico(nick):
    metas = aba_metas.get("A:L")
    retorno = []
    for linha in metas:
        for coluna in linha:
            if coluna == nick:
                retorno.append([linha[0], linha[1], linha[2], linha[3], linha[4], linha[5], linha[6], linha[7], linha[8]])
    return retorno

#busca avs
def busca_avs(nick):
    avs = aba_todas_av.get('A:M')
    retorno = []
    for linha in avs:
        if linha[3] == nick:
            comentario = linha[10]
            newComent = comentario.replace('"', "'")
            retorno.append([linha[0], linha[1], linha[2], linha[3], linha[4], linha[5], linha[6], linha[7], linha[8], linha[9], str(newComent), linha[11], linha[12]])
    return retorno

#busca projetos
def busca_projetos(nick):
    projetos = aba_projetos.get('M6:U')
    retorno = []
    for linha in projetos:
        if linha[1] == nick:
            retorno.append([linha[0], linha[1], linha[2], linha[3], linha[4], linha[5]])
    return retorno

#busca historia
def busca_historia(nick):
    historia = aba_historia.get('B2:H')
    retorno = []
    for linha in historia:
        if linha[0] == nick:
            return linha

#colocar site no ar
if __name__ == "__main__":
    app.run(debug=True)