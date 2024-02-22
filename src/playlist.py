# coding:utf-8
import subprocess
import sys
import random

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QMessageBox, \
    QListWidgetItem, QLabel
from qfluentwidgets import (SearchLineEdit, PushButton, ListWidget, MessageBox)
from spotdl import __main__ as spotdl


class DownloaderThread(QThread):
    progress_update = Signal(int)
    finished = Signal(str)

    def __init__(self, spotifylink, list_item):
        super().__init__()
        self.spotifylink = spotifylink
        self.list_item = list_item

    def run(self):
        try:
            process = subprocess.Popen([sys.executable, spotdl.__file__, self.spotifylink], stdout=subprocess.PIPE,
                                       universal_newlines=True)
            while True:
                output = process.stdout.readline().strip()
                if output == '' and process.poll() is not None:
                    break
                if output.startswith('[download]'):
                    try:
                        percent = int(output.split()[1][:-1])
                        self.progress_update.emit(percent)
                    except (IndexError, ValueError) as e:
                        print("Error:", e)  # Add this line for debugging
                        pass
            self.finished.emit("Download Completed!")
            self.list_item.setText(f"{self.spotifylink} - Downloaded")  # Update list item text
        except subprocess.CalledProcessError as e:
            print("Error:", e)  # Add this line for debugging
            self.finished.emit("Download Failed!")


class Playlist(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.hBoxLayout)
        self.setObjectName("Playlist")

        self.searchBox = SearchLineEdit(self)
        self.searchBox.setPlaceholderText("Enter Spotify Playlist URL")
        self.hBoxLayout.addWidget(self.searchBox, 8, Qt.AlignmentFlag.AlignTop)

        # Add QLabel for GIF
        self.loading_label = QLabel(self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setVisible(False)  # Initially hide the loading label
        self.mainLayout.addWidget(self.loading_label)

        self.download_button = PushButton(self)
        self.download_button.setText("Download Playlist")
        self.download_button.clicked.connect(self.start_download)
        self.hBoxLayout.addWidget(self.download_button, 1, Qt.AlignmentFlag.AlignTop)

        self.music_list = ListWidget(self)

        def get_gif():
            gifs = ["loading.gif", "loading_1.gif", "loading_2.gif"]
            gif = random.choice(gifs)
            gif_path = "resource/misc/" + gif
            return gif_path

        # Load the GIF
        self.movie = QMovie(get_gif())
        self.loading_label.setMovie(self.movie)
        self.movie.start()

        self.mainLayout.addWidget(self.music_list)

        self.downloader_thread = None  # Initialize downloader thread

    def start_download(self):
        spotifylink = self.searchBox.text()
        if "track" in spotifylink:
            w = MessageBox(
                "You're in the wrong tab bud.",
                "You're trying to download Tracks in 'Playlist' tab. Head over to the Songs tab and download Playlists at ease!",
                self
            )
            w.cancelButton.setText("No worries bud!")

            if w.exec():
                pass

        elif "artist" in spotifylink:
            w = MessageBox(
                "You're in the wrong tab bud.",
                "You're trying to download Artist in 'Songs' tab. Head over to the Artist tab and download all songs from an Artist at ease!",
                self
            )

            w.cancelButton.setText("No worries bud!")

            if w.exec():
                pass
        else:
            self.loading_label.setVisible(True)  # Show the loading label
            list_item = QListWidgetItem(spotifylink)  # Create list item
            self.music_list.addItem(list_item)  # Add list item to list
            self.downloader_thread = DownloaderThread(spotifylink, list_item)
            self.downloader_thread.finished.connect(self.finish_download)
            self.downloader_thread.start()

    def finish_download(self, message):
        w = MessageBox(
            'Yayyy🥰',
            'Your Playlist has been successfully downloaded. Enjoy!',
            self
        )

        w.cancelButton.setText("Let's goooo")

        if w.exec():
            pass
