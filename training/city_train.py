import numpy as np
import random
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Генерация случайных обучающих данных для второй модели
def generate_city_reach_data(num_samples=100):
    X = []
    y = []
    
    # Возможные значения
    distances = [5, 10, 20, 50, 100, 200, 500, 1000]  # Расстояние до города в км
    gas_volumes = [50, 100, 200, 300, 500, 1000]  # Общий объем газа в м³
    wind_speeds = [0.3, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0]  # Скорость ветра в м/с
    
    # Генерируем случайные примеры
    for _ in range(num_samples):
        distance = random.choice(distances)  # Расстояние до города в км
        total_gas = random.choice(gas_volumes)  # Общий объем газа
        wind_speed = random.choice(wind_speeds)  # Скорость ветра в м/с
        
        # Учитываем влияние на вероятность того, дойдет ли газ до города
        # Чем больше газа и ветра, тем выше шанс, что газ дойдет
        # Чем больше расстояние, тем ниже вероятность
        probability = (total_gas * wind_speed) / (distance + 1)  # Сложная модель

        # Если вероятность > 0.5, считаем, что газ дойдет (1), иначе нет (0)
        reached = 1 if probability > 0.5 else 0
        
        X.append([distance, total_gas, wind_speed])
        y.append(reached)
    
    return np.array(X), np.array(y)

# Генерация данных
X, y = generate_city_reach_data(num_samples=100)

# Разделяем данные на обучающие и тестовые (80% на обучение, 20% на тест)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Создаем и обучаем модель нейросети
model = MLPClassifier(hidden_layer_sizes=(20,), max_iter=2000, tol=1e-4, learning_rate_init=0.001)
model.fit(X_train, y_train)

# Прогнозируем на тестовых данных
y_pred = model.predict(X_test)

# Оценка точности модели на тестовых данных
accuracy = accuracy_score(y_test, y_pred)
print(f"Точность модели на тестовых данных: {accuracy * 100:.2f}%")

# Сохраняем обученную модель в файл
joblib.dump(model, 'city_reach_model.pkl')

print("Модель успешно обучена и сохранена в файл 'city_reach_model.pkl'.")