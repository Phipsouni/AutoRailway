import os
import re # Импортируем модуль re для работы с регулярными выражениями (для извлечения чисел из имени файла)
from PyPDF2 import PdfReader, PdfWriter # Используем pypdf для работы с PDF

def extract_number_from_filename(filename):
    """
    Извлекает числовое значение из имени файла (без расширения).
    Например, для "897.pdf" вернет "897".
    """
    # Удаляем расширение файла
    name_without_extension = os.path.splitext(filename)[0]
    # Находим все последовательности цифр в имени файла
    numbers = re.findall(r'\d+', name_without_extension)
    if numbers:
        # Возвращаем первую найденную последовательность цифр
        return numbers[0]
    return None # Если чисел в имени файла нет

def process_matching_pdfs(railway_dir="Railway", stamp_dir="Stamp", output_dir="Railway+Stamp"):
    """
    Накладывает фоновый PDF из 'Stamp' на соответствующий PDF из 'Railway'
    по совпадению числовых значений в именах файлов.
    """
    print("🚀 Запуск обработки PDF-файлов по совпадению имен...")

    # Создаем выходную директорию, если ее нет
    os.makedirs(output_dir, exist_ok=True)

    # Проверяем наличие входных директорий
    if not os.path.exists(railway_dir):
        print(f"❌ Ошибка: Директория 'Railway' ({railway_dir}) не найдена. Создайте ее и добавьте PDF-файлы.")
        return
    if not os.path.exists(stamp_dir):
        print(f"❌ Ошибка: Директория 'Stamp' ({stamp_dir}) не найдена. Создайте ее и добавьте PDF-файлы.")
        return

    # 1. Загружаем все PDF-файлы из папки 'Stamp' в словарь для быстрого поиска
    # Ключ: числовое значение из имени файла, Значение: полный путь к файлу штампа
    stamp_files = {}
    print(f"🔎 Загрузка файлов штампов из '{stamp_dir}'...")
    for filename in os.listdir(stamp_dir):
        if filename.lower().endswith(".pdf"):
            number_id = extract_number_from_filename(filename)
            if number_id:
                stamp_files[number_id] = os.path.join(stamp_dir, filename)
                # print(f"  Найден штамп: {number_id}.pdf")
            else:
                print(f"  ⚠️ Файл штампа '{filename}' игнорируется: не содержит числового ID в имени.")
        else:
            print(f"  ℹ️ Файл '{filename}' в 'Stamp' игнорируется (не PDF).")

    if not stamp_files:
        print("⚠️ В директории 'Stamp' не найдено подходящих PDF-файлов штампов. Никакие файлы 'Railway' не будут обработаны.")
        return

    print(f"✅ Загружено {len(stamp_files)} уникальных штампов.")

    # 2. Обрабатываем каждый PDF-файл в папке 'Railway'
    print(f"\n⚙️ Обработка файлов из '{railway_dir}'...")
    processed_count = 0
    skipped_count = 0

    for railway_filename in os.listdir(railway_dir):
        if railway_filename.lower().endswith(".pdf"):
            railway_number_id = extract_number_from_filename(railway_filename)
            railway_file_path = os.path.join(railway_dir, railway_filename)
            output_file_path = os.path.join(output_dir, railway_filename)

            if railway_number_id and railway_number_id in stamp_files:
                stamp_file_path = stamp_files[railway_number_id]

                try:
                    print(f"  Обработка '{railway_filename}': Наложение фона из '{os.path.basename(stamp_file_path)}'...")

                    reader_railway = PdfReader(railway_file_path)
                    reader_stamp = PdfReader(stamp_file_path)

                    # Проверяем, есть ли страницы в файле штампа
                    if not reader_stamp.pages:
                        print(f"  ❌ Ошибка: Файл штампа '{os.path.basename(stamp_file_path)}' пуст. Пропускаем.")
                        skipped_count += 1
                        continue

                    # Используем первую страницу штампа как фон
                    background_page = reader_stamp.pages[0]
                    writer = PdfWriter()

                    # Накладываем фон на каждую страницу документа Railway
                    for page in reader_railway.pages:
                        page.merge_page(background_page)
                        writer.add_page(page)

                    # Сохраняем объединенный PDF в выходную директорию
                    with open(output_file_path, "wb") as output_file:
                        writer.write(output_file)

                    print(f"  ✅ '{railway_filename}' успешно обработан и сохранен в '{output_dir}'.")
                    processed_count += 1

                except Exception as e:
                    print(f"  ❌ Ошибка при обработке '{railway_filename}' или '{os.path.basename(stamp_file_path)}': {e}")
                    skipped_count += 1
            else:
                print(f"  ℹ️ Файл '{railway_filename}' игнорируется: Не найдено соответствующего штампа в 'Stamp' (ID: {railway_number_id}).")
                skipped_count += 1
        else:
            print(f"  ℹ️ Файл '{railway_filename}' в 'Railway' игнорируется (не PDF).")
            skipped_count += 1

    print(f"\n🎉 Процесс завершен. Обработано файлов: {processed_count}, Пропущено/Ошибки: {skipped_count}.")


if __name__ == "__main__":
    # --- Настройка директорий (для удобства тестирования) ---
    # Эти папки должны быть созданы и содержать PDF-файлы
    # Если их нет, скрипт выведет предупреждение и завершится
    os.makedirs("Railway", exist_ok=True)
    os.makedirs("Stamp", exist_ok=True)
    
    # Пример: Для тестирования, убедитесь, что у вас есть:
    # - В папке Railway: 123.pdf, 456.pdf
    # - В папке Stamp: 123.pdf, 789.pdf (штамп 456.pdf не будет найден)
    # После запуска в папке StampedRailway появится 123.pdf с наложенным штампом.

    process_matching_pdfs()
