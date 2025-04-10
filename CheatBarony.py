import pymem
import tkinter as tk
from tkinter import ttk, messagebox
from pymem.exception import ProcessNotFound

class BaronyHack:
    def __init__(self):
        self.pm = pymem.Pymem()
        self.base_addr = None
        self.current_player = 0
        self.player_addresses = [0]*4

        self.offsets = {
            # Персонаж
            'name': (0x4C, True),
            'current_health': (0x180, False),
            'max_health': (0x184, False),
            'current_mana': (0x190, False),
            'max_mana': (0x18C, False),
            'level': (0x1B0, False),
            'xp': (0x1AC, False),
            'gold': (0x1B4, False),
            'sex': (0x44, False),
            # Атрибуты
            'strength': (0x194, False),
            'dexterity': (0x198, False),
            'constitution': (0x19C, False),
            'intelligence': (0x1A0, False),
            'perception': (0x1A4, False),
            'charisma': (0x1A8, False),
            # Навыки
            'tinkering': (0x0, False),
            'stealth': (0x4, False),
            'trading': (0x8, False),
            'appraisal': (0xC, False),
            'swimming': (0x10, False),
            'leadership': (0x14, False),
            'magic': (0x1C, False),
            'ranged': (0x20, False),
            'swords': (0x24, False),
            'maces': (0x28, False),
            'axes': (0x2C, False),
            'polearms': (0x30, False),
            'blocking': (0x34, False),
            'unarmed': (0x38, False),
            'alchemy': (0x3C, False),
            # Мир
            'skybox': (0xC21090, 0x48)
        }

        self.setup_gui()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Barony Cheat By MelgosaSko 1.0")
        self.root.geometry("1000x800")

        # Status Bar
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = tk.Label(self.status_frame, text="Статус: Не подключено", fg="red")
        self.status_label.pack(side=tk.LEFT)
        
        self.addr_label = tk.Label(self.status_frame, text="Адрес: Нет")
        self.addr_label.pack(side=tk.RIGHT)
        
        # Control Buttons
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=5)
        
        self.connect_btn = tk.Button(self.control_frame, text="Подключиться к игре", 
                                   command=self.connect)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = tk.Button(self.control_frame, text="Обновить все значения", 
                                    command=self.load_current_values, state=tk.DISABLED)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=1, fill=tk.BOTH)
        
        # Character Tab
        self.char_frame = tk.Frame(self.notebook)
        self.setup_character_tab()
        
        # World Tab
        self.world_frame = tk.Frame(self.notebook)
        self.setup_world_tab()
        
        self.notebook.add(self.char_frame, text="Персонажи")
        self.notebook.add(self.world_frame, text="Мир")

    def create_section(self, parent, title, fields):
        frame = tk.LabelFrame(parent, text=title)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        for i, (label_text, field) in enumerate(fields):
            row = i // 3
            col = i % 3
            
            if i % 3 == 0:
                subframe = tk.Frame(frame)
                subframe.pack(fill=tk.X)
            
            lbl = tk.Label(subframe, text=label_text, width=15, anchor=tk.W)
            lbl.pack(side=tk.LEFT, padx=5)
            
            entry = tk.Entry(subframe, width=10)
            entry.pack(side=tk.LEFT)
            
            btn = tk.Button(subframe, text="Set", command=lambda f=field: self.update_field(f))
            btn.pack(side=tk.LEFT, padx=5)
            
            setattr(self, f"{field}_entry", entry)
            setattr(self, f"{field}_btn", btn)

    def setup_character_tab(self):
        # Player Selector
        self.player_selector = ttk.Combobox(self.char_frame, 
                                          values=[f"Персонаж {i+1}" for i in range(4)])
        self.player_selector.current(0)
        self.player_selector.pack(pady=5)
        self.player_selector.bind("<<ComboboxSelected>>", self.on_player_change)
        
        # Основные параметры
        main_fields = [
            ("Имя:", 'name'),
            ("Здоровье:", 'current_health'),
            ("Макс. здоровье:", 'max_health'),
            ("Мана:", 'current_mana'),
            ("Макс. мана:", 'max_mana'),
            ("Уровень:", 'level'),
            ("Опыт:", 'xp'),
            ("Золото:", 'gold'),
            ("Пол:", 'sex')
        ]
        self.create_section(self.char_frame, "Основные параметры", main_fields)
        
        # Атрибуты
        attributes = [
            ("Сила", 'strength'),
            ("Ловкость", 'dexterity'),
            ("Телосложение", 'constitution'),
            ("Интеллект", 'intelligence'),
            ("Восприятие", 'perception'),
            ("Харизма", 'charisma')
        ]
        self.create_section(self.char_frame, "Атрибуты", attributes)
        
        # Навыки
        skills = [
            ("Ремесло", 'tinkering'),
            ("Стелс", 'stealth'),
            ("Торговля", 'trading'),
            ("Оценка", 'appraisal'),
            ("Плавание", 'swimming'),
            ("Лидерство", 'leadership'),
            ("Магия", 'magic'),
            ("Дальний бой", 'ranged'),
            ("Мечи", 'swords'),
            ("Булавы", 'maces'),
            ("Топоры", 'axes'),
            ("Древковое", 'polearms'),
            ("Блок", 'blocking'),
            ("Рукопашный", 'unarmed'),
            ("Алхимия", 'alchemy')
        ]
        self.create_section(self.char_frame, "Навыки", skills)

    def setup_world_tab(self):
        frame = tk.Frame(self.world_frame)
        frame.pack(pady=20)
        
        lbl = tk.Label(frame, text="ID текстуры скайбокса:")
        lbl.pack(side=tk.LEFT)
        
        self.skybox_entry = tk.Entry(frame)
        self.skybox_entry.pack(side=tk.LEFT, padx=5)
        
        btn = tk.Button(frame, text="Применить", command=self.update_skybox)
        btn.pack(side=tk.LEFT)

    def connect(self):
        try:
            self.pm.open_process_from_name("barony.exe")
            base = self.pm.base_address
            self.base_addr = base + 0xAE1FD0
            
            # Получаем адреса персонажей
            for i in range(4):
                self.player_addresses[i] = self.pm.read_longlong(self.base_addr + i*8)
            
            self.connect_btn.config(state=tk.DISABLED)
            self.refresh_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Статус: Подключено", fg="green")
            self.addr_label.config(text=f"PID: {self.pm.process_id} | Base: 0x{base:X}")
            self.load_current_values()
            
        except ProcessNotFound:
            messagebox.showerror("Ошибка", "Игра не запущена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {str(e)}")

    def get_current_address(self):
        return self.player_addresses[self.current_player]

    def read_value(self, field):
        try:
            if field == 'skybox':
                base = self.pm.read_longlong(self.pm.base_address + self.offsets[field][0])
                return self.pm.read_int(base + self.offsets[field][1])
            
            offset, is_string = self.offsets[field]
            addr = self.get_current_address() + offset
            return self.pm.read_string(addr, 11) if is_string else self.pm.read_int(addr)
        except:
            return 0

    def write_skybox(self, value):
        try:
            # Получаем базовый адрес игры
            base = self.pm.base_address
        
            # Вычисляем абсолютный адрес: barony.exe + C21090 + 48
            skybox_addr = base + 0xC21090 + 0x48
        
            # Записываем значение напрямую
            self.pm.write_int(skybox_addr, int(value))
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка записи скайбокса: {str(e)}")
            return False

    def load_current_values(self):
        for field in self.offsets:
            entry = getattr(self, f"{field}_entry", None)
            if entry:
                try:
                    value = self.read_value(field)
                    entry.delete(0, tk.END)
                    entry.insert(0, str(value))
                except:
                    pass

    def update_field(self, field):
        entry = getattr(self, f"{field}_entry")
        value = entry.get()
        if self.write_value(field, value):
            messagebox.showinfo("Успех", "Значение обновлено!")

    def update_skybox(self):
        try:
            value = int(self.skybox_entry.get())
            base = self.pm.base_address
            skybox_addr = base + 0xC21090 + 0x48
            self.pm.write_int(skybox_addr, value)
            messagebox.showinfo("Успех", "Скайбокс успешно изменен!")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целое число!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")

    def on_player_change(self, event):
        self.current_player = self.player_selector.current()
        self.load_current_values()

if __name__ == "__main__":
    app = BaronyHack()
    app.root.mainloop()
