# Профессиональный SEO-Анализатор & Extractor (Standalone Version)
# Выполняет парсинг, чистку DOM-дерева, N-gram аналитику и экспорт отчетов.

import requests
import re
import csv
from collections import Counter
from datetime import datetime

# Встроенный словарь стоп-слов (PL + EN + технический мусор)
STOP_WORDS = {
    # PL
    'jest', 'oraz', 'tylko', 'przez', 'dla', 'jak', 'tak', 'nie', 'jako', 
    'przy', 'czy', 'to', 'że', 'na', 'do', 'od', 'ale', 'lub', 'tej', 'tym',
    'jego', 'ich', 'się', 'bardzo', 'więc', 'aby', 'gdzie', 'tego', 'praca',
    # EN
    'this', 'that', 'with', 'from', 'your', 'have', 'more', 'about', 'home',
    'contact', 'us', 'the', 'and', 'for', 'you', 'are', 'will', 'can',
    # Tech
    'http', 'https', 'href', 'span', 'class', 'div', 'false', 'true', 'null'
}

def fetch_html(url):
    """Безопасный HTTP-запрос с имитацией браузера пользователя."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8'
    }
    try:
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Сбой подключения: {e}")
        return None

def extract_seo_text(html):
    """Извлекает текст, придавая математический вес заголовкам (H1/Title)."""
    # Ищем заголовки, чтобы дать их словам больший маркетинговый вес
    titles = re.findall(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE)
    h1_tags = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE)
    
    # Жесткая чистка DOM-дерева от скриптов, стилей и векторной графики
    clean_html = re.sub(r'<(script|style|svg)[^>]*>.*?</\1>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
    clean_html = re.sub(r'<[^>]+>', ' ', clean_html) # Срезаем оставшиеся теги
    
    # Нормализация текста (только слова от 4 символов)
    all_words = re.findall(r'[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{4,}', clean_html.lower())
    
    # Усиливаем слова из H1 и Title (умножаем их присутствие в массиве)
    bonus_text = " ".join(titles + h1_tags).lower()
    bonus_words = re.findall(r'[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{4,}', bonus_text)
    
    # Добавляем бонусные слова 3 раза для увеличения веса в статистике
    all_words.extend(bonus_words * 3) 
    
    return [w for w in all_words if w not in STOP_WORDS]

def get_bigrams(words):
    """Создает биграммы (словосочетания из 2 слов) для анализа связок."""
    # zip склеивает список сам с собой со сдвигом на 1 элемент
    bigrams = zip(words, words[1:])
    return [f"{w1} {w2}" for w1, w2 in bigrams]

def run_seo_audit(url, export_csv=True):
    """Главный контроллер: запуск парсинга, расчет аналитики и экспорт."""
    print(f"\n[🚀] Запуск глубокого SEO-аудита для: {url}")
    html = fetch_html(url)
    if not html: 
        return
    
    print("[⚡] Обработка DOM-дерева и извлечение семантики...")
    words = extract_seo_text(html)
    
    word_counts = Counter(words)
    bigram_counts = Counter(get_bigrams(words))
    
    print("\n=== ТОП-10 ОДИНОЧНЫХ КЛЮЧЕЙ (Усилено H1/Title) ===")
    for w, c in word_counts.most_common(10):
        print(f" 🔑 {w:<15} | {c} вхождений")
        
    print("\n=== ТОП-5 СВЯЗОК (Биграммы для контекстной рекламы) ===")
    for b, c in bigram_counts.most_common(5):
        print(f" 🔗 {b:<25} | {c} вхождений")
        
    if export_csv:
        # Генерируем уникальное имя файла с таймстампом
        filename = f"seo_report_{datetime.now().strftime('%H%M%S')}.csv"
        # Контекстный менеджер (with open) сам закроет файл после записи
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Keyword', 'Type', 'Count'])
            for w, c in word_counts.most_common(20): writer.writerow([w, 'Single', c])
            for b, c in bigram_counts.most_common(10): writer.writerow([b, 'Bigram', c])
        print(f"\n[💾] Отчет успешно сохранен в файл: {filename}")

if __name__ == "__main__":
    # URL для анализа (можно подставить конкурентов)
    target = "https://www.olx.pl/praca/goldap/" 
    run_seo_audit(target)