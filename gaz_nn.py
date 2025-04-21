import os
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel
from tkinter import ttk  # Для выпадающего списка
from sklearn.neural_network import MLPClassifier  # Нейросеть для классификации
import joblib
import numpy as np
import random
from collections import deque
from PIL import Image, ImageTk

def load_model():
    print('загружена модель нейросети загазованности помещений');
    return joblib.load('training/trained_model.pkl')

model = load_model()

def load_city_reach_model():
    print('загружена модель нейросети прогнозирования загрязнения города');
    return joblib.load('training/city_reach_model.pkl')

def predict_city_reach():
    # Вводим расстояние до города через диалоговое окно
    distance_to_city = simpledialog.askfloat("Введите расстояние", "Введите расстояние до города (м):", minvalue=0.1)
    
    if not distance_to_city:
        return
    
    # Получаем общий объем газа и скорость ветра
    total_gas = sum(zone['gas_volume'] for zone in zones_info.values())
    speed = wind_speed.get()
    
    # Прогнозируем, дойдет ли газ до города
    model = load_city_reach_model()
    
    prediction = model.predict([[distance_to_city, total_gas, speed]])
    
    if prediction == 1:
        messagebox.showinfo("Предсказание", "Газ дойдет до города!")
    else:
        messagebox.showinfo("Предсказание", "Газ не дойдет до города.")
        
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
    1: {"name": "Производственная зона", "gas_volume": 0, "explosion_risk": "Высокая", "has_leakage": False, "max_leakage": 100},
    2: {"name": "Склад", "gas_volume": 0, "explosion_risk": "Средняя", "has_leakage": False, "max_leakage": 20},
    3: {"name": "Офис", "gas_volume": 0, "explosion_risk": "Низкая", "has_leakage": False, "max_leakage": 0},
    4: {"name": "Лаборатория", "gas_volume": 0, "explosion_risk": "Средняя", "has_leakage": False, "max_leakage": 20},
    5: {"name": "Котельная", "gas_volume": 0, "explosion_risk": "Высокая", "has_leakage": False, "max_leakage": 20},
    6: {"name": "Склад химикатов", "gas_volume": 0, "explosion_risk": "Высокая", "has_leakage": False, "max_leakage": 20},
    7: {"name": "Трансформаторная подстанция", "gas_volume": 0, "explosion_risk": "Низкая", "has_leakage": False, "max_leakage": 0},
    8: {"name": "Подземное помещение 2", "gas_volume": 0, "explosion_risk": "Низкая", "has_leakage": False, "max_leakage": 0},
    9: {"name": "Техническое помещение", "gas_volume": 0, "explosion_risk": "Средняя", "has_leakage": False, "max_leakage": 20},
}

gases_info = {
    "Хлор": {"pdv": 1},  # Пример ПДК для метана
    "Аммиак": {"pdv": 20},  # Пример ПДК для пропана
    "Угарный газ": {"pdv": 20},    # Пример ПДК для аммиака
}

# Список для отслеживания зон, в которых нужно распространять газ
spread_queue = deque()

# Направление и сила ветра
wind_direction = tk.StringVar(value="Восток")
wind_speed = tk.DoubleVar(value=1.0)

# Загрузка изображения фона
background_image = Image.open("background.png")  # сюда путь к твоей картинке
background_image = background_image.resize((600, 600), Image.Resampling.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)

# Канвас с фоном
canvas = tk.Canvas(root, width=1000, height=600)
canvas.grid(row=1, column=0, columnspan=3, rowspan=2)  # расширяем на два ряда
canvas.create_image(0, 0, anchor=tk.NW, image=background_photo)

# Создание фреймов для зон и формы ввода
zone_frame = tk.Frame(canvas, bg="", bd=0)
zone_window = canvas.create_window(0, 0, anchor="nw", window=zone_frame)
zone_frame.grid(row=1, column=0, columnspan=3, pady=10, padx=70)

input_frame = tk.Frame(root)  # Определение input_frame перед его использованием
input_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=70)

last_explosion_risk = {}
# Создание формы для ввода направления и силы ветра
wind_frame = tk.Frame(canvas, bg="#f0f0f0")

canvas.create_window(70, 230, anchor="nw", window=wind_frame)

wind_label = tk.Label(wind_frame, text="Направление ветра: Восток", bg="#f0f0f0")

