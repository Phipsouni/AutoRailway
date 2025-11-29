import os
import re
import time
import datetime
import shutil  # Добавлено для перемещения файлов
from math import ceil
from colorama import init, Fore, Style
from PyPDF2 import PdfReader, PdfWriter

# Инициализация colorama для цветного вывода
init(autoreset=True)

# --- КОНФИГУРАЦИЯ ПАПОК ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DIR_RAILWAY = os.path.join(BASE_DIR, "Railway")
DIR_TEMPLATE = os.path.join(BASE_DIR, "Template")
DIR_STAMP = os.path.join(BASE_DIR, "Stamp")
DIR_READY = os.path.join(BASE_DIR, "Ready")
DIR_MERGED = os.path.join(BASE_DIR, "Merged Railway")

# Папки для выполненных файлов
DIR_RAILWAY_DONE = os.path.join(DIR_RAILWAY, "Done")
DIR_READY_DONE = os.path.join(DIR_READY, "Done")

# --- КОНСТАНТА ДЛЯ ОТСУТСТВИЯ ИНСТРУКЦИИ ---
NO_INSTRUCTION_FLAG = "NO_INSTRUCTION"


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def print_step(text):
    print(f"\n{Fore.YELLOW}🟧 {text}{Style.RESET_ALL}")


def print_info(text):
    print(f"{Fore.CYAN}ℹ️  {text}{Style.RESET_ALL}")


def print_success(text):
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")


def print_error(text):
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")


def print_bold_input(prompt_text):
    return input(f"{Style.BRIGHT}{prompt_text}{Style.RESET_ALL} ")


def ensure_directories():
    """Создает необходимые папки, если они отсутствуют."""
    # Добавили папки Done в список проверки
    folders = [DIR_RAILWAY, DIR_TEMPLATE, DIR_STAMP, DIR_READY, DIR_MERGED, DIR_RAILWAY_DONE, DIR_READY_DONE]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            # print_info(f"Создана папка: {folder}")


def move_file_to_done(src_path, done_folder):
    """Перемещает файл в папку Done."""
    if not os.path.exists(done_folder):
        os.makedirs(done_folder)

    filename = os.path.basename(src_path)
    dst_path = os.path.join(done_folder, filename)

    try:
        shutil.move(src_path, dst_path)
        # print(f"    -> Перемещен в Done: {filename}")
    except Exception as e:
        print_error(f"Не удалось переместить {filename} в Done: {e}")


def extract_number_from_filename(filename):
    """Извлекает первое число из имени файла."""
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return int(numbers[0])
    return None


def get_file_creation_date(filepath):
    """Возвращает форматированную дату изменения/создания файла."""
    timestamp = os.path.getmtime(filepath)
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')


def find_stamp_path(file_number):
    """Ищет PDF файл в папке Stamp, содержащий указанное число."""
    if not os.path.exists(DIR_STAMP):
        return None

    for fname in os.listdir(DIR_STAMP):
        if fname.lower().endswith(".pdf"):
            if extract_number_from_filename(fname) == file_number:
                return os.path.join(DIR_STAMP, fname)
    return None


# --- ШАГ 1: ВЫБОР ИНСТРУКЦИИ ---

def select_instruction():
    print_step("Шаг 1. Выбор файла инструкции")

    if not os.path.exists(DIR_TEMPLATE):
        print_error(f"Папка '{DIR_TEMPLATE}' не найдена.")
        return None

    files = [f for f in os.listdir(DIR_TEMPLATE) if
             f.lower().startswith("instruction (china)") and f.lower().endswith(".pdf")]
    files.sort()

    print(f"Найдены следующие варианты:")
    for idx, filename in enumerate(files, 1):
        full_path = os.path.join(DIR_TEMPLATE, filename)
        date_str = get_file_creation_date(full_path)
        print(f"{idx}. {filename} / {Fore.YELLOW}{date_str}{Style.RESET_ALL}")

    no_instruction_idx = len(files) + 1
    print(f"{no_instruction_idx}. {Fore.MAGENTA}Не накладывать инструкции{Style.RESET_ALL}")

    while True:
        try:
            choice = print_bold_input("Введите номер варианта:")
            choice_idx = int(choice)

            if choice_idx == no_instruction_idx:
                print_info("Выбрано: Без наложения инструкций.")
                return NO_INSTRUCTION_FLAG

            if 1 <= choice_idx <= len(files):
                selected_file = os.path.join(DIR_TEMPLATE, files[choice_idx - 1])
                print_success(f"Выбрана инструкция: {files[choice_idx - 1]}")
                return selected_file
            else:
                print_error("Неверный номер. Попробуйте еще раз.")
        except ValueError:
            print_error("Пожалуйста, введите число.")


