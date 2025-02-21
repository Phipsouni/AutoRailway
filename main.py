import os
from PyPDF2 import PdfReader, PdfWriter


def overlay_background(input_pdf, instructions_pdf):
    """Накладывает фон из instructions.pdf на все страницы."""
    reader = PdfReader(input_pdf)
    instructions_reader = PdfReader(instructions_pdf)
    output_writer = PdfWriter()

    overlay_page = instructions_reader.pages[0]  # Фон для наложения

    for page in reader.pages:
        page.merge_page(overlay_page)
        output_writer.add_page(page)

    return output_writer


def add_blank_pages(pdf_writer):
    """Добавляет пустые страницы после всех листов, кроме 3-го и 6-го."""
    output_writer = PdfWriter()

    for i, page in enumerate(pdf_writer.pages, start=1):
        output_writer.add_page(page)
        if i != 3 and i != 6:  # Пропускаем 3-й и 6-й лист
            output_writer.add_blank_page()

    return output_writer


def insert_template_pages(pdf_writer, template_pdf):
    """Вставляет страницы из template_pdf после 5-го и 11-го листа."""
    template_reader = PdfReader(template_pdf)
    output_writer = PdfWriter()

    insert_positions = {5: template_reader.pages[0], 10: template_reader.pages[1]}  # Страницы из 3-6.pdf
    new_positions = []  # Для хранения новых позиций после вставки

    for i, page in enumerate(pdf_writer.pages, start=1):
        output_writer.add_page(page)
        if i in insert_positions:
            output_writer.add_page(insert_positions[i])  # Вставляем страницу из 3-6.pdf
            new_positions.append(i + len(new_positions) + 1)  # Корректируем новые позиции

    return output_writer


def process_pdfs():
    railway_folder = "Railway"
    template_folder = "Template"
    output_folder = "Print"

    os.makedirs(output_folder, exist_ok=True)

    template_pdf = os.path.join(template_folder, "3-6.pdf")
    instructions_pdf = os.path.join(template_folder, "Instructions.pdf")

    for file_name in os.listdir(railway_folder):
        if file_name.endswith(".pdf"):
            input_pdf = os.path.join(railway_folder, file_name)
            output_pdf = os.path.join(output_folder, file_name)

            # 1. Накладываем фон на все страницы
            writer = overlay_background(input_pdf, instructions_pdf)

            # 2. Добавляем пустые страницы после всех листов, кроме 3-го и 6-го
            writer = add_blank_pages(writer)

            # 3. Вставляем страницы из "3-6.pdf" после 5-го и 10-го листа
            writer = insert_template_pages(writer, template_pdf)

            # Сохраняем файл
            with open(output_pdf, "wb") as output_file:
                writer.write(output_file)

            print(f"Обработан файл: {file_name}")


if __name__ == "__main__":
    process_pdfs()