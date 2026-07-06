# bulk_import.py
import gspread
import requests
import pandas as pd
import time
import re
import os
import json

# ══════════════════════════════════════════════
# تحميل الإعدادات: Streamlit Cloud أو محلي
# ══════════════════════════════════════════════
def _load_zr_config():
    try:
        import streamlit as st
        return (
            str(st.secrets["ZR_API_KEY"]),
            str(st.secrets["ZR_TENANT_ID"]),
            str(st.secrets["ZR_BASE_URL"]),
        )
    except Exception:
        from config import ZR_API_KEY, ZR_TENANT_ID, ZR_BASE_URL
        return ZR_API_KEY, ZR_TENANT_ID, ZR_BASE_URL

def _get_gspread_client():
    try:
        import streamlit as st
        from google.oauth2.service_account import Credentials
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception:
        return gspread.service_account(filename="credentials.json")

ZR_API_KEY, ZR_TENANT_ID, ZR_BASE_URL = _load_zr_config()


# ==========================================
# ⚙️ إعدادات الحالة المطلوبة للرفع
# ==========================================
TARGET_STATUS = "Confirmer"

# ==========================================
# 🗺️ القاموس السري للولايات
# ==========================================
WILAYA_MAP = {
    1: 'Adrar', 2: 'Chlef', 3: 'Laghouat', 4: 'Oum El Bouaghi', 5: 'Batna', 6: 'Bejaia', 7: 'Biskra', 8: 'Bechar', 
    9: 'Blida', 10: 'Bouira', 11: 'Tamanrasset', 12: 'Tebessa', 13: 'Tlemcen', 14: 'Tiaret', 15: 'Tizi Ouzou', 16: 'Alger', 
    17: 'Djelfa', 18: 'Jijel', 19: 'Setif', 20: 'Saida', 21: 'Skikda', 22: 'Sidi Bel Abbes', 23: 'Annaba', 24: 'Guelma', 
    25: 'Constantine', 26: 'Medea', 27: 'Mostaganem', 28: 'Msila', 29: 'Mascara', 30: 'Ouargla', 31: 'Oran', 32: 'El Bayadh', 
    33: 'Illizi', 34: 'Bordj Bou Arreridj', 35: 'Boumerdes', 36: 'El Tarf', 37: 'Tindouf', 38: 'Tissemsilt', 39: 'El Oued', 
    40: 'Khenchela', 41: 'Souk Ahras', 42: 'Tipaza', 43: 'Mila', 44: 'Ain Defla', 45: 'Naama', 46: 'Ain Temouchent', 
    47: 'Ghardaia', 48: 'Relizane', 49: 'Timimoun', 50: 'Bordj Badji Mokhtar', 51: 'Ouled Djellal', 52: 'Beni Abbes', 
    53: 'In Salah', 54: 'In Guezzam', 55: 'Touggourt', 56: 'Djanet', 57: 'El Meghaier', 58: 'El Menia'
}

# ==========================================
# 🛍️ القاموس السري للمنتجات
# ==========================================
PRODUCT_MAP = {
    "the cane": "عصا المشي القابلة للطي - avec autorisation ouverture",
    # يمكنك إضافة المزيد من المنتجات هنا مستقبلاً
}

def extract_wilaya_name(city_str):
    match = re.search(r'\b(\d{1,2})\b', str(city_str))
    if match: 
        w_code = int(match.group(1))
        return WILAYA_MAP.get(w_code, 'alger')
    return 'alger'

def format_algerian_phone(phone_str):
    cleaned = re.sub(r'[^\d+]', '', str(phone_str))
    if not cleaned: return "0000000000"
    if cleaned.startswith('+213'): return cleaned
    if cleaned.startswith('00213'): return '+' + cleaned[2:]
    if cleaned.startswith('213'): return '+' + cleaned
    if cleaned.startswith('0'): return '+213' + cleaned[1:]
    if len(cleaned) == 9 and cleaned[0] in ['5', '6', '7']: return '+213' + cleaned
    return cleaned

