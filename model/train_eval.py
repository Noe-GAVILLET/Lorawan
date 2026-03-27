"""
Évaluation du modèle de persistance (baseline jumeau numérique ruche).

Protocole :
  - Split chronologique 70 % train / 30 % test.
  - Segmentation nominal / extrême selon le protocole expérimental.
  - Validation des hypothèses H1 et H2 sur les seuils verrouillés a priori.
"""
import os
import sys
from pathlib import Path

import pandas as pd

from metrics import mae, rmse

# ---------------------------------------------------------------------------
# Chemins & constantes
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = os.getenv(
    "CSV_PATH",
    str(BASE_DIR / "data" / "processed" / "hive_timeseries.csv"),
)

TRAIN_RATIO = 0.70

# Seuils verrouillés a priori (cf. docs/protocole_experimental.md §2.1)
NOMINAL_DELTA_TEMP = 1.5    # °C — variation max entre deux mesures consécutives
NOMINAL_DELTA_MASS = 0.20   # kg
H1_MAE_THRESHOLD = 1.0      # °C
H1_RMSE_THRESHOLD = 1.3     # °C


# ---------------------------------------------------------------------------
# Segmentation nominal / extrême
# ---------------------------------------------------------------------------
def classify_extreme(df: pd.DataFrame) -> pd.Series:
    """Retourne un masque booléen True = extrême, False = nominal."""
    delta_temp = df["temperature_real"].diff().abs()
    delta_mass = df["masse_real"].diff().abs()
    return (delta_temp > NOMINAL_DELTA_TEMP) | (delta_mass > NOMINAL_DELTA_MASS)


# ---------------------------------------------------------------------------
# Évaluation d'un sous-ensemble
# ---------------------------------------------------------------------------
def evaluate_segment(df: pd.DataFrame, label: str) -> dict:
    if df.empty:
        print(f"  [{label:8s}]  aucun point — segment ignoré.")
        return {}

    # La prédiction de persistance est la valeur réelle précédente.
    # On utilise .shift(1) sur l'index original, puis bfill pour le premier point.
    y_true = df["temperature_real"].reset_index(drop=True)
    y_pred = df["temperature_real"].shift(1).bfill().reset_index(drop=True)

    result = {
        "n": len(df),
        "mae": mae(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
    }
    print(
        f"  [{label:8s}]  n={result['n']:4d}  "
        f"MAE={result['mae']:.3f} °C  RMSE={result['rmse']:.3f} °C"
    )
    return result


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

    # Split chronologique
    split_idx = int(len(df) * TRAIN_RATIO)
    test = df.iloc[split_idx:].copy().reset_index(drop=True)

    print(f"\n{'='*60}")
    print(f"  Évaluation baseline — persistance  (test : {len(test)} points)")
    print(f"{'='*60}\n")

    # Résultats globaux
    global_res = evaluate_segment(test, "Global")

    # Segmentation
    test["extreme"] = classify_extreme(test)
    nom_df = test[~test["extreme"]].copy()
    ext_df = test[test["extreme"]].copy()

    nom_res = evaluate_segment(nom_df, "Nominal")
    ext_res = evaluate_segment(ext_df, "Extrême")

    # ------------------------------------------------------------------
    # Validation des hypothèses
    # ------------------------------------------------------------------
    print(f"\n{'='*60}")
    print("  Validation des hypothèses")
    print(f"{'='*60}\n")

    # H1
    if nom_res:
        h1 = nom_res["mae"] <= H1_MAE_THRESHOLD and nom_res["rmse"] <= H1_RMSE_THRESHOLD
        verdict = "VALIDÉE ✅" if h1 else "REJETÉE ❌"
        print(
            f"  H1 (MAE_nom ≤ {H1_MAE_THRESHOLD} °C ET RMSE_nom ≤ {H1_RMSE_THRESHOLD} °C) : "
            f"{verdict}  (MAE={nom_res['mae']:.3f}, RMSE={nom_res['rmse']:.3f})"
        )
    else:
        print("  H1 : impossible à évaluer — segment nominal vide.")

    # H2
    if nom_res and ext_res:
        h2 = ext_res["mae"] > nom_res["mae"]
        verdict = "VALIDÉE ✅" if h2 else "REJETÉE ❌"
        print(
            f"  H2 (MAE_ext > MAE_nom) : {verdict}  "
            f"(MAE_ext={ext_res['mae']:.3f}, MAE_nom={nom_res['mae']:.3f})"
        )
    else:
        print("  H2 : impossible à évaluer — un des deux segments est vide.")

    print()


if __name__ == "__main__":
    main()