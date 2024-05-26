import datetime
import tkinter as tk
from tkinter import messagebox
from tkVideoPlayer import TkinterVideo
import requests
import tempfile
import threading


class VideoPlayerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Video Player")
        self.geometry("800x600")

        # Создание виджета для отображения видео
        self.vid_player = TkinterVideo(scaled=True, master=self)
        self.vid_player.pack(expand=True, fill="both")

        # Добавление кнопок управления
        control_frame = tk.Frame(self)
        control_frame.pack(fill="x")

        self.load_videos_btn = tk.Button(control_frame, text="Load Videos", command=self.load_original_videos)
        self.load_videos_btn.pack(side="left")

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
        self.original_video_list = []
        self.proceed_video_list = []
        self.timecodes = []

    def load_original_videos(self):
        """ Загрузка списка оригинальных видео с сервера """
        try:
            response = requests.get("http://localhost:8000/api/videos/")
            response.raise_for_status()
            self.original_video_list = response.json()
            self.update_original_video_listbox()
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to load video list: {e}")

    def load_proceed_videos(self, original_video_id):
        """ Загрузка списка оригинальных видео с сервера """
        try:
            response = requests.get(f"http://localhost:8000/api/proceed-videos/{original_video_id}/")
            response.raise_for_status()
            self.proceed_video_list = response.json()
            print(self.proceed_video_list)
            print(self.original_video_list)
            self.update_proceed_video_listbox()
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to load video list: {e}")

    def update_proceed_video_listbox(self):
        """ Обновление списка видео в Listbox """
        self.proceed_video_listbox.delete(0, tk.END)
        for video in self.proceed_video_list:
            self.proceed_video_listbox.insert(tk.END, video["title"])

    def update_original_video_listbox(self):
        """ Обновление списка видео в Listbox """
        self.original_video_listbox.delete(0, tk.END)
        for video in self.original_video_list:
            self.original_video_listbox.insert(tk.END, video["title"])

    def select_original_video(self, event):
        """ Выбор видео из списка и загрузка """
        selected_index = self.original_video_listbox.curselection()
        if selected_index:
            selected_video = self.original_video_list[selected_index[0]]
            self.load_proceed_videos(selected_video["id"])

    def select_proceed_video(self, event):
        selected_index = self.proceed_video_listbox.curselection()
        if selected_index:
            selected_video = self.proceed_video_list[selected_index[0]]
            self.download_video(selected_video["id"])

    def download_video(self, video_id):
        """ Загрузка видеофайла с сервера """
        self.playing = False
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        threading.Thread(target=self._download_video_thread, args=(video_id,)).start()

    def _download_video_thread(self, video_id):
        try:
            with open(self.temp_file.name, 'wb') as f:
                response = requests.get(f'http://localhost:8000/api/proceed-videos/{video_id}/download/', stream=True)
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
            self.load_video(self.temp_file.name)
            self.load_timecodes(video_id)
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to download video: {e}")

    def load_video(self, file_path):
        """ Загрузка видео в плеер """
        self.vid_player.load(file_path)
        self.progress_slider.config(to=0, from_=0)
        self.play_pause_btn["text"] = "Play"
        self.progress_value.set(0)
        self.play_video()

    def load_timecodes(self, video_id):
        """ Загрузка таймкодов для выбранного видео """
        try:
            response = requests.get(f"http://localhost:8000/api/timecodes/{video_id}/")
            response.raise_for_status()
            self.timecodes = response.json()
            self.update_timecode_listbox()
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to load timecodes: {e}")

    def update_timecode_listbox(self):
        """ Обновление списка таймкодов в Listbox """
        self.timecode_listbox.delete(0, tk.END)
        for timecode in self.timecodes:
            self.timecode_listbox.insert(tk.END,
                                         f"{timecode['prediction']} - {str(datetime.timedelta(seconds=timecode['time_in_seconds']))}")

    def select_timecode(self, event):
        """ Выбор таймкода из списка """
        selected_index = self.timecode_listbox.curselection()
        if selected_index:
            selected_time = self.timecodes[selected_index[0]]['time_in_seconds']
            self.seek(selected_time)

    def play_video(self):
        """ Воспроизведение видео """
        self.vid_player.play()
        self.play_pause_btn["text"] = "Pause"

    def pause_video(self):
        """ Пауза видео """
        self.vid_player.pause()
        self.play_pause_btn["text"] = "Play"

    def play_pause(self):
        """ Переключение между воспроизведением и паузой """
        if self.vid_player.is_paused():
            self.play_video()
        else:
            self.pause_video()

    def seek(self, value):
        """ Перемотка видео на заданную позицию """
        self.vid_player.seek(int(float(value)))

    def skip(self, value):
        """ Перемотка видео вперед или назад на заданное количество секунд """
        self.vid_player.seek(int(self.progress_slider.get()) + value)
        self.progress_value.set(self.progress_slider.get() + value)

    def update_duration(self, event):
        """ Обновление продолжительности видео """
        duration = self.vid_player.video_info()["duration"]
        self.end_time["text"] = str(datetime.timedelta(seconds=duration))
        self.progress_slider["to"] = duration

    def update_scale(self, event):
        """ Обновление текущей позиции видео на слайдере """
        current_time = self.vid_player.current_duration()
        self.progress_value.set(current_time)
        self.start_time["text"] = str(datetime.timedelta(seconds=current_time))

    def video_ended(self, event):
        """ Обработка окончания видео """
        self.progress_slider.set(self.progress_slider["to"])
        self.play_pause_btn["text"] = "Play"
        self.progress_slider.set(0)


if __name__ == "__main__":
    app = VideoPlayerApp()
    app.mainloop()
