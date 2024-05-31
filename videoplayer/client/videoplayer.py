import tkinter as tk
from tkinter import filedialog, messagebox
from tkVideoPlayer import TkinterVideo


class VideoPlayerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Video Player")
        self.geometry("800x600")

        # Video player setup
        self.vid_player = TkinterVideo(master=self, scaled=True)
        self.vid_player.pack(expand=True, fill="both")

        # Control panel
        control_frame = tk.Frame(self)
        control_frame.pack(fill="x")

        self.upload_video_btn = tk.Button(control_frame, text="Upload Video", command=self.upload_video)
        self.upload_video_btn.pack(side="left")

    def upload_video(self):
        """Prompt user for video details and upload video to the server."""
        title = tk.simpledialog.askstring("Название видео", "Введите название видео:")
        if not title:
            messagebox.showwarning("Загрузка отменена", "Загрузка отменен(нет названия).")
            return

        file_path = tk.filedialog.askopenfilename(title="Выберите видео",
                                                 filetypes=[("Видеофайлы", "*.mp4 *.avi *.mov *.mkv")])
        if not file_path:
            messagebox.showwarning("Загрузка отменена", "Загрузка отменена (Видеофайлы).")
            return

        self.process_video(title, file_path=file_path)

    def process_video(self, title: str, file_path: str):
        from .с import file
        file = file(file_path=file_path, output_folder="/Users/kirill201/Desktop/Новая папка")
        self.vid_player.load(file)
        self.vid_player.play()


if __name__ == "__main__":
    app = VideoPlayerApp()
    app.mainloop()
