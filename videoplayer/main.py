from server.videoplayer import VideoPlayerApp as serverVideoPlayer
from client.videoplayer import VideoPlayerApp as clientVideoPlayer
import tkinter as tk


class SelectPlayerType(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VideoPlayer")
        self.geometry("300x150")

        tk.Label(self, text="Выберите способ обработки:").pack(pady=10)

        tk.Button(self, text="Обработка через сервер", command=lambda: self.launch_player("server")).pack(
            fill="x")

        tk.Button(self, text="Обработка через клиент", command=lambda: self.launch_player("client")).pack(
            fill="x")

    def launch_player(self, player_type):
        self.destroy()
        if player_type == "server":
            app = serverVideoPlayer()
        elif player_type == "client":
            app = clientVideoPlayer()
        else:
            raise Exception()
        app.mainloop()


if __name__ == "__main__":
    app = SelectPlayerType()
    app.mainloop()
