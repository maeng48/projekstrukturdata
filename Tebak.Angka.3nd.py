import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
from datetime import datetime
import logging

class TebakAngkaGame:
    def __init__(self, root):
        self.root = root
        self.setup_logging()
        self.load_config()
        self.init_game_state()
        self.setup_ui()
        self.load_leaderboard()
        self.tampilkan_menu_utama()

    # ==================== INITIAL SETUP ====================
    def setup_logging(self):
        """Setup logging untuk mencatat aktivitas game"""
        logging.basicConfig(
            filename='game.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("Game initialized")

    def load_config(self):
        """Load konfigurasi game dari file atau gunakan default"""
        try:
            with open('config.json') as f:
                config = json.load(f)
                self.tingkat_kesulitan = config.get('difficulty_levels', {
                    'Mudah': {'range': (1, 50), 'nyawa': 10, 'petunjuk': True},
                    'Normal': {'range': (1, 100), 'nyawa': 7, 'petunjuk': True},
                    'Sulit': {'range': (1, 200), 'nyawa': 5, 'petunjuk': False},
                    'Expert': {'range': (1, 500), 'nyawa': 3, 'petunjuk': False}
                })
        except FileNotFoundError:
            logging.warning("Config file not found, using defaults")
            self.tingkat_kesulitan = {
                'Mudah': {'range': (1, 50), 'nyawa': 10, 'petunjuk': True},
                'Normal': {'range': (1, 100), 'nyawa': 7, 'petunjuk': True},
                'Sulit': {'range': (1, 200), 'nyawa': 5, 'petunjuk': False},
                'Expert': {'range': (1, 500), 'nyawa': 3, 'petunjuk': False}
            }

    def init_game_state(self):
        """Inisialisasi state permainan"""
        self.root.title("Tebak Angka")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        self.mode = "menu"
        self.kode_rahasia = 0
        self.riwayat_tebakan = []
        self.pemain = {}
        self.pemain_aktif = None
        self.level_terpilih = 'Normal'
        self.leaderboard = []
        
        # Setup style GUI
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10))
        self.style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Pemain1.TLabel', foreground='blue')
        self.style.configure('Pemain2.TLabel', foreground='red')
        self.style.configure('Pemain3.TLabel', foreground='green')
        self.style.configure('Pemain4.TLabel', foreground='purple')

    def setup_ui(self):
        """Setup antarmuka utama"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.footer_frame = ttk.Frame(self.main_frame)
        self.footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Label(self.header_frame, text="TEBAK ANGKA", style='Title.TLabel').pack()
        ttk.Label(self.footer_frame, text="© 2023 Game Tebak Angka").pack(side=tk.LEFT)

    # ==================== GAME LOGIC ====================
    def generate_secret_number(self, level):
        """Generate angka rahasia berdasarkan level"""
        return random.randint(*self.tingkat_kesulitan[level]['range'])

    def analisis_tebakan(self, tebakan):
        """Analisis hasil tebakan pemain"""
        selisih = abs(tebakan - self.kode_rahasia)
        
        if selisih == 0:
            return "TEPAT SASARAN"
        elif selisih <= 5:
            return f"SANGAT DEKAT ({'RENDAH' if tebakan < self.kode_rahasia else 'TINGGI'})"
        elif selisih <= 15:
            return f"DEKAT ({'RENDAH' if tebakan < self.kode_rahasia else 'TINGGI'})"
        elif selisih <= 30:
            return f"AGAK JAUH ({'RENDAH' if tebakan < self.kode_rahasia else 'TINGGI'})"
        else:
            return f"SANGAT JAUH ({'RENDAH' if tebakan < self.kode_rahasia else 'TINGGI'})"

    # ==================== MENU SYSTEM ====================
    def clear_content(self):
        """Hapus konten dari frame utama"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def tampilkan_menu_utama(self):
        """Tampilkan menu utama"""
        self.clear_content()
        self.mode = "menu"
        
        ttk.Label(self.content_frame, text="Pilih Mode Permainan:").pack(pady=(20, 10))
        
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)
        
        buttons = [
            ("SOLO PLAYER", self.tampilkan_menu_level),
            ("MULTIPLAYER OFFLINE", self.tampilkan_menu_multiplayer),
            ("LEADERBOARD", self.tampilkan_leaderboard),
            ("PANDUAN", self.tampilkan_panduan),
            ("KELUAR", self.root.quit)
        ]
        
        for text, command in buttons:
            ttk.Button(btn_frame, text=text, command=command).pack(fill=tk.X, pady=5)

    def tampilkan_menu_level(self):
        """Tampilkan menu pemilihan level"""
        self.clear_content()
        
        ttk.Label(self.content_frame, text="PILIH TINGKAT KESULITAN", style='Title.TLabel').pack(pady=(10, 20))
        
        for level in self.tingkat_kesulitan:
            info = self.tingkat_kesulitan[level]
            text = f"{level} (1-{info['range'][1]}, {info['nyawa']} nyawa)"
            
            ttk.Button(
                self.content_frame,
                text=text,
                command=lambda l=level: self.set_level(l)
            ).pack(fill=tk.X, pady=3)
        
        ttk.Button(
            self.content_frame,
            text="KEMBALI",
            command=self.tampilkan_menu_utama
        ).pack(fill=tk.X, pady=(20, 0))

    def set_level(self, level):
        """Set level permainan dan mulai game"""
        self.level_terpilih = level
        if self.mode == "menu":
            self.mulai_game_solo()
        else:
            self.mulai_game_multiplayer()

    # ==================== GAME MODES ====================
    def mulai_game_solo(self):
        """Mulai permainan solo"""
        self.pemain = {
            1: {
                "nama": "Anda",
                "skor": 0,
                "nyawa": self.tingkat_kesulitan[self.level_terpilih]['nyawa'],
                "petunjuk": self.tingkat_kesulitan[self.level_terpilih]['petunjuk']
            }
        }
        self.pemain_aktif = 1
        self.kode_rahasia = self.generate_secret_number(self.level_terpilih)
        self.riwayat_tebakan = []
        self.mode = "solo"
        self.tampilkan_game_ui()

    def tampilkan_menu_multiplayer(self):
        """Tampilkan menu multiplayer offline"""
        self.clear_content()
        self.mode = "multiplayer_menu"
        
        header_frame = ttk.Frame(self.content_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="MULTIPLAYER OFFLINE", style='Title.TLabel').pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Kembali", command=self.tampilkan_menu_utama).pack(side=tk.RIGHT)
        
        ttk.Label(self.content_frame, text="Pilih Tingkat Kesulitan:").pack(pady=(20, 10))
        
        for level in self.tingkat_kesulitan:
            info = self.tingkat_kesulitan[level]
            text = f"{level} (1-{info['range'][1]}, {info['nyawa']} nyawa)"
            
            ttk.Button(
                self.content_frame,
                text=text,
                command=lambda l=level: self.set_level_multiplayer(l)
            ).pack(fill=tk.X, pady=3)

    def set_level_multiplayer(self, level):
        """Set level untuk multiplayer dan lanjut ke input nama pemain"""
        self.level_terpilih = level
        self.tampilkan_input_nama_pemain()

    def tampilkan_input_nama_pemain(self):
        """Tampilkan form input nama pemain untuk multiplayer"""
        self.clear_content()
        
        ttk.Label(self.content_frame, text="MASUKKAN NAMA PEMAIN", style='Title.TLabel').pack(pady=20)
        
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(pady=10)
        
        self.pemain_entries = []
        for i in range(1, 5):
            frame = ttk.Frame(input_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=f"Pemain {i}:").pack(side=tk.LEFT, padx=5)
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.pemain_entries.append(entry)
        
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="MULAI", command=self.mulai_game_multiplayer).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="BATAL", command=self.tampilkan_menu_multiplayer).pack(side=tk.LEFT, padx=5)

    def mulai_game_multiplayer(self):
        """Mulai permainan multiplayer dengan nama pemain yang diinput"""
        self.pemain = {}
        
        for i, entry in enumerate(self.pemain_entries, 1):
            nama = entry.get().strip()
            if nama:
                self.pemain[i] = {
                    "nama": nama,
                    "skor": 0,
                    "nyawa": self.tingkat_kesulitan[self.level_terpilih]['nyawa'],
                    "petunjuk": self.tingkat_kesulitan[self.level_terpilih]['petunjuk']
                }
        
        if len(self.pemain) < 2:
            messagebox.showerror("Error", "Minimal 2 pemain untuk mode multiplayer")
            return
        
        self.kode_rahasia = self.generate_secret_number(self.level_terpilih)
        self.riwayat_tebakan = []
        self.pemain_aktif = 1
        self.mode = "offline"
        self.tampilkan_game_ui()

    # ==================== GAME UI ====================
    def tampilkan_game_ui(self):
        """Tampilkan antarmuka permainan"""
        self.clear_content()
        
        # Label giliran pemain
        self.label_giliran = ttk.Label(
            self.content_frame, 
            text=f"Giliran: {self.pemain[self.pemain_aktif]['nama']}", 
            style=f'Pemain{self.pemain_aktif}.TLabel' if self.pemain_aktif in [1,2,3,4] else 'TLabel'
        )
        self.label_giliran.pack(pady=10)

        # Frame input tebakan
        tebakan_frame = ttk.Frame(self.content_frame)
        tebakan_frame.pack(pady=10)
        
        ttk.Label(tebakan_frame, text="Masukkan Tebakan:").pack(side=tk.LEFT, padx=(0, 10))
        self.entry_tebakan = ttk.Entry(tebakan_frame)
        self.entry_tebakan.pack(side=tk.LEFT)
        self.entry_tebakan.bind('<Return>', lambda e: self.aksi_tebakan())
        
        self.btn_tebak = ttk.Button(tebakan_frame, text="TEBAK", command=self.aksi_tebakan)
        self.btn_tebak.pack(side=tk.LEFT, padx=5)

        # Riwayat tebakan
        self.riwayat_tree = ttk.Treeview(
            self.content_frame, 
            columns=("Waktu", "Pemain", "Tebakan", "Hasil"), 
            show="headings",
            height=10
        )
        for col in ("Waktu", "Pemain", "Tebakan", "Hasil"):
            self.riwayat_tree.heading(col, text=col)
            self.riwayat_tree.column(col, width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.riwayat_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.riwayat_tree.configure(yscrollcommand=scrollbar.set)
        self.riwayat_tree.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

        # Petunjuk tebakan
        self.petunjuk_text = tk.Text(
            self.content_frame, 
            height=8, 
            state=tk.DISABLED,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.petunjuk_text.pack(fill=tk.BOTH, padx=10, pady=10)

        # Tombol kontrol
        control_frame = ttk.Frame(self.content_frame)
        control_frame.pack(pady=10)
        
        if self.mode == "offline":
            ttk.Button(control_frame, text="BATALKAN TEBAKAN", command=self.batalkan_tebakan).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="CHAT", command=self.tampilkan_chat).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="KEMBALI KE MENU", command=self.tampilkan_menu_utama).pack(side=tk.LEFT, padx=5)

        self.update_info_pemain()
        self.update_riwayat_tebakan()
        self.update_petunjuk()

    def aksi_tebakan(self):
        """Proses tebakan dari pemain"""
        tebakan_str = self.entry_tebakan.get().strip()
        if not tebakan_str:
            return
            
        try:
            tebakan = int(tebakan_str)
        except ValueError:
            messagebox.showerror("Error", "Tebakan harus berupa angka")
            return
            
        level_info = self.tingkat_kesulitan[self.level_terpilih]
        if not (1 <= tebakan <= level_info["range"][1]):
            messagebox.showerror("Error", f"Tebakan harus antara 1 - {level_info['range'][1]}")
            return
            
        self.entry_tebakan.delete(0, tk.END)
        
        if self.mode == "solo":
            self.proses_tebakan_solo(tebakan)
        elif self.mode == "offline":
            self.proses_tebakan_offline(tebakan)

    def proses_tebakan_solo(self, tebakan):
        """Proses tebakan untuk mode solo"""
        waktu = datetime.now().strftime("%H:%M:%S")
        self.riwayat_tebakan.append({
            "waktu": waktu,
            "pemain": 1,
            "tebakan": tebakan,
            "hasil": self.analisis_tebakan(tebakan)
        })
        
        self.pemain[1]["nyawa"] -= 1
        
        if tebakan == self.kode_rahasia:
            self.pemain[1]["skor"] += 1
            self.add_to_leaderboard("Anda", self.pemain[1]["skor"], "Solo", self.level_terpilih)
            self.update_riwayat_tebakan()
            messagebox.showinfo("Selamat!", f"Anda menang! Angka rahasia: {self.kode_rahasia}")
            self.tampilkan_menu_utama()
            return
        
        if self.pemain[1]["nyawa"] <= 0:
            self.update_riwayat_tebakan()
            messagebox.showinfo("Game Over", f"Anda kalah! Angka rahasia: {self.kode_rahasia}")
            self.tampilkan_menu_utama()
            return
        
        self.update_info_pemain()
        self.update_riwayat_tebakan()
        self.update_petunjuk(tebakan)

    def proses_tebakan_offline(self, tebakan):
        """Proses tebakan untuk mode offline multiplayer"""
        waktu = datetime.now().strftime("%H:%M:%S")
        self.riwayat_tebakan.append({
            "waktu": waktu,
            "pemain": self.pemain_aktif,
            "tebakan": tebakan,
            "hasil": self.analisis_tebakan(tebakan)
        })
        
        self.pemain[self.pemain_aktif]["nyawa"] -= 1
        
        if tebakan == self.kode_rahasia:
            self.pemain[self.pemain_aktif]["skor"] += 1
            self.add_to_leaderboard(
                self.pemain[self.pemain_aktif]['nama'], 
                self.pemain[self.pemain_aktif]["skor"], 
                "Offline", 
                self.level_terpilih
            )
            self.update_riwayat_tebakan()
            messagebox.showinfo("Selamat!", f"{self.pemain[self.pemain_aktif]['nama']} menang! Angka rahasia: {self.kode_rahasia}")
            self.tampilkan_menu_utama()
            return
        
        if all(p["nyawa"] <= 0 for p in self.pemain.values()):
            self.update_riwayat_tebakan()
            messagebox.showinfo("Game Over", f"Semua pemain kalah! Angka rahasia: {self.kode_rahasia}")
            self.tampilkan_menu_utama()
            return
        
        # Ganti giliran ke pemain berikutnya
        self.next_player()
        
        self.update_info_pemain()
        self.update_riwayat_tebakan()
        self.update_petunjuk(tebakan)

    def next_player(self):
        """Ganti ke pemain berikutnya yang masih memiliki nyawa"""
        total_pemain = len(self.pemain)
        next_p = self.pemain_aktif % total_pemain + 1
        
        while self.pemain[next_p]["nyawa"] <= 0:
            next_p = next_p % total_pemain + 1
            if all(p["nyawa"] <= 0 for p in self.pemain.values()):
                break
                
        self.pemain_aktif = next_p

    def batalkan_tebakan(self):
        """Batalkan tebakan terakhir (hanya untuk mode offline)"""
        if self.riwayat_tebakan and self.mode == "offline":
            tebakan_dibatalkan = self.riwayat_tebakan.pop()
            pemain_id = tebakan_dibatalkan["pemain"]
            self.pemain[pemain_id]["nyawa"] += 1
            self.pemain_aktif = pemain_id
            
            self.update_info_pemain()
            self.update_riwayat_tebakan()
            messagebox.showinfo("Info", f"Tebakan {tebakan_dibatalkan['tebakan']} dibatalkan")
        else:
            messagebox.showwarning("Peringatan", "Tidak ada tebakan untuk dibatalkan")

    # ==================== CHAT SYSTEM ====================
    def tampilkan_chat(self):
        """Tampilkan window chat untuk multiplayer"""
        self.chat_window = tk.Toplevel(self.root)
        self.chat_window.title("Chat Room")
        self.chat_window.geometry("400x300")
        
        chat_frame = ttk.Frame(self.chat_window)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_text = tk.Text(chat_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X)
        
        self.entry_chat = ttk.Entry(input_frame)
        self.entry_chat.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry_chat.bind('<Return>', lambda e: self.kirim_pesan_chat())
        
        ttk.Button(input_frame, text="Kirim", command=self.kirim_pesan_chat).pack(side=tk.RIGHT)
        
        self.chat_text.see(tk.END)

    def kirim_pesan_chat(self):
        """Kirim pesan chat"""
        pesan = self.entry_chat.get().strip()
        if not pesan:
            return
        
        self.entry_chat.delete(0, tk.END)
        self.tampilkan_pesan_chat(self.pemain_aktif, pesan)

    def tampilkan_pesan_chat(self, pemain_id, pesan):
        """Tampilkan pesan di window chat"""
        if not hasattr(self, 'chat_text'):
            return
        
        nama = self.pemain[pemain_id]["nama"]
        waktu = datetime.now().strftime("%H:%M:%S")
        
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"[{waktu}] {nama}: {pesan}\n")
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)

    # ==================== UI UPDATES ====================
    def update_info_pemain(self):
        """Update informasi pemain di UI"""
        if hasattr(self, 'label_giliran'):
            self.label_giliran.config(text=f"Giliran: {self.pemain[self.pemain_aktif]['nama']}")
            if self.pemain_aktif in [1,2,3,4]:
                self.label_giliran.configure(style=f"Pemain{self.pemain_aktif}.TLabel")
            else:
                self.label_giliran.configure(style="TLabel")
        
        if hasattr(self, 'btn_tebak'):
            self.btn_tebak.config(state=tk.NORMAL)

    def update_riwayat_tebakan(self):
        """Update tampilan riwayat tebakan"""
        if not hasattr(self, 'riwayat_tree'):
            return
            
        for item in self.riwayat_tree.get_children():
            self.riwayat_tree.delete(item)
        
        for tebak in self.riwayat_tebakan:
            pemain_nama = self.pemain[tebak["pemain"]]["nama"]
            self.riwayat_tree.insert("", tk.END, values=(
                tebak["waktu"],
                pemain_nama,
                tebak["tebakan"],
                tebak["hasil"]
            ))

    def update_petunjuk(self, tebakan=None):
        """Update petunjuk berdasarkan tebakan terakhir"""
        if not hasattr(self, 'petunjuk_text'):
            return
            
        self.petunjuk_text.config(state=tk.NORMAL)
        self.petunjuk_text.delete(1.0, tk.END)
        
        level_info = self.tingkat_kesulitan[self.level_terpilih]
        
        if not tebakan or not self.riwayat_tebakan:
            petunjuk = f"Tebak angka antara 1-{level_info['range'][1]}\n"
            petunjuk += f"Nyawa: {self.pemain[self.pemain_aktif]['nyawa']}"
            
            if level_info['petunjuk']:
                petunjuk += "\n\nPetunjuk akan muncul setelah tebakan pertama"
        else:
            tebakan_terakhir = self.riwayat_tebakan[-1]['tebakan']
            pemain_terakhir = self.riwayat_tebakan[-1]['pemain']
            selisih = abs(tebakan_terakhir - self.kode_rahasia)
            
            petunjuk = f"Tebakan terakhir ({self.pemain[pemain_terakhir]['nama']}): {tebakan_terakhir}\n"
            
            if tebakan_terakhir < self.kode_rahasia:
                petunjuk += "➤ Terlalu rendah\n"
            else:
                petunjuk += "➤ Terlalu tinggi\n"
            
            if selisih <= 5:
                petunjuk += "★ Sangat dekat! (±5 angka)\n"
            elif selisih <= 15:
                petunjuk += "○ Dekat (±15 angka)\n"
            elif selisih <= 30:
                petunjuk += "△ Agak jauh (±30 angka)\n"
            else:
                petunjuk += "✖ Masih sangat jauh\n"
            
            petunjuk += f"\nNyawa: {self.pemain[self.pemain_aktif]['nyawa']}"
        
        self.petunjuk_text.insert(tk.END, petunjuk)
        self.petunjuk_text.config(state=tk.DISABLED)

    # ==================== LEADERBOARD ====================
    def tampilkan_leaderboard(self):
        """Tampilkan leaderboard"""
        self.clear_content()
        
        header_frame = ttk.Frame(self.content_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="LEADERBOARD", style='Title.TLabel').pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Kembali", command=self.tampilkan_menu_utama).pack(side=tk.RIGHT)
        
        # Filter options
        filter_frame = ttk.Frame(self.content_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT)
        
        self.filter_mode = tk.StringVar(value="Semua")
        mode_menu = ttk.OptionMenu(
            filter_frame, self.filter_mode, "Semua", 
            "Semua", "Solo", "Offline", 
            command=lambda _: self.update_leaderboard_display()
        )
        mode_menu.pack(side=tk.LEFT, padx=5)
        
        self.filter_level = tk.StringVar(value="Semua")
        level_menu = ttk.OptionMenu(
            filter_frame, self.filter_level, "Semua", 
            "Semua", "Mudah", "Normal", "Sulit", "Expert",
            command=lambda _: self.update_leaderboard_display()
        )
        level_menu.pack(side=tk.LEFT, padx=5)
        
        # Leaderboard table
        table_frame = ttk.Frame(self.content_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Peringkat", "Nama", "Skor", "Mode", "Level", "Tanggal")
        self.leaderboard_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        for col in columns:
            self.leaderboard_tree.heading(col, text=col)
            self.leaderboard_tree.column(col, width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.leaderboard_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.leaderboard_tree.configure(yscrollcommand=scrollbar.set)
        self.leaderboard_tree.pack(fill=tk.BOTH, expand=True)
        
        # Reset button
        ttk.Button(
            self.content_frame,
            text="Reset Leaderboard",
            command=self.reset_leaderboard_confirmation
        ).pack(pady=(10, 0))
        
        self.update_leaderboard_display()

    def update_leaderboard_display(self):
        """Update tampilan leaderboard berdasarkan filter"""
        for item in self.leaderboard_tree.get_children():
            self.leaderboard_tree.delete(item)
        
        filtered_data = self.leaderboard.copy()
        
        if self.filter_mode.get() != "Semua":
            filtered_data = [entry for entry in filtered_data if entry["mode"] == self.filter_mode.get()]
        
        if self.filter_level.get() != "Semua":
            filtered_data = [entry for entry in filtered_data if entry["level"] == self.filter_level.get()]
        
        filtered_data = filtered_data[:50]  # Limit to top 50
        
        for i, entry in enumerate(filtered_data, 1):
            self.leaderboard_tree.insert("", tk.END, values=(
                i,
                entry["nama"],
                entry["skor"],
                entry["mode"],
                entry["level"],
                entry["tanggal"]
            ))

    def reset_leaderboard_confirmation(self):
        """Konfirmasi reset leaderboard"""
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin mereset leaderboard? Semua data akan hilang."):
            self.leaderboard = []
            self.save_leaderboard()
            self.update_leaderboard_display()
            messagebox.showinfo("Info", "Leaderboard telah direset")

    def load_leaderboard(self):
        """Load leaderboard dari file"""
        try:
            with open('leaderboard.json', 'r') as f:
                self.leaderboard = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.leaderboard = []
            logging.warning("Leaderboard file not found or corrupted, creating new one")

    def add_to_leaderboard(self, nama, skor, mode, level):
        """Tambahkan entri baru ke leaderboard"""
        entry = {
            "nama": nama,
            "skor": skor,
            "mode": mode,
            "level": level,
            "tanggal": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        self.leaderboard.append(entry)
        self.leaderboard = sorted(self.leaderboard, key=lambda x: x["skor"], reverse=True)
        self.save_leaderboard()

    def save_leaderboard(self):
        """Simpan leaderboard ke file"""
        try:
            with open('leaderboard.json', 'w') as f:
                json.dump(self.leaderboard, f, indent=2)
        except Exception as e:
            logging.error(f"Gagal menyimpan leaderboard: {e}")

    # ==================== PANDUAN ====================
    def tampilkan_panduan(self):
        """Tampilkan panduan permainan"""
        self.clear_content()
        
        panduan_text = """
        PANDUAN PERMAINAN TEBAK ANGKA

        1. MODE PERMAINAN:
           - SOLO: Bermain sendiri melawan komputer
           - OFFLINE: 2-4 pemain bergantian di 1 device

        2. TINGKAT KESULITAN:
           - Mudah: Angka 1-50, 10 nyawa, petunjuk lengkap
           - Normal: Angka 1-100, 7 nyawa, petunjuk lengkap
           - Sulit: Angka 1-200, 5 nyawa, petunjuk terbatas
           - Expert: Angka 1-500, 3 nyawa, tanpa petunjuk

        3. CARA BERMAIN:
           - Setiap pemain menebak angka secara bergiliran
           - Sistem akan memberikan petunjuk apakah tebakan terlalu tinggi/rendah
           - Pemain yang menebak angka dengan benar pertama kali menang
           - Jika nyawa habis sebelum ada yang menebak dengan benar, semua pemain kalah

        4. FITUR:
           - Leaderboard untuk melihat skor tertinggi
           - Riwayat semua tebakan yang sudah dilakukan
           - Petunjuk berdasarkan level kesulitan
           - Batalkan tebakan terakhir (mode offline)
           - Chat room (mode multiplayer)
        """
        
        text_widget = tk.Text(
            self.content_frame, 
            wrap=tk.WORD, 
            font=('Helvetica', 10), 
            padx=10, 
            pady=10,
            height=20
        )
        text_widget.insert(tk.END, panduan_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(
            self.content_frame, 
            text="KEMBALI KE MENU UTAMA", 
            command=self.tampilkan_menu_utama
        ).pack(fill=tk.X, pady=(10, 0))

if __name__ == "__main__":
    root = tk.Tk()
    game = TebakAngkaGame(root)
    root.mainloop()