import os
import datetime
import tkinter as tk
from tkinter import messagebox
from tkVideoPlayer import TkinterVideo
import requests
import tempfile
import threading
from typing import List, Dict, Optional, Any


class VideoPlayerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Video Player")
        self.geometry("800x600")

        # Получение URL API из переменной окружения
        self.api_url = os.getenv("API_URL", "http://95.163.223.21/api")

        # Создание виджета для отображения видео
        self.vid_player = TkinterVideo(scaled=True, master=self)
        self.vid_player.pack(expand=True, fill="both")

        # Добавление кнопок управления
        control_frame = tk.Frame(self)
        control_frame.pack(fill="x")

        self.load_videos_btn = tk.Button(control_frame, text="Load Videos", command=self.load_original_videos)
        self.load_videos_btn.pack(side="left")

        self.upload_video_btn = tk.Button(control_frame, text="Upload Video", command=self.upload_video)
        self.upload_video_btn.pack(side="left")

        self.play_pause_btn = tk.Button(control_frame, text="Play", command=self.play_pause)
        self.play_pause_btn.pack(side="left")

        self.skip_minus_5sec = tk.Button(control_frame, text="Skip -5 sec", command=lambda: self.skip(-5))
        self.skip_minus_5sec.pack(side="left")

        self.start_time = tk.Label(control_frame, text=str(datetime.timedelta(seconds=0)))
        self.start_time.pack(side="left")

        self.progress_value = tk.IntVar(self)
        self.progress_slider = tk.Scale(control_frame, variable=self.progress_value, from_=0, to=0, orient="horizontal",
                                        command=self.seek)
        self.progress_slider.pack(side="left", fill="x", expand=True)

        self.end_time = tk.Label(control_frame, text=str(datetime.timedelta(seconds=0)))
        self.end_time.pack(side="left")

        self.skip_plus_5sec = tk.Button(control_frame, text="Skip +5 sec", command=lambda: self.skip(5))
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

    def api_request(self, endpoint: str, method: str = "GET") -> Optional[Any]:
        """Выполнение запроса к API"""
        try:
            url = f"{self.api_url}/{endpoint}"
            response = requests.request(method, url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to make request to {url}: {e}")
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
                self.selected_proceed_video_id = selected_video["id"]
                self.download_video(selected_video["id"])

    def download_video(self, video_id: int) -> None:
        """Загрузка видеофайла с сервера"""
        self.playing = False
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        threading.Thread(target=self._download_video_thread, args=(video_id,)).start()

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
            messagebox.showerror("Error", f"Failed to download video: {e}")

    def load_video(self, file_path: str) -> None:
        """Загрузка видео в плеер"""
        # Проверка на инициализацию объекта vid_player
        if self.vid_player is None:
            messagebox.showerror("Error", "Video player not initialized.")
            return

        self.vid_player.load(file_path)
        self.progress_slider.config(to=0, from_=0)
        self.play_pause_btn["text"] = "Play"
        self.progress_value.set(0)
        self.play_video()

    def upload_video(self):
        """Prompt user for video details and upload video to the server."""
        title = tk.simpledialog.askstring("Video Title", "Enter the title of the video:")
        if not title:
            messagebox.showwarning("Upload Cancelled", "Upload cancelled (no title provided).")
            return

        filepath = tk.filedialog.askopenfilename(title="Select a Video File",
                                              filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
        if not filepath:
            messagebox.showwarning("Upload Cancelled", "Upload cancelled (no file selected).")
            return

        files = {'video': open(filepath, 'rb')}
        data = {'title': title}
        try:
            response = requests.post(f"{self.api_url}/videos/", files=files, data=data)
            response.raise_for_status()
            messagebox.showinfo("Upload Successful", "The video was uploaded successfully!")
        except requests.RequestException as e:
            messagebox.showerror("Upload Failed", f"Failed to upload video: {e}")

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
