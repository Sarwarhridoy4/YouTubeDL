import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QProgressBar, QComboBox, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from yt_dlp import YoutubeDL, DownloadError


class DownloadThread(QThread):
    progress = pyqtSignal(int)
    completed = pyqtSignal(bool)  # Emits True for success, False for failure

    def __init__(self, url, format, destination):
        super().__init__()
        self.url = url
        self.format = format
        self.destination = destination

    def run(self):
        ydl_opts = {
            'format': self.format,
            'outtmpl': os.path.join(self.destination, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook]
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.completed.emit(True)  # Success
        except DownloadError:
            self.completed.emit(False)  # Error

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            progress_percent = d.get('downloaded_bytes', 0) * 100 / d.get('total_bytes', 1)
            self.progress.emit(int(progress_percent))

        if d['status'] == 'finished':
            self.completed.emit(True)


class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Basic window setup
        self.setWindowTitle('YouTube Video Downloader')
        self.setGeometry(200, 200, 500, 250)

        layout = QVBoxLayout()

        # Video URL input
        self.url_label = QLabel('Video URL:')
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText('Enter YouTube video URL here...')

        # Video Quality selection
        self.height_label = QLabel('Select Video Quality:')
        self.height_combo = QComboBox(self)
        self.height_combo.addItems(['720', '1080', '1440', '2160'])

        # Destination Folder selection
        self.dest_button = QPushButton('Select Destination Folder', self)
        self.dest_button.clicked.connect(self.select_folder)
        self.destination_label = QLabel('No folder selected')

        # Download button
        self.download_button = QPushButton('Download', self)
        self.download_button.clicked.connect(self.start_download)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        # Adding widgets to the layout
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.height_label)
        layout.addWidget(self.height_combo)
        layout.addWidget(self.dest_button)
        layout.addWidget(self.destination_label)
        layout.addWidget(self.download_button)
        layout.addWidget(self.progress_bar)

        # Adding padding and spacing
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.setLayout(layout)

        # Adding modern styling using stylesheets
        self.setStyleSheet("""
            QWidget {
                background-color: #2C3E50;
                color: white;
                font-family: Roboto, Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #34495E;
                background-color: #34495E;
                color: white;
            }
            QPushButton {
                padding: 10px;
                background-color: #1ABC9C;
                border-radius: 5px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #16A085;
            }
            QComboBox {
                padding: 10px;
                border-radius: 5px;
                background-color: #34495E;
                color: white;
            }
            QProgressBar {
                height: 20px;
                border-radius: 10px;
                background-color: #95A5A6;
            }
            QProgressBar::chunk {
                background-color: #1ABC9C;
                border-radius: 10px;
            }
        """)

        self.destination_folder = None
        self.show()

    def select_folder(self):
        self.destination_folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.destination_label.setText(self.destination_folder if self.destination_folder else 'No folder selected')

    def start_download(self):
        if not self.destination_folder:
            self.destination_label.setText('Please select a folder!')
            return

        url = self.url_input.text()
        if not url:
            self.url_label.setText('Please enter a video URL!')
            return

        height = self.height_combo.currentText()
        format_option = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'

        self.thread = DownloadThread(url, format_option, self.destination_folder)
        self.thread.progress.connect(self.update_progress)
        self.thread.completed.connect(self.download_completed)
        self.thread.start()

    def update_progress(self, percent):
        self.progress_bar.setValue(percent)

    def download_completed(self, success):
        if success:
            self.show_message_box('Download Complete', 'The video has been downloaded successfully!')
        else:
            self.show_message_box('Download Error', 'An error occurred during the download process.')

    def show_message_box(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information if title == 'Download Complete' else QMessageBox.Critical)
        msg_box.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DownloaderApp()
    sys.exit(app.exec_())
