import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from tkVideoPlayer import TkinterVideo
import requests
import tempfile
import threading
import json

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

        self.load_video_btn = tk.Button(control_frame, text="Load Video", command=self.load_video)
        self.load_video_btn.pack(side="left")

        self.load_timecodes_btn = tk.Button(control_frame, text="Load Timecodes", command=self.load_timecodes)
        self.load_timecodes_btn.pack(side="left")

        self.play_pause_btn = tk.Button(control_frame, text="Play", command=self.play_pause)
        self.play_pause_btn.pack(side="left")

        self.skip_minus_5sec = tk.Button(control_frame, text="Skip -5 sec", command=lambda: self.skip(-5))
        self.skip_minus_5sec.pack(side="left")

        self.start_time = tk.Label(control_frame, text=str(datetime.timedelta(seconds=0)))
        self.start_time.pack(side="left")

        self.progress_value = tk.IntVar(self)
        self.progress_slider = tk.Scale(control_frame, variable=self.progress_value, from_=0, to=0, orient="horizontal", command=self.seek)
        self.progress_slider.pack(side="left", fill="x", expand=True)

        self.end_time = tk.Label(control_frame, text=str(datetime.timedelta(seconds=0)))
        self.end_time.pack(side="left")

        self.skip_plus_5sec = tk.Button(control_frame, text="Skip +5 sec", command=lambda: self.skip(5))
        self.skip_plus_5sec.pack(side="left")

        self.timecode_listbox = tk.Listbox(self)
        self.timecode_listbox.pack(side="left", fill="y")
        self.timecode_listbox.bind('<<ListboxSelect>>', self.select_timecode)

        # Привязка событий
        self.vid_player.bind("<<Duration>>", self.update_duration)
        self.vid_player.bind("<<SecondChanged>>", self.update_scale)
        self.vid_player.bind("<<Ended>>", self.video_ended)

        self.playing = False
        self.temp_file = None
        self.timecodes = []

    def load_video(self):
        """ Загрузка видеофайла """
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
        if file_path:
            self.vid_player.load(file_path)
            self.progress_slider.config(to=0, from_=0)
            self.play_pause_btn["text"] = "Play"
            self.progress_value.set(0)
            self.play_video()

    def load_timecodes(self):
        """ Загрузка файла с таймкодами """
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                self.timecodes = json.load(f)
            self.update_timecode_listbox()

    def update_timecode_listbox(self):
        """ Обновление списка таймкодов в Listbox """
        self.timecode_listbox.delete(0, tk.END)
        for timecode in self.timecodes:
            self.timecode_listbox.insert(tk.END, f"{timecode['label']} - {str(datetime.timedelta(seconds=timecode['time']))}")

    def select_timecode(self, event):
        """ Выбор таймкода из списка """
        selected_index = self.timecode_listbox.curselection()
        if selected_index:
            selected_time = self.timecodes[selected_index[0]]['time']
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
