"""
Semaine 4 - Interface utilisateur Streamlit
Plateforme de transport décentralisée multimodale
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'optimization'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'blockchain'))

import streamlit as st
import folium
from streamlit_folium import st_folium
from optimizer import TransportOptimizer
from blockchain import get_blockchain

# =====================
#  Configuration
# =====================
st.set_page_config(
    page_title="TransportChain",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1F3864; margin-bottom: 0; }
    .subtitle   { color: #666; margin-top: 0; font-size: 1rem; }
    .metric-card {
        background: #f8f9fa; border-radius: 10px; padding: 1rem;
        border-left: 4px solid #2E75B6; margin-bottom: 0.5rem;
    }
    .step-card {
        background: white; border-radius: 8px; padding: 0.8rem 1rem;
        margin: 0.3rem 0; border: 1px solid #e0e0e0;
        display: flex; align-items: center; gap: 0.5rem;
    }
    .tag-bus       { background:#dbeafe; color:#1e40af; padding:2px 8px; border-radius:99px; font-size:12px; }
    .tag-velo      { background:#dcfce7; color:#166534; padding:2px 8px; border-radius:99px; font-size:12px; }
    .tag-trott     { background:#fef9c3; color:#854d0e; padding:2px 8px; border-radius:99px; font-size:12px; }
    .tag-marche    { background:#f3e8ff; color:#6b21a8; padding:2px 8px; border-radius:99px; font-size:12px; }
    .hash-box {
        background:#1e293b; color:#4ade80; font-family:monospace;
        padding:0.6rem 1rem; border-radius:6px; font-size:0.8rem; word-break:break-all;
    }
</style>
""", unsafe_allow_html=True)

# =====================
#  Sidebar
# =====================
with st.sidebar:
    st.markdown("## ⚙️ Paramètres")
    mode = st.selectbox(
        "Mode d'optimisation",
        options=['equilibre', 'rapide', 'economique'],
        format_func=lambda m: {
            'equilibre': '⚖️ Équilibré (temps + prix)',
            'rapide': '⚡ Rapide (priorité temps)',
            'economique': '💰 Économique (priorité prix)'
        }[m]
    )

    st.markdown("---")
    st.markdown("### 👤 Utilisateur")
    user_address = st.text_input("Adresse portefeuille", value="0xUSER_DEMO_001")

    st.markdown("---")
    st.markdown("### ℹ️ À propos")
    st.markdown("""
    **TransportChain** est une plateforme de mobilité multimodale décentralisée.

    - 🚌 Bus urbain
    - 🚲 Vélo partagé
    - 🛴 Trottinette
    - 🚶 Marche à pied

    Paiements sécurisés via **blockchain**.
    """)

# =====================
#  Header
# =====================
st.markdown('<p class="main-title">🔗 TransportChain</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plateforme de transport multimodale décentralisée — Blockchain + IA</p>', unsafe_allow_html=True)
st.markdown("---")

# =====================
#  Onglets
# =====================
tab1, tab2, tab3 = st.tabs(["🗺️ Planifier un trajet", "⛓️ Blockchain & Paiements", "📊 Tableau de bord"])

