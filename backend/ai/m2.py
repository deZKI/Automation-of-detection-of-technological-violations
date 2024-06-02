import os
import cv2
import torch
import numpy as np
import pandas as pd
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from torchvision.transforms import Compose, Lambda, Normalize, Resize, CenterCrop

# Установка устройства для вычислений (CPU или GPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Загрузка предобученной модели
model = torch.hub.load('facebookresearch/pytorchvideo', 'slowfast_r50', pretrained=False)
model.blocks[-1].proj = torch.nn.Linear(model.blocks[-1].proj.in_features,
                                        3)  # Три выхода для многоклассовой классификации
model = model.to(device)

# Параметры для обработки видео
side_size = 256
mean = [0.45, 0.45, 0.45]
std = [0.225, 0.225, 0.225]
crop_size = 256
num_frames = 32
sampling_rate = 2
frames_per_second = 30
slowfast_alpha = 4


# Преобразования для видео
class VideoTransform:
    def __init__(self, side_size, mean, std, crop_size):
        self.transforms = Compose([
            Lambda(lambda x: x / 255.0),
            Resize((side_size, side_size)),
            CenterCrop(crop_size),
            Lambda(lambda x: self.normalize_video(x, mean, std))
        ])

    def __call__(self, x):
        return self.transforms(x)

    def normalize_video(self, video, mean, std):
        mean = torch.tensor(mean).view(3, 1, 1, 1)
        std = torch.tensor(std).view(3, 1, 1, 1)
        return (video - mean) / std


transform = VideoTransform(side_size, mean, std, crop_size)


class PackPathway(torch.nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, frames: torch.Tensor):
        fast_pathway = frames
        slow_pathway = torch.index_select(
            frames,
            1,
            torch.linspace(
                0, frames.shape[1] - 1, frames.shape[1] // slowfast_alpha
            ).long(),
        )
        frame_list = [slow_pathway, fast_pathway]
        return frame_list


def load_and_preprocess_video(video_path, transform, num_frames=32, sampling_rate=2):
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count / fps

    for i in range(num_frames):
        frame_id = i * sampling_rate
        if frame_id >= frame_count:
            break
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame)

    cap.release()

    if not frames:
        raise ValueError(f"Не удалось загрузить кадры из видео: {video_path}")

    if len(frames) < num_frames:
        # Повторение последнего кадра, если видео короче ожидаемого числа кадров
        frames += [frames[-1]] * (num_frames - len(frames))

    frames = np.stack(frames)
    frames = torch.from_numpy(frames).permute(3, 0, 1, 2)  # Преобразование в CTHW
    frames = transform(frames)  # Применение преобразований

    pack_pathway = PackPathway()
    video_tensor = pack_pathway(frames)
    return video_tensor


# Словарь для преобразования меток в текстовые описания
label_to_description = {
    0: "Нарушение: Работы под составом",
    1: "Нарушение: Передвижение на подвижном составе",
    2: "Без нарушений"
}


def run_inference(video_path: str, checkpoint_path: str):
    # Загрузка контрольной точки
    checkpoint = torch.load(checkpoint_path)

    # Восстановление весов модели
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    video_tensor = load_and_preprocess_video(video_path, transform)
    video_tensor = [i.unsqueeze(0).to(device) for i in video_tensor]  # Добавление batch dimension

    with torch.no_grad():
        outputs = model(video_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        pred = torch.argmax(outputs, dim=1).item()
        description = label_to_description[pred]

    return video_path, description, probabilities.squeeze().cpu().numpy()


def split_video(video_path, segment_length=0.1):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps
    segment_paths = []

    segment_length = segment_length * duration  # Преобразование относительной длины в абсолютную

    for start_time in range(0, int(duration), int(segment_length)):
        end_time = start_time + segment_length
        if end_time > duration:
            end_time = duration
        segment_path = f"{video_path.split('.')[0]}_segment_{start_time}_{end_time}.mp4"
        ffmpeg_extract_subclip(video_path, start_time, end_time, targetname=segment_path)
        segment_paths.append((segment_path, start_time, end_time))

    cap.release()
    return segment_paths


def run_inference_on_segments(segment_paths, checkpoint_path):
    predictions = []
    for segment_path, start_time, end_time in segment_paths:
        video_path, description, probabilities = run_inference(segment_path, checkpoint_path)
        if predictions and predictions[-1][1] == description:
            # Обновление времени окончания предыдущего предсказания
            predictions[-1][3] = end_time
        else:
            predictions.append([video_path, description, start_time, end_time])
    return predictions


# Пример использования функции split_video и run_inference_on_segments
video_path = 'testing/2_5395803543229709828_0.mp4'
checkpoint_path = 'slowfast_epoch_5.pth'
segment_paths = split_video(video_path)
predictions = run_inference_on_segments(segment_paths, checkpoint_path)


# Объединение предсказаний и сохранение в Excel
def save_predictions_to_excel(predictions, excel_path):
    data = []
    for prediction in predictions:
        file_name = os.path.basename(prediction[0])
        description = prediction[1]
        time_interval = f"{prediction[2]} - {prediction[3]}"
        data.append([file_name, description, time_interval])

    df = pd.DataFrame(data, columns=['Файл', 'Нарушение', 'Интервал'])
    df.to_excel(excel_path, index=False)


# Пример сохранения в Excel
excel_path = 'violations_report.xlsx'
save_predictions_to_excel(predictions, excel_path)