wind_label.pack(side="left", padx=5)

wind_speed_label = tk.Label(wind_frame, text="Сила ветра: 3 м/с", bg="#f0f0f0")

wind_speed_label.pack(side="left", padx=5)

# Функция для создания сетки с зонами
def create_grid():
    for i in range(3):
        for j in range(3):
            zone_number = i * 3 + j + 1
            zone = tk.Label(zone_frame, text=f"Зона {zone_number}\n{zones_info[zone_number]['name']}", width=12, height=5, relief="solid", anchor="center", bg="white", wraplength=80)
            zone.grid(row=i, column=j, padx=5, pady=5)
            zone.bind("<Button-1>", lambda event, zone=zone_number: select_zone_for_leak(zone))  # Левый клик — старт утечки
            zone.bind("<Button-3>", lambda event, zone=zone_number: open_zone_settings(zone))  # Правый клик — настройки зоны

# Функция для открытия диалогового окна настроек зоны
def open_zone_settings(zone_number):
    zone_name = zones_info[zone_number]["name"]
    current_risk = zones_info[zone_number]["explosion_risk"]
    max_leakage = zones_info[zone_number]["max_leakage"]
    current_staff_count = zones_info[zone_number].get("staff_count", 50)  # Добавим численность сотрудников

    # Создаем новое окно для настройки
    settings_window = tk.Toplevel(root)
    settings_window.title(f"Настройки зоны {zone_name}")

    # Список для выбора нового названия зоны
    available_names = ["Производственная зона", "Склад", "Офис", "Лаборатория", "Котельная", "Склад химикатов", "Подземное помещение 1", "Подземное помещение 2", "Техническое помещение"]
    
    tk.Label(settings_window, text="Выберите новое название зоны:").grid(row=0, column=0, padx=5, pady=5)
    zone_name_dropdown = ttk.Combobox(settings_window, values=available_names, state="readonly")
    zone_name_dropdown.set(zone_name)  # Устанавливаем текущее название
    zone_name_dropdown.grid(row=0, column=1, padx=5, pady=5)

    # Поле для численности сотрудников
    tk.Label(settings_window, text="Численность сотрудников:").grid(row=1, column=0, padx=5, pady=5)
    staff_count_entry = tk.Entry(settings_window)
    staff_count_entry.insert(0, str(current_staff_count))  # Устанавливаем текущее количество сотрудников
    staff_count_entry.grid(row=1, column=1, padx=5, pady=5)

    # Выпадающий список для риска взрыва
    tk.Label(settings_window, text="Выберите риск взрыва:").grid(row=2, column=0, padx=5, pady=5)
    explosion_risk_options = ["Высокая", "Средняя", "Низкая"]
    risk_dropdown = ttk.Combobox(settings_window, values=explosion_risk_options, state="readonly")
    risk_dropdown.set(current_risk)  # Устанавливаем текущий риск взрыва
    risk_dropdown.grid(row=2, column=1, padx=5, pady=5)

    # Поле ввода для максимального объема утечки
    tk.Label(settings_window, text="Максимальный объем утечки (м³):").grid(row=3, column=0, padx=5, pady=5)
    max_leakage_entry = tk.Entry(settings_window)
    max_leakage_entry.insert(0, str(max_leakage))  # Устанавливаем текущий максимальный объем
    max_leakage_entry.grid(row=3, column=1, padx=5, pady=5)

    # Кнопка для сохранения настроек
    def save_settings():
        new_zone_name = zone_name_dropdown.get()
        new_staff_count = int(staff_count_entry.get())
        selected_risk = risk_dropdown.get()
        new_max_leakage = float(max_leakage_entry.get())
        
        # Обновляем данные зоны
        zones_info[zone_number]["name"] = new_zone_name
        zones_info[zone_number]["staff_count"] = new_staff_count  # Сохраняем численность сотрудников
        zones_info[zone_number]["explosion_risk"] = selected_risk
        zones_info[zone_number]["max_leakage"] = new_max_leakage
        
        # Обновляем метку зоны в интерфейсе
        zone = zone_frame.grid_slaves(row=(zone_number - 1) // 3, column=(zone_number - 1) % 3)[0]
        zone.config(text=f"Зона {zone_number}\n{new_zone_name}")

        messagebox.showinfo("Настройки сохранены", f"Настройки зоны {new_zone_name} обновлены.")
        settings_window.destroy()  # Закрыть окно настроек

    save_button = tk.Button(settings_window, text="Сохранить", command=save_settings)
    save_button.grid(row=4, column=0, columnspan=2, pady=10)

# Функция для открытия диалогового окна выбора зоны для утечки
def select_zone_for_leak(zone_number):
    zone_name = zones_info[zone_number]["name"]
    
    if zone_name in ["Бухгалтерия", "Офис", "Гардероб"]:
        messagebox.showerror("Ошибка", f"Невозможно начать утечку в зоне {zone_name}.")
        return
    
    # Создаем окно для выбора газа и объема утечки
    leak_window = Toplevel(root)
    leak_window.title(f"Утечка газа в зоне {zone_name}")

    # Создаем выпадающий список для выбора газа
    gas_var = tk.StringVar()
    gas_dropdown = ttk.Combobox(leak_window, textvariable=gas_var, values=list(gases_info.keys()), state="readonly")
    gas_dropdown.set(list(gases_info.keys())[0])  # Устанавливаем по умолчанию первый газ
    gas_dropdown.grid(row=0, column=0, padx=5, pady=5)

    # Поле для ввода объема утечки
    tk.Label(leak_window, text="Объем утечки (м³):").grid(row=1, column=0, padx=5, pady=5)
    leak_volume_entry = tk.Entry(leak_window)
    leak_volume_entry.grid(row=1, column=1, padx=5, pady=5)

    # Показать ПДК выбранного газа
    def update_pdv():
        selected_gas = gas_var.get()
        pdv = gases_info[selected_gas]["pdv"]
        pdv_label.config(text=f"ПДК для {selected_gas}: {pdv} мг/м³")
    
    # Метка для отображения ПДК выбранного газа
    pdv_label = tk.Label(leak_window, text="")
    pdv_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    # Обновление ПДК при изменении газа
    gas_dropdown.bind("<<ComboboxSelected>>", lambda event: update_pdv())

    # Кнопка для старта утечки
    def start_leak_action():
        leak_volume = float(leak_volume_entry.get())
        selected_gas = gas_var.get()
        pdv = gases_info[selected_gas]["pdv"]
        
        # Проверяем, что объем утечки в допустимых пределах
        if leak_volume < 1 or leak_volume > zones_info[zone_number]["max_leakage"]:
            messagebox.showerror("Ошибка", f"Объем утечки должен быть от 1 до {zones_info[zone_number]['max_leakage']} м³")
            return

        # Запуск утечки газа
        start_leak(zone_number, leak_volume, selected_gas, pdv)
        leak_window.destroy()

    start_button = tk.Button(leak_window, text="Запустить утечку", command=start_leak_action)
    start_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Закрыть окно без действий
    close_button = tk.Button(leak_window, text="Закрыть", command=leak_window.destroy)
    close_button.grid(row=4, column=0, columnspan=2, pady=5)

    update_pdv()
       
# Функция для открытия диалогового окна для мониторинга загазованности
def open_gas_monitoring_window():
    monitoring_window = Toplevel(root)
    monitoring_window.title("Мониторинг загазованности")
    
    # Создаем список для отображения данных о загазованности
    log_text = tk.Text(monitoring_window, width=50, height=15)
    log_text.pack(padx=10, pady=10)
    
    # Функция для обновления информации в текстовом окне
    def update_log():
        log_text.delete(1.0, tk.END)  # Очистим старые данные
        
        # Заполняем текстовое окно данными о загазованности
        for zone_number, zone_data in zones_info.items():
            air_volume = 10000  # Предполагаемый объем воздуха в помещении (100 м³)
            gas_volume = zone_data["gas_volume"]
            gas_type = zone_data.get("gas_type", "")
            
            # Устанавливаем ПДК для газа в каждой зоне
            if gas_type == "Хлор":
                pdv = 1  # ПДК для хлора
            else:
                pdv = 20  # ПДК для остальных газов (например, аммиак, угарный газ)
            
            # Если в зоне есть газ, рассчитываем концентрацию
            if gas_volume > 0:
                # Расчет концентрации в зависимости от типа газа
                if gas_type == "Хлор":
                    concentration = (gas_volume * 3.2 * 1000) / air_volume  # для хлора
                elif gas_type == "Аммиак":
                    concentration = (gas_volume * 0.73 * 1000) / air_volume  # для аммиака
                elif gas_type == "Угарный газ":
                    concentration = (gas_volume * 1.14 * 1000) / air_volume  # для угарного газа
                else:
                    concentration = 0  # Если газ не выбран, то концентрация равна 0
            else:
                # Если газа нет в зоне, то для этой зоны концентрация = 0, но нужно учитывать газ из соседних зон
                concentration = 0  
            
            # Сравниваем концентрацию с ПДК
            if concentration > pdv:
                risk_status = "Перевышен ПДК!"
            else:
                risk_status = "Концентрация в пределах нормы"
            
            # Если концентрация очень мала, показываем 0
            if concentration < 0.01:
                concentration = 0
            
            # Отображаем концентрацию с точностью до 4 знаков
            log_text.insert(tk.END, f"Зона {zone_number}: {zone_data['name']} - Газ: {gas_type}\n")
            log_text.insert(tk.END, f"  Концентрация: {concentration:.4f} мг/м³ (ПДК: {pdv} мг/м³) - {risk_status}\n")
    
    # Кнопка для обновления мониторинга
    update_button = tk.Button(monitoring_window, text="Обновить", command=update_log)
    update_button.pack(pady=10)
    
    # Кнопка для закрытия окна мониторинга
    close_button = tk.Button(monitoring_window, text="Закрыть", command=monitoring_window.destroy)
    close_button.pack(pady=10)

    # Изначально обновим данные в окне
    update_log()
    
# Прогнозируем вероятность взрыва
def predict_explosion_risk(model, gas_volume, wind_speed, risk_level, zone):
    # Прогнозируем, нужно ли эвакуировать (1 - да, 0 - нет)
    prediction = model.predict([[gas_volume, wind_speed, risk_level, zone]])
    
    current_risk = "Высокий" if prediction == 1 else "Низкий"

    # Сравниваем с последним состоянием, чтобы не показывать одинаковые сообщения
    global last_explosion_risk

    if zone not in last_explosion_risk:
        last_explosion_risk[zone] = {"risk": current_risk, "notified": False}
    
    # Показать сообщение только если риск изменился или не было уведомления
    if not last_explosion_risk[zone]["notified"]:
        last_explosion_risk[zone]["risk"] = current_risk  # Обновляем риск
        
        # Уведомление для высокого риска
        if current_risk == "Высокий":
            messagebox.showwarning("Экстренная мера", f"Зона {zones_info[zone]['name']}: Необходима эвакуация! Вероятность взрыва высока!")
            last_explosion_risk[zone]["notified"] = True
        elif gas_volume >= 7:  # Уведомление для высокой загазованности
            messagebox.showwarning("Экстренная мера", f"Зона {zones_info[zone]['name']}: Необходима эвакуация! Высокая загазованность помещения!")
            last_explosion_risk[zone]["notified"] = True
        elif gas_volume < 6:
        # Если газ в зоне меньше 10 м³, сбрасываем флаг, чтобы сообщение не выводилось снова
            last_explosion_risk[zone]["notified"] = False

# Реализуем вызов экстренной службы при любой утечке
def emergency_call():
    messagebox.showinfo("Экстренный вызов", "Экстренная служба вызвана!")

# Функция для старта утечки газа
# Функция для старта утечки газа
def start_leak(zone_number, leak_volume, selected_gas, pdv):
    # Устанавливаем начальный объем газа для этой зоны и тип газа
    zones_info[zone_number]["has_leakage"] = True
    zones_info[zone_number]["gas_volume"] = leak_volume
    zones_info[zone_number]["gas_type"] = selected_gas  # Тип газа
    zones_info[zone_number]["pdv"] = pdv  # ПДК выбранного газа
    zones_info[zone_number]["initial_volume"] = leak_volume

    # Обновляем тип газа для всех зон
    for zone_num in zones_info:
        zones_info[zone_num]["gas_type"] = selected_gas

    # Прогнозируем риск взрыва и необходимость эвакуации
    gas_volume = zones_info[zone_number]["gas_volume"]
    wind_speed_value = wind_speed.get()  # Правильное получение значения ветра
    risk_level = 2 if zones_info[zone_number]["explosion_risk"] == "Высокая" else 1  # Средний или высокий риск
    predict_explosion_risk(model, gas_volume, wind_speed_value, risk_level, zone_number)

    # Добавляем зону в очередь для распространения газа
    spread_queue.append(zone_number)

    update_gas_volume()

# Функция для обновления объема газа с учетом ветра
def update_gas_volume():
    direction = wind_direction.get()
    speed = wind_speed.get()

    total_gas = sum(zone['gas_volume'] for zone in zones_info.values())

    if total_gas >= 100:  # Прекращаем распространение, если газ слишком много
        return

    # Обрабатываем все зоны в очереди на распространение газа
    for _ in range(len(spread_queue)):
        zone_number = spread_queue.popleft()
        zone_data = zones_info[zone_number]
        
        # Газ увеличивается постепенно
        gas_increase = random.uniform(0.1, 0.3) * speed
        new_gas_volume = zone_data['gas_volume'] + gas_increase

        zone_data['gas_volume'] = new_gas_volume

        # Распространение газа по соседним зонам
        move_gas_to_neighbors(zone_number, direction, speed)        

    update_zone_colors()
    for zone_number in zones_info:
        gas_volume = zones_info[zone_number]["gas_volume"]
        risk_level = 2 if zones_info[zone_number]["explosion_risk"] == "Высокая" else 1  # Средний или высокий риск
        predict_explosion_risk(model, gas_volume, speed, risk_level, zone_number)

    # Повторно вызываем обновление каждые 1000 мс
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
        for zone_number in zones_info:
            gas_volume = zones_info[zone_number]["gas_volume"]
            risk_level = 2 if zones_info[zone_number]["explosion_risk"] == "Высокая" else 1  # Средний или высокий риск
            predict_explosion_risk(model, gas_volume, speed, risk_level, zone_number)
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

# Функция для обновления цветов зон в зависимости от объема газа и концентрации газа
def update_zone_colors():
    for i in range(3):
        for j in range(3):
            zone_number = i * 3 + j + 1
            zone = zone_frame.grid_slaves(row=i, column=j)[0]
            zone_data = zones_info[zone_number]

            # Получаем тип газа для этой зоны
            gas_type = zone_data.get("gas_type", "")
            gas_volume = zone_data["gas_volume"]
            
            # Если газа нет в зоне, зона будет зеленой
            if gas_volume == 0:
                end_color = "00ff00"  # Зеленый, если газа нет
            elif gas_type == "Хлор":
                # Для хлора: ПДК = 1 мг/м³, и условие: если меньше 1, то желтый, иначе красный
                if gas_volume < 1:
                    end_color = "00ff00"  #Зеленый
                elif gas_volume < 8:
                    end_color = "ffff00"    #Желтый
                else:
                    end_color = "ff0000"  # Красный
            else:
                # Для других газов: ПДК = 20 мг/м³
                if gas_volume < 20:
                    end_color = "00ff00"  # Зеленый
                elif gas_volume < 50:
                    end_color = "ffff00"  # Желтый
                else:
                    end_color = "ff0000"  # Красный

            # Начальный цвет — белый
            start_color = "ffffff"
            # Анимация изменения цвета
            animate_zone_color(zone, start_color, end_color)

# Функция для сброса симуляции
def reset_simulation():
    os.execl(sys.executable, sys.executable, *sys.argv)

# Экстренный звонок
def emergency_call():
    messagebox.showinfo("Экстренный вызов", "Экстренная служба вызвана!")
    
city_reach_button = tk.Button(root, text="Вероятность загрязнения города", width=30, command=predict_city_reach)
city_reach_button.grid(row=0, column=0, pady=1, padx=1, sticky="n")

monitoring_button = tk.Button(root, text="Мониторинг загазованности", width=30, command=open_gas_monitoring_window)
monitoring_button.grid(row=0, column=1, pady=1, padx=1, sticky="n")

# Кнопки для экстренной службы и сброса симуляции
reset_button = tk.Button(root, text="Сбросить симуляцию", width=30, command=reset_simulation)
reset_button.grid(row=1, column=0, pady=1, padx=1, sticky="n", rowspan=1)

# Верхняя панель с экстренным вызовом
emergency_button = tk.Button(root, text="Вызвать экстренную службу (112)", width=30, command=emergency_call)
emergency_button.grid(row=1, column=1, pady=1, padx=1, sticky="n", rowspan=1)

# Создание сетки для отображения зон
create_grid()

# Запуск основного цикла приложения
root.mainloop()
