# TransportChain — Plateforme de Transport Décentralisée

Plateforme multimodale (bus, vélo, trottinette, marche) avec optimisation IA et blockchain.

## Structure du projet

```
projet_transport/
├── data/
│   ├── stops.csv          # Dataset des arrêts
│   ├── segments.csv       # Dataset des segments/connexions
│   └── graph.json         # Graphe exporté (généré)
├── optimization/
│   ├── graph_builder.py   # Construction du graphe NetworkX
│   └── optimizer.py       # Algorithme Dijkstra multi-objectif
├── blockchain/
│   └── blockchain.py      # Blockchain simulée Python (SHA-256)
├── contracts/
│   └── TripPayment.sol    # Smart contract Solidity (Ethereum)
├── api/
│   └── app.py             # API REST Flask
├── interface/
│   └── app_streamlit.py   # Interface utilisateur Streamlit
└── requirements.txt
```

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

### Option 1 : Interface Streamlit (recommandé)
```bash
cd interface
streamlit run app_streamlit.py
```

### Option 2 : API Flask seule
```bash
cd api
python app.py
```

## Endpoints API

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/stops` | Liste tous les arrêts |
| POST | `/route` | Calcule le trajet optimal |
| POST | `/route/compare` | Compare les 3 modes |
| POST | `/pay` | Enregistre un paiement blockchain |
| GET | `/blockchain` | État de la blockchain |
| GET | `/history/<address>` | Historique utilisateur |
| GET | `/transaction/<tx_id>` | Détail d'une transaction |

## Modes d'optimisation

- **rapide** : α=0.8, β=0.2 (priorité temps)
- **economique** : α=0.2, β=0.8 (priorité prix)
- **equilibre** : α=0.5, β=0.5 (compromis)

## Exemple d'appel API

```bash
curl -X POST http://localhost:5000/route \
  -H "Content-Type: application/json" \
  -d '{"depart_id": 1, "arrivee_id": 3, "mode": "rapide"}'
```
