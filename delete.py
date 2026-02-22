import json

def fix_text(text):
    if not isinstance(text, str):
        return text
    try:
        # Пробуем раскодировать кракозябры (latin1 -> utf-8)
        return text.encode('latin1').decode('utf-8')
    except:
        return text

# Читаем битый дамп (utf-8-sig автоматически удаляет BOM)
with open('dump.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

print(f"Загружено {len(data)} записей")

# Фиксим все строки
fixed_count = 0
for item in data:
    if 'fields' in item:
        for key, value in item['fields'].items():
            if isinstance(value, str):
                original = value
                item['fields'][key] = fix_text(value)
                if original != item['fields'][key]:
                    fixed_count += 1

print(f"Исправлено {fixed_count} полей")

# Сохраняем исправленный
with open('dump_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Готово! Используй dump_fixed.json")