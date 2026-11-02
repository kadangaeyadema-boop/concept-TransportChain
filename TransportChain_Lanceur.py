"""
TransportChain - Lanceur automatique
Double-clic sur ce fichier pour lancer l'interface
"""

import subprocess
import sys
import os
import time
import webbrowser
import threading

def installer_dependances():
    print("Installation des dependances...")
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "streamlit", "folium", "streamlit-folium",
        "networkx", "pandas", "flask", "flask-cors",
        "--quiet"
    ])
    print("OK.\n")

def ouvrir_navigateur():
    time.sleep(5)
    webbrowser.open("http://localhost:8501")

def lancer_streamlit(script_path):
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", script_path,
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--server.port", "8501"
    ])

if __name__ == "__main__":
    print()
    print("================================================")
    print("  TRANSPORTCHAIN - Plateforme de Transport")
    print("================================================")
    print()

    # Trouver app_streamlit.py automatiquement
    dossier_lanceur = os.path.dirname(os.path.abspath(__file__))

    chemins_possibles = [
        os.path.join(dossier_lanceur, "app_streamlit.py"),
        os.path.join(dossier_lanceur, "interface", "app_streamlit.py"),
        os.path.join(dossier_lanceur, "Code_Source", "interface", "app_streamlit.py"),
    ]

    script = None
    for chemin in chemins_possibles:
        if os.path.exists(chemin):
            script = chemin
            break

    if not script:
        print("ERREUR : app_streamlit.py introuvable.")
        print("Place ce fichier dans le meme dossier que Code_Source\\")
        input("\nAppuie sur Entree pour fermer...")
        sys.exit(1)

    print(f"Fichier trouve : {script}")
    print()

    installer_dependances()

    # Ouvrir le navigateur en arriere-plan
    thread = threading.Thread(target=ouvrir_navigateur)
    thread.daemon = True
    thread.start()

    print("Lancement de l'interface...")
    print("Le navigateur va s'ouvrir sur http://localhost:8501")
    print()
    print("(Garde cette fenetre ouverte)")
    print("(Pour arreter : ferme cette fenetre)")
    print()

    lancer_streamlit(script)
