import numpy as np
import pandas as pd

def run_simulation(biaya_produksi, harga_awal, demand_awal, elastisitas):
    """
    Simulasi dynamic pricing dengan model linear.
    
    Rumus:
        Demand = a - b * Harga
        Profit = (Harga - Biaya) * Demand
    """
    # Hitung koefisien model
    b = elastisitas * (demand_awal / harga_awal)
    a = demand_awal + b * harga_awal

    # Range harga yang disimulasikan: dari 10% di atas biaya sampai 2.5x harga awal
    harga_min = biaya_produksi * 1.10
    harga_max = harga_awal * 2.5
    harga_list = np.linspace(harga_min, harga_max, 40)  # 40 titik harga

    hasil = []
    for harga in harga_list:
        demand  = max(0.0, a - b * harga)
        profit  = (harga - biaya_produksi) * demand
        revenue = harga * demand
        hasil.append({
            "harga":   round(float(harga),   0),
            "demand":  round(float(demand),  2),
            "profit":  round(float(profit),  0),
            "revenue": round(float(revenue), 0)
        })

    df          = pd.DataFrame(hasil)
    idx_optimal = df["profit"].idxmax()
    opt         = df.loc[idx_optimal]

    profit_sekarang = (harga_awal - biaya_produksi) * demand_awal
    if profit_sekarang > 0:
        peningkatan = round(
            ((opt["profit"] - profit_sekarang) / profit_sekarang) * 100, 1
        )
    else:
        peningkatan = 0.0

    return {
        "data_simulasi": df.to_dict(orient="records"),
        "rekomendasi": {
            "harga_optimal":             opt["harga"],
            "demand_estimasi":           opt["demand"],
            "profit_maksimal":           opt["profit"],
            "revenue_estimasi":          opt["revenue"],
            "harga_saat_ini":            harga_awal,
            "profit_saat_ini":           round(float(profit_sekarang), 0),
            "peningkatan_profit_persen": peningkatan
        }
    }