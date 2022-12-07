from pathlib import Path
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QAction, QFileSystemModel, QCursor
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QTextEdit, QMenuBar, QFileDialog, QMessageBox, \
    QTabWidget, QHBoxLayout, QTreeView, QMenu
from configparser import ConfigParser
import sys
from lang import ru, en

config = ConfigParser()
config.read('config.ini')


class EditWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.text_input = QTextEdit()

    def set_text(self, data):
        self.setText(data)

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

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        self.new_editor_list = []
        self.default_style = config.get('style', 'COLOR_SCHEME')

        match self.default_style:
            case 'Dark':
                self.setStyleSheet("background-color: #424242; color: #fff")
            case 'Light':
                self.setStyleSheet("background-color: #bfbfbf; color: #000")

        self.default_lang = config.get('lang', 'LANG')
        self.lang_dict = en
        match self.default_lang:
            case 'RU':
                self.lang_dict = ru
            case 'EN':
                self.lang_dict = en

        self.setMinimumSize(900, 600)

        self.setWindowTitle("PandaPad")

        self.home_dir = str(Path.home())

        self.main_layout = QVBoxLayout()

        self.v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()
        self.main_layout.addLayout(self.v_layout)
        self.main_layout.addLayout(self.h_layout)

        self.setLayout(self.main_layout)

        menubar = QMenuBar(self)
        self.managebar = QMenuBar(self)

        file_new = QAction(self.lang_dict['New'], self)
        file_new.setShortcut('Ctrl+N')
        file_new.triggered.connect(self.create_new_tab)

        file_open = QAction(self.lang_dict["Open"], self)
        file_open.setShortcut('Ctrl+O')
        file_open.triggered.connect(self.open_file_dialog)

        file_save_as = QAction(self.lang_dict["Save As"], self)

        file_save_as.triggered.connect(self.save_as_text)

        file_save = QAction(self.lang_dict["Save"], self)
        file_save.setShortcut('Ctrl+S')
        file_save.triggered.connect(self.save_as_text)

        pad_exit = QAction(self.lang_dict["Exit"], self)
        pad_exit.triggered.connect(lambda: self.close())

        pad_dark_style = QAction(self.lang_dict["Dark"], self)
        pad_dark_style.triggered.connect(lambda: self.change_style("Dark"))

        pad_light_style = QAction(self.lang_dict["Light"], self)
        pad_light_style.triggered.connect(lambda: self.change_style("Light"))

        pad_ru_lang = QAction(self.lang_dict["RU"], self)
        pad_ru_lang.triggered.connect(lambda: self.change_lang("RU"))

        pad_en_lang = QAction(self.lang_dict["EN"], self)
        pad_en_lang.triggered.connect(lambda: self.change_lang("EN"))

        about_menu = QAction(self.lang_dict["About"], self)
        about_menu.triggered.connect(self.show_about)

        enable_file_browser = QAction(self.lang_dict["Enable/Disable File browser"], self)
        enable_file_browser.triggered.connect(self.enable_file_browser)
        enable_file_browser.setShortcut('Ctrl+Q')

        file_menu = menubar.addMenu(self.lang_dict['&File'])

        file_menu.addAction(file_new)
        file_menu.addSection('Actions')
        file_menu.addAction(file_open)
        file_menu.addAction(file_save)
        file_menu.addAction(file_save_as)
        file_menu.addSeparator()
        file_menu.addAction(pad_exit)

        view = menubar.addMenu(self.lang_dict['&View'])

        style = view.addMenu(self.lang_dict['Style'])
        style.addAction(pad_dark_style)
        style.addAction(pad_light_style)

        lang = view.addMenu(self.lang_dict['Lang'])
        lang.addAction(pad_ru_lang)
        lang.addAction(pad_en_lang)

        view.addAction(enable_file_browser)

        q = menubar.addMenu('&?')
        q.addAction(about_menu)

        collapse_button = self.managebar.addAction("🗕")
        collapse_button.triggered.connect(lambda: self.showMinimized())

        self.expand = False

        self.expand_button = self.managebar.addAction("🗖")

        self.expand_button.triggered.connect(lambda: self.expand_widget(self.expand))

        close_button = self.managebar.addAction("🗙")
        close_button.triggered.connect(lambda: self.close())

        self.editor = EditWidget()
        self.new_editor_list.append(self.editor)

        self.editor.change_style(self.default_style)
        self.file_browser_enable = False
        self.file_tree = QTreeView()
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
        self.menu_layout.addWidget(menubar, alignment=Qt.AlignmentFlag.AlignLeft)
        self.menu_layout.addWidget(self.managebar, alignment=Qt.AlignmentFlag.AlignRight)
        self.h_layout.addWidget(self.tab)

    def expand_widget(self, expand):
        match expand:
            case False:
                self.expand = True
                self.expand_button.setText("🗗")
                self.showMaximized()
            case True:
                self.expand = False
                self.expand_button.setText("🗖")
                self.showNormal()

    def close_tab(self):
        if self.count >= 1:
            self.tab.removeTab(self.tab.currentIndex())
            self.count -= 1
            self.new_editor_list.pop(self.tab.currentIndex())

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

    def open_file_tab(self, name, data):
        self.create_new_tab()
        index = self.tab.indexOf(self.tab.currentWidget())
        self.new_editor_list[index].set_text(data)
        self.tab.setTabText(self.tab.indexOf(self.tab.currentWidget()), name)

    def open_file_dialog(self):
        name = QFileDialog.getOpenFileName(self, 'Open file', self.home_dir)
        name = name[0].split('/')[-1]
        f = open(self.home_dir + '/' + name, 'r')
        with f:
            data = f.read()
        self.open_file_tab(name, data)

    def open_tree_file(self):
        index = self.file_tree.currentIndex()
        name = self.model.fileName(index)

        f = open(self.home_dir + '/' + name, 'r')
        with f:
            data = f.read()
        self.open_file_tab(name, data)

    def save_as_text(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')
        name = name[0].split('/')[-1]
        index = self.tab.indexOf(self.tab.currentWidget())
        if name:
            f = open(self.home_dir + '/' + name, 'w')
            with f:
                f.writelines(i for i in self.new_editor_list[index].toPlainText())
        self.tab.setTabText(self.tab.indexOf(self.tab.currentWidget()), name)

    def change_style(self, style):
        match style:
            case 'Dark':
                self.setStyleSheet("background-color: #424242; color: #fff")
                self.editor.change_style(style)
                for i in self.new_editor_list:
                    i.change_style(style)
                config.set('style', 'COLOR_SCHEME', 'Dark')
            case 'Light':
                self.setStyleSheet("background-color: #bfbfbf; color: #000")
                self.editor.change_style(style)
                for i in self.new_editor_list:
                    i.change_style(style)
                config.set('style', 'COLOR_SCHEME', 'Light')
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def change_lang(self, lang):
        match lang:
            case 'RU':
                self.lang_dict = ru
                self.default_lang = config.get('lang', 'LANG')
                config.set('lang', 'LANG', 'RU')

            case 'EN':
                self.lang_dict = en
                self.default_lang = config.get('lang', 'LANG')
                config.set('lang', 'LANG', 'EN')

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def show_about(self):
        about = QMessageBox(self)
        about.setWindowTitle("About app PandaPad")
        about.setWindowFlag(Qt.WindowType.FramelessWindowHint)
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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._move()
            return super().mousePressEvent(event)

    def _move(self):
        window = self.window().windowHandle()
        window.startSystemMove()

    def _resize(self):
        window = self.window().windowHandle()
        window.startSystemResize(Qt.Edge.RightEdge)


app = QApplication(sys.argv)

pandapad = PandaPad()
pandapad.show()

app.exec()
