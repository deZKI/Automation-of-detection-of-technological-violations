import os
import time
import tempfile
import numpy as np
import matplotlib
import torch
import ultralytics

matplotlib.use('Agg')  # Использование безголового backend для Matplotlib
import pandas as pd
import cv2
import io

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.platypus.flowables import Image as ReportLabImage
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from tqdm import tqdm

from m2 import split_video, run_inference_on_segments
from django.core.files.base import ContentFile

from video.models import OriginalVideo, ProceedVideo, TimeCode
from enum import Enum

FRAME_SKIP = 20
FRAME_RATE_THRESHOLD = 1  # in seconds
CONFIDENCE_THRESHOLD = 0.3
VIDEO_CODEC = 'mp4v'
ANNOTATED_IMAGE_WIDTH = 200
ANNOTATED_IMAGE_HEIGHT = 150
TABLE_COLUMN_WIDTHS = [350, 200]
OUTPUT_VIDEO_PREFIX = 'processed_'
OUTPUT_EXCEL_SUFFIX = '.xlsx'
OUTPUT_PDF_SUFFIX = '.pdf'
CHART_WIDTH = 500
CHART_HEIGHT = 300
CHART_COLOR = 'skyblue'
CHECKPOINT_PATH = 'slowfast_epoch_5.pth'


class ViolationType(Enum):
    """ Типы нарушений """
    MISSING_VEST = 'Отсутствует жилет'
    MISSING_HELMET = 'Отсутствует каска'
    FRAUD_DETECTED = 'Fraud detected'


class ModelNameType(Enum):
    """ Типы объектов"""
    VEST = 'vest'
    HELMET = 'helmet'
    HEAT = 'heat'
    PERSON = 'person'


def format_time(seconds: int):
    """Функция для форматирования времени в формат HH:MM:SS"""
    return time.strftime('%H:%M:%S', time.gmtime(seconds))


import ffmpeg
import os
from django.core.files.base import ContentFile


def transcode_to_h264(input_video_path, output_video_path):
    # Транскодирование видео в формат H.264
    ffmpeg.input(input_video_path).output(output_video_path, vcodec='libx264', acodec='aac').run()


def time_str_to_seconds(time_str):
    """Конвертирует строку времени в формате HH:MM:SS в количество секунд."""
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s


