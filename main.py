from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

CATEGORIAS_PADRAO = [
    "Aluguel/Financiamento", "Condomínio", "Energia elétrica", "Água e esgoto",
    "Internet", "Telefone/Celular", "Transporte", "Mensalidade escolar",
    "Plano de saúde", "Seguros", "Supermercado", "Farmácia", "Gás de cozinha",
    "Refeições fora de casa", "Cuidados pessoais", "Cartão de crédito",
    "Empréstimos", "Parcelamentos", "Juros/Multas", "Lazer", "Compras",
    "Viagens", "Presentes", "Assinaturas", "Reparos domésticos",
    "Materiais de limpeza", "Móveis/Eletrodomésticos", "Equipamentos/Ferramentas",
    "Educação", "Pets", "Crianças", "Ajuda a parentes", "Outros"
]

app = Flask(__name__)
DATA_FILE = "dados_usuarios.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        usuarios = json.load(f)
else:
    usuarios = {"usuario": {"receita": 0.0, "gastos": []}}

def salvar_dados():
    with open(DATA_FILE, "w") as f:
        json.dump(usuarios, f, indent=2)

@app.route("/", methods=["GET", "POST"])
def index():
    usuario = usuarios["usuario"]

    if request.method == "POST":
        if "nova_categoria" in request.form and request.form.get("acao") == "nova_categoria":
            nova_categoria = request.form["nova_categoria"].strip()
            if nova_categoria and nova_categoria not in CATEGORIAS_PADRAO:
                CATEGORIAS_PADRAO.append(nova_categoria)
                CATEGORIAS_PADRAO.sort()
            return redirect(url_for("index"))
        elif "receita" in request.form:
            try:
                usuario["receita"] = float(request.form["receita"].replace(",", "."))
                salvar_dados()
            except ValueError:
                pass
        elif "descricao" in request.form:
            try:
                descricao = request.form["descricao"]
                valor = float(request.form["valor"].replace(",", "."))
                categoria = request.form["categoria"]
                data = datetime.strptime(request.form["data"], "%Y-%m-%d").strftime("%d/%m/%Y")

                if categoria not in CATEGORIAS_PADRAO:
                    CATEGORIAS_PADRAO.append(categoria)
                    CATEGORIAS_PADRAO.sort()

                gasto = {
                    "descricao": descricao,
                    "valor": valor,
                    "categoria": categoria,
                    "data": data
                }
                usuario["gastos"].append(gasto)
                salvar_dados()
            except ValueError:
                pass
        return redirect(url_for("index"))

    total_gastos = sum(g["valor"] for g in usuario["gastos"])
    saldo = usuario["receita"] - total_gastos
    percentual_restante = (saldo / usuario["receita"]) * 100 if usuario["receita"] > 0 else 0

    categorias = {}
    for g in usuario["gastos"]:
        categorias[g["categoria"]] = categorias.get(g["categoria"], 0) + g["valor"]

    return render_template("index.html", receita=usuario["receita"], gastos=usuario["gastos"],
                           total=total_gastos, saldo=saldo, restante=percentual_restante,
                           categorias=categorias, categorias_padrao=CATEGORIAS_PADRAO)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