# --- ЯДРО ОБРАБОТКИ (Слои) ---

def prepare_base_pages(input_pdf_path, instruction_path):
    """
    Создает writer, в котором на страницы input_pdf уже наложены:
    1. Штамп (если найден соответствующий номер).
    2. Инструкция (если выбрана).
    Возвращает: PdfWriter с готовыми визуальными слоями.
    """
    filename = os.path.basename(input_pdf_path)
    file_number = extract_number_from_filename(filename)

    # 1. Читаем исходный файл
    reader = PdfReader(input_pdf_path)
    output_writer = PdfWriter()

    # Сначала просто добавляем страницы во writer
    for page in reader.pages:
        output_writer.add_page(page)

    # 2. Поиск и наложение Штампа
    stamp_path = find_stamp_path(file_number)
    if stamp_path:
        try:
            stamp_reader = PdfReader(stamp_path)
            if stamp_reader.pages:
                stamp_page = stamp_reader.pages[0]
                # Накладываем штамп на все страницы
                for page in output_writer.pages:
                    page.merge_page(stamp_page)
                print(f"    {Fore.MAGENTA}+ Штамп:{Style.RESET_ALL} {os.path.basename(stamp_path)}")
        except Exception as e:
            print_error(f"Ошибка при наложении штампа: {e}")

    # 3. Наложение Инструкции (фона)
    if instruction_path != NO_INSTRUCTION_FLAG:
        try:
            bg_reader = PdfReader(instruction_path)
            if bg_reader.pages:
                bg_page = bg_reader.pages[0]
                # Накладываем инструкцию ПОВЕРХ штампа
                for page in output_writer.pages:
                    page.merge_page(bg_page)
        except Exception as e:
            print_error(f"Ошибка при наложении инструкции: {e}")

    return output_writer


# --- СЦЕНАРИИ ---

def scenario_two_sided(instruction_path):
    """
    Сценарий 1: Двухсторонняя Ж/Д накладная.
    Логика: (Слои) -> (Пустые страницы) -> (Вставка шаблонов) -> Перемещение в Done.
    """
    print_info("Запуск сценария: Двухсторонняя Ж/Д накладная")
    template_3_6_path = os.path.join(DIR_TEMPLATE, "3-6.pdf")

    if not os.path.exists(template_3_6_path):
        print_error(f"Файл '{template_3_6_path}' не найден!")
        return

    processed_count = 0
    files = [f for f in os.listdir(DIR_RAILWAY) if f.lower().endswith(".pdf")]

    if not files:
        print_info(f"В папке '{DIR_RAILWAY}' нет PDF файлов.")
        return

    for filename in files:
        input_path = os.path.join(DIR_RAILWAY, filename)
        output_path = os.path.join(DIR_READY, filename)

        try:
            print(f"Обработка: {filename}...")
            # 1. Готовим страницы со штампами и фоном
            base_writer = prepare_base_pages(input_path, instruction_path)

            # 2. Добавляем пустые страницы
            writer_with_blanks = PdfWriter()
            for i, page in enumerate(base_writer.pages, start=1):
                writer_with_blanks.add_page(page)
                if i != 3 and i != 6:
                    writer_with_blanks.add_blank_page()

            # 3. Вставляем страницы из шаблона 3-6.pdf
            reader_3_6 = PdfReader(template_3_6_path)
            final_writer = PdfWriter()
            insert_positions = {5: reader_3_6.pages[0], 10: reader_3_6.pages[1]}

            for i, page in enumerate(writer_with_blanks.pages, start=1):
                final_writer.add_page(page)
                if i in insert_positions:
                    final_writer.add_page(insert_positions[i])

            with open(output_path, "wb") as f:
                final_writer.write(f)

            print_success(f"Готово -> {DIR_READY}")

            # 4. Перемещение в Done
            move_file_to_done(input_path, DIR_RAILWAY_DONE)

            processed_count += 1

        except Exception as e:
            print_error(f"Ошибка с файлом {filename}: {e}")

    print_info(f"Обработано файлов: {processed_count}")


def scenario_one_sided(instruction_path):
    """
    Сценарий 2: Односторонняя Ж/Д накладная.
    Логика: (Слои) -> Сохранение -> Перемещение в Done.
    """
    print_info("Запуск сценария: Односторонняя Ж/Д накладная")
    processed_count = 0
    files = [f for f in os.listdir(DIR_RAILWAY) if f.lower().endswith(".pdf")]

    if not files:
        print_info(f"В папке '{DIR_RAILWAY}' нет PDF файлов.")
        return

    for filename in files:
        input_path = os.path.join(DIR_RAILWAY, filename)
        output_path = os.path.join(DIR_READY, filename)

        try:
            print(f"Обработка: {filename}...")
            writer = prepare_base_pages(input_path, instruction_path)

            with open(output_path, "wb") as f:
                writer.write(f)

            print_success(f"Готово -> {DIR_READY}")

            # Перемещение в Done
            move_file_to_done(input_path, DIR_RAILWAY_DONE)

            processed_count += 1
        except Exception as e:
            print_error(f"Ошибка с файлом {filename}: {e}")

    print_info(f"Обработано файлов: {processed_count}")


