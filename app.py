import os
import sys
from flask import Flask, render_template, jsonify
import requests
from dotenv import load_dotenv

# Thiết lập encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Nạp biến môi trường từ file .env
load_dotenv()

app = Flask(__name__)

# Đọc thông tin kết nối Supabase từ biến môi trường
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

if not url or not key:
    raise EnvironmentError("Thiếu biến môi trường SUPABASE_URL hoặc SUPABASE_KEY. Vui lòng kiểm tra file .env")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

HOSPITALS = [
    "BỆNH_VIỆN_ĐA_KHOA_KHU_VỰC_MIỀN_NÚI_PHÍA_BẮC_QUẢNG_NAM",
    "Bệnh_viện_Đa_khoa_khu_vực_Quảng_Nam",
    "Bệnh_viện_đa_khoa_Nam_Liên_Chiểu",
    "BỆNH_VIỆN_ĐA_KHOA_QUẢNG_NAM",
    "Bệnh_viện_Đà_Nẵng",
    "Bệnh_viện_Mắt_Đà_Nẵng",
    "BỆNH_VIỆN_PHẠM_NGỌC_THẠCH_QUẢNG_NAM",
    "Bệnh_viện_Phổi_Đà_Nẵng",
    "Bệnh_viện_Phụ_sản_Nhi_Đà_Nẵng",
    "BỆNH_VIỆN_PHỤ_SẢN_NHI_QUẢNG_NAM",
    "BỆNH_VIỆN_PHỤC_HỒI_CHỨC_NĂNG_THÀNH_PHỐ_ĐÀ_NẴNG",
    "Bệnh_viện_Răng_Hàm_Mặt_thành_phố_Đà_Nẵng",
    "BỆNH_VIỆN_TÂM_THẦN_THÀNH_PHỐ_ĐÀ_NẴNG",
    "Bệnh_viện_Ung_bướu_Đà_Nẵng",
    "Bệnh_viện_Việt_Đức",
    "Bệnh_viện_Việt_Hàn_Đà_Nẵng",
    "Bệnh_viện_Y_học_cổ_truyền_Quảng_Nam",
    "BỆNH_VIỆN_Y_HỌC_CỔ_TRUYỀN_TP_ĐÀ_NẴNG",
    "CƠ_SỞ_2_BỆNH_VIỆN_ĐA_KHOA_KHU_VỰC_MIỀN_NÚI_PHÍA_BẮC_QUẢNG_NAM",
    "Trung_tâm_Y_tế_khu_vực_Bắc_Trà_My",
    "Trung_Tâm_Y_tế_khu_vực_Cẩm_Lệ",
    "TRUNG_TÂM_Y_TẾ_KHU_VỰC_ĐÔNG_GIANG",
    "TRUNG_TÂM_Y_TẾ_KHU_VỰC_DUY_XUYÊN",
    "Trung_tâm_Y_tế_khu_vực_Hải_Châu",
    "Trung_tâm_Y_tế_khu_vực_Hòa_Vang",
    "TRUNG_TÂM_Y_TẾ_KHU_VỰC_HỘI_AN",
    "TRUNG_TÂM_Y_TẾ_KHU_VỰC_LIÊN_CHIỂU",
    "Trung_tâm_Y_tế_khu_vực_Nam_Giang",
    "TRUNG_TÂM_Y_TẾ_KHU_VỰC_NAM_TRÀ_MY",
    "Trung_tâm_Y_tế_Khu_vực_Nông_Sơn",
    "Trung_Tâm_Y_Tế_Khu_Vực_Phú_Ninh",
    "Trung_tâm_Y_tế_khu_vực_Phước_Sơn",
    "Trung_tâm_Y_tế_khu_vực_Quế_Sơn",
    "Trung_tâm_Y_tế_khu_vực_Sơn_Trà",
    "Trung_tâm_Y_tế_khu_vực_Tam_Kỳ",
    "TRUNG_TÂM_Y_TẾ_KHU_VỰC_TÂY_GIANG",
    "Trung_tâm_Y_tế_khu_vực_Thăng_Bình",
    "TRUNG_TÂM_Y_TẾ_KHU_VỰC_THANH_KHÊ",
    "TRUNG_TÂM_Y_TẾ_KHU_VỰC_TIÊN_PHƯỚC"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/hospitals')
def get_hospitals():
    try:
        tables = []
        for name in HOSPITALS:
            display_name = name.replace('_', ' ')
            tables.append({"id": name, "name": display_name})
                
        tables = sorted(tables, key=lambda x: x["name"])
        return jsonify({"status": "success", "data": tables})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/data/<table>')
def get_table_data(table):
    try:
        # Use requests instead of supabase-py
        res = requests.get(f"{url}/rest/v1/{table}?select=*", headers=headers)
        res.raise_for_status()
        rows = res.json()
        
        data = []
        for i, row in enumerate(rows):
            # Check for standard field names
            ma = str(row.get('ma', '')).strip() if row.get('ma') is not None else ""
            ten = str(row.get('ten23', '')).strip() if row.get('ten23') is not None else ""
            tenpheduyet = str(row.get('tenpheduyet', '')).strip() if row.get('tenpheduyet') is not None else ""
            
            gia = row.get('gia')
            if gia is not None:
                try:
                    gia = float(str(gia).replace(',', ''))
                except ValueError:
                    gia = ""
            else:
                gia = ""
                
            ghichu = str(row.get('ghichu', '')).strip() if row.get('ghichu') is not None else ""
            
            item = {
                "stt": i + 1,
                "ma": ma,
                "ten": ten,
                "tenpheduyet": tenpheduyet,
                "gia": gia,
                "ghichu": ghichu
            }
            if item["gia"] != "":
                item["gia"] = f"{item['gia']:,.0f}"
            data.append(item)
            
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    print("Khởi động server quản lý giá (Supabase qua Requests)...")
    app.run(debug=True, port=5000)
