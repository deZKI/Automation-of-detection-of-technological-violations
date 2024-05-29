import os
import time
import threading
import cv2
import torch

from ultralytics import YOLO
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class OriginalVideo(models.Model):
    """Изначальное необработанное видео"""
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to='videos/')


class ProceedVideo(models.Model):
    title = models.CharField(max_length=100, default='Processed')
    original_video = models.ForeignKey(OriginalVideo, on_delete=models.CASCADE)
    version = models.IntegerField(verbose_name='Версия нейросети')
    video = models.FileField(upload_to='proceed-videos/')
    excel_file = models.FileField(upload_to='excels/', blank=True)


class TimeCode(models.Model):
    proceed_video = models.ForeignKey(ProceedVideo, on_delete=models.CASCADE)
    prediction = models.CharField(max_length=128)
    time_in_seconds = models.IntegerField()


def format_time(seconds):
    """Функция для форматирования времени в формат HH:MM:SS"""
    return time.strftime('%H:%M:%S', time.gmtime(seconds))


def process_video(original_video_id, video_path):
    # Загружаем модель YOLOv8 из указанного пути
    model = YOLO('ai/last.pt')

    # Определяем устройство для вычислений (используем GPU, если доступно)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    # Путь к папке для сохранения обработанных видео
    output_folder = 'media/proceed-videos'
    excel_file_folder = 'media/excels'

    media_folder = 'proceed-videos'
    media_file_folder = 'excels'

    os.makedirs(output_folder, exist_ok=True)

    # Словарь для отслеживания объектов по ID
    tracked_objects = {}

    cap = cv2.VideoCapture(video_path)
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Настройка записи выходного видео
    output_video_path = os.path.join(output_folder, f'processed_{os.path.basename(video_path)}')

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (width, height))

    current_frame = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model.track(frame, device=device, verbose=False, conf=0.4, tracker="bytetrack.yaml")[0]
        frame_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

        if results.boxes:
            bboxes = results.boxes.xyxy
            clss = results.boxes.cls.cpu().tolist()
            ids = results.boxes.id
            ids = ids.cpu().tolist() if ids is not None else []

            for bbox, cls, obj_id in zip(bboxes, clss, ids):
                if obj_id not in tracked_objects:
                    tracked_objects[obj_id] = {'start': frame_time, 'end': frame_time, 'fraud': False}

                contains_protection = any(
                    other_cls in {0, 2, 5} and
                    other_bbox[0] >= bbox[0] and
                    other_bbox[1] >= bbox[1] and
                    other_bbox[2] <= bbox[2] and
                    other_bbox[3] <= bbox[3]
                    for other_bbox, other_cls in zip(bboxes, clss)
                )
                contains_head = any(
                    other_cls == 1 and
                    other_bbox[0] >= bbox[0] and
                    other_bbox[1] >= bbox[1] and
                    other_bbox[2] <= bbox[2] and
                    other_bbox[3] <= bbox[3]
                    for other_bbox, other_cls in zip(bboxes, clss)
                )
                if not contains_protection or contains_head:
                    tracked_objects[obj_id]['fraud'] = True
                    tracked_objects[obj_id]['end'] = frame_time
                else:
                    tracked_objects[obj_id]['fraud'] = False

                cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {int(obj_id)}", (int(bbox[0]), int(bbox[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        out.write(frame)
        current_frame += 1

    cap.release()
    out.release()

    # Сохранение обработанного видео и создание записи в базе данных
    proceed_video = ProceedVideo.objects.create(
        title=f'Processed {os.path.basename(video_path)}',
        original_video_id=original_video_id,
        version=1,
        video=os.path.join(media_folder, f'processed_{os.path.basename(video_path)}')
    )


    fraud_entries = []

    # Сохранение информации о нарушениях в Excel файл
    import pandas as pd

    output_video_excel = os.path.join(excel_file_folder, f'processed{proceed_video.id}.xlsx')

    for obj_id, times in tracked_objects.items():
        if times['fraud'] and (times['end'] - times['start']) >= 1:
            TimeCode.objects.create(
                proceed_video=proceed_video,
                prediction='Fraud detected',
                time_in_seconds=int(times['start'])
            )

            fraud_entries.append(
                [format_time(times['start']), format_time(times['end']), int(obj_id)])


    df = pd.DataFrame(fraud_entries, columns=['start_fraud', 'end_fraud', 'object_id'])
    df.to_excel(output_video_excel, index=False)

    proceed_video.excel_file = os.path.join(media_file_folder, f'processed{proceed_video.id}.xlsx')
    proceed_video.save()



@receiver(post_save, sender=OriginalVideo)
def create_proceed_video(sender, instance, created, **kwargs):
    if created:
        threading.Thread(target=process_video, args=(instance.id, instance.video.path)).start()
