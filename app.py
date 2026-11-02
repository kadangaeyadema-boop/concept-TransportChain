"""
Semaine 4 - API REST Flask
Connecte le module d'optimisation et la blockchain
Plateforme de transport décentralisée
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'optimization'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'blockchain'))

from flask import Flask, request, jsonify
from flask_cors import CORS
from optimizer import TransportOptimizer
from blockchain import get_blockchain

app = Flask(__name__)
CORS(app)

# Compteur de trajet global
_trip_counter = 1000


def next_trip_id():
    global _trip_counter
    _trip_counter += 1
    return _trip_counter


# ==================
#  Routes API
# ==================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'api': 'Plateforme Transport Décentralisée',
        'version': '1.0',
        'endpoints': ['/stops', '/route', '/pay', '/blockchain', '/history/<address>']
    })


@app.route('/stops', methods=['GET'])
def get_stops():
    """Retourne la liste de tous les arrêts disponibles."""
    opt = TransportOptimizer()
    stops = opt.get_all_stops()
    return jsonify({'stops': stops, 'total': len(stops)})


@app.route('/route', methods=['POST'])
def calculate_route():
    """
    Calcule le trajet optimal.
    Body JSON: { depart_id, arrivee_id, mode }
    """
    data = request.get_json()
    if not data:
        return jsonify({'erreur': 'Corps JSON requis'}), 400

    depart_id = data.get('depart_id')
    arrivee_id = data.get('arrivee_id')
    mode = data.get('mode', 'equilibre')

    if not depart_id or not arrivee_id:
        return jsonify({'erreur': 'depart_id et arrivee_id sont requis'}), 400

    try:
        opt = TransportOptimizer(mode=mode)
        result = opt.find_route(int(depart_id), int(arrivee_id))

        if 'erreur' in result:
            return jsonify(result), 404

        return jsonify({'success': True, 'itineraire': result})

    except ValueError as e:
        return jsonify({'erreur': str(e)}), 400
    except Exception as e:
        return jsonify({'erreur': f'Erreur serveur: {str(e)}'}), 500


@app.route('/route/compare', methods=['POST'])
def compare_routes():
    """Compare les 3 modes d'optimisation pour un même trajet."""
    data = request.get_json()
    depart_id = int(data.get('depart_id', 0))
    arrivee_id = int(data.get('arrivee_id', 0))

    if not depart_id or not arrivee_id:
        return jsonify({'erreur': 'depart_id et arrivee_id requis'}), 400

    opt = TransportOptimizer()
    comparaison = opt.compare_modes(depart_id, arrivee_id)
    return jsonify({'success': True, 'comparaison': comparaison})


@app.route('/pay', methods=['POST'])
def pay_trip():
    """
    Enregistre le paiement d'un trajet sur la blockchain.
    Body JSON: { user_address, montant, depart, arrivee, mode }
    """
    data = request.get_json()
    if not data:
        return jsonify({'erreur': 'Corps JSON requis'}), 400

    user_address = data.get('user_address', '0xUSER_DEFAULT')
    montant = float(data.get('montant', 0))
    depart = data.get('depart', 'Inconnu')
    arrivee = data.get('arrivee', 'Inconnu')
    mode = data.get('mode', 'equilibre')

    if montant <= 0:
        return jsonify({'erreur': 'Montant invalide'}), 400

    trip_id = next_trip_id()
    bc = get_blockchain()

    result = bc.pay_trip(
        user_address=user_address,
        montant=montant,
        trajet_id=trip_id,
        details={
            'depart': depart,
            'arrivee': arrivee,
            'mode': mode,
            'montant_dollar': montant
        }
    )

    return jsonify({
        'success': True,
        'trip_id': trip_id,
        'transaction': result
    })


@app.route('/blockchain', methods=['GET'])
def get_blockchain_status():
    """Retourne l'état de la blockchain."""
    bc = get_blockchain()
    valid, errors = bc.is_valid()
    return jsonify({
        'stats': bc.get_stats(),
        'valide': valid,
        'erreurs': errors,
        'chaine': [b.to_dict() for b in bc.chain[-5:]]  # 5 derniers blocs
    })


@app.route('/history/<user_address>', methods=['GET'])
def get_user_history(user_address):
    """Retourne l'historique des transactions d'un utilisateur."""
    bc = get_blockchain()
    history = bc.get_user_history(user_address)
    return jsonify({
        'user': user_address,
        'transactions': history,
        'total': len(history)
    })


@app.route('/transaction/<tx_id>', methods=['GET'])
def get_transaction(tx_id):
    """Recherche une transaction par son ID."""
    bc = get_blockchain()
    result = bc.get_transaction(tx_id)
    if result:
        return jsonify({'success': True, 'result': result})
    return jsonify({'erreur': 'Transaction introuvable'}), 404


if __name__ == '__main__':
    print("=== API Transport Décentralisée ===")
    print("Démarrage sur http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
