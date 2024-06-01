import cv2
import torch
from ultralytics import YOLOv10
import os
from datetime import timedelta
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image

# Путь к корневой папке с видеофайлами
root_folder = 'cc'
output_folder = 'railway_output2200'
font_path = 'DejaVuSans-ExtraLight.ttf'  # Убедитесь, что путь правильный


# DejaVuSans-ExtraLight.ttf
def initialize_directories():
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    files = []
    for root, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(('mp4', 'avi', 'mov', 'mkv')):
                files.append(os.path.join(root, filename))
    return files


def seconds_to_time(seconds):
    return str(timedelta(seconds=seconds))


def format_time(seconds):
    return time.strftime('%H:%M:%S', time.gmtime(seconds))


def process_video(file_path, model, frame_skip=20):
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        print(f"Не удалось открыть видеофайл: {file_path}")
        return []

    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = total_frames / frame_rate

    # Настройка записи выходного видео
    output_video_path = os.path.join(output_folder, os.path.basename(file_path))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (width, height))

    frame_index = 0

    # Переменные для отслеживания нарушений
    current_violation = None
    violation_start_frame = None
    violations_logged = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_height, frame_width, _ = frame.shape
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Выполнение трекинга объектов с помощью модели YOLOv8
        results = model(image_rgb, conf=0.3)

        # Обработка результатов
        predictions = results[0].boxes  # Предполагая, что мы хотим обработать предсказания первого изображения
        labels = predictions.cls.cpu().numpy()  # метки классов
        boxes = predictions.xyxyn.cpu().numpy()  # ограничивающие рамки
        scores = predictions.conf.cpu().numpy()  # коэффициенты уверенности

        violations = []

        for label, box, score in zip(labels, boxes, scores):
            if score >= 0.3:
                x1, y1, x2, y2 = map(float, box)

                # Проверка на нарушения
                if model.names[int(label)] == 'person':
                    person_box = box
                    has_vest = False
                    has_helmet = False

                    for other_label, other_box, other_score in zip(labels, boxes, scores):
                        if other_score >= 0.3 and not np.array_equal(other_box, person_box):
                            # Проверяем, пересекаются ли ограничивающие рамки человека и жилета/каски
                            if (other_box[0] < person_box[2] and other_box[2] > person_box[0] and
                                    other_box[1] < person_box[3] and other_box[3] > person_box[1]):
                                if model.names[int(other_label)] == 'vest':
                                    has_vest = True
                                if model.names[int(other_label)] == 'helmet':
                                    has_helmet = True
                                if model.names[int(other_label)] == 'heat':
                                    has_helmet = False

                    if not has_vest or not has_helmet:
                        violation_type = 'Отсутствует жилет' if not has_vest else 'Отсутствует каска'
                        violations.append({
                            'frame': frame_index,
                            'time': format_time(frame_index / frame_rate),
                            'violation': violation_type,
                            'bbox': person_box.tolist()
                        })

                        if current_violation == violation_type:
                            continue  # Continue tracking the current violation
                        else:
                            # End the current violation if it existed
                            if current_violation is not None:
                                duration = frame_index - violation_start_frame
                                if duration / frame_rate > 1:  # Duration is more than one second
                                    violations_logged.append({
                                        'file': os.path.basename(file_path),
                                        'start_time': format_time(violation_start_frame / frame_rate),
                                        'end_time': format_time((frame_index - frame_skip) / frame_rate),
                                        'violation': current_violation,
                                        'frame': violation_start_frame
                                    })
                            # Start tracking a new violation
                            current_violation = violation_type
                            violation_start_frame = frame_index

        if not violations and current_violation is not None:
            # End the current violation if it existed and wasn't tracked in this frame
            duration = frame_index - violation_start_frame
            if duration / frame_rate > 1:  # Duration is more than one second
                violations_logged.append({
                    'file': os.path.basename(file_path),
                    'start_time': format_time(violation_start_frame / frame_rate),
                    'end_time': format_time((frame_index - frame_skip) / frame_rate),
                    'violation': current_violation,
                    'frame': violation_start_frame
                })
            current_violation = None
            violation_start_frame = None

        # Сохранение исходного кадра с аннотациями
        for violation in violations:
            x1, y1, x2, y2 = map(int, [violation['bbox'][0] * frame_width, violation['bbox'][1] * frame_height,
                                       violation['bbox'][2] * frame_width, violation['bbox'][3] * frame_height])
            cropped_person = frame[int(y1 * frame_height):int(y2 * frame_height),
                             int(x1 * frame_width):int(x2 * frame_width)]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Красная рамка для нарушения
            cv2.putText(frame, violation['violation'], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255),
                        2)  # Текст с нарушением

        # Запись аннотированного кадра в выходное видео
        out.write(frame)

        output_annotated_image_path = os.path.join(output_folder, 'annotated_images',
                                                   f"{os.path.basename(file_path)}_frame_{frame_index}.jpg")
        os.makedirs(os.path.dirname(output_annotated_image_path), exist_ok=True)
        cv2.imwrite(output_annotated_image_path, frame)

        # Увеличение индекса кадра на заданное значение frame_skip
        frame_index += frame_skip

    cap.release()
    out.release()
    print(f"Обработка завершена для видео: {file_path}")
    return violations_logged


