"""
Semaine 2 - Module de construction du graphe multimodal
Plateforme de transport décentralisée
"""

import csv
import json
import os
import networkx as nx


DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
STOPS_FILE = os.path.join(DATA_DIR, 'stops.csv')
SEGMENTS_FILE = os.path.join(DATA_DIR, 'segments.csv')


def load_stops():
    """Charge les arrêts depuis le CSV et retourne un dict {stop_id: {...}}"""
    stops = {}
    with open(STOPS_FILE, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stop_id = int(row['stop_id'])
            stops[stop_id] = {
                'stop_id': stop_id,
                'nom': row['nom'],
                'type': row['type'],
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude']),
                'adresse': row['adresse']
            }
    return stops


def load_segments():
    """Charge les segments depuis le CSV et retourne une liste de dicts"""
    segments = []
    with open(SEGMENTS_FILE, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            segments.append({
                'segment_id': int(row['segment_id']),
                'depart_id': int(row['depart_id']),
                'arrivee_id': int(row['arrivee_id']),
                'mode': row['mode'],
                'duree_min': float(row['duree_min']),
                'prix_dollar': float(row['prix_dollar']),
                'distance_km': float(row['distance_km'])
            })
    return segments


def build_graph(alpha=0.5, beta=0.5):
    """
    Construit le graphe multimodal orienté.

    Paramètres de pondération :
    - alpha : poids du temps (0.0 à 1.0)
    - beta  : poids du prix (0.0 à 1.0)
    -> alpha + beta = 1.0

    Retourne : (graphe NetworkX, stops dict, segments list)
    """
    stops = load_stops()
    segments = load_segments()

    G = nx.DiGraph()

    # Ajout des nœuds avec leurs attributs
    for stop_id, attrs in stops.items():
        G.add_node(stop_id, **attrs)

    # Ajout des arêtes avec poids combiné
    for seg in segments:
        # Normalisation simple : on suppose durée max ~30 min, prix max ~3$
        # Poids = alpha * (duree/30) + beta * (prix/3)
        poids = alpha * (seg['duree_min'] / 30.0) + beta * (seg['prix_dollar'] / 3.0)

        G.add_edge(
            seg['depart_id'],
            seg['arrivee_id'],
            segment_id=seg['segment_id'],
            mode=seg['mode'],
            duree_min=seg['duree_min'],
            prix_dollar=seg['prix_dollar'],
            distance_km=seg['distance_km'],
            poids=poids
        )

    return G, stops, segments


def get_graph_stats(G):
    """Retourne des statistiques sur le graphe"""
    return {
        'nb_noeuds': G.number_of_nodes(),
        'nb_aretes': G.number_of_edges(),
        'est_connexe': nx.is_weakly_connected(G),
        'modes_disponibles': list(set(d['mode'] for _, _, d in G.edges(data=True)))
    }


def export_graph_json(G, stops, output_path):
    """Exporte le graphe en JSON pour l'interface"""
    data = {
        'nodes': [
            {'id': n, **attrs}
            for n, attrs in G.nodes(data=True)
        ],
        'edges': [
            {'source': u, 'target': v, **d}
            for u, v, d in G.edges(data=True)
        ]
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


if __name__ == '__main__':
    print("=== Construction du graphe multimodal ===")
    G, stops, segments = build_graph(alpha=0.5, beta=0.5)
    stats = get_graph_stats(G)
    print(f"Nœuds (arrêts)   : {stats['nb_noeuds']}")
    print(f"Arêtes (segments): {stats['nb_aretes']}")
    print(f"Graphe connexe   : {stats['est_connexe']}")
    print(f"Modes disponibles: {', '.join(stats['modes_disponibles'])}")

    out = os.path.join(os.path.dirname(__file__), '..', 'data', 'graph.json')
    export_graph_json(G, stops, out)
    print(f"\nGraphe exporté → {out}")
