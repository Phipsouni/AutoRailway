import os
import shutil  # Импортируем модуль shutil для перемещения файлов
from PyPDF2 import PdfReader, PdfWriter


def overlay_background(input_pdf, instructions_pdf):
    """
    Накладывает фон из instructions_pdf на все страницы input_pdf.
    """
    reader = PdfReader(input_pdf)
    instructions_reader = PdfReader(instructions_pdf)
    output_writer = PdfWriter()

    # Берем первую страницу из файла инструкций как фон
    overlay_page = instructions_reader.pages[0]

    for page in reader.pages:
        # Накладываем фон на текущую страницу
        page.merge_page(overlay_page)
        output_writer.add_page(page)

    return output_writer


def add_blank_pages(pdf_writer):
    """
    Добавляет пустые страницы после всех листов, кроме 3-го и 6-го.
    """
    output_writer = PdfWriter()

    for i, page in enumerate(pdf_writer.pages, start=1):
        output_writer.add_page(page)
        # Проверяем, не является ли текущая страница 3-й или 6-й
        if i != 3 and i != 6:
            output_writer.add_blank_page()

    return output_writer


def insert_template_pages(pdf_writer, template_pdf):
    """
    Вставляет страницы из template_pdf после 5-го и 10-го листа.
    """
    template_reader = PdfReader(template_pdf)
    output_writer = PdfWriter()

    # Определяем страницы из template_pdf для вставки:
    # 0-я страница template_pdf вставляется после 5-й страницы основного документа
    # 1-я страница template_pdf вставляется после 10-й страницы основного документа
    insert_positions = {5: template_reader.pages[0], 10: template_reader.pages[1]}

    # current_page_idx = 0 # Эта переменная была в исходном коде, но не использовалась
    for i, page in enumerate(pdf_writer.pages, start=1):
        output_writer.add_page(page)
        if i in insert_positions:
            # Вставляем соответствующую страницу из template_pdf
            output_writer.add_page(insert_positions[i])

    return output_writer


def process_pdfs():
    """
    Основная функция для обработки PDF-файлов:
    - Накладывает фон.
    - Добавляет пустые страницы.
    - Вставляет страницы из шаблона.
    - Сохраняет результат в папку 'Print'.
    - Перемещает исходные файлы в папку 'Ready'.
    """
    railway_folder = "Railway"
    template_folder = "Template"
    output_folder = "Print"
    ready_folder = "Ready"  # Новая папка для перемещенных файлов

    # Создаем необходимые папки, если они еще не существуют
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(ready_folder, exist_ok=True) # Создаем папку 'Ready'

    template_pdf_path = os.path.join(template_folder, "3-6.pdf")
    instructions_pdf_path = os.path.join(template_folder, "Instructions.pdf")

    # Проверяем наличие необходимых файлов шаблонов
    if not os.path.exists(instructions_pdf_path):
        print(f"Ошибка: Файл шаблона инструкций '{instructions_pdf_path}' не найден.")
        return
    if not os.path.exists(template_pdf_path):
        print(f"Ошибка: Файл шаблона 3-6.pdf '{template_pdf_path}' не найден.")
        return

    # Перебираем все файлы в папке 'Railway'
    for file_name in os.listdir(railway_folder):
        # Проверяем, является ли файл PDF
        if file_name.endswith(".pdf"):
            input_pdf_path = os.path.join(railway_folder, file_name)
            output_pdf_path = os.path.join(output_folder, file_name)
            destination_ready_path = os.path.join(ready_folder, file_name) # Полный путь для перемещения в 'Ready'

            try:
                print(f"Обработка файла: {file_name}...")

                # 1. Накладываем фон
                writer = overlay_background(input_pdf_path, instructions_pdf_path)

                # 2. Добавляем пустые страницы
                writer = add_blank_pages(writer)

                # 3. Вставляем страницы из шаблона
                writer = insert_template_pages(writer, template_pdf_path)

                # Сохраняем обработанный PDF в папку 'Print'
                with open(output_pdf_path, "wb") as output_file:
                    writer.write(output_file)

                print(f"  ✅ Файл '{file_name}' обработан и сохранен в '{output_folder}'.")

                # Перемещаем исходный PDF-файл в папку 'Ready'
                shutil.move(input_pdf_path, destination_ready_path)
                print(f"  ➡️ Исходный файл '{file_name}' перемещен в '{ready_folder}'.")

            except Exception as e:
                # В случае ошибки выводим сообщение, но продолжаем обработку других файлов
                print(f"  ❌ Ошибка при обработке или перемещении файла '{file_name}': {e}")
        else:
            # Игнорируем файлы, которые не являются PDF
            print(f"  ℹ️ Файл '{file_name}' игнорируется (не PDF).")

    print("\nПроцесс обработки PDF-файлов завершен.")


if __name__ == "__main__":
    # Убедитесь, что существуют папки "Railway" и "Template"
    # и что в них находятся соответствующие PDF-файлы
    # (например, Instructions.pdf и 3-6.pdf в "Template").
    
    print("Запуск скрипта обработки PDF...")
    process_pdfs()
