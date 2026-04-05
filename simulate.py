import numpy as np
import pandas as pd

def run_simulation(biaya_produksi, harga_awal, demand_awal, elastisitas, jumlah_langkah=50):
    """
    Menjalankan simulasi dynamic pricing.
    
    Parameter:
    - biaya_produksi : biaya per unit (Rp)
    - harga_awal     : harga jual saat ini (Rp)
    - demand_awal    : perkiraan jumlah terjual di harga_awal
    - elastisitas    : seberapa sensitif demand terhadap harga
                       (nilai wajar: 0.1 - 2.0)
    - jumlah_langkah : berapa banyak titik harga yang disimulasikan
    """
    
    # Hitung koefisien b dari elastisitas dan demand awal
    # b = elastisitas * (demand_awal / harga_awal)
    b = elastisitas * (demand_awal / harga_awal)
    
    # Hitung koefisien a (baseline demand)
    # Dari: demand_awal = a - b * harga_awal → a = demand_awal + b * harga_awal
    a = demand_awal + b * harga_awal
    
    # Range harga yang akan dicoba: 50% sampai 200% dari harga awal
    harga_min = biaya_produksi * 1.1  # minimal 10% di atas biaya
    harga_max = harga_awal * 2.5
    
    harga_range = np.linspace(harga_min, harga_max, jumlah_langkah)
    
    hasil = []
    for harga in harga_range:
        # Model permintaan linear: Demand = a - b * Harga
        demand = max(0, a - b * harga)
        
        # Model profit: Profit = (Harga - Biaya) * Demand
        profit = (harga - biaya_produksi) * demand
        
        hasil.append({
            "harga": round(harga, 0),
            "demand": round(demand, 2),
            "profit": round(profit, 0),
            "revenue": round(harga * demand, 0)
        })
    
    df = pd.DataFrame(hasil)
    
    # Temukan harga optimal (profit tertinggi)
    idx_optimal = df["profit"].idxmax()
    harga_optimal = df.loc[idx_optimal]
    
    return {
        "data_simulasi": df.to_dict(orient="records"),
        "rekomendasi": {
            "harga_optimal": harga_optimal["harga"],
            "demand_estimasi": harga_optimal["demand"],
            "profit_maksimal": harga_optimal["profit"],
            "revenue_estimasi": harga_optimal["revenue"],
            "harga_saat_ini": harga_awal,
            "profit_saat_ini": round((harga_awal - biaya_produksi) * demand_awal, 0),
            "peningkatan_profit_persen": round(
                ((harga_optimal["profit"] - (harga_awal - biaya_produksi) * demand_awal) 
                 / max(1, (harga_awal - biaya_produksi) * demand_awal)) * 100, 1
            )
        }
    }