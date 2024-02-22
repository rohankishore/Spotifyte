# coding:utf-8
import subprocess
import sys
from spotdl import __main__ as spotdl
from PySide6.QtCore import Qt, Signal, QEasingCurve, QUrl, QThread
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QApplication, QFrame, QWidget, QListWidgetItem
from qfluentwidgets import (NavigationBar, NavigationItemPosition, MessageBox,
                            isDarkTheme, setTheme, Theme,
                            PopUpAniStackedWidget, ListWidget, PushButton, SearchLineEdit)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, TitleBar

import artist
import playlist
from song import Song


class Widget(QWidget):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.mainLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.hBoxLayout)

        self.searchBox = SearchLineEdit(self)
        self.searchBox.setPlaceholderText("Enter Spotify Playlist URL")
        self.hBoxLayout.addWidget(self.searchBox, 8, Qt.AlignmentFlag.AlignTop)

        self.download_button = PushButton(self)
        self.download_button.setText("Download Playlist")
        self.download_button.clicked.connect(self.start_download)
        self.hBoxLayout.addWidget(self.download_button, 1, Qt.AlignmentFlag.AlignTop)

        self.music_list = ListWidget(self)

        self.mainLayout.addWidget(self.music_list)

    def start_download(self):
        spotifylink = self.searchBox.text()
        print(spotifylink)
        list_item = QListWidgetItem(spotifylink)  # Create list item
        self.music_list.addItem(list_item)  # Add list item to list
        self.downloader_thread = DownloaderThread(spotifylink, list_item)
        self.downloader_thread.finished.connect(self.finish_download)
        self.downloader_thread.start()

    def finish_download(self, message):
        w = MessageBox(
            'Yayyy🥰',
            'Your Track has been successfully downloaded. Enjoy!',
            self
        )

        w.cancelButton.setText("Let's goooo")

        if w.exec():
            pass


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
                print(output)  # Add this line for debugging
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


class StackedWidget(QFrame):
    """ Stacked widget """

    currentChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)

        self.view.currentChanged.connect(self.currentChanged)

    def addWidget(self, widget):
        """ add widget to view """
        self.view.addWidget(widget)

    def widget(self, index: int):
        return self.view.widget(index)

    def setCurrentWidget(self, widget, popOut=False):
        if not popOut:
            self.view.setCurrentWidget(widget, duration=300)
        else:
            self.view.setCurrentWidget(
                widget, True, False, 200, QEasingCurve.InQuad)

    def setCurrentIndex(self, index, popOut=False):
        self.setCurrentWidget(self.view.widget(index), popOut)


class CustomTitleBar(TitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.hBoxLayout.removeWidget(self.minBtn)
        self.hBoxLayout.removeWidget(self.maxBtn)
        self.hBoxLayout.removeWidget(self.closeBtn)

        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(20, 20)
        self.hBoxLayout.insertSpacing(0, 20)
        self.hBoxLayout.insertWidget(
            1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.window().windowIconChanged.connect(self.setIcon)

        # add title label
        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(
            2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.titleLabel.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)

        self.vBoxLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(0)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setAlignment(Qt.AlignTop)
        self.buttonLayout.addWidget(self.minBtn)  # This line adds the minBtn
        self.buttonLayout.addWidget(self.maxBtn)  # This line adds the maxBtn
        self.buttonLayout.addWidget(self.closeBtn)  # This line adds the closeBtn
        self.vBoxLayout.addLayout(self.buttonLayout)
        self.vBoxLayout.addStretch(1)
        self.hBoxLayout.addLayout(self.vBoxLayout, 0)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(20, 20))

    def resizeEvent(self, e):
        pass


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))

        # use dark theme mode
        setTheme(Theme.DARK)

        # change the theme color
        # setThemeColor('#0078d4')

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationBar = NavigationBar(self)
        self.stackWidget = StackedWidget(self)

        # create sub interface
        self.songInterface = Song(self)
        self.playlistInterface = playlist.Playlist(self)
        self.artistInterface = artist.Artist(self)
        self.libraryInterface = Widget('library Interface', self)

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.hBoxLayout.addWidget(self.navigationBar)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.songInterface, FIF.MUSIC, 'Songs', selectedIcon=FIF.MUSIC)
        self.addSubInterface(self.playlistInterface, FIF.MUSIC_FOLDER, 'Playlists', selectedIcon=FIF.MUSIC_FOLDER)
        self.addSubInterface(self.artistInterface, FIF.PEOPLE, 'Artists', selectedIcon=FIF.PEOPLE)
        self.addSubInterface(self.libraryInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM,
                             FIF.SETTING)
        self.navigationBar.addItem(
            routeKey='About',
            icon=FIF.HELP,
            text='About',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationBar.setCurrentItem(self.songInterface.objectName())

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon('resource/icons/icon.png'))
        self.setWindowTitle('Spotifyte')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, selectedIcon=None):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationBar.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            selectedIcon=selectedIcon,
            position=position,
        )

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationBar.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        text_for_about = "Heya! it's Rohan, the creator of Spotifyte. I hope you've enjoyed using this app as much as I enjoyed making it." + "" + "\n" + "\n" \
                                                                                                                                                          "I'm a school student and I can't earn my own money LEGALLY. So any donations will be largely appreciated. Also, if you find any bugs / have any feature requests, you can open a Issue/ Pull Request in the Repo." \
                                                                                                                                                          "You can visit GitHub by pressing the button below. You can find Ko-Fi link there :) " + "\n" + "\n" + \
                         "Once again, thank you for using Spotifyte. Please consider giving it a star ⭐ as it will largely motivate me to create more of such apps. Also do consider giving me a follow ;) "
        w = MessageBox(
            'Spotifyte',
            text_for_about,
            self
        )
        w.yesButton.setText('GitHub')
        w.cancelButton.setText('Return')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://github.com/rohankishore/Spotifyte"))


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # ----- DEPRECIATED ------ #

    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # ----- DEPRECIATED ------ #

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()
