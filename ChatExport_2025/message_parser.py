from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

html_file_path = "D:/MatveyHistory/ChatExport_2025/messages.html"

with open(html_file_path, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

filtered_messages = []
current_date = None

# Ищем все элементы, которые могут быть заголовками дней или сообщениями
for element in soup.find_all(["div"], class_=True):
    classes = element.get("class", [])
    
    # Если это заголовок дня (пример классов: "day", "day-header")
    if "day" in classes or "date" in classes:
        date_header = element.find(class_="date")
        if date_header:
            date_str = date_header.text.strip()
            try:
                # Пробуем разные форматы даты
                current_date = datetime.strptime(date_str, "%d %B %Y")  # 10 March 2025
            except ValueError:
                try:
                    current_date = datetime.strptime(date_str, "%B %d, %Y")  # March 10, 2025
                except ValueError:
                    print(f"Неизвестный формат даты: {date_str}")
    
    # Если это сообщение
    elif "message" in classes:
        if not current_date:
            print("Пропущено сообщение: нет данных о дате.")
            continue

        # Обработка времени сообщения
        time_element = element.find(class_="date")
        if time_element:
            time_str = re.search(r"\d{1,2}:\d{2}", time_element.text.strip())
            if time_str:
                try:
                    hours, minutes = map(int, time_str.group().split(':'))
                    # Используем current_date для даты и добавляем время
                    full_date = datetime.combine(current_date, datetime.min.time()).replace(hour=hours, minute=minutes)
                except Exception as e:
                    print(f"Ошибка парсинга времени: {e}")
                    continue
            else:
                print(f"Неверный формат времени: {time_element.text}")
                continue
        else:
            print("Пропущено сообщение: нет времени.")
            continue

        # Фильтр по дате (после 1 августа 2024)
        if full_date >= datetime(2024, 8, 1):  # Изменено на 2024 год
            text_element = element.find(class_="text")
            text = text_element.text.strip() if text_element else ""

            media_element = element.find(class_="media")
            media_link = media_element.find("a")["href"] if media_element else None

            # Сохраняем дату в формате "10 March 2025"
            filtered_messages.append({
                "date": full_date.strftime("%d %B %Y"),  # Форматируем дату
                "text": text,
                "media": media_link
            })

# Сохранение в JSON
output_json_path = "D:/MatveyHistory/ChatExport_2025/filtered_messages.json"
with open(output_json_path, "w", encoding="utf-8") as json_file:
    json.dump(filtered_messages, json_file, ensure_ascii=False, indent=4)

print(f"Сохранено сообщений: {len(filtered_messages)}")