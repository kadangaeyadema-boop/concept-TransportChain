# 🚀 Guide de Démarrage Rapide — TransportChain

## Prérequis
- Python 3.9 ou supérieur installé
- pip (gestionnaire de paquets Python)

---

## 1. Installation (une seule fois)

```bash
pip install flask flask-cors networkx pandas streamlit folium streamlit-folium
```

---

## 2. Lancer l'interface complète (recommandé)

```bash
cd interface
streamlit run app_streamlit.py
```

➜ Ouvre automatiquement http://localhost:8501 dans ton navigateur

---

## 3. Lancer l'API Flask seule (optionnel)

```bash
cd api
python app.py
```

➜ API disponible sur http://localhost:5000

Endpoints disponibles :
- GET  /stops              → liste des arrêts
- POST /route              → calcul de trajet
- POST /route/compare      → comparaison 3 modes
- POST /pay                → paiement blockchain
- GET  /blockchain         → état de la chaîne
- GET  /history/<address>  → historique utilisateur

---

## 4. Tester les modules individuellement

```bash
# Tester le graphe et l'optimisation
cd optimization
python graph_builder.py
python optimizer.py

# Tester la blockchain
cd blockchain
python blockchain.py
```

---

## 5. Structure du projet

```
projet_transport/
├── data/               # Dataset CSV (arrêts + segments)
├── optimization/       # Graphe NetworkX + Dijkstra
├── blockchain/         # Blockchain Python SHA-256
├── contracts/          # Smart contract Solidity
├── api/                # API REST Flask
├── interface/          # Interface Streamlit
└── requirements.txt
```

---

## 6. Déployer le smart contract (optionnel)

1. Ouvre https://remix.ethereum.org
2. Crée un fichier `TripPayment.sol` et colle le contenu de `contracts/TripPayment.sol`
3. Compile avec Solidity 0.8.19
4. Dans "Deploy & Run Transactions", sélectionne "Injected Provider - MetaMask"
5. Connecte MetaMask sur le réseau Sepolia Testnet
6. Clique "Deploy"

---

*Projet 8 — Plateforme de Transport Décentralisée — Mars 2026*
