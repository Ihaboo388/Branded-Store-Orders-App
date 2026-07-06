import gspread
import json

SHEET_NAME = "Branded Store Orders"

def upload_hubs_to_sheets():
    print("[*] جاري قراءة قاعدة بيانات المكاتب (Hubs)...")
    try:
        with open('zr_hubs_database.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
    except FileNotFoundError:
        print("❌ لم أجد ملف zr_hubs_database.json!")
        return

    print("[*] جاري الاتصال بجوجل شيت...")
    gc = gspread.service_account(filename='credentials.json')
    spreadsheet = gc.open(SHEET_NAME)

    # إنشاء التبويب الجديد
    try:
        worksheet = spreadsheet.worksheet("Hubs_DB")
        worksheet.clear()
        print("[*] تم العثور على تبويب Hubs_DB القديم، جاري تحديثه...")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title="Hubs_DB", rows="500", cols="60")
        print("[*] تم إنشاء تبويب Hubs_DB جديد...")

    wilayas = list(db.keys())
    max_hubs = max(len(hubs) for hubs in db.values()) if db else 0

    data_matrix = [wilayas] # الصف الأول هو أرقام الولايات (01, 16, 31...)
    
    for i in range(max_hubs):
        row = []
        for w in wilayas:
            if i < len(db[w]):
                row.append(db[w][i])
            else:
                row.append("")
        data_matrix.append(row)

    worksheet.update(values=data_matrix, range_name="A1")
    print("✅ تمت العملية بنجاح! قاعدة المكاتب أصبحت حية داخل جوجل شيت.")

if __name__ == "__main__":
    upload_hubs_to_sheets()