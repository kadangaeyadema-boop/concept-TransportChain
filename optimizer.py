"""
Semaine 3 - Module d'optimisation multi-objectif
Algorithme de Dijkstra pondéré prix + temps
Plateforme de transport décentralisée
"""

import networkx as nx
from graph_builder import build_graph, load_stops


class TransportOptimizer:
    """Moteur de calcul d'itinéraire multimodal multi-objectif."""

    MODES = {
        'rapide':    {'alpha': 0.8, 'beta': 0.2, 'label': 'Priorité temps'},
        'economique':{'alpha': 0.2, 'beta': 0.8, 'label': 'Priorité prix'},
        'equilibre': {'alpha': 0.5, 'beta': 0.5, 'label': 'Équilibré'},
    }

    def __init__(self, mode='equilibre'):
        if mode not in self.MODES:
            raise ValueError(f"Mode inconnu: {mode}. Choisir parmi {list(self.MODES.keys())}")
        self.mode = mode
        params = self.MODES[mode]
        self.alpha = params['alpha']
        self.beta = params['beta']
        self.G, self.stops, self.segments = build_graph(self.alpha, self.beta)

    def find_route(self, depart_id, arrivee_id):
        """
        Calcule le trajet optimal entre deux arrêts.

        Retourne un dict avec :
        - chemin      : liste des stop_id traversés
        - segments    : détail de chaque étape
        - duree_totale: durée totale en minutes
        - prix_total  : coût total en dollars
        - distance_km : distance totale en km
        - mode        : mode d'optimisation utilisé
        """
        if depart_id not in self.G:
            raise ValueError(f"Arrêt de départ {depart_id} introuvable")
        if arrivee_id not in self.G:
            raise ValueError(f"Arrêt d'arrivée {arrivee_id} introuvable")

        try:
            chemin = nx.dijkstra_path(self.G, depart_id, arrivee_id, weight='poids')
        except nx.NetworkXNoPath:
            return {'erreur': f"Aucun trajet trouvé entre {depart_id} et {arrivee_id}"}

        # Reconstruction des étapes
        etapes = []
        duree_totale = 0.0
        prix_total = 0.0
        distance_totale = 0.0

        for i in range(len(chemin) - 1):
            u, v = chemin[i], chemin[i+1]
            edge = self.G[u][v]
            stop_dep = self.stops[u]
            stop_arr = self.stops[v]

            etape = {
                'etape': i + 1,
                'depart': stop_dep['nom'],
                'arrivee': stop_arr['nom'],
                'mode': edge['mode'],
                'duree_min': edge['duree_min'],
                'prix_dollar': edge['prix_dollar'],
                'distance_km': edge['distance_km'],
                'icone': self._get_icon(edge['mode'])
            }
            etapes.append(etape)
            duree_totale += edge['duree_min']
            prix_total += edge['prix_dollar']
            distance_totale += edge['distance_km']

        return {
            'depart': self.stops[depart_id]['nom'],
            'arrivee': self.stops[arrivee_id]['nom'],
            'chemin_ids': chemin,
            'etapes': etapes,
            'duree_totale_min': round(duree_totale, 1),
            'prix_total': round(prix_total, 2),
            'distance_km': round(distance_totale, 2),
            'nb_correspondances': len(chemin) - 2,
            'mode': self.MODES[self.mode]['label'],
            'alpha': self.alpha,
            'beta': self.beta
        }

    def compare_modes(self, depart_id, arrivee_id):
        """Compare les 3 modes d'optimisation pour une même paire départ/arrivée."""
        resultats = {}
        for mode in self.MODES:
            opt = TransportOptimizer(mode)
            resultats[mode] = opt.find_route(depart_id, arrivee_id)
        return resultats

    def get_all_stops(self):
        """Retourne la liste des arrêts pour l'interface"""
        return [
            {'id': sid, 'nom': s['nom'], 'type': s['type'],
             'lat': s['latitude'], 'lon': s['longitude']}
            for sid, s in self.stops.items()
        ]

    @staticmethod
    def _get_icon(mode):
        icons = {
            'bus': '🚌',
            'velo': '🚲',
            'trottinette': '🛴',
            'marche': '🚶'
        }
        return icons.get(mode, '?')


if __name__ == '__main__':
    print("=== Test de l'optimiseur ===\n")

    # Test trajet Gare Centrale (1) → Université Nord (3)
    for mode in ['rapide', 'economique', 'equilibre']:
        opt = TransportOptimizer(mode)
        result = opt.find_route(1, 3)
        print(f"Mode {mode.upper()} ({result['mode']}) :")
        print(f"  Durée   : {result['duree_totale_min']} min")
        print(f"  Prix    : ${result['prix_total']:.2f}")
        print(f"  Distance: {result['distance_km']} km")
        print(f"  Étapes  : {len(result['etapes'])}")
        for e in result['etapes']:
            print(f"    {e['icone']} {e['depart']} → {e['arrivee']} ({e['mode']}, {e['duree_min']}min, ${e['prix_dollar']})")
        print()
