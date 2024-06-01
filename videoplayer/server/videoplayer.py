import os
import datetime
import tkinter as tk

import requests
import tempfile
import threading

from tkinter import messagebox, filedialog
from tkVideoPlayer import TkinterVideo
from typing import List, Dict, Optional, Any

from dotenv import load_dotenv

load_dotenv()


class VideoPlayerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RZD Видеоплеер нарушений")
        self.geometry("1200x600")

        # Получение URL API из переменной окружения
        self.api_url = os.getenv("API_URL", "http://95.163.223.21/api")
        self.media_url = os.getenv("MEDIA_URL", "http://95.163.223.21")

        # Создание виджета для отображения видео
        self.vid_player = TkinterVideo(scaled=True, master=self)
        self.vid_player.pack(expand=True, fill="both")

        # Добавление кнопок управления
        control_frame = tk.Frame(self)
        control_frame.pack(fill="x")

        self.load_videos_btn = tk.Button(control_frame, text="Загрузить видео", command=self.load_original_videos)
        self.load_videos_btn.pack(side="left")

        self.upload_video_btn = tk.Button(control_frame, text="Выгрузить видео", command=self.upload_video)
        self.upload_video_btn.pack(side="left")

        self.play_pause_btn = tk.Button(control_frame, text="Play", command=self.play_pause)
        self.play_pause_btn.pack(side="left")

        self.skip_minus_5sec = tk.Button(control_frame, text="-5 sec", command=lambda: self.skip(-5))
        self.skip_minus_5sec.pack(side="left")

        self.start_time = tk.Label(control_frame, text=str(datetime.timedelta(seconds=0)))
        self.start_time.pack(side="left")

        self.progress_value = tk.IntVar(self)
        self.progress_slider = tk.Scale(control_frame, variable=self.progress_value, from_=0, to=0, orient="horizontal",
                                        command=self.seek)
        self.progress_slider.pack(side="left", fill="x", expand=True)

        self.end_time = tk.Label(control_frame, text=str(datetime.timedelta(seconds=0)))
        self.end_time.pack(side="left")

        self.skip_plus_5sec = tk.Button(control_frame, text="+5 sec", command=lambda: self.skip(5))
        self.skip_plus_5sec.pack(side="left")

        self.original_video_listbox = tk.Listbox(self)
        self.original_video_listbox.pack(side="left", fill="y")
        self.original_video_listbox.bind('<<ListboxSelect>>', self.select_original_video)

        self.proceed_video_listbox = tk.Listbox(self)
        self.proceed_video_listbox.pack(side="left", fill="y")
        self.proceed_video_listbox.bind('<<ListboxSelect>>', self.select_proceed_video)

        self.timecode_listbox = tk.Listbox(self)
        self.timecode_listbox.pack(side="left", fill="y")
        self.timecode_listbox.bind('<<ListboxSelect>>', self.select_timecode)

        self.download_pdf_btn = tk.Button(text="Загрузить PDF", command=self.download_pdf)
        self.download_pdf_btn.pack(side="left", fill="y")

        self.download_excel_btn = tk.Button(text="Загрузить Excel", command=self.download_excel)
        self.download_excel_btn.pack(side="left", fill="y")

        # Привязка событий
        self.vid_player.bind("<<Duration>>", self.update_duration)
        self.vid_player.bind("<<SecondChanged>>", self.update_scale)
        self.vid_player.bind("<<Ended>>", self.video_ended)

        self.playing = False
        self.temp_file = None
        self.original_video_list: List[Dict[str, Any]] = []
        self.proceed_video_list: List[Dict[str, Any]] = []
        self.timecodes: List[Dict[str, Any]] = []
        self.selected_original_video_id: Optional[int] = None
        self.selected_proceed_video_id: Optional[int] = None

        self.selected_pdf_url: Optional[str] = None
        self.selected_excel_url: Optional[str] = None

    def api_request(self, endpoint: str, method: str = "GET") -> Optional[Any]:
        """Выполнение запроса к API"""
        try:
            url = f"{self.api_url}/{endpoint}"
            response = requests.request(method, url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Ошибка в созданиие запроса на сервер {url}: {e}")
            return None

    def load_original_videos(self) -> None:
        """Загрузка списка оригинальных видео с сервера"""
        self.original_video_list = self.api_request("videos/") or []
        self.update_listbox(self.original_video_listbox, [video["title"] for video in self.original_video_list])

    def load_proceed_videos(self, original_video_id: int) -> None:
        """Загрузка списка обработанных видео с сервера"""
        self.proceed_video_list = self.api_request(f"proceed-videos/{original_video_id}/") or []
        self.update_listbox(self.proceed_video_listbox, [video["title"] for video in self.proceed_video_list])

    def load_timecodes(self, video_id: int) -> None:
        """Загрузка таймкодов для выбранного видео"""
        self.timecodes = self.api_request(f"timecodes/{video_id}/") or []
        self.update_listbox(self.timecode_listbox, [
            f"{timecode['prediction']} - {str(datetime.timedelta(seconds=timecode['time_in_seconds']))}"
            for timecode in self.timecodes
        ])

    def update_listbox(self, listbox: tk.Listbox, items: List[str]) -> None:
        """Обновление содержимого listbox"""
        listbox.delete(0, tk.END)
        for item in items:
            listbox.insert(tk.END, item)

    def select_original_video(self, event: tk.Event) -> None:
        """Выбор видео из списка и загрузка"""
        selected_index = self.original_video_listbox.curselection()
        if selected_index:
            selected_video = self.original_video_list[selected_index[0]]
            if selected_video["id"] != self.selected_original_video_id:
                self.selected_original_video_id = selected_video["id"]
                self.load_proceed_videos(selected_video["id"])

    def select_proceed_video(self, event: tk.Event) -> None:
        selected_index = self.proceed_video_listbox.curselection()
        if selected_index:
            selected_video = self.proceed_video_list[selected_index[0]]
            if selected_video["id"] != self.selected_proceed_video_id:
                self.selected_pdf_url = selected_video["pdf_file"]
                self.selected_excel_url = selected_video["excel_file"]
                self.selected_proceed_video_id = selected_video["id"]
                self.download_video(selected_video["id"])

    def download_video(self, video_id: int) -> None:
        """Загрузка видеофайла с сервера"""
        self.playing = False
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        threading.Thread(target=self._download_video_thread, args=(video_id,)).start()

    def download_pdf(self) -> None:
        """Download PDF file for the selected proceed video."""
        if self.selected_proceed_video_id:
            threading.Thread(target=self._download_file_thread,
                             args=(self.selected_pdf_url, self.selected_proceed_video_id, 'pdf')).start()
        else:
            messagebox.showwarning("Видео не выбрано", "Выберите видео!.")

    def download_excel(self) -> None:
        """Download Excel file for the selected proceed video."""
        if self.selected_proceed_video_id:
            threading.Thread(target=self._download_file_thread,
                             args=(self.selected_excel_url, self.selected_proceed_video_id, 'excel')).start()
        else:
            messagebox.showwarning("Видео не выбрано", "Выберите видео!")

    def _download_file_thread(self, url: str, file_type: str) -> None:
        try:
            file_extension = 'pdf' if file_type == 'pdf' else 'xlsx'
            file_name = filedialog.asksaveasfilename(defaultextension=f".{file_extension}",
                                                     filetypes=[(f"{file_type.upper()} files", f"*.{file_extension}")])
            if not file_name:
                return  # User cancelled the save dialog

            response = requests.get(f'{self.media_url}{url}', stream=True)
            response.raise_for_status()
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
            messagebox.showinfo("Успешно", f"The {file_type.upper()} загружен успешно!")
            os.startfile(file_name)
        except Exception as error:
            print(error)

    def _download_video_thread(self, video_id: int) -> None:
        try:
            with open(self.temp_file.name, 'wb') as f:
                response = requests.get(f'{self.api_url}/proceed-videos/{video_id}/download/', stream=True)
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
            self.load_video(self.temp_file.name)
            self.load_timecodes(video_id)
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Ошибка в загрузке файла: {e}")

    def load_video(self, file_path: str) -> None:
        """Загрузка видео в плеер"""
        # Проверка на инициализацию объекта vid_player
        if self.vid_player is None:
            messagebox.showerror("Error", "Видеоплеер не запущен.")
            return

        self.vid_player.load(file_path)
        self.progress_slider.config(to=0, from_=0)
        self.play_pause_btn["text"] = "Play"
        self.progress_value.set(0)
        self.play_video()

    def upload_video(self):
        """Prompt user for video details and upload video to the server."""
        title = tk.simpledialog.askstring("Название видео", "Введите название видео:")
        if not title:
            messagebox.showwarning("Выгрузка отменена", "Название не может быть пустым.")
            return

        filepath = tk.filedialog.askopenfilename(title="Выберите видеофайл",
                                                 filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
        if not filepath:
            messagebox.showwarning("Выгрузка отменена", "Нет файла.")
            return

        files = {'video': open(filepath, 'rb')}
        data = {'title': title}
        try:
            response = requests.post(f"{self.api_url}/videos/", files=files, data=data)
            response.raise_for_status()
            messagebox.showinfo("Успешно", "Видео успешно выгружено!")
        except requests.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")

    def select_timecode(self, event: tk.Event) -> None:
        """Выбор таймкода из списка"""
        selected_index = self.timecode_listbox.curselection()
        if selected_index:
            selected_time = self.timecodes[selected_index[0]]['time_in_seconds']
            self.seek(selected_time)

    def play_video(self) -> None:
        """Воспроизведение видео"""
        self.vid_player.play()
        self.play_pause_btn["text"] = "Pause"

    def pause_video(self) -> None:
        """Пауза видео"""
        self.vid_player.pause()
        self.play_pause_btn["text"] = "Play"

    def play_pause(self) -> None:
        """Переключение между воспроизведением и паузой"""
        if self.vid_player.is_paused():
            self.play_video()
        else:
            self.pause_video()

    def seek(self, value: Any) -> None:
        """Перемотка видео на заданную позицию"""
        self.vid_player.seek(int(float(value)))

    def skip(self, value: int) -> None:
        """Перемотка видео вперед или назад на заданное количество секунд"""
        self.vid_player.seek(int(self.progress_slider.get()) + value)
        self.progress_value.set(self.progress_slider.get() + value)

    def update_duration(self, event: tk.Event) -> None:
        """Обновление продолжительности видео"""
        duration = self.vid_player.video_info()["duration"]
        self.end_time["text"] = str(datetime.timedelta(seconds=duration))
        self.progress_slider["to"] = duration

    def update_scale(self, event: tk.Event) -> None:
        """Обновление текущей позиции видео на слайдере"""
        current_time = self.vid_player.current_duration()
        self.progress_value.set(current_time)
        self.start_time["text"] = str(datetime.timedelta(seconds=current_time))

    def video_ended(self, event: tk.Event) -> None:
        """Обработка окончания видео"""
        self.progress_slider.set(self.progress_slider["to"])
        self.play_pause_btn["text"] = "Play"
        self.progress_slider.set(0)