def save_to_excel(violations, excel_path):
    df = pd.DataFrame(violations, columns=['file', 'start_time', 'end_time', 'violation'])
    df.to_excel(excel_path, index=False)


font_path = 'DejaVuSans-ExtraLight.ttf'  # Убедитесь, что путь правильный


def create_violation_chart(violations):
    # Extract violation types
    violation_types = [violation['violation'] for violation in violations]

    # Count each type of violation
    violation_counts = pd.Series(violation_types).value_counts()

    # Plot the violation counts
    plt.figure(figsize=(10, 6))
    violation_counts.plot(kind='bar', color='skyblue')
    plt.title('Types of Violations')
    plt.xlabel('Violation Type')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart_path = 'violation_chart.png'
    plt.savefig(chart_path)
    plt.close()
    return chart_path


def create_violation_chart(violations):
    # Extract violation types
    violation_types = [violation['violation'] for violation in violations]

    # Count each type of violation
    violation_counts = pd.Series(violation_types).value_counts()

    # Plot the violation counts
    plt.figure(figsize=(10, 6))
    violation_counts.plot(kind='bar', color='skyblue')
    plt.title('Types of Violations')
    plt.xlabel('Violation Type')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart_path = 'violation_chart.png'
    plt.savefig(chart_path)
    plt.close()
    return chart_path


def create_pdf_report(violations, output_pdf_path, chart_path):
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.fontSize = 24
    title_style.textColor = colors.darkblue

    normal_style = styles['Normal']
    normal_style.fontSize = 12
    normal_style.leading = 14

    elements.append(Paragraph("Report of Violations", title_style))
    elements.append(Spacer(1, 20))

    # Add introduction about the report's purpose
    intro_text = ("This report provides an overview of safety violations detected in the analyzed videos. "
                  "The main purpose is to identify areas of improvement for safety compliance. "
                  "The chart below shows the frequency of different types of violations.")
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 20))

    # Embed the violation chart at the beginning and align it to the left
    if os.path.exists(chart_path):
        elements.append(Image(chart_path, width=500, height=300))
        elements.append(Spacer(1, 40))

    for violation in violations:
        file_text = f"File: {violation['file']}"
        start_time_text = f"Start Time: {violation['start_time']}"
        end_time_text = f"End Time: {violation['end_time']}"
        violation_text = f"Violation: {violation['violation']}"

        text_data = [
            Paragraph(file_text, normal_style),
            Paragraph(start_time_text, normal_style),
            Paragraph(end_time_text, normal_style),
            Paragraph(violation_text, normal_style)
        ]

        image_folder = os.path.join(output_folder, 'annotated_images')
        image_name = f"{violation['file']}_frame_{violation.get('frame', '')}.jpg"
        image_path = os.path.join(image_folder, image_name)

        if os.path.exists(image_path):
            img = Image(image_path, width=200, height=150)
            img.hAlign = 'LEFT'
            table_data = [
                [text_data, img]
            ]
            table = Table(table_data, colWidths=[350, 200])
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (0, 0), 'TOP')
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))
        else:
            print(f"Image not found: {image_path}")
            for paragraph in text_data:
                elements.append(paragraph)
            elements.append(Spacer(1, 20))

    doc.build(elements)
    print(f"PDF report created: {output_pdf_path}")


def main():
    initialize_directories()
    files = initialize_directories()
    # model = initialize_model()

    all_violations = []

    for file_path in files:
        violations = process_video(file_path, model)
        all_violations.extend(violations)

    print(all_violations)  # Debug statement

    save_to_excel(all_violations, 'frauds.xlsx')
    return all_violations


b = main()
chart_path = create_violation_chart(b)  # Generate the chart
create_pdf_report(b, 'frauds_repor2t.pdf', chart_path)
print("Все видео были обработаны и результаты сохранены в Excel файл и PDF отчет.")
