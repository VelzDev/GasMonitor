import numpy as np
import pandas as pd
import random

# Настройки для генерации данных
wind_directions = ['Север', 'Юг', 'Восток', 'Запад']
gas_types = ['Метан', 'Пропан', 'Аммиак', 'Хлор']
explosion_risks = ['Низкая', 'Средняя', 'Высокая']

# Генерация качественных данных для тренировки
def generate_data(num_samples=1000):
    data = []
    
    for _ in range(num_samples):
        # Случайные входные данные
        wind_direction = random.choice(wind_directions)
        personnel_count = random.randint(10, 1000)
        gas_type = random.choice(gas_types)
        explosion_risk = random.choice(explosion_risks)
        leakage_amount = random.randint(1, 100)
        
        # Зоны и их уровень опасности (начальные значения)
        zone_dangers = [0] * 9  # Все зоны начально имеют низкую опасность
        
        # Определяем уровень опасности для каждой зоны в зависимости от параметров
        for i in range(9):
            # Влияние ветра на зоны (используем правильное распространение газа)
            if wind_direction == 'Север' and i < 3:  # Газ идет на юг
                zone_dangers[i] = 2  # Сильная опасность в северных зонах
            elif wind_direction == 'Север' and i >= 3 and i < 6:  # Газ доходит до центральных зон
                zone_dangers[i] = 1  # Средняя опасность
            elif wind_direction == 'Север' and i >= 6:  # Газ уже ослаблен на южных зонах
                zone_dangers[i] = 0  # Низкая опасность

            elif wind_direction == 'Юг' and i >= 6:  # Газ идет на север
                zone_dangers[i] = 2  # Сильная опасность на южных зонах
            elif wind_direction == 'Юг' and i < 3 and i >= 0:  # Газ доходит до центральных зон
                zone_dangers[i] = 1  # Средняя опасность
            elif wind_direction == 'Юг' and i < 6:  # Газ ослабляется
                zone_dangers[i] = 0  # Низкая опасность

            elif wind_direction == 'Восток' and i in [2, 5, 8]:  # Газ идет на запад
                zone_dangers[i] = 2
            elif wind_direction == 'Запад' and i in [0, 3, 6]:  # Газ идет на восток
                zone_dangers[i] = 2

            # Влияние числа персонала
            if personnel_count > 500:
                zone_dangers[i] = max(zone_dangers[i], 1)  # Более 500 человек увеличивает опасность
            
            # Влияние типа газа
            if gas_type == 'Хлор':
                zone_dangers[i] = 2  # Хлор опасен для всех зон
            elif gas_type == 'Пропан' and i < 5:
                zone_dangers[i] = max(zone_dangers[i], 1)  # Пропан более опасен вблизи утечки
            
            # Влияние опасности взрыва
            if explosion_risk == 'Высокая' and i in [4, 5, 6]:
                zone_dangers[i] = 2  # Высокая опасность взрыва делает зоны очень опасными
            
            # Влияние объема утечки
            if leakage_amount > 50:
                if i in [2, 3, 5, 6]:  # Утечка газа большого объема влияет на ближние зоны
                    zone_dangers[i] = 2
            elif leakage_amount > 20:
                if i in [1, 4, 7]:  # Утечка среднего объема влияет на средние зоны
                    zone_dangers[i] = 1
        
        # Собираем данные в список для строки
        data.append([wind_direction, personnel_count, gas_type, explosion_risk, leakage_amount] + zone_dangers)
    
    # Создаем DataFrame
    columns = ['wind_direction', 'personnel_count', 'gas_type', 'explosion_risk', 'leakage_amount', 
               'zone_1', 'zone_2', 'zone_3', 'zone_4', 'zone_5', 'zone_6', 'zone_7', 'zone_8', 'zone_9']
    
    df = pd.DataFrame(data, columns=columns)
    return df

# Генерация 1000 примеров данных
df = generate_data(1000)

# Просмотр первых нескольких строк
print(df.head())

# Сохранить данные в CSV файл для дальнейшего использования
df.to_csv('realistic_training_data.csv', index=False)
