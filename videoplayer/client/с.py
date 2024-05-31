import cv2
import torch
from ultralytics import YOLO
import os
from datetime import timedelta
import pandas as pd
import time
import numpy as np


# Путь к файлу Excel для сохранения данных о нарушениях
excel_path = 'frauds.xlsx'

# Список для хранения информации о детекциях
detection_info = []
tracked_objects = {}  # Словарь для отслеживания объектов по ID


# Функция для преобразования секунд в формат времени
def seconds_to_time(seconds):
    return str(timedelta(seconds=seconds))


# Функция для форматирования времени в формат HH:MM:SS
def format_time(seconds):
    return time.strftime('%H:%M:%S', time.gmtime(seconds))


current_frame = 0
last_shown_time = time.time()

# Общее количество видеофайлов

model = YOLO('/Users/kirill201/Desktop/Projects/Automation-of-detection-of-technological-violations/videoplayer/client/best.pt')  # Укажите правильный путь к вашей модели
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# Количество кадров для пропуска
frame_skip = 20

# Обработка каждого видеофайла
def file(file_path, output_folder):
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        Exception(f"Не удалось открыть видеофайл: {file_path}")

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
    while cap.isOpened():
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
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

        # Сохранение данных о предсказаниях (метки и ограничивающие рамки)
        output_data_path = os.path.join(output_folder, 'labels',
                                        f"{os.path.basename(file_path)}_frame_{frame_index}.txt")
        os.makedirs(os.path.dirname(output_data_path), exist_ok=True)

        violations = []

        with open(output_data_path, 'w') as f:
            for label, box, score in zip(labels, boxes, scores):
                if score >= 0.3:
                    x1, y1, x2, y2 = map(float, box)
                    f.write(f"{model.names[int(label)]} {x1} {y1} {x2} {y2}\n")

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

                        if not has_vest or not has_helmet:

                            violations.append({
                                'frame': frame_index,
                                'time': format_time(frame_index / frame_rate),
                                'violation': 'Отсутствует жилет' if not has_vest else 'Отсутствует каска',
                                'bbox': person_box.tolist()
                            })

        # Сохранение исходного кадра с аннотациями
        for violation in violations:
            x1, y1, x2, y2 = map(int, [violation['bbox'][0] * frame_width, violation['bbox'][1] * frame_height,
                                       violation['bbox'][2] * frame_width, violation['bbox'][3] * frame_height])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Красная рамка для нарушения
            cv2.putText(frame, violation['violation'], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255),
                        2)  # Текст с нарушением
        detections = results[0]
        excel = pd.DataFrame(data=violations)
        excel.to_excel("excel.xls")


        # new_result_array = detections.plot()
        # plt.figure(figsize=(12, 12))
        # plt.imshow(new_result_array)
        # plt.show()
        #
        # # Отображение аннотированных изображений с помощью matplotlib
        # if violations:
        #     plt.figure(figsize=(12, 8))
        #     plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        #     plt.title(f'Нарушения на кадре {frame_index}')
        #     plt.axis('off')
        #     plt.show()

        output_annotated_image_path = os.path.join(output_folder, 'annotated_images',
                                                   f"{os.path.basename(file_path)}_frame_{frame_index}.jpg")
        os.makedirs(os.path.dirname(output_annotated_image_path), exist_ok=True)
        cv2.imwrite(output_annotated_image_path, frame)

        # Увеличение индекса кадра на заданное значение frame_skip
        frame_index += frame_skip

    cap.release()
    out.release()
    print(f"Обработка завершена для видео: {file_path}")
    return output_video_path

