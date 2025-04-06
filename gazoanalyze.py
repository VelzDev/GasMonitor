import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk  # Для выпадающего списка
import random
from collections import deque

# Создаем основное окно приложения
root = tk.Tk()
root.title("Экспертная система")

# Устанавливаем автомасштабирование
root.geometry("600x600")
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

# Данные по зонам
zones_info = {
    1: {"name": "Производственное помещение", "gas_volume": 0, "explosion_risk": "Высокая", "has_leakage": False, "max_leakage": 20},
    2: {"name": "Склад", "gas_volume": 0, "explosion_risk": "Средняя", "has_leakage": False, "max_leakage": 20},
    3: {"name": "Офис", "gas_volume": 0, "explosion_risk": "Низкая", "has_leakage": False, "max_leakage": 20},
    4: {"name": "Лаборатория", "gas_volume": 0, "explosion_risk": "Средняя", "has_leakage": False, "max_leakage": 20},
    5: {"name": "Котельная", "gas_volume": 0, "explosion_risk": "Высокая", "has_leakage": False, "max_leakage": 20},
    6: {"name": "Склад химикатов", "gas_volume": 0, "explosion_risk": "Высокая", "has_leakage": False, "max_leakage": 20},
    7: {"name": "Бухгалтерия", "gas_volume": 0, "explosion_risk": "Низкая", "has_leakage": False, "max_leakage": 20},
    8: {"name": "Гардероб", "gas_volume": 0, "explosion_risk": "Низкая", "has_leakage": False, "max_leakage": 20},
    9: {"name": "Техническое помещение", "gas_volume": 0, "explosion_risk": "Средняя", "has_leakage": False, "max_leakage": 20},
}

# Список для отслеживания зон, в которых нужно распространять газ
spread_queue = deque()

# Направление и сила ветра
wind_direction = tk.StringVar(value="Восток")
wind_speed = tk.DoubleVar(value=1.0)

# Создание фреймов для зон и формы ввода
zone_frame = tk.Frame(root)
zone_frame.grid(row=1, column=0, columnspan=3, pady=10)

input_frame = tk.Frame(root)  # Определение input_frame перед его использованием
input_frame.grid(row=2, column=0, columnspan=3, pady=10)

# Создание формы для ввода направления и силы ветра
def create_wind_input():
    tk.Label(input_frame, text="Направление ветра:").grid(row=0, column=0, padx=5, pady=5)
    wind_direction_dropdown = tk.OptionMenu(input_frame, wind_direction, "Север", "Юг", "Восток", "Запад")
    wind_direction_dropdown.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="Сила ветра (м/с):").grid(row=1, column=0, padx=5, pady=5)
    wind_speed_entry = tk.Entry(input_frame, textvariable=wind_speed)
    wind_speed_entry.grid(row=1, column=1, padx=5, pady=5)

create_wind_input()

# Функция для создания сетки с зонами
def create_grid():
    for i in range(3):
        for j in range(3):
            zone_number = i * 3 + j + 1
            zone = tk.Label(zone_frame, text=f"Зона {zone_number}\n{zones_info[zone_number]['name']}", width=12, height=5, relief="solid", anchor="center", bg="white")
            zone.grid(row=i, column=j, padx=5, pady=5)
            zone.bind("<Button-1>", lambda event, zone=zone_number: select_zone_for_leak(zone))  # Левый клик — старт утечки
            zone.bind("<Button-3>", lambda event, zone=zone_number: open_zone_settings(zone))  # Правый клик — настройки зоны

