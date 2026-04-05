from flask import Flask, request, jsonify
from flask_cors import CORS
from simulate import run_simulation
import requests
import os

app = Flask(__name__)
CORS(app)  # Penting! Agar Appsmith bisa akses

# Isi ini setelah setup Baserow nanti
BASEROW_TOKEN = os.environ.get("BASEROW_TOKEN", "")
BASEROW_TABLE_ID = os.environ.get("BASEROW_TABLE_ID", "")

@app.route("/")
def home():
    return jsonify({"status": "Dynamic Pricing API berjalan!", "versi": "1.0"})

@app.route("/simulate", methods=["POST"])
def simulate():
    """
    Endpoint utama: terima input, jalankan simulasi, simpan ke Baserow.
    
    Contoh input JSON:
    {
        "biaya_produksi": 15000,
        "harga_awal": 25000,
        "demand_awal": 100,
        "elastisitas": 0.8,
        "nama_produk": "Keripik Singkong"
    }
    """
    try:
        data = request.get_json()
        
        # Validasi input
        required_fields = ["biaya_produksi", "harga_awal", "demand_awal", "elastisitas"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Field '{field}' wajib diisi"}), 400
        
        biaya = float(data["biaya_produksi"])
        harga_awal = float(data["harga_awal"])
        demand_awal = float(data["demand_awal"])
        elastisitas = float(data["elastisitas"])
        nama_produk = data.get("nama_produk", "Produk")
        
        # Validasi logika bisnis
        if biaya >= harga_awal:
            return jsonify({"error": "Biaya produksi harus lebih kecil dari harga jual"}), 400
        if demand_awal <= 0:
            return jsonify({"error": "Perkiraan permintaan harus lebih dari 0"}), 400
        
        # Jalankan simulasi
        hasil = run_simulation(biaya, harga_awal, demand_awal, elastisitas)
        
        # Simpan ke Baserow (kalau token sudah diisi)
        if BASEROW_TOKEN and BASEROW_TABLE_ID:
            simpan_ke_baserow(nama_produk, biaya, harga_awal, demand_awal, elastisitas, hasil)
        
        return jsonify({
            "sukses": True,
            "nama_produk": nama_produk,
            "hasil": hasil
        })
    
    except ValueError as e:
        return jsonify({"error": f"Nilai tidak valid: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500

def simpan_ke_baserow(nama_produk, biaya, harga_awal, demand_awal, elastisitas, hasil):
    """Menyimpan hasil simulasi ke database Baserow."""
    rekomendasi = hasil["rekomendasi"]
    
    url = f"https://api.baserow.io/api/database/rows/table/{BASEROW_TABLE_ID}/?user_field_names=true"
    headers = {
        "Authorization": f"Token {BASEROW_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "Nama Produk": nama_produk,
        "Biaya Produksi": biaya,
        "Harga Awal": harga_awal,
        "Demand Awal": demand_awal,
        "Elastisitas": elastisitas,
        "Harga Optimal": rekomendasi["harga_optimal"],
        "Profit Maksimal": rekomendasi["profit_maksimal"],
        "Peningkatan Profit (%)": rekomendasi["peningkatan_profit_persen"]
    }
    
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)