def generate_merge_filename(file_tuples):
    """Генерирует имя файла для объединения."""
    numbers = sorted([item[0] for item in file_tuples])
    count = len(numbers)

    if not numbers:
        return f"Railway_Merged_{int(time.time())}.pdf"

    ranges = []
    range_start = numbers[0]
    prev = numbers[0]

    for curr in numbers[1:]:
        if curr == prev + 1:
            prev = curr
        else:
            if range_start == prev:
                ranges.append(f"{range_start}")
            else:
                ranges.append(f"{range_start}-{prev}")
            range_start = curr
            prev = curr

    if range_start == prev:
        ranges.append(f"{range_start}")
    else:
        ranges.append(f"{range_start}-{prev}")

    ranges_str = ";".join(ranges)
    return f"Railway {ranges_str} {count} pcs..pdf"


def scenario_merge():
    """
    Сценарий 3: Скрепление Ж/Д накладных.
    После успешного скрепления файлы из Ready перемещаются в Ready/Done.
    """
    print_info("Запуск сценария: Скрепление Ж/Д накладных из папки Ready")

    files_with_nums = []
    for fname in os.listdir(DIR_READY):
        if fname.lower().endswith(".pdf"):
            num = extract_number_from_filename(fname)
            if num is not None:
                files_with_nums.append((num, os.path.join(DIR_READY, fname)))

    if not files_with_nums:
        print_error("В папке Ready нет подходящих файлов.")
        return

    files_with_nums.sort(key=lambda x: x[0])
    chunk_size = 4
    chunks = [files_with_nums[i:i + chunk_size] for i in range(0, len(files_with_nums), chunk_size)]

    processed_groups = 0

    for chunk in chunks:
        writer = PdfWriter()
        output_filename = generate_merge_filename(chunk)
        output_path = os.path.join(DIR_MERGED, output_filename)

        try:
            print(f"  Скрепление: {[os.path.basename(x[1]) for x in chunk]}")
            for _, fpath in chunk:
                reader = PdfReader(fpath)
                for page in reader.pages:
                    writer.add_page(page)

            with open(output_path, "wb") as f:
                writer.write(f)

            print_success(f"Создан: {output_filename}")

            # Перемещение исходников в Done после успешного создания общего файла
            for _, fpath in chunk:
                move_file_to_done(fpath, DIR_READY_DONE)

            processed_groups += 1

        except Exception as e:
            print_error(f"Ошибка {output_filename}: {e}")

    print_info(f"Всего создано файлов: {processed_groups}")


# --- ГЛАВНОЕ МЕНЮ ---

def main():
    ensure_directories()
    current_instruction = None

    while True:
        if not current_instruction:
            current_instruction = select_instruction()
            if not current_instruction:
                retry = input("Попробовать снова? (y/n): ")
                if retry.lower() != 'y':
                    break
                continue

        print_step("Шаг 2. Выбор сценария")

        if current_instruction == NO_INSTRUCTION_FLAG:
            instr_display = "Без наложения инструкций"
        else:
            instr_display = os.path.basename(current_instruction)

        print(f"Активная инструкция: {Fore.CYAN}{instr_display}{Style.RESET_ALL}")
        print("-" * 30)
        print("1. Двухсторонняя Ж/Д накладная (Авто: Штамп + Фон + Вставки)")
        print("2. Односторонняя Ж/Д накладная (Авто: Штамп + Фон)")
        print("3. Скрепление Ж/Д накладных (из Ready -> Merged Railway)")
        print("0. Вернуться к выбору инструкций")
        print("-" * 30)

        choice = print_bold_input("Ваш выбор:")

        if choice == "1":
            scenario_two_sided(current_instruction)
        elif choice == "2":
            scenario_one_sided(current_instruction)
        elif choice == "3":
            scenario_merge()
        elif choice == "0":
            current_instruction = None
            continue
        else:
            print_error("Неверный выбор.")

        print("\n" + "=" * 40 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем.")
    except Exception as e:
        print(f"\n{Fore.RED}КРИТИЧЕСКАЯ ОШИБКА: {e}{Style.RESET_ALL}")
        input("Нажмите Enter для выхода...")
