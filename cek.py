import google.generativeai as genai

# Ganti dengan API Key milikmu yang asli
API_KEY = "AIzaSyDEdaMYsa2-atfoYl_Ef1Q37TIuCDhXTIY"
genai.configure(api_key=API_KEY)

print("Mencari model yang tersedia untuk API Key ini...")
print("-" * 40)

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
    print("-" * 40)
    print("Pencarian selesai!")
except Exception as e:
    print("Terjadi error saat mengecek:", e)