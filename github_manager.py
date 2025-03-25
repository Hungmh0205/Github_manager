import sys
import os
import github
import webbrowser
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QLabel, QListWidget, QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QFont
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QComboBox



class SplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap("splash.png").scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        super().__init__(pixmap, Qt.WindowType.FramelessWindowHint)  # Ẩn viền cửa sổ
        
    def paintEvent(self, event):
            """ Vẽ chữ trực tiếp lên Splash Screen với font tùy chỉnh """
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
            # Chỉnh font chữ theo ý muốn
            font = QFont("Arial", 16, QFont.Weight.Bold)  # Thay "Arial" bằng font khác nếu muốn
            painter.setFont(font)
            painter.setPen(Qt.GlobalColor.black)  # Đổi màu chữ nếu cần

            # Vẽ chữ lên ảnh Splash Screen
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, "Developed by Mai Huu Hung")

    def mousePressEvent(self, event):
        pass  
        
class GitHubManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("splash.png"))  # Đặt icon cho cửa sổ ứng dụng
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
        layout = QVBoxLayout()

        self.token_input = QLineEdit(self)
        self.token_input.setPlaceholderText("Nhập GitHub Token...")
        layout.addWidget(self.token_input)

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

        #tạo token
        self.generate_token_btn = QPushButton("Tạo Token GitHub", self)
        self.generate_token_btn.clicked.connect(self.generate_github_token)
        layout.addWidget(self.generate_token_btn)

        self.setLayout(layout)
        self.setWindowTitle("GitHub Manager")
        self.resize(400, 600)

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
            self.current_path = path  # Cập nhật đường dẫn hiện tại
            self.file_list.clear()

        # Nếu đang trong thư mục con, thêm nút quay lại
            if path:
                self.file_list.addItem("⬆️ .. (Quay lại)")

            for content in contents:
                item_label = content.path if content.type == "file" else f"📁 {content.path}"
                self.file_list.addItem(item_label)

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

