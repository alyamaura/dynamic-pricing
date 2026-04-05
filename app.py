from flask import Flask, request, jsonify
from flask_cors import CORS
from simulate import run_simulation
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BASEROW_TOKEN    = os.environ.get("BASEROW_TOKEN", "")
BASEROW_TABLE_ID = os.environ.get("BASEROW_TABLE_ID", "")


@app.route("/")
def home():
    return jsonify({"status": "ok", "pesan": "Dynamic Pricing API aktif"})


@app.route("/simulate", methods=["POST"])
def simulate():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "Body kosong. Kirim data JSON."}), 400

        # Cek field wajib
        for field in ["biaya_produksi", "harga_awal", "demand_awal", "elastisitas"]:
            if field not in data:
                return jsonify({"error": f"Field '{field}' wajib diisi."}), 400

        biaya       = float(data["biaya_produksi"])
        harga_awal  = float(data["harga_awal"])
        demand_awal = float(data["demand_awal"])
        elastisitas = float(data["elastisitas"])
        nama_produk = str(data.get("nama_produk", "Produk"))

        # Validasi logika
        if biaya <= 0:
            return jsonify({"error": "Biaya produksi harus lebih dari 0."}), 400
        if harga_awal <= biaya:
            return jsonify({"error": "Harga jual harus lebih besar dari biaya produksi."}), 400
        if demand_awal <= 0:
            return jsonify({"error": "Perkiraan permintaan harus lebih dari 0."}), 400
        if not (0.05 <= elastisitas <= 5.0):
            return jsonify({"error": "Elastisitas harus antara 0.05 dan 5.0."}), 400

        # Jalankan simulasi
        hasil = run_simulation(biaya, harga_awal, demand_awal, elastisitas)

        # Simpan ke Baserow jika sudah dikonfigurasi
        if BASEROW_TOKEN and BASEROW_TABLE_ID:
            _simpan_baserow(nama_produk, biaya, harga_awal, demand_awal, elastisitas, hasil)

        return jsonify({"sukses": True, "nama_produk": nama_produk, "hasil": hasil})

    except ValueError as e:
        return jsonify({"error": f"Format angka tidak valid: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Kesalahan server: {str(e)}"}), 500


def _simpan_baserow(nama, biaya, harga_awal, demand_awal, elastisitas, hasil):
    rek = hasil["rekomendasi"]
    try:
        requests.post(
            f"https://api.baserow.io/api/database/rows/table/{BASEROW_TABLE_ID}/"
            "?user_field_names=true",
            headers={
                "Authorization": f"Token {BASEROW_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "Nama Produk":            nama,
                "Biaya Produksi":         biaya,
                "Harga Awal":             harga_awal,
                "Demand Awal":            demand_awal,
                "Elastisitas":            elastisitas,
                "Harga Optimal":          rek["harga_optimal"],
                "Profit Maksimal":        rek["profit_maksimal"],
                "Peningkatan Profit (%)": rek["peningkatan_profit_persen"]
            },
            timeout=5
        )
    except Exception:
        pass