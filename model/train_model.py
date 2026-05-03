import os
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.pkl")
MODEL_PATH = os.path.join(BASE_DIR, "model", "kmeans_model.pkl")

FEATURE_COLUMNS = [
    "TBC_CDR",
    "TBC_SR",
    "AIDS",
    "Kusta",
    "Malaria",
    "DBD"
]

PROVINSI_INDONESIA = [
    "Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi", 
    "Sumatera Selatan", "Bengkulu", "Lampung", "Kepulauan Bangka Belitung", "Kepulauan Riau",
    "DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur", "Banten",
    "Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur", 
    "Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Selatan", "Kalimantan Timur", "Kalimantan Utara",
    "Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Selatan", "Sulawesi Tenggara", "Gorontalo", "Sulawesi Barat",
    "Maluku", "Maluku Utara", "Papua Barat", "Papua"
]

def generate_dataset(random_state=42) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    n_samples = len(PROVINSI_INDONESIA)
    
    data = {
        "Provinsi": PROVINSI_INDONESIA,
        "TBC_CDR": rng.integers(30, 100, size=n_samples), # Case Detection Rate (persen)
        "TBC_SR": rng.integers(50, 100, size=n_samples),  # Success Rate (persen)
        "AIDS": rng.integers(50, 5000, size=n_samples),   # Jumlah kasus AIDS
        "Kusta": rng.integers(10, 2000, size=n_samples),  # Kasus Kusta
        "Malaria": rng.integers(0, 10000, size=n_samples),# Kasus Malaria
        "DBD": rng.integers(100, 15000, size=n_samples),  # Kasus DBD
    }
    return pd.DataFrame(data)

def train_and_save():
    df = generate_dataset()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[FEATURE_COLUMNS])

    # Menggunakan 3 cluster sesuai permintaan
    model = KMeans(n_clusters=3, random_state=42, n_init=10)
    model.fit(X_scaled)
    df["Cluster"] = model.predict(X_scaled)

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
    
    df.to_csv(DATA_PATH, index=False)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(model, MODEL_PATH)
    print(f"Dataset disimpan di {DATA_PATH}")
    print(f"Scaler disimpan di {SCALER_PATH}")
    print(f"Model disimpan di {MODEL_PATH}")

if __name__ == "__main__":
    train_and_save()
