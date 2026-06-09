import sys
import os
import time
import secrets
import PyPDF2
from core import get_ai_response, generate_image

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_slow(text, color="\033[0m"):
    sys.stdout.write(color)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.005)
    print("\033[0m")

def extract_text(filepath):
    if not os.path.exists(filepath):
        return None, "File tidak ditemukan."
    try:
        if filepath.endswith('.pdf'):
            with open(filepath, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                return text, None
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read(), None
    except Exception as e:
        return None, str(e)

def main():
    clear_screen()
    print("\033[95m" + "╔" + "═"*58 + "╗")
    print("║" + " "*21 + "🚀 HAZZ-1 SUPER CLI 🚀" + " "*21 + "║")
    print("║" + " "*17 + "Intelligence Series (Ver 2.0)" + " "*18 + "║")
    print("╚" + "═"*58 + "╝" + "\033[0m")
    print("Ketik \033[92m/help\033[0m untuk perintah lengkap.")
    print("Ketik \033[91m/exit\033[0m untuk keluar.\n")

    history = []
    current_model = 'hazz-1-ultra'
    current_engine = 'ultra'
    attached_context = ""
    custom_personality = ""

    while True:
        try:
            model_name = current_model.split('-')[-1].upper()
            user_input = input(f"\033[94m[{model_name}] User »\033[0m ").strip()

            if not user_input:
                continue

            if user_input.lower() == '/exit':
                print_slow("\n[Hazz-1] Sampai jumpa! 🌌", "\033[93m")
                break

            if user_input.lower() == '/help':
                print("\n\033[96m💠 PERINTAH NAVIGASI:")
                print("  /model [ultra/thinking/search/vision] : Ganti mode AI")
                print("  /engine [ultra/fast]                 : Ganti engine respon")
                print("  /clear                               : Bersihkan terminal")

                print("\n\033[92m💠 FITUR LANJUTAN:")
                print("  /load [path_file]    : Analisis dokumen (PDF/TXT)")
                print("  /image [prompt]      : Generate gambar (Flux)")
                print("  /personality [text]  : Setel kepribadian custom")
                print("  /reset               : Reset chat & context")
                print("  /tools               : Daftar shortcut perintah")

                print("\n\033[93m💠 STATUS:")
                print(f"  Current: {current_model} | {current_engine}")
                print(f"  Context: {'Aktif' if attached_context else 'Kosong'}\033[0m\n")
                continue

            if user_input.lower() == '/reset':
                history = []
                attached_context = ""
                custom_personality = ""
                print("\033[92m[Sistem] Memori dan konteks telah dibersihkan.\033[0m\n")
                continue

            if user_input.lower() == '/tools':
                print("\n\033[95m🛠️ QUICK TOOLS:")
                print("  /t [text] : Translate ke Indo")
                print("  /s [text] : Ringkas teks")
                print("  /c [text] : Rapikan kode")
                print("  /m [text] : Selesaikan matematika\033[0m\n")
                continue

            if user_input.startswith('/model '):
                m = user_input.split(' ')[1].lower()
                if m in ['ultra', 'thinking', 'search', 'vision']:
                    current_model = f'hazz-1-{m}'
                    print(f"\033[92m[Sistem] Mode beralih ke {current_model.upper()}\033[0m\n")
                continue

            if user_input.startswith('/load '):
                path = user_input[6:].strip()
                print(f"\033[93m[Sistem] Membaca {path}...\033[0m")
                text, err = extract_text(path)
                if err:
                    print(f"\033[91mError: {err}\033[0m\n")
                else:
                    attached_context = f"\n[FILE: {path}]\n{text}\n"
                    print(f"\033[92m[Sistem] File dimuat!\033[0m\n")
                    current_model = 'hazz-1-vision'
                continue

            if user_input.startswith('/personality '):
                custom_personality = user_input[13:].strip()
                print(f"\033[92m[Sistem] Kepribadian baru ditetapkan.\033[0m\n")
                continue

            if user_input.startswith('/t '): user_input = "Translate ke Indonesia: " + user_input[3:]
            elif user_input.startswith('/s '): user_input = "Ringkas teks ini: " + user_input[3:]
            elif user_input.startswith('/c '): user_input = "Format dan jelaskan kode ini: " + user_input[3:]
            elif user_input.startswith('/m '): user_input = "Selesaikan soal matematika ini: " + user_input[3:]

            if user_input.startswith('/image '):
                prompt = user_input[7:]
                print("\033[93m🎨 Menggenerasi visual...\033[0m")
                url = generate_image(prompt)
                print(f"\033[92mLink Gambar: {url}\033[0m\n")
                continue

            print("\033[95mThinking...\033[0m", end="\r")

            full_context = attached_context
            if custom_personality:
                full_context = f"PERSONA: {custom_personality}\n{full_context}"

            response = get_ai_response(user_input, model=current_model, engine=current_engine, history=history, context=full_context)

            sys.stdout.write("\033[K")
            print(f"\n\033[96mAI »\033[0m")

            if "<thought>" in response:
                try:
                    thought, clean_resp = response.split("</thought>")
                    thought = thought.replace("<thought>", "").strip()
                    print(f"\033[90m[Thought Process]\033[0m\n\033[90m{thought}\033[0m\n")
                    print_slow(clean_resp.strip())
                except:
                    print_slow(response)
            else:
                print_slow(response)

            print()

            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})

            if len(history) > 20:
                history = history[-20:]

        except KeyboardInterrupt:
            print("\n\033[93m[Sistem] Keluar...\033[0m")
            break
        except Exception as e:
            print(f"\n\033[91m[Error] {e}\033[0m\n")

if __name__ == "__main__":
    main()
