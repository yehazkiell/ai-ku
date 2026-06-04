import sys
import os
import time
from core import get_ai_response, generate_image

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_slow(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.005)
    print()

def main():
    clear_screen()
    print("\033[95m" + "="*50)
    print("      🚀 HAZZ-1 SUPER AI - CLI EDITION 🚀")
    print("="*50 + "\033[0m")
    print("Ketik '/help' untuk melihat perintah.")
    print("Ketik '/exit' untuk keluar.\n")

    history = []
    current_model = 'hazz-1-ultra'
    current_engine = 'ultra'

    while True:
        try:
            user_input = input(f"\033[94m[Hazz-{current_model.split('-')[-1]}] User:\033[0m ").strip()

            if not user_input:
                continue

            if user_input.lower() == '/exit':
                print("\n\033[93mSampai jumpa! Hazz-1 pamit.\033[0m")
                break

            if user_input.lower() == '/help':
                print("\n\033[92mPerintah yang tersedia:")
                print("- /model [ultra/thinking/search/vision] : Ganti model")
                print("- /engine [ultra/fast] : Ganti engine")
                print("- /image [prompt] : Generate gambar")
                print("- /clear : Bersihkan layar")
                print("- /history : Tampilkan riwayat percakapan")
                print("- /exit : Keluar\033[0m\n")
                continue

            if user_input.lower() == '/clear':
                clear_screen()
                continue

            if user_input.startswith('/model '):
                m = user_input.split(' ')[1]
                if m in ['ultra', 'thinking', 'search', 'vision']:
                    current_model = f'hazz-1-{m}'
                    print(f"\033[92mModel diganti ke {current_model}\033[0m\n")
                continue

            if user_input.startswith('/engine '):
                e = user_input.split(' ')[1]
                if e in ['ultra', 'fast']:
                    current_engine = e
                    print(f"\033[92mEngine diganti ke {current_engine}\033[0m\n")
                continue

            if user_input.startswith('/image '):
                prompt = user_input[7:]
                print("\033[93mMenggenerasi gambar...\033[0m")
                url = generate_image(prompt)
                print(f"\033[92mGambar berhasil dibuat: {url}\033[0m\n")
                continue

            # Standard Chat
            print("\033[95mHazz-1 sedang berpikir...\033[0m", end="\r")
            response = get_ai_response(user_input, model=current_model, engine=current_engine, history=history)

            # Remove "Hazz-1 sedang berpikir..."
            sys.stdout.write("\033[K")

            print(f"\n\033[96mAI:\033[0m")
            print_slow(response)
            print()

            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})

        except KeyboardInterrupt:
            print("\n\033[93mKeluar...\033[0m")
            break
        except Exception as e:
            print(f"\n\033[91mTerjadi kesalahan: {e}\033[0m\n")

if __name__ == "__main__":
    main()