# ==========================
#  Onglet 1 : Planifier
# ==========================
with tab1:
    opt = TransportOptimizer(mode=mode)
    stops = opt.get_all_stops()
    stop_names = {s['id']: f"{s['nom']} ({s['type']})" for s in stops}

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 📍 Votre trajet")
        depart_id = st.selectbox(
            "Départ",
            options=list(stop_names.keys()),
            format_func=lambda x: stop_names[x],
            index=0
        )
        arrivee_id = st.selectbox(
            "Arrivée",
            options=list(stop_names.keys()),
            format_func=lambda x: stop_names[x],
            index=2
        )

        if st.button("🔍 Calculer l'itinéraire", type="primary", use_container_width=True):
            if depart_id == arrivee_id:
                st.warning("Départ et arrivée identiques.")
            else:
                with st.spinner("Calcul en cours..."):
                    result = opt.find_route(depart_id, arrivee_id)
                    st.session_state['last_route'] = result
                    st.session_state['depart_name'] = stop_names[depart_id]
                    st.session_state['arrivee_name'] = stop_names[arrivee_id]

        # Affichage du résultat
        if 'last_route' in st.session_state:
            r = st.session_state['last_route']
            st.markdown("---")
            st.markdown(f"**{r['depart']} → {r['arrivee']}**")

            c1, c2, c3 = st.columns(3)
            c1.metric("⏱ Durée", f"{r['duree_totale_min']} min")
            c2.metric("💰 Prix", f"${r['prix_total']:.2f}")
            c3.metric("📏 Distance", f"{r['distance_km']} km")

            st.markdown("**Étapes du trajet :**")
            MODE_COLORS = {'bus':'🚌','velo':'🚲','trottinette':'🛴','marche':'🚶'}
            for e in r['etapes']:
                icone = MODE_COLORS.get(e['mode'], '?')
                st.markdown(
                    f"**{e['etape']}.** {icone} `{e['depart']}` → `{e['arrivee']}` "
                    f"— {e['mode']} | {e['duree_min']} min | ${e['prix_dollar']:.2f}",
                )

            st.markdown("---")
            if st.button("💳 Payer ce trajet", type="secondary", use_container_width=True):
                bc = get_blockchain()
                tx = bc.pay_trip(
                    user_address=user_address,
                    montant=r['prix_total'],
                    trajet_id=int(r['prix_total'] * 1000),
                    details={'depart': r['depart'], 'arrivee': r['arrivee'], 'mode': mode}
                )
                st.success("✅ Paiement confirmé sur la blockchain !")
                st.markdown(f'<div class="hash-box">TX: {tx["tx_id"]}<br>Bloc: #{tx["block_index"]}<br>Hash: {tx["block_hash"][:32]}...</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("### 🗺️ Carte du réseau")
        m = folium.Map(location=[45.51, -73.58], zoom_start=12, tiles='CartoDB positron')

        # Couleurs par type
        colors = {'bus': 'blue', 'velo': 'green', 'trottinette': 'orange', 'marche': 'purple'}
        icons_map = {'bus': 'bus', 'velo': 'bicycle', 'trottinette': 'bolt', 'marche': 'male'}

        for s in stops:
            color = colors.get(s['type'], 'gray')
            folium.CircleMarker(
                location=[s['lat'], s['lon']],
                radius=7,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                tooltip=f"{s['nom']} ({s['type']})",
                popup=f"<b>{s['nom']}</b><br>Type: {s['type']}<br>ID: {s['id']}"
            ).add_to(m)

        # Afficher le trajet calculé
        if 'last_route' in st.session_state:
            r = st.session_state['last_route']
            route_coords = []
            for sid in r['chemin_ids']:
                s = next(x for x in stops if x['id'] == sid)
                route_coords.append([s['lat'], s['lon']])

            if len(route_coords) > 1:
                folium.PolyLine(
                    route_coords, color='red', weight=4, opacity=0.8,
                    tooltip="Trajet optimal"
                ).add_to(m)
                folium.Marker(
                    route_coords[0], tooltip="Départ",
                    icon=folium.Icon(color='green', icon='play')
                ).add_to(m)
                folium.Marker(
                    route_coords[-1], tooltip="Arrivée",
                    icon=folium.Icon(color='red', icon='flag')
                ).add_to(m)

        # Légende
        legend = """
        <div style="position:fixed;bottom:30px;left:30px;z-index:999;
             background:white;padding:10px 14px;border-radius:8px;
             box-shadow:0 2px 6px rgba(0,0,0,0.2);font-size:13px;">
          <b>Légende</b><br>
          🔵 Bus &nbsp; 🟢 Vélo &nbsp; 🟠 Trottinette &nbsp; 🟣 Marche
        </div>"""
        m.get_root().html.add_child(folium.Element(legend))

        st_folium(m, width=700, height=480)

# ==========================
#  Onglet 2 : Blockchain
# ==========================
with tab2:
    bc = get_blockchain()
    stats = bc.get_stats()
    valid, errors = bc.is_valid()

    st.markdown("### ⛓️ État de la blockchain")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🧱 Blocs", stats['nb_blocs'])
    col2.metric("💸 Transactions", stats['nb_transactions'])
    col3.metric("⏳ En attente", stats['pending'])
    col4.metric("✅ Intégrité", "Valide" if valid else "❌ Invalide")

    if errors:
        for e in errors:
            st.error(e)

    st.markdown("---")
    st.markdown("### 🔍 Rechercher une transaction")
    tx_id_search = st.text_input("ID de transaction")
    if tx_id_search:
        result = bc.get_transaction(tx_id_search)
        if result:
            st.json(result)
        else:
            st.warning("Transaction introuvable.")

    st.markdown("---")
    st.markdown("### 📋 Historique utilisateur")
    if st.button("🔄 Charger l'historique"):
        history = bc.get_user_history(user_address)
        if history:
            for tx in history:
                with st.expander(f"TX {tx['tx_id']} — ${tx['montant']} — Trajet #{tx['trajet_id']}"):
                    st.json(tx)
        else:
            st.info("Aucune transaction pour cet utilisateur.")

    st.markdown("---")
    st.markdown("### 🧱 Derniers blocs")
    for block in reversed(bc.chain[-3:]):
        bd = block.to_dict()
        with st.expander(f"Bloc #{bd['index']} — {bd['nb_transactions']} transaction(s) — Hash: {bd['hash'][:20]}..."):
            st.json(bd)

# ==========================
#  Onglet 3 : Dashboard
# ==========================
with tab3:
    st.markdown("### 📊 Tableau de bord du réseau")

    # Graphe de comparaison des modes
    st.markdown("#### Comparaison des modes d'optimisation")
    st.markdown("Trajet exemple : **Gare Centrale → Université Nord**")

    opt_eq = TransportOptimizer('equilibre')
    opt_rp = TransportOptimizer('rapide')
    opt_ec = TransportOptimizer('economique')

    r_eq = opt_eq.find_route(1, 3)
    r_rp = opt_rp.find_route(1, 3)
    r_ec = opt_ec.find_route(1, 3)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**⚖️ Équilibré**")
        st.metric("Durée", f"{r_eq.get('duree_totale_min','-')} min")
        st.metric("Prix", f"${r_eq.get('prix_total', 0):.2f}")
    with col2:
        st.markdown("**⚡ Rapide**")
        st.metric("Durée", f"{r_rp.get('duree_totale_min','-')} min")
        st.metric("Prix", f"${r_rp.get('prix_total', 0):.2f}")
    with col3:
        st.markdown("**💰 Économique**")
        st.metric("Durée", f"{r_ec.get('duree_totale_min','-')} min")
        st.metric("Prix", f"${r_ec.get('prix_total', 0):.2f}")

    st.markdown("---")
    st.markdown("#### Répartition des arrêts par type")

    all_stops = opt_eq.get_all_stops()
    from collections import Counter
    type_counts = Counter(s['type'] for s in all_stops)

    import pandas as pd
    df = pd.DataFrame(list(type_counts.items()), columns=['Mode', 'Nombre'])
    st.bar_chart(df.set_index('Mode'))

    st.markdown("---")
    st.markdown("#### Statistiques blockchain")
    bc_stats = bc.get_stats()
    st.markdown(f"""
    | Métrique | Valeur |
    |---|---|
    | Nombre de blocs | {bc_stats['nb_blocs']} |
    | Total transactions | {bc_stats['nb_transactions']} |
    | Transactions en attente | {bc_stats['pending']} |
    | Dernier hash | `{bc_stats['dernier_hash']}` |
    """)
