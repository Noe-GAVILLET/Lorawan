import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metrics import mae, rmse

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

THERMOREG_TARGET = 34.5  # °C — température cible du couvain (BEEHAVE)

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

    # Colonne d'heure (UTC) utilisée par plusieurs sections
    df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60.0

    print(f"\n{'='*60}")
    print(f"  Évaluation Jumeau Numérique — Precision Apiculture")
    print(f"{'='*60}\n")

    # 1. Métriques de thermorégulation (MAE / RMSE vs. cible BEEHAVE)
    temp_col = "temperature" if "temperature" in df.columns else "temperature_real"
    if temp_col in df.columns and df[temp_col].notna().any():
        df_t = df[df[temp_col].notna()]
        df_nom = df_t[~df_t['hour'].between(13.5, 14.5)]
        df_ext = df_t[df_t['hour'].between(13.5, 14.5)]

        print(f"  Thermorégulation — Fidélité au modèle BEEHAVE ({THERMOREG_TARGET} °C)")
        print(f"  {'─'*50}")
        print(f"  MAE  globale : {mae(df_t[temp_col], [THERMOREG_TARGET] * len(df_t)):.3f} °C")
        print(f"  RMSE globale : {rmse(df_t[temp_col], [THERMOREG_TARGET] * len(df_t)):.3f} °C")
        if len(df_nom) > 0:
            print(f"\n  Régime nominal  ({len(df_nom)} pts) :")
            print(f"    MAE  = {mae(df_nom[temp_col], [THERMOREG_TARGET] * len(df_nom)):.3f} °C"
                  f"  |  RMSE = {rmse(df_nom[temp_col], [THERMOREG_TARGET] * len(df_nom)):.3f} °C")
        if len(df_ext) > 0:
            print(f"  Régime extrême  ({len(df_ext)} pts) :")
            print(f"    MAE  = {mae(df_ext[temp_col], [THERMOREG_TARGET] * len(df_ext)):.3f} °C"
                  f"  |  RMSE = {rmse(df_ext[temp_col], [THERMOREG_TARGET] * len(df_ext)):.3f} °C")
        print()

    # 2. Calcul de la dérivée temporelle de masse (kg/min)
    df['time_diff_min'] = df['timestamp'].diff().dt.total_seconds() / 60.0
    # On gère les gaps créés par la perte LoRaWAN > on interpole de manière linéaire très basique la masse
    df['masse_interp'] = df['mass'].interpolate(method='linear') if 'mass' in df.columns else df['masse_real'].interpolate(method='linear')
    df['mass_diff'] = df['masse_interp'].diff()
    df['mass_derivative'] = df['mass_diff'] / df['time_diff_min']

    # 3. Détection par le Jumeau numérique (Predict)
    # Si la perte de poids est plus violente que le seuil
    df['predicted_swarming'] = df['mass_derivative'] <= SWARM_DERIVATIVE_THRESHOLD

    # 4. Vérité terrain (Ground Truth)
    # L'intervalle 13:30 - 14:30 est 'True' (forcé par le Publisher en mode SCENARIO=extreme).
    df['true_swarming'] = (df['hour'] >= 13.5) & (df['hour'] <= 14.5) & (df['mass_diff'] < -0.1)

    # 5. Métriques de classification (F1 Score)
    TP = ((df['predicted_swarming'] == True) & (df['true_swarming'] == True)).sum()
    FP = ((df['predicted_swarming'] == True) & (df['true_swarming'] == False)).sum()
    FN = ((df['predicted_swarming'] == False) & (df['true_swarming'] == True)).sum()
    TN = ((df['predicted_swarming'] == False) & (df['true_swarming'] == False)).sum()

    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    print(f"  Détection d'essaimage — Classification")
    print(f"  {'─'*50}")
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