def process_video(original_video: OriginalVideo, proceed_video: ProceedVideo, frame_skip=FRAME_SKIP):
    """ Обработка оригинального видео и создание обработанного"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_video_path = os.path.join(temp_dir,
                                             f'{OUTPUT_VIDEO_PREFIX}{os.path.basename(original_video.video.name)}')
            output_excel_path = os.path.join(temp_dir, f'{OUTPUT_VIDEO_PREFIX}{proceed_video.id}{OUTPUT_EXCEL_SUFFIX}')
            output_pdf_path = os.path.join(temp_dir, f'{OUTPUT_VIDEO_PREFIX}{proceed_video.id}{OUTPUT_PDF_SUFFIX}')

            cap = cv2.VideoCapture(original_video.video.path)
            frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Настройка записи выходного видео
            fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC)
            out = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (width, height))
            frame_index = 0

            current_violation = None
            violation_start_frame = None
            violations_logged = []

            # Загружаем модель YOLOv8 из указанного пути
            model = ultralytics.YOLO('ai/best.pt')
            DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            # Определяем устройство для вычислений (используем GPU, если доступно)
            model.to(DEVICE)

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            with tqdm(total=total_frames, desc="Processing Video") as pbar:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    if frame_index % frame_skip == 0:
                        frame_height, frame_width, _ = frame.shape
                        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                        # Выполнение трекинга объектов с помощью модели YOLOv8
                        results = model(image_rgb, conf=CONFIDENCE_THRESHOLD, verbose=False)

                        predictions = results[0].boxes
                        labels = predictions.cls.cpu().numpy()
                        boxes = predictions.xyxyn.cpu().numpy()
                        scores = predictions.conf.cpu().numpy()

                        violations = []

                        for label, box, score in zip(labels, boxes, scores):
                            if score >= CONFIDENCE_THRESHOLD:
                                if model.names[int(label)] == ModelNameType.PERSON.value:
                                    person_box = box
                                    has_vest = False
                                    has_helmet = False

                                    for other_label, other_box, other_score in zip(labels, boxes, scores):
                                        if other_score >= CONFIDENCE_THRESHOLD and not np.array_equal(other_box,
                                                                                                      person_box):
                                            if (other_box[0] < person_box[2] and other_box[2] > person_box[0] and
                                                    other_box[1] < person_box[3] and other_box[3] > person_box[1]):
                                                if model.names[int(other_label)] == ModelNameType.VEST.value:
                                                    has_vest = True
                                                elif model.names[int(other_label)] == ModelNameType.HELMET.value:
                                                    has_helmet = True
                                                elif model.names[int(other_label)] == ModelNameType.HEAT.value:
                                                    has_helmet = False

                                    if not has_vest or not has_helmet:
                                        violation_type = ViolationType.MISSING_VEST.value if not has_vest else ViolationType.MISSING_HELMET.value
                                        violations.append({
                                            'frame': frame_index,
                                            'time': format_time(frame_index / frame_rate),
                                            'violation': violation_type,
                                            'bbox': person_box.tolist()
                                        })

                                        if current_violation == violation_type:
                                            continue
                                        else:
                                            if current_violation is not None:
                                                duration = frame_index - violation_start_frame
                                                if duration / frame_rate > FRAME_RATE_THRESHOLD:
                                                    violations_logged.append({
                                                        'file': os.path.basename(original_video.video.path),
                                                        'start_time': format_time(violation_start_frame / frame_rate),
                                                        'end_time': format_time(
                                                            (frame_index - frame_skip) / frame_rate),
                                                        'violation': current_violation,
                                                        'frame': violation_start_frame
                                                    })
                                            current_violation = violation_type
                                            violation_start_frame = frame_index

                        if not violations and current_violation is not None:
                            duration = frame_index - violation_start_frame
                            if duration / frame_rate > FRAME_RATE_THRESHOLD:
                                violations_logged.append({
                                    'file': os.path.basename(original_video.video.path),
                                    'start_time': format_time(violation_start_frame / frame_rate),
                                    'end_time': format_time((frame_index - frame_skip) / frame_rate),
                                    'violation': current_violation,
                                    'frame': violation_start_frame
                                })
                            current_violation = None
                            violation_start_frame = None

                        for violation in violations:
                            x1, y1, x2, y2 = map(int, [
                                violation['bbox'][0] * frame_width, violation['bbox'][1] * frame_height,
                                violation['bbox'][2] * frame_width, violation['bbox'][3] * frame_height
                            ])

                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            # cv2.putText(frame, violation['violation'], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                            #             (0, 0, 255), 2)

                    frame_index += 1
                    out.write(frame)
                    pbar.update(1)

                cap.release()
                out.release()

            for violation in violations_logged:
                TimeCode.objects.create(
                    proceed_video=proceed_video,
                    prediction=ViolationType.FRAUD_DETECTED.value,
                    time_in_seconds=time_str_to_seconds(violation['start_time'])
                )

            segment_paths = split_video(output_video_path)
            predictions = run_inference_on_segments(segment_paths, CHECKPOINT_PATH)

            create_pdf_report(violations_logged, output_pdf_path, width, height)
            save_predictions_to_excel(predictions, output_excel_path)

            transcoded_video_path = os.path.join(temp_dir, f'transcoded_{os.path.basename(output_video_path)}')
            transcode_to_h264(output_video_path, transcoded_video_path)

            with open(transcoded_video_path, 'rb') as f:
                """ Сохранение преобразованного видео """
                video_content = f.read()
                proceed_video.video.save(f'{OUTPUT_VIDEO_PREFIX}{os.path.basename(original_video.video.name)}',
                                         ContentFile(video_content))

            with open(output_excel_path, 'rb') as f:
                """ Сохранение excel """
                excel_content = f.read()
                proceed_video.excel_file.save(f'{OUTPUT_VIDEO_PREFIX}{proceed_video.id}{OUTPUT_EXCEL_SUFFIX}',
                                              ContentFile(excel_content))

            with open(output_pdf_path, 'rb') as f:
                """ Сохранение pdf """
                pdf_content = f.read()
                proceed_video.pdf_file.save(f'{OUTPUT_VIDEO_PREFIX}{proceed_video.id}{OUTPUT_PDF_SUFFIX}',
                                            ContentFile(pdf_content))

            proceed_video.save()

    except Exception as e:
        print(f"Error processing video {original_video.video.path}: {e}")


def create_pdf_report(violations, output_pdf_path, frame_width, frame_height):
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    elements = []

    # Register a font that supports Cyrillic characters
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'ai/DejaVuSans.ttf'))

    styles = getSampleStyleSheet()

    title_style = styles['Title']
    title_style.fontName = 'DejaVuSans'
    title_style.fontSize = 24
    title_style.textColor = colors.darkblue

    normal_style = styles['Normal']
    normal_style.fontName = 'DejaVuSans'
    normal_style.fontSize = 12
    normal_style.leading = 14

    elements.append(Paragraph("Отчет о нарушениях", title_style))
    elements.append(Spacer(1, 20))

    intro_text = ("Этот отчет предоставляет обзор нарушений безопасности, обнаруженных в анализируемых видео. "
                  "Основная цель - выявить области для улучшения соблюдения требований безопасности. "
                  "Диаграмма ниже показывает частоту различных типов нарушений.")
    elements.append(Paragraph(intro_text, normal_style))
    elements.append(Spacer(1, 20))

    for violation in violations:
        file_text = f"Файл: {violation['file']}"
        start_time_text = f"Время начала: {format_time(time_str_to_seconds(violation['start_time']))}"
        end_time_text = f"Время окончания: {format_time(time_str_to_seconds(violation['end_time']))}"
        violation_text = f"Нарушение: {violation['violation']}"

        text_data = [
            Paragraph(file_text, normal_style),
            Paragraph(start_time_text, normal_style),
            Paragraph(end_time_text, normal_style),
            Paragraph(violation_text, normal_style)
        ]

        if 'bbox' in violation:
            frame_img = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
            x1, y1, x2, y2 = map(int, [
                violation['bbox'][0] * frame_width, violation['bbox'][1] * frame_height,
                violation['bbox'][2] * frame_width, violation['bbox'][3] * frame_height
            ])
            cv2.rectangle(frame_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame_img, violation['violation'], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            _, buffer = cv2.imencode('.jpg', frame_img)
            img_buffer = io.BytesIO(buffer)

            img = ReportLabImage(img_buffer, width=ANNOTATED_IMAGE_WIDTH, height=ANNOTATED_IMAGE_HEIGHT)
            img.hAlign = 'LEFT'
            table_data = [
                [text_data, img]
            ]
            table = Table(table_data, colWidths=TABLE_COLUMN_WIDTHS)
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (0, 0), 'TOP')
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))
        else:
            for paragraph in text_data:
                elements.append(paragraph)
            elements.append(Spacer(1, 20))

    doc.build(elements)


def save_predictions_to_excel(predictions, excel_path):
    data = []
    for prediction in predictions:
        file_name = os.path.basename(prediction[0])
        description = prediction[1]
        time_interval = f"{prediction[2]} - {prediction[3]}"
        data.append([file_name, description, time_interval])

    df = pd.DataFrame(data, columns=['Файл', 'Нарушение', 'Интервал'])
    df.to_excel(excel_path, index=False)
