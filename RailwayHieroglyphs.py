import os
from PyPDF2 import PdfReader, PdfWriter

def apply_background_to_pdfs(railway_dir="Railway", template_dir="Template", output_dir="Railway+Hieroglyphs"):
    """
    Накладывает PDF-файл из 'Template/Instructions.pdf' в качестве фона на все PDF-файлы
    в директории 'Railway' и сохраняет результат в 'Railway+Hieroglyphs'.
    """

    # Создаем выходную директорию, если ее нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Путь к файлу шаблона
    template_path = os.path.join(template_dir, "Instructions.pdf")

    # Проверяем, существует ли файл шаблона
    if not os.path.exists(template_path):
        print(f"Ошибка: Файл шаблона '{template_path}' не найден. Убедитесь, что 'Instructions.pdf' находится в папке 'Template'.")
        return

    try:
        reader_template = PdfReader(template_path)
        if len(reader_template.pages) == 0:
            print(f"Ошибка: Файл шаблона '{template_path}' пуст.")
            return
        background_page = reader_template.pages[0] # Берем первую страницу шаблона как фон
    except Exception as e:
        print(f"Ошибка при чтении файла шаблона '{template_path}': {e}")
        return

    # Обрабатываем файлы в директории 'Railway'
    if not os.path.exists(railway_dir):
        print(f"Ошибка: Директория '{railway_dir}' не найдена. Создайте ее и добавьте PDF-файлы.")
        return

    for filename in os.listdir(railway_dir):
        if filename.lower().endswith(".pdf"):
            input_pdf_path = os.path.join(railway_dir, filename)
            output_pdf_path = os.path.join(output_dir, filename)

            try:
                reader_input = PdfReader(input_pdf_path)
                writer = PdfWriter()

                for i, page in enumerate(reader_input.pages):
                    # Создаем новую страницу, чтобы наложить фон
                    # Важно: pypdf позволяет накладывать страницы напрямую
                    # Без необходимости вручную копировать контент.
                    page.merge_page(background_page)
                    writer.add_page(page)

                # Сохраняем объединенный PDF
                with open(output_pdf_path, "wb") as output_file:
                    writer.write(output_file)
                print(f"Файл '{filename}' обработан и сохранен в '{output_dir}'.")

            except Exception as e:
                print(f"Ошибка при обработке файла '{filename}': {e}")
        else:
            print(f"Файл '{filename}' игнорируется, так как это не PDF.")

# --- Структура директорий и запуск скрипта ---
if __name__ == "__main__":
    # Создаем необходимые директории, если их нет (для удобства тестирования)
    os.makedirs("Railway", exist_ok=True)
    os.makedirs("Template", exist_ok=True)

    # Примечание: Для работы скрипта, вам нужно будет вручную
    # поместить ваши PDF-файлы в папку "Railway"
    # и файл "Instructions.pdf" в папку "Template".

    print("Запуск скрипта для наложения фона...")
    apply_background_to_pdfs()
    print("Скрипт завершил работу.")
