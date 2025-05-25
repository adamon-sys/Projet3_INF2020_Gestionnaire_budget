from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER
from uuid import uuid4  # Déplace ici pour tout le fichier
import json
import os

DATA_FILE = "transactions.json"

def charger_transactions():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                contenu = f.read().strip()
                if not contenu:
                    return []  # Fichier vide
                return json.loads(contenu)
        except json.JSONDecodeError:
            print("⚠️ Erreur de lecture JSON : fichier corrompu, réinitialisation.")
            return []
    return []


def sauvegarder_transactions():
    with open(DATA_FILE, "w") as f:
        json.dump(transactions, f)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

transactions = charger_transactions()

@app.get("/", response_class=HTMLResponse)
async def afficher_formulaire(request: Request):
    global transactions
    solde = 0
    revenu = 0
    depense = 0

    for t in transactions:
        if t["categorie"] == "Revenu":
            revenu += t["montant"]
            solde += t["montant"]
        elif t["categorie"] == "Dépense":
            depense += t["montant"]
            solde -= t["montant"]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "transactions": transactions,
        "solde": solde,
        "revenu": revenu,
        "depense": depense
    })

@app.post("/ajouter")
async def ajouter_transaction(
    request: Request,
    description: str = Form(...),
    montant: float = Form(...),
    categorie: str = Form(...)
):
    global transactions
    transactions.append({
        "id": str(uuid4()),
        "description": description,
        "montant": montant,
        "categorie": categorie
    })
    sauvegarder_transactions()
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

@app.get("/supprimer/{transaction_id}")
async def supprimer_transaction(transaction_id: str):
    global transactions
    transactions = [t for t in transactions if t["id"] != transaction_id]
    sauvegarder_transactions()
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

@app.get("/reinitialiser")
async def reinitialiser_transactions():
    global transactions
    transactions.clear()
    sauvegarder_transactions()
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)
