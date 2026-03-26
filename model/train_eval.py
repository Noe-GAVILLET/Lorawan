import pandas as pd
from metrics import mae, rmse


def main() -> None:
    # Example pipeline: load processed data and compute naive baseline errors.
    df = pd.read_csv('data/processed/hive_timeseries.csv')
    y_true = df['temperature_real']
    y_pred = df['temperature_real'].shift(1).bfill()

    print(f"MAE: {mae(y_true, y_pred):.3f}")
    print(f"RMSE: {rmse(y_true, y_pred):.3f}")


if __name__ == '__main__':
    main()