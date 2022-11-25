from pathlib import Path
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QAction, QFileSystemModel, QCursor
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QTextEdit, QMenuBar, QFileDialog, QMessageBox, \
    QTabWidget, QHBoxLayout, QTreeView, QMenu, QFrame

import sys


class EditWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.text_input = QTextEdit()

    def set_text(self, data):
        self.text_input.setText(data)

    def change_style(self, style):
        match style:
            case 'Dark':
                self.setStyleSheet("background-color: #303030; color: #fff")
            case 'Light':
                self.setStyleSheet("background-color: #f2f2f2; color: #000 ")


class PandaPad(QWidget):
    def __init__(self):
        super().__init__()
        self.dragPos = None
        self.new_editor = None

        self.setAutoFillBackground(True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: #424242; color: #fff; border: 50px;")
        self.new_editor_list = []
        self.default_style = 'Dark'
        self.setMinimumSize(900, 600)

        self.setWindowTitle("PandaPad")

        self.home_dir = str(Path.home())

        self.frame = QFrame()
        self.frame.setStyleSheet("background-color: #ff9494; color: #fff; ")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.frame)

        self.v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()

        self.setLayout(self.main_layout)

        menubar = QMenuBar(self)
        self.managebar = QMenuBar(self)

        file_new = QAction("New", self)
        file_new.setShortcut('Ctrl+N')
        file_new.triggered.connect(self.create_new_tab)

        file_open = QAction("Open", self)
        file_open.setShortcut('Ctrl+O')
        file_open.triggered.connect(self.open_dialog)

        file_save = QAction("Save", self)
        file_save.setShortcut('Ctrl+S')
        file_save.triggered.connect(self.save_as_text)

        pad_exit = QAction("Exit", self)
        pad_exit.triggered.connect(lambda: self.close())

        pad_dark_style = QAction("Dark", self)
        pad_dark_style.triggered.connect(lambda: self.change_style("Dark"))

        pad_light_style = QAction("Light", self)
        pad_light_style.triggered.connect(lambda: self.change_style("Light"))

        pad_ru_lang = QAction("RU", self)
        pad_ru_lang.triggered.connect(lambda: self.change_style("Dark"))

        pad_en_lang = QAction("EN", self)
        pad_en_lang.triggered.connect(lambda: self.change_style("Dark"))

        about_menu = QAction("About", self)
        about_menu.triggered.connect(self.show_about)

        enable_file_browser = QAction("Enable File browser", self)
        enable_file_browser.triggered.connect(self.enable_file_browser)
        enable_file_browser.setShortcut('Ctrl+Q')

        file_menu = menubar.addMenu('&File')

        file_menu.addAction(file_new)
        file_menu.addAction(file_open)
        file_menu.addAction(file_save)
        file_menu.addAction(pad_exit)

        view = menubar.addMenu('&View')

        style = view.addMenu('Style')
        style.addAction(pad_dark_style)
        style.addAction(pad_light_style)

        lang = view.addMenu('Lang')
        lang.addAction(pad_ru_lang)
        lang.addAction(pad_en_lang)

        view.addAction(enable_file_browser)

        q = menubar.addMenu('&?')
        q.addAction(about_menu)

        collapse_button = self.managebar.addAction("🗕")
        collapse_button.triggered.connect(lambda: self.showMinimized())

        self.expand_pic = "🗖"

        self.expand_button = self.managebar.addAction(self.expand_pic)
        self.expand_button.triggered.connect(lambda: self.expand_widget(self.expand_pic))

        close_button = self.managebar.addAction("🗙")
        close_button.triggered.connect(lambda: self.close())

        self.editor = EditWidget()
        self.editor.change_style(self.default_style)
        self.file_browser_enable = False
        self.file_tree = QTreeView(self)
        self.file_tree.hide()
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.model = QFileSystemModel()

        self.tab = QTabWidget(self)
        self.count = 1
        self.tab.addTab(self.editor, f"New text {self.count}")
        self.index = 1
        self.tab.setTabsClosable(True)
        self.tab.setCurrentIndex(self.index)
        self.tab.tabCloseRequested.connect(self.close_tab)
        self.menu_layout = QHBoxLayout()

        self.v_layout.addLayout(self.menu_layout)
        self.menu_layout.addWidget(menubar)
        self.menu_layout.addWidget(self.managebar, alignment=Qt.AlignmentFlag.AlignRight)
        self.h_layout.addWidget(self.tab)
        self.main_layout.addLayout(self.v_layout)
        self.main_layout.addLayout(self.h_layout)

    def expand_widget(self, pic):
        match pic:
            case "🗖":
                self.showMaximized()
                self.expand_pic = "🗗"
            case "🗗":
                self.resize(900, 600)
                self.expand_pic = "🗖"

    def close_tab(self):
        if self.count >= 1:
            self.tab.removeTab(self.tab.currentIndex())
            self.count -= 1

    def create_new_tab(self):
        self.count += 1
        self.new_editor = EditWidget()
        self.index = self.tab.addTab(self.new_editor, f"New Text {self.count}")
        self.tab.setCurrentIndex(self.index)
        if self.default_style == 'Dark':
            self.new_editor.change_style('Dark')
        else:
            self.new_editor.change_style('Light')
        self.new_editor_list.append(self.new_editor)

    def save_as_text(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')
        file_name = name[0].split('/')[-1]

        if name[0]:
            f = open(name[0], 'w')
            with f:
                f.writelines(i for i in self.tab.currentWidget().text_input.toPlainText())
                self.tab.setTabText(self.tab.indexOf(self.tab.currentWidget()), file_name)

    def open_dialog(self):
        name = QFileDialog.getOpenFileName(self, 'Open file', self.home_dir)
        file_name = name[0].split('/')[-1]
        if name[0]:
            f = open(name[0], 'r')
            with f:
                data = f.read()
                self.new_editor.set_text(data)
                self.tab.setTabText(self.tab.indexOf(self.tab.currentWidget()), file_name)

    def change_style(self, style):
        match style:
            case 'Dark':
                self.setStyleSheet("background-color: #424242; color: #fff")
                self.editor.change_style(style)
                for i in self.new_editor_list:
                    i.change_style(style)
                self.default_style = 'Dark'
            case 'Light':
                self.setStyleSheet("background-color: #bfbfbf; color: #000")
                self.editor.change_style(style)
                for i in self.new_editor_list:
                    i.change_style(style)
                self.default_style = 'Light'

    def show_about(self):
        about = QMessageBox(self)
        about.setWindowTitle("About app PandaPad")
        about.setText(f"\nVer: PandaPad v0.0.1\n"
                      f"\nInfo: PandaPad it's simple text editor for Linux Desktop\n"
                      f"\nAuthor: Slavakamrad")
        about.exec()

    def enable_file_browser(self):
        if not self.file_browser_enable:
            self.file_tree.show()
            self.model.setRootPath(QDir.rootPath())
            self.file_tree.customContextMenuRequested.connect(self.context_menu)
            self.file_tree.setModel(self.model)
            self.file_tree.setRootIndex(self.model.index(self.home_dir))
            self.h_layout.addWidget(self.file_tree, alignment=Qt.AlignmentFlag.AlignRight)
            self.file_browser_enable = True
        else:
            self.file_tree.close()
            self.file_browser_enable = False

    def context_menu(self):
        menu = QMenu()
        file_open = menu.addAction("Open")
        file_open.triggered.connect(self.open_tree_file)
        cursor = QCursor()
        menu.exec(cursor.pos())

    def open_tree_file(self):
        index = self.file_tree.currentIndex()
        file_name = self.model.fileName(index)
        f = open(file_name, 'r')
        with f:
            data = f.read()
            self.create_new_tab()
            self.new_editor.set_text(data)
            self.tab.setTabText(self.tab.indexOf(self.tab.currentWidget()), file_name)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        self.move(event.globalPosition().toPoint() - self.dragPos)


app = QApplication(sys.argv)

window = PandaPad()
window.show()

app.exec()
