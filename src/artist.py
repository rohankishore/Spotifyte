# coding:utf-8
import subprocess
import sys
import random

from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, \
    QListWidgetItem, QLabel, QFileDialog
from qfluentwidgets import (SearchLineEdit, PushButton, ListWidget, MessageBox)


class DownloaderThread(QThread):
    progress_update = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, spotifylink, list_item, custom_directory):
        super().__init__()
        self.spotifylink = spotifylink
        self.list_item = list_item
        self.custom_directory = custom_directory

    def run(self):
        try:
            # Adjust the spotdl command to include the custom directory
            process = subprocess.Popen([
                sys.executable,
                "-m", "spotdl",
                self.spotifylink,
                '--output', self.custom_directory
            ], stdout=subprocess.PIPE, universal_newlines=True)

            # Communicate progress or handle stdout as needed
            for line in process.stdout:
                # Process stdout, update progress, etc.
                pass

            # Wait for the process to finish and get the return code
            return_code = process.wait()

            # Emit appropriate signal based on the return code
            if return_code == 0:
                self.finished.emit("Download Completed!")
            else:
                self.finished.emit("Download Failed!")

        except Exception as e:
            print("Error:", e)  # Print the error for debugging
            self.finished.emit("Download Failed!")

class Artist(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.hBoxLayout)
        self.setObjectName("Artist")

        # Add QLabel for GIF
        self.loading_label = QLabel(self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setVisible(False)  # Initially hide the loading label
        self.mainLayout.addWidget(self.loading_label)

        self.searchBox = SearchLineEdit(self)
        self.searchBox.setPlaceholderText("Enter Spotify Artist URL")
        self.hBoxLayout.addWidget(self.searchBox, 8, Qt.AlignmentFlag.AlignTop)

        self.download_button = PushButton(self)
        self.download_button.setText("Download All Songs from the Artist")
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
        if "playlist" in spotifylink:
            w = MessageBox(
                "You're in the wrong tab bud.",
                "You're trying to download Playlist in 'Songs' tab. Head over to the Playlist tab and download Playlists at ease!",
                self
            )
            w.cancelButton.setText("No worries bud!")

            if w.exec():
                pass

        elif "track" in spotifylink:
            w = MessageBox(
                "You're in the wrong tab bud.",
                "You're trying to download tracks in 'Artists' tab. Head over to the Songs tab and download all songs from an Artist at ease!",
                self
            )

            w.cancelButton.setText("No worries bud!")

            if w.exec():
                pass
        else:
            custom_directory = QFileDialog.getExistingDirectory(self, "Select Directory", "/")
            self.loading_label.setVisible(True)  # Show the loading label
            list_item = QListWidgetItem(spotifylink)  # Create list item
            self.music_list.addItem(list_item)  # Add list item to list
            self.downloader_thread = DownloaderThread(spotifylink, list_item, custom_directory)
            self.downloader_thread.finished.connect(self.finish_download)
            self.downloader_thread.start()

    def finish_download(self, message):
        w = MessageBox(
            'Yayyy🥰',
            'All songs from the given artist has been successfully downloaded. Enjoy!',
            self
        )

        w.cancelButton.setText("Let's goooo")

        if w.exec():
            pass
