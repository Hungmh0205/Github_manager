import sys
import os
import github
import webbrowser
import requests
import shutil
import pyperclip
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QLabel, QListWidget, QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QFont
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu


class SplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap("splash.png").scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        super().__init__(pixmap, Qt.WindowType.FramelessWindowHint)  # Ẩn viền cửa sổ
        
    def paintEvent(self, event):
            """ Vẽ chữ trực tiếp lên Splash Screen với font tùy chỉnh """
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
            # Chỉnh font chữ theo ý muốn
            font = QFont("UTM Akashi", 13, QFont.Weight.Bold)  # Thay "Arial" bằng font khác nếu muốn
            painter.setFont(font)
            painter.setPen(Qt.GlobalColor.white)  # Đổi màu chữ nếu cần

            # Vẽ chữ lên ảnh Splash Screen
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, "Developed by Mai Huu Hung")

    def mousePressEvent(self, event):
        pass  
        
class GitHubManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("splash1.png"))  # Đặt icon cho cửa sổ ứng dụng
        self.tokens = []  # Danh sách lưu trữ tokens
        self.token_tab = QWidget()  # Khởi tạo trước khi thêm vào tab
        self.initUI()
        self.github_token = ""
        self.repo = None
        self.current_path = ""

    def closeEvent(self, event):
        """ Chặn đóng cửa sổ khi click vào logo, hiển thị cảnh báo """
        reply = QMessageBox.question(
            self, "Thoát ứng dụng", "Bạn có chắc muốn thoát không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()  # Cho phép đóng ứng dụng
        else:
            event.ignore()  # Hủy sự kiện đóng

    def initUI(self):
        main_layout = QVBoxLayout()
    
        self.tabs = QTabWidget()
        self.main_tab = QWidget()
        self.download_tab = QWidget()

        self.tabs.addTab(self.main_tab, "Quản lý Repository")
        self.tabs.addTab(self.download_tab, "Tải File")
        self.tabs.addTab(self.token_tab, "Danh sách Tokens")
        main_layout.addWidget(self.tabs)

        self.initMainTab()  # Hàm xử lý giao diện tab chính
        self.initDownloadTab()  # Hàm xử lý giao diện tab tải file
        self.initTokenTab()

        self.setLayout(main_layout)
        self.setWindowTitle("GitHub Manager")
        self.resize(500, 600)

    def initMainTab(self):
        layout = QVBoxLayout()
    
        self.token_input = QLineEdit(self)
        self.token_input.setPlaceholderText("Nhập GitHub Token...")
        layout.addWidget(self.token_input)

        #tạo token
        self.generate_token_btn = QPushButton("Tạo Token GitHub", self)
        self.generate_token_btn.clicked.connect(self.generate_github_token)
        layout.addWidget(self.generate_token_btn)

        #lưu token
        self.save_token_btn = QPushButton("Lưu Token", self)
        self.save_token_btn.clicked.connect(self.save_token)
        layout.addWidget(self.save_token_btn)

        self.connect_btn = QPushButton("Kết nối GitHub", self)
        self.connect_btn.clicked.connect(self.connect_github)
        layout.addWidget(self.connect_btn)

        self.repo_input = QLineEdit(self)
        self.repo_input.setPlaceholderText("Nhập tên repository (username/repo)...")
        layout.addWidget(self.repo_input)

        self.list_repos_btn = QPushButton("Danh sách Repository", self)
        self.list_repos_btn.clicked.connect(self.list_repositories)
        layout.addWidget(self.list_repos_btn)


        self.load_repo_btn = QPushButton("Tải danh sách file", self)
        self.load_repo_btn.clicked.connect(self.load_repository_files)
        layout.addWidget(self.load_repo_btn)

        self.file_list = QListWidget(self)
        self.file_list.itemDoubleClicked.connect(self.open_repository)
        layout.addWidget(self.file_list)

        self.back_btn = QPushButton("Quay lại", self)
        self.back_btn.clicked.connect(self.go_back)
        layout.addWidget(self.back_btn)


        self.upload_btn = QPushButton("Upload file", self)
        self.upload_btn.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_btn)

        self.upload_folder_btn = QPushButton("Upload thư mục", self)
        self.upload_folder_btn.clicked.connect(self.upload_folder)
        layout.addWidget(self.upload_folder_btn)

        self.update_btn = QPushButton("Cập nhật file", self)
        self.update_btn.clicked.connect(self.update_file)
        layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Xóa file/thư mục", self)
        self.delete_btn.clicked.connect(self.delete_file)
        layout.addWidget(self.delete_btn)

        # Thêm phần tạo repository
        self.new_repo_input = QLineEdit(self)
        self.new_repo_input.setPlaceholderText("Nhập tên repository ...")
        layout.addWidget(self.new_repo_input)

        self.repo_visibility = QComboBox(self)
        self.repo_visibility.addItems(["Public", "Private"])
        layout.addWidget(self.repo_visibility)

        self.create_repo_btn = QPushButton("Tạo Repository", self)
        self.create_repo_btn.clicked.connect(self.create_repository)
        layout.addWidget(self.create_repo_btn)

        #xoá repository
        self.delete_repo_btn = QPushButton("Xóa Repository", self)
        self.delete_repo_btn.clicked.connect(self.delete_repository)
        layout.addWidget(self.delete_repo_btn)
        
        self.main_tab.setLayout(layout)

    def initDownloadTab(self):
        """Tạo giao diện cho tab 'Tải File'"""
        layout = QVBoxLayout()

        self.file_list_download = QListWidget(self)  # Danh sách file trong tab tải file
        layout.addWidget(self.file_list_download)

        self.download_file_btn = QPushButton("Tải File Đã Chọn", self)
        self.download_file_btn.clicked.connect(self.download_selected_file)
        layout.addWidget(self.download_file_btn)

        self.download_repo_btn = QPushButton("Tải Toàn Bộ Repository", self)
        self.download_repo_btn.clicked.connect(self.download_repository)
        layout.addWidget(self.download_repo_btn)

        self.download_tab.setLayout(layout)

    def initTokenTab(self):
        layout = QVBoxLayout()

        self.token_list = QListWidget(self)
        self.token_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.token_list.customContextMenuRequested.connect(self.show_token_menu)
        layout.addWidget(self.token_list)

        self.load_tokens_from_file()  # Gọi hàm đúng tên để load token khi khởi động

        self.token_list.itemClicked.connect(self.copy_token)
        self.token_tab.setLayout(layout)


    def load_tokens_from_file(self):
        """Đọc danh sách token từ file khi mở ứng dụng"""
        if os.path.exists("tokens.txt"):
            with open("tokens.txt", "r") as file:
                self.tokens = [line.strip() for line in file.readlines()]
                self.token_list.addItems(self.tokens)  # Hiển thị token trong danh sách


    def load_saved_tokens(self):
        """Hiển thị danh sách token khi mở tab"""
        self.token_list.clear()
        for token in self.tokens:
            self.token_list.addItem(token)

    def copy_token(self, item):
        """Sao chép token khi click vào danh sách"""
        token = item.text()
        pyperclip.copy(token)
        QMessageBox.information(self, "Thông báo", "Token đã được sao chép vào clipboard!")

    def add_token(self, token):
        """Thêm token vào danh sách và hiển thị"""
        if token and token not in self.tokens:
            self.tokens.append(token)
            self.token_list.addItem(token)  # Cập nhật danh sách ngay


    def save_token(self):
        """Lưu token khi nhập vào ô và ghi vào file"""
        token = self.token_input.text().strip()
        if token and token not in self.tokens:
            self.tokens.append(token)
            self.token_list.addItem(token)
            self.save_tokens_to_file()  # Ghi vào file
            self.token_input.clear()
            QMessageBox.information(self, "Thành công", "Token đã được lưu!")
        else:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập token hợp lệ hoặc token đã tồn tại!")

    def show_token_menu(self, position):
        """Hiển thị menu chuột phải để xóa token"""
        menu = QMenu()
        delete_action = QAction("Xóa Token", self)
        delete_action.triggered.connect(self.delete_selected_token)
        menu.addAction(delete_action)
        menu.exec(self.token_list.mapToGlobal(position))

    def delete_selected_token(self):
        """Xóa token đã chọn khỏi danh sách và file"""
        selected_item = self.token_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn token để xóa!")
            return

        token = selected_item.text()
        confirm = QMessageBox.question(self, "Xác nhận", f"Bạn có chắc muốn xóa token này?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.tokens.remove(token)  # Xóa khỏi danh sách
            self.token_list.takeItem(self.token_list.row(selected_item))  # Xóa khỏi giao diện
            self.save_tokens_to_file()  # Cập nhật lại file token
            QMessageBox.information(self, "Thành công", "Token đã được xóa!")

    def save_tokens_to_file(self):
        """Ghi danh sách token vào file với mã hóa UTF-8"""
        with open("tokens.txt", "w", encoding="utf-8") as file:
            for token in self.tokens:
                file.write(token + "\n")



    def connect_github(self):
        self.github_token = self.token_input.text().strip()
        try:
            self.github_client = github.Github(self.github_token)
            self.repo = None
            self.file_list.clear()
            self.file_list.addItem("✅ Kết nối GitHub thành công!")
        except Exception as e:
            self.file_list.addItem(f"❌ Lỗi kết nối: {e}")

    def list_repositories(self):
        """ Liệt kê danh sách repository của tài khoản GitHub """
        if not self.github_token:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập GitHub Token!")
            return
    
        try:
            g = github.Github(self.github_token)
            user = g.get_user()
            repos = user.get_repos()
            self.file_list.clear()
            for repo in repos:
                self.file_list.addItem(repo.full_name)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lấy danh sách repository: {e}")


    def load_repository_files(self, path=""):
        repo_name = self.repo_input.text().strip()
        if not repo_name:
            self.file_list.addItem("❌ Vui lòng nhập tên repository!")
            return

    # Nếu path bị False, đặt lại thành rỗng ("")
        if not isinstance(path, str):
            print("⚠️ Lỗi: path nhận giá trị False, đặt lại về ''")
            path = ""

        try:
            if "/" not in repo_name:
                self.file_list.addItem("❌ Tên repository không hợp lệ! Hãy nhập dạng username/repo.")
                return

            try:
                self.repo = self.github_client.get_repo(repo_name)
            except github.GithubException as e:
                self.file_list.addItem(f"❌ Không tìm thấy repository: {repo_name}. Hãy kiểm tra lại!")
                return
            try:
                contents = self.repo.get_contents(path)
            except github.GithubException as e:
                if e.status == 404:  # Repo rỗng
                    self.file_list.clear()
                    self.file_list.addItem("📂 Repository này đang trống!")
                    return
                else:
                    self.file_list.addItem(f"❌ Lỗi tải file: {e}")
                    return

            # Xóa danh sách cũ
            self.file_list.clear()
            self.file_list_download.clear()

            self.current_path = path  # Cập nhật đường dẫn hiện tại
            self.file_list.clear()

        # Nếu đang trong thư mục con, thêm nút quay lại
            if path:
                self.file_list.addItem("⬆️ .. (Quay lại)")
                self.file_list_download.addItem("⬆️ .. (Quay lại)")

        # Hiển thị file và thư mục trong cả 2 danh sách
            for content in contents:
                item_label = content.path if content.type == "file" else f"📁 {content.path}"
                self.file_list.addItem(item_label)
                self.file_list_download.addItem(item_label)  # Cập nhật vào danh sách tải file

        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(error_msg)  # In lỗi chi tiết ra terminal
            self.file_list.addItem(f"❌ Lỗi tải file: {e}")

    def go_back(self):
        if self.current_path:
            parent_path = "/".join(self.current_path.split("/")[:-1])
            self.load_repository_files(parent_path)

    def upload_file(self):
        repo_name = self.repo_input.text().strip()
    
        if not repo_name:
            self.file_list.addItem("❌ Vui lòng nhập repository!")
            return

    # Chọn file để upload
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Chọn file để upload")

        if not file_path:
            return

    # Lấy tên file (không gồm đường dẫn)
        file_name = os.path.basename(file_path)

    # Đưa file vào thư mục hiện tại (nếu có)
        remote_path = f"{self.current_path}/{file_name}" if self.current_path else file_name

        try:
            self.repo = self.github_client.get_repo(repo_name)

            # Kiểm tra repo có trống không
            try:
                contents = self.repo.get_contents("")
            except github.GithubException as e:
                if e.status == 404:  # Repo trống
                    self.file_list.addItem("📂 Repository trống! Đang tạo file đầu tiên...")
                    self.create_initial_file(file_name, file_path)
                    return

        # Đọc nội dung file
            with open(file_path, "rb") as f:
                content = f.read()

        # Kiểm tra xem file đã tồn tại chưa
            try:
                existing_file = self.repo.get_contents(remote_path)
                self.repo.update_file(
                    existing_file.path, f"🔄 Cập nhật {file_name}", content, existing_file.sha, branch="main"
                )
                self.file_list.addItem(f"✅ Cập nhật file: {file_name}")
            except:
                self.repo.create_file(remote_path, f"📤 Upload {file_name}", content, branch="main")
                self.file_list.addItem(f"✅ Upload thành công: {file_name}")

        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(error_msg)  # In lỗi chi tiết ra terminal
            self.file_list.addItem(f"❌ Lỗi upload file: {e}")

    def update_file(self):
        selected_item = self.file_list.currentItem()
        if selected_item and self.repo:
            file_path = selected_item.text()
            local_file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file để cập nhật")
            if local_file_path:
                with open(local_file_path, "rb") as file:
                    content = file.read()
                try:
                    contents = self.repo.get_contents(file_path)
                    self.repo.update_file(contents.path, f"Cập nhật {file_path}", content, contents.sha, branch="main")
                    self.file_list.addItem(f"✅ Đã cập nhật {file_path}")
                except Exception as e:
                    self.file_list.addItem(f"❌ Lỗi cập nhật {file_path}: {e}")

    def upload_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục")
        if folder_path and self.repo:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, folder_path)
                    with open(file_path, "rb") as f:
                        content = f.read()
                    try:
                        self.repo.create_file(relative_path, f"Upload {relative_path}", content, branch="main")
                        self.file_list.addItem(f"✅ Đã upload {relative_path}")
                    except Exception as e:
                        self.file_list.addItem(f"❌ Lỗi upload {relative_path}: {e}")

    def delete_file(self):
        selected_item = self.file_list.currentItem()
        if selected_item and self.repo:
            file_path = selected_item.text()
            try:
                contents = self.repo.get_contents(file_path)
                self.repo.delete_file(contents.path, f"Xóa {file_path}", contents.sha, branch="main")
                self.file_list.takeItem(self.file_list.row(selected_item))
                self.file_list.addItem(f"✅ Đã xóa {file_path}")
            except Exception as e:
                self.file_list.addItem(f"❌ Lỗi xóa {file_path}: {e}")

    def create_repository(self):
        repo_name = self.new_repo_input.text().strip()
        is_private = self.repo_visibility.currentText() == "Private"
        
        if not self.github_token:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập GitHub Token!")
            return
        if not repo_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên repository!")
            return

        try:
            g = github.Github(self.github_token)
            user = g.get_user()

            # Kiểm tra nếu token không có quyền tạo repo
            if not user.login:
                QMessageBox.critical(self, "Lỗi", "Token không có quyền tạo repository. Hãy kiểm tra lại!")
                return
            for repo in user.get_repos():
                if repo.name == repo_name:
                    QMessageBox.warning(self, "Lỗi", f"Repository '{repo_name}' đã tồn tại!")
                    return

            user.create_repo(repo_name, private=is_private)
            QMessageBox.information(self, "Thành công", f"Repository '{repo_name}' đã được tạo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tạo repository: {e}")

    def create_initial_file(self, file_name, file_path):
        """ Tạo file đầu tiên trong repository trống """
        try:
            if not self.repo:
                self.file_list.addItem("❌ Chưa kết nối GitHub!")
                return

            with open(file_path, "rb") as f:
                content = f.read()

            self.repo.create_file(file_name, f"📤 Tạo file đầu tiên: {file_name}", content, branch="main")
            self.file_list.addItem(f"✅ Đã tạo file đầu tiên: {file_name}!")

        except Exception as e:
            self.file_list.addItem(f"❌ Lỗi khi tạo file đầu tiên: {e}")

    def generate_github_token(self):
        """ Mở trang tạo token GitHub với các quyền cần thiết """
        token_url = "https://github.com/settings/tokens/new?scopes=repo,public_repo,delete_repo&description=GitHubManagerToken"
        webbrowser.open(token_url)
        QMessageBox.information(self, "Hướng dẫn", "Hãy tạo token với các quyền: repo, public_repo, delete_repo và sao chép vào ứng dụng.")

    def delete_repository(self):
        """ Xóa repository đã nhập """
        repo_name = self.repo_input.text().strip()
        if not repo_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên repository!")
            return

        confirm = QMessageBox.question(self, "Xác nhận xóa", f"Bạn có chắc chắn muốn xóa repository '{repo_name}'? Hành động này không thể hoàn tác!",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.No:
            return

        try:
            g = github.Github(self.github_token)
            repo = g.get_repo(repo_name)
            repo.delete()
            QMessageBox.information(self, "Thành công", f"Repository '{repo_name}' đã được xóa thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa repository: {e}")

    def open_repository(self, item):
        """ Mở repository hoặc thư mục khi click đúp """
        item_text = item.text().strip()

        if item.text() == "⬆️ .. (Quay lại)":
            self.go_back()
            return

        if item_text.startswith("📁 "):
            folder_name = item_text[2:].strip()  # Loại bỏ biểu tượng "📁 "
            self.current_path = f"{self.current_path}/{folder_name}" if self.current_path else folder_name
            self.load_repository_files(self.current_path)
        else:
            self.repo_input.setText(item_text)
            self.current_path = ""  # Reset đường dẫn khi mở repo mới
            self.load_repository_files()

    def download_selected_file(self):
        """Tải file đã chọn từ repository"""
        selected_item = self.file_list_download.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một file để tải!")
            return

        file_path = selected_item.text().strip()
        if not file_path or file_path.startswith("📁 "):
            QMessageBox.warning(self, "Lỗi", "Không thể tải thư mục, chỉ hỗ trợ tải file!")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Lưu file", file_path)
        if not save_path:
            return

        try:
            file_content = self.repo.get_contents(file_path)
            file_url = file_content.download_url
            response = requests.get(file_url, stream=True)

            # Xác định file có phải là file nhị phân không
            binary_extensions = [".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".exe"]
            is_binary = any(file_path.endswith(ext) for ext in binary_extensions)

            if is_binary:
                # Lưu file nhị phân
                with open(save_path, "wb") as file:
                    file.write(response.content)
            else:
                # Lấy encoding đúng của file
                encoding = response.apparent_encoding if response.encoding is None else response.encoding
                # Chuẩn hóa ký tự xuống dòng về '\n' (Unix)
                content_text = response.text.replace("\r\n", "\n")  # Chuyển từ Windows CRLF -> LF
                with open(save_path, "w", encoding=encoding, newline="\n") as file:
                    file.write(content_text)

            QMessageBox.information(self, "Thành công", f"File '{file_path}' đã được tải về thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải file: {e}")




    def download_repository(self):
        """Tải toàn bộ repository về máy"""
        if not self.repo:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn repository trước!")
            return

        save_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu repository")
        if not save_path:
            return

        repo_url = self.repo.clone_url
        repo_name = self.repo.name  # Lấy tên repo chính xác
        full_path = os.path.join(save_path, repo_name)

        try:
            os.system(f'git clone "{repo_url}" "{full_path}"')  # Đặt đường dẫn trong dấu ngoặc kép để tránh lỗi
            QMessageBox.information(self, "Thành công", f"Repository '{repo_name}' đã được tải về thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải repository: {e}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Hiển thị Splash Screen trong 3 giây
    splash = SplashScreen()
    splash.show()
    
    def start_app():
        global window  # Giữ biến window tồn tại
        splash.close()
        window = GitHubManager()
        window.show()

    
    QTimer.singleShot(3000, start_app)  # 3 giây rồi mở app
    
    sys.exit(app.exec())