# Функция для открытия диалогового окна настроек зоны
def open_zone_settings(zone_number):
    zone_name = zones_info[zone_number]["name"]
    current_risk = zones_info[zone_number]["explosion_risk"]
    max_leakage = zones_info[zone_number]["max_leakage"]

    # Создаем новое окно для настройки
    settings_window = tk.Toplevel(root)
    settings_window.title(f"Настройки зоны {zone_name}")

    # Выпадающий список для риска взрыва
    tk.Label(settings_window, text="Выберите риск взрыва:").grid(row=0, column=0, padx=5, pady=5)
    explosion_risk_options = ["Высокая", "Средняя", "Низкая"]
    risk_dropdown = ttk.Combobox(settings_window, values=explosion_risk_options, state="readonly")
    risk_dropdown.set(current_risk)  # Устанавливаем текущий риск взрыва
    risk_dropdown.grid(row=0, column=1, padx=5, pady=5)

    # Поле ввода для максимального объема утечки
    tk.Label(settings_window, text="Максимальный объем утечки (м³):").grid(row=1, column=0, padx=5, pady=5)
    max_leakage_entry = tk.Entry(settings_window)
    max_leakage_entry.insert(0, str(max_leakage))  # Устанавливаем текущий максимальный объем
    max_leakage_entry.grid(row=1, column=1, padx=5, pady=5)

    # Кнопка для сохранения настроек
    def save_settings():
        selected_risk = risk_dropdown.get()
        new_max_leakage = float(max_leakage_entry.get())
        
        # Обновляем данные зоны
        zones_info[zone_number]["explosion_risk"] = selected_risk
        zones_info[zone_number]["max_leakage"] = new_max_leakage
        
        messagebox.showinfo("Настройки сохранены", f"Настройки зоны {zone_name} обновлены.")
        settings_window.destroy()  # Закрыть окно настроек

    save_button = tk.Button(settings_window, text="Сохранить", command=save_settings)
    save_button.grid(row=2, column=0, columnspan=2, pady=10)

# Функция для открытия диалогового окна выбора зоны для утечки
def select_zone_for_leak(zone_number):
    zone_name = zones_info[zone_number]["name"]
    
    if zone_name in ["Бухгалтерия", "Офис", "Гардероб"]:
        messagebox.showerror("Ошибка", f"Невозможно начать утечку в зоне {zone_name}.")
        return
    
    # Если зона подходящая, запрашиваем объем утечки
    leak_volume = simpledialog.askfloat("Утечка газа", f"Введите объем утечки для зоны {zone_name} (макс {zones_info[zone_number]['max_leakage']} м³):", minvalue=1, maxvalue=zones_info[zone_number]["max_leakage"])
    
    if leak_volume:
        start_leak(zone_number, leak_volume)

# Функция для старта утечки газа
def start_leak(zone_number, leak_volume):
    # Установим начальный объем газа для этой зоны
    zones_info[zone_number]["has_leakage"] = True
    zones_info[zone_number]["gas_volume"] = leak_volume
    zones_info[zone_number]["initial_volume"] = leak_volume

    # Добавляем зону в очередь для распространения газа
    spread_queue.append(zone_number)

    # Сохраняем максимальный объем газа в системе
    global total_max_gas
    total_max_gas = leak_volume * 10  # Максимум 10 раз увеличиваем объем

    update_gas_volume()

# Функция для обновления объема газа с учетом ветра
def update_gas_volume():
    direction = wind_direction.get()
    speed = wind_speed.get()

    total_gas = sum(zone['gas_volume'] for zone in zones_info.values())

    # Если общий объем газа в системе больше лимита, прекращаем распространение
    if total_gas >= total_max_gas:
        return

    # Обрабатываем все зоны в очереди на распространение газа
    for _ in range(len(spread_queue)):
        zone_number = spread_queue.popleft()
        zone_data = zones_info[zone_number]
        
        # Газ увеличивается постепенно
        gas_increase = random.uniform(0.1, 0.3) * speed
        new_gas_volume = zone_data['gas_volume'] + gas_increase

        # Ограничиваем рост объема газа (не больше максимального объема)
        if total_gas + gas_increase > total_max_gas:
            gas_increase = total_max_gas - total_gas
            new_gas_volume = zone_data['gas_volume'] + gas_increase

        zone_data['gas_volume'] = new_gas_volume

        # Распространение газа по соседним зонам в зависимости от ветра
        move_gas_to_neighbors(zone_number, direction, speed)

    update_zone_colors()

    # Повторно вызываем обновление каждые 500 мс (замедляем анимацию)
    root.after(1000, update_gas_volume)