# ==========================================
# 🚀 الدالة الرئيسية (تعمل بناءً على أوامر الواجهة)
# ==========================================
def bulk_upload_orders(sheet_name, tab_name):
    print(f"\n[*] 🌐 جاري الاتصال بمتجر: [{sheet_name}]...")
    try:
        gc = _get_gspread_client()
        sheet = gc.open(sheet_name).worksheet(tab_name)
    except Exception as e:
        print(f"[❌] خطأ في الاتصال! {e}")
        return

    data = sheet.get_all_values()
    if len(data) <= 1:
        print("[❌] الشيت فارغ!")
        return

    headers = [str(h).strip().lower() for h in data[0]]
    
    try:
        idx_status   = headers.index("state")
        idx_name     = headers.index("full name")
        idx_phone    = headers.index("phone")
        idx_city     = headers.index("city")       
        idx_commune  = headers.index("communes")    
        idx_stopdesk = headers.index("stopdesk")   
        idx_hub      = headers.index("hubs")       
        idx_address  = headers.index("address 1")
        idx_product  = headers.index("product sku")
        idx_price    = headers.index("t.p")
        idx_tracking = headers.index("tracking")
        idx_customer_id = headers.index("customer id")
        
        # أعمدة الأسعار الجديدة
        idx_delivery_price = headers.index("delivery price")
        idx_return_price = headers.index("return price")
    except ValueError as e:
        print(f"[❌] خطأ تقني: لم أتمكن من العثور على أحد الأعمدة المطلوبة! تأكد من وجود الأعمدة: 'Customer ID', 'Delivery Price', 'Return Price'")
        return

    idx_quantity = headers.index("q") if "q" in headers else -1

    print(f"[*] 🔍 جاري سحب الطلبيات الجاهزة '{TARGET_STATUS}' وتغليفها...")
    
    excel_data = []
    row_mapping = {} 
    current_excel_row = 2 
    
    for gsheet_row_idx, row in enumerate(data[1:], start=2):
        # 2️⃣ تحديث الحماية لتشمل جميع الأعمدة لضمان عدم حدوث خطأ IndexError
        max_idx = max(idx_status, idx_tracking, idx_hub, idx_customer_id, idx_delivery_price, idx_return_price)
        if len(row) <= max_idx:
            row.extend([""] * (max_idx - len(row) + 1))
            
        status = str(row[idx_status]).strip()
        tracking = str(row[idx_tracking]).strip()
        customer_id_val = str(row[idx_customer_id]).strip() # قراءة القيمة الحالية لـ Customer ID
        
        # 3️⃣ تعديل الشرط: الآن نبحث عن الحالة المؤكدة بشرط أن يكون عمود Customer ID فارغاً
        if status.lower() == TARGET_STATUS.lower() and not customer_id_val:
            zr_wilaya = extract_wilaya_name(row[idx_city])
            
            raw_name = str(row[idx_name]).strip()
            if not raw_name: raw_name = "Client Inconnu"

            clean_phone = format_algerian_phone(row[idx_phone])

            raw_sku = str(row[idx_product]).strip()
            if not raw_sku: raw_sku = "Produit"
            
            search_sku = raw_sku.lower()
            descriptive_product_name = PRODUCT_MAP.get(search_sku, raw_sku)

            try:
                qty = int(str(row[idx_quantity]).strip() or 1) if idx_quantity != -1 else 1
            except:
                qty = 1

            try:
                clean_price = int(float(str(row[idx_price]).strip().replace(",", "").replace(" ", "") or 0))
            except:
                clean_price = 0

            is_stopdesk = str(row[idx_stopdesk]).strip().upper() == "OUI"
            sd_value = "OUI" if is_stopdesk else "NON"
            hub_name = str(row[idx_hub]).strip() if is_stopdesk else None

            excel_row = {
                'Nom Complet*': raw_name,
                'Téléphone 1*': clean_phone,      
                'Téléphone 2': None, 
                'Produit': descriptive_product_name,  
                'Quantité*': qty,
                'Sku': raw_sku,                                       
                'Type de stock': 'local',
                'Adresse': str(row[idx_address]).strip() or None,
                'Wilaya': zr_wilaya,
                'Commune': str(row[idx_commune]).strip() or None,
                'Prix total de la commande*': clean_price,
                'Note': '--',                                      
                'ID': None,
                'Stopdesk ( OUI )*': sd_value,
                'Nom StopDesk': hub_name
            }
            
            excel_data.append(excel_row)
            row_mapping[current_excel_row] = gsheet_row_idx
            current_excel_row += 1

    if not excel_data:
        print(f"[!] 🛑 لا توجد طلبيات جديدة لرفعها. كل شيء مكتمل في متجر {sheet_name}!")
        return

    print(f"[✅] تم تغليف {len(excel_data)} طلبية بنجاح! جاري الانطلاق نحو سيرفر التوصيل...")
    
    df = pd.DataFrame(excel_data)
    safe_filename_suffix = sheet_name.replace(" ", "_")
    temp_filename = f"auto_upload_{safe_filename_suffix}.xlsx"
    df.to_excel(temp_filename, index=False, sheet_name='Sheet')
    
    url = f"{ZR_BASE_URL.rstrip('/')}/parcels/import-parcels"
    api_headers = {
        "accept": "application/json",
        "X-Api-Key": ZR_API_KEY,
        "X-Tenant": ZR_TENANT_ID
    }
    
    print("🚀 [==== جاري الإرسال ====] 🚀")
    
    try:
        with open(temp_filename, 'rb') as f:
            files = {'file': (temp_filename, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(url, headers=api_headers, files=files)
            
        if response.status_code == 200:
            result = response.json()
            successes = result.get("succeededs", [])
            failures = result.get("faileds", [])
            
            print(f"🎯 [النتيجة الرسمية]: تم الاستلام! ({len(successes)} نجاح، {len(failures)} فشل)")
            
            if successes:
                print("[*] 📝 جاري تحديث الشيت (كتابة التتبع + تغيير الحالة)...")
                
                # تحديث UUID والحالة أولاً لكل الطلبيات الناجحة
                parcel_ids_to_fetch = []
                for s in successes:
                    zr_row_index = s.get("rowIndex")
                    tracking_id = s.get("parcelId")
                    if zr_row_index in row_mapping:
                        gsheet_row = row_mapping[zr_row_index]
                        sheet.update_cell(gsheet_row, idx_customer_id + 1, tracking_id)
                        time.sleep(0.8)
                        sheet.update_cell(gsheet_row, idx_status + 1, "Action")
                        time.sleep(0.8)
                        parcel_ids_to_fetch.append((gsheet_row, tracking_id))
                        print(f"  [+] الصف {gsheet_row} ⬅️ UUID: {tracking_id} | الحالة: Action ✅")

                # الانتظار لحين فهرسة الطلبيات الجديدة في API
                if parcel_ids_to_fetch:
                    print(f"[*] ⏳ انتظار 5 ثوانٍ لمزامنة بيانات الأسعار...")
                    time.sleep(5)
                    
                    search_url = f"{ZR_BASE_URL.rstrip('/')}/parcels/search"
                    search_headers = {
                        "accept": "application/json",
                        "Content-Type": "application/json",
                        "X-Api-Key": ZR_API_KEY,
                        "X-Tenant": ZR_TENANT_ID
                    }
                    
                    for gsheet_row, parcel_id in parcel_ids_to_fetch:
                        delivery_price = ""
                        return_price = ""
                        real_tracking = ""
                        
                        # البحث بـ advancedFilter مع الـ UUID (الطريقة الصحيحة حسب الـ API)
                        search_payload = {
                            "advancedFilter": {
                                "field": "id",
                                "operator": "eq",
                                "value": parcel_id
                            },
                            "pageSize": 1,
                            "pageNumber": 1
                        }
                        try:
                            search_res = requests.post(search_url, headers=search_headers, json=search_payload)
                            if search_res.status_code == 200:
                                items = search_res.json().get("items", [])
                                if items:
                                    matched = next((x for x in items if x.get("id") == parcel_id), items[0])
                                    delivery_price = matched.get("deliveryPrice", "")
                                    return_price = matched.get("returnPrice", "")
                                    real_tracking = matched.get("trackingNumber", "")
                        except Exception as ex:
                            print(f"  [⚠️] فشل في جلب تفاصيل الطلبية {parcel_id}: {ex}")
                        
                        # كتابة القيم المجلوبة في الشيت
                        if real_tracking:
                            sheet.update_cell(gsheet_row, idx_tracking + 1, real_tracking)
                            time.sleep(0.8)
                        if delivery_price != "":
                            sheet.update_cell(gsheet_row, idx_delivery_price + 1, delivery_price)
                            time.sleep(0.8)
                        if return_price != "":
                            sheet.update_cell(gsheet_row, idx_return_price + 1, return_price)
                            time.sleep(0.8)
                        
                        print(f"  [📊] الصف {gsheet_row}: Tracking={real_tracking} | Delivery={delivery_price} | Return={return_price}")
            
            if failures:
                print("⚠️ [تنبيه] تم رفض بعض الطلبيات من الشركة:")
                for f in failures:
                    print(f" - الصف {f.get('rowIndex')} في الإكسل | السبب: {f.get('reason')}")
                    
        else:
            print(f"[❌] رفض السيرفر استقبال الملف (الكود {response.status_code}):\n{response.text}")
            
    except Exception as e:
        print(f"[❌] حدث خطأ طارئ أثناء الرفع: {e}")
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
    print(f"🎉 تمت المهمة لمتجر {sheet_name}! تحقق من الشيت الآن.")
if __name__ == "__main__":
    pass