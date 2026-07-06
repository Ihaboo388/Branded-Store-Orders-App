import gspread
import json

SHEET_NAME = "Branded Store Orders"

def upload_database_to_sheets():
    print("[*] جاري قراءة ملف JSON للبلديات...")
    try:
        with open('zr_communes_database.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
    except FileNotFoundError:
        print("❌ لم أجد ملف zr_communes_database.json!")
        return

    print("[*] جاري الاتصال بجوجل شيت...")
    gc = gspread.service_account(filename='credentials.json')
    spreadsheet = gc.open(SHEET_NAME)

    # إنشاء تبويب جديد باسم "Communes_DB" (أو مسحه وتحديثه إذا كان موجوداً)
    try:
        worksheet = spreadsheet.worksheet("Communes_DB")
        worksheet.clear()
        print("[*] تم العثور على تبويب Communes_DB القديم، جاري تحديثه...")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title="Communes_DB", rows="1600", cols="60")
        print("[*] تم إنشاء تبويب Communes_DB جديد...")

    # تجهيز البيانات لتكون على شكل أعمدة (الولاية في الأعلى، والبلديات تحتها)
    wilayas = list(db.keys())
    max_communes = max(len(communes) for communes in db.values())

    data_matrix = [wilayas] # الصف الأول هو أسماء الولايات
    
    # ملء الصفوف بالبلديات
    for i in range(max_communes):
        row = []
        for wilaya in wilayas:
            if i < len(db[wilaya]):
                row.append(db[wilaya][i])
            else:
                row.append("") # خلية فارغة إذا انتهت بلديات هذه الولاية
        data_matrix.append(row)

    print("[*] جاري ضخ قاعدة البيانات في جوجل شيت (قد يستغرق بضع ثوانٍ)...")
    worksheet.update("A1", data_matrix)
    print("✅ تمت العملية بنجاح! قاعدة البيانات أصبحت حية داخل جوجل شيت.")

if __name__ == "__main__":
    upload_database_to_sheets()