# Функция для перемещения газа по соседним зонам с учетом ветра
def move_gas_to_neighbors(zone_number, direction, speed):
    # Маппинг для соседних зон
    neighbors = {
        1: [2, 4], 2: [1, 3, 5], 3: [2, 6], 4: [1, 5, 7], 5: [2, 4, 6, 8], 6: [3, 5, 9],
        7: [4, 8], 8: [5, 7, 9], 9: [6, 8]
    }
    
    # Коэффициенты для направления ветра (большая часть идет в направлении ветра)
    wind_coefficients = {
        "Север": {1: 0.2, 4: 0.3, 7: 0.3},  # Пример для Северного ветра
        "Юг": {2: 0.2, 5: 0.3, 8: 0.3},
        "Восток": {5: 0.7, 4: 0.2, 7: 0.1},  # Если ветер с Востока
        "Запад": {4: 0.7, 5: 0.2, 6: 0.1},  # Если ветер с Запада
    }

    # Коэффициенты для обычных направлений (когда ветер не попадает прямо в соседние зоны)
    normal_coeff = 0.1

    # Перемещение газа с учетом направления ветра
    flow_map = wind_coefficients.get(direction, {})

    for neighbor in neighbors[zone_number]:
        if neighbor in flow_map:
            gas_moved = zones_info[zone_number]["gas_volume"] * flow_map[neighbor]
        else:
            gas_moved = zones_info[zone_number]["gas_volume"] * normal_coeff

        # Ограничиваем перемещаемый газ, чтобы он не был слишком большим
        max_move_limit = 5.0  # максимальное количество газа, которое может переместиться в одну зону за один шаг
        if gas_moved > max_move_limit:
            gas_moved = max_move_limit

        # Уменьшаем газ в исходной зоне
        zones_info[zone_number]["gas_volume"] -= gas_moved
        # Увеличиваем газ в целевой зоне
        zones_info[neighbor]["gas_volume"] += gas_moved

        log_gas_movement(zone_number, neighbor, gas_moved)

        # Каждая зона, куда перемещается газ, добавляется в очередь для дальнейшего распространения
        if neighbor not in spread_queue:
            spread_queue.append(neighbor)

# Функция для логирования движения газа
def log_gas_movement(from_zone, to_zone, gas_amount):
    print(f"Газ перемещается: Зона {from_zone} -> Зона {to_zone}. Количество газа: {gas_amount:.2f} м³")

# Функция для анимированного изменения цвета зоны
def animate_zone_color(zone, start_color, end_color, steps=20, delay=500, step=0):
    if step < steps:
        factor = step / float(steps)
        new_color = interpolate_color(start_color, end_color, factor)
        zone.config(bg=new_color)
        root.after(delay, animate_zone_color, zone, start_color, end_color, steps, delay, step + 1)

# Функция для линейной интерполяции между двумя цветами
def interpolate_color(start_color, end_color, factor):
    start_rgb = [int(start_color[i:i+2], 16) for i in (0, 2, 4)]
    end_rgb = [int(end_color[i:i+2], 16) for i in (0, 2, 4)]
    new_rgb = [int(start_rgb[i] + factor * (end_rgb[i] - start_rgb[i])) for i in range(3)]
    return '#{:02x}{:02x}{:02x}'.format(new_rgb[0], new_rgb[1], new_rgb[2])

# Функция для обновления цветов зон в зависимости от объема газа
def update_zone_colors():
    for i in range(3):
        for j in range(3):
            zone_number = i * 3 + j + 1
            zone = zone_frame.grid_slaves(row=i, column=j)[0]
            zone_data = zones_info[zone_number]

            # Определяем конечный цвет в зависимости от объема газа
            if zone_data['gas_volume'] < 10:
                end_color = "00ff00"  # Зеленый
            elif zone_data['gas_volume'] < 50:
                end_color = "ffff00"  # Желтый
            else:
                end_color = "ff0000"  # Красный

            # Начальный цвет — белый
            start_color = "ffffff"
            # Анимация изменения цвета
            animate_zone_color(zone, start_color, end_color)

# Функция для сброса симуляции
def reset_simulation():
    for zone_number in zones_info:
        zones_info[zone_number]["gas_volume"] = zones_info[zone_number]["initial_volume"]
        zones_info[zone_number]["has_leakage"] = False
    update_zone_colors()

# Кнопки для экстренной службы и сброса симуляции
reset_button = tk.Button(root, text="Сбросить симуляцию", width=30, command=reset_simulation)
reset_button.grid(row=0, column=1, pady=10)

# Экстренный звонок
def emergency_call():
    print("Экстренный звонок 112")

# Верхняя панель с экстренным вызовом
emergency_button = tk.Button(root, text="Вызвать экстренную службу (112)", width=30, command=emergency_call)
emergency_button.grid(row=0, column=0, pady=10)

# Создание сетки для отображения зон
create_grid()

# Запуск основного цикла приложения
root.mainloop()
