import os
import time
import tempfile

import pandas as pd
import cv2

from tqdm import tqdm

from django.conf import settings
from django.core.files.base import ContentFile

from video.models import OriginalVideo, ProceedVideo, TimeCode


def format_time(seconds: int):
    """Функция для форматирования времени в формат HH:MM:SS"""
    return time.strftime('%H:%M:%S', time.gmtime(seconds))


def process_video(original_video: OriginalVideo, proceed_video: ProceedVideo):
    """ Обработка оргинальнального видео и создание обработанного"""
    try:
        # Создание временных директорий для видео и Excel файлов
        with tempfile.TemporaryDirectory() as temp_dir:
            output_video_path = os.path.join(temp_dir, f'processed_{os.path.basename(original_video.video.name)}')
            output_excel_path = os.path.join(temp_dir, f'processed_{proceed_video.id}.xlsx')

            # Словарь для отслеживания объектов по ID
            tracked_objects = {}

            cap = cv2.VideoCapture(original_video.video.path)
            frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Настройка записи выходного видео
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (width, height))

            model = settings.MODEL
            device = settings.DEVICE

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            with tqdm(total=total_frames, desc="Processing Video") as pbar:
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

                            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])),
                                          (0, 255, 0), 2)
                            cv2.putText(frame, f"ID: {int(obj_id)}", (int(bbox[0]), int(bbox[1]) - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    out.write(frame)
                    pbar.update(1)

            cap.release()
            out.release()

            # Сохранение обработанного видео в ProceedVideo
            with open(output_video_path, 'rb') as f:
                video_content = f.read()
                proceed_video.video.save(f'processed_{os.path.basename(original_video.video.name)}',
                                         ContentFile(video_content))

            fraud_entries = []

            for obj_id, times in tracked_objects.items():
                if times['fraud'] and (times['end'] - times['start']) >= 1:
                    TimeCode.objects.create(
                        proceed_video=proceed_video,
                        prediction='Fraud detected',
                        time_in_seconds=int(times['start'])
                    )

                    fraud_entries.append([format_time(times['start']), format_time(times['end']), int(obj_id)])

            df = pd.DataFrame(fraud_entries, columns=['start_fraud', 'end_fraud', 'object_id'])
            df.to_excel(output_excel_path, index=False)

            # Сохранение Excel файла в ProceedVideo
            with open(output_excel_path, 'rb') as f:
                excel_content = f.read()
                proceed_video.excel_file.save(f'processed_{proceed_video.id}.xlsx', ContentFile(excel_content))

            proceed_video.save()

    except Exception as e:
        print(f"Error processing video {original_video.video.path}: {e}")
