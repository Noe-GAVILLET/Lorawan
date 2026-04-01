import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Chemins & constantes
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = os.getenv(
    "CSV_PATH",
    str(BASE_DIR / "data" / "processed" / "hive_timeseries.csv"),
)

# Seuils Swarming (Essaimage)
# Si la derivée (kg / minute) est inférieure à ce seuil négatif, alerte !
# Un essaimage provoque une forte baisse de poids.
SWARM_DERIVATIVE_THRESHOLD = -0.05  # kg / minute

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    if not Path(CSV_PATH).exists():
        print(f"ERREUR : CSV introuvable à {CSV_PATH}", file=sys.stderr)
        print("Lancer d'abord : python model/export_csv.py", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    if len(df) < 10:
        print("AVERTISSEMENT : moins de 10 points dans le CSV — résultats peu significatifs.")

    print(f"\n{'='*60}")
    print(f"  Évaluation Jumeau Numérique — Precision Apiculture")
    print(f"{'='*60}\n")

    # 1. Calcul de la dérivée temporelle de masse (kg/min)
    df['time_diff_min'] = df['timestamp'].diff().dt.total_seconds() / 60.0
    # On gère les gaps créés par la perte LoRaWAN > on interpole de manière linéaire très basique la masse
    df['masse_interp'] = df['mass'].interpolate(method='linear') if 'mass' in df.columns else df['masse_real'].interpolate(method='linear')
    df['mass_diff'] = df['masse_interp'].diff()
    df['mass_derivative'] = df['mass_diff'] / df['time_diff_min']
    
    # 2. Détection par le Jumeau numérique (Predict)
    # Si la perte de poids est plus violente que le seuil
    df['predicted_swarming'] = df['mass_derivative'] <= SWARM_DERIVATIVE_THRESHOLD
    
    # 3. Vérité terrain (Ground Truth)
    # Nous pouvons simuler que l'intervalle 13:30 - 14:30 est 'True' (car forcé par notre Publisher en mode extrême).
    df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60.0
    df['true_swarming'] = (df['hour'] >= 13.5) & (df['hour'] <= 14.5) & (df['mass_diff'] < -0.1)

    # 4. Calcul des métriques de classification (F1 Score)
    TP = ((df['predicted_swarming'] == True) & (df['true_swarming'] == True)).sum()
    FP = ((df['predicted_swarming'] == True) & (df['true_swarming'] == False)).sum()
    FN = ((df['predicted_swarming'] == False) & (df['true_swarming'] == True)).sum()
    TN = ((df['predicted_swarming'] == False) & (df['true_swarming'] == False)).sum()

    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    print(f"  Événements d'essaimage réels (Truth) : {df['true_swarming'].sum()}")
    print(f"  Alertes générées (Predicted)          : {df['predicted_swarming'].sum()}")
    print()
    print(f"  Vrais Positifs (TP)  : {TP}")
    print(f"  Faux Positifs (FP)   : {FP}")
    print(f"  Faux Négatifs (FN)   : {FN}")
    print()
    print(f"  Précision : {precision:.2f}")
    print(f"  Rappel    : {recall:.2f}")
    print(f"  F1-Score  : {f1_score:.2f}")

    print(f"\n{'='*60}")
    print("  Validation des hypothèses")
    print(f"{'='*60}\n")
    
    h1 = precision >= 0.90
    verdict1 = "VALIDÉE ✅" if h1 else "REJETÉE ❌"
    print(f"  H1 (Le jumeau détecte l'essaimage avec Précision >= 90%) : {verdict1}")

    print("\n  H2 nécessite de tester ce même script sur un dataset avec forte perte radio LoRa,")
    print("  et d'observer une chute du Rappel (FN qui augmentent suite aux trous de données ignorés).")

if __name__ == "__main__":
    main()