from aqt import mw
from aqt.qt import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QDialogButtonBox,
)


class ConfigDialog(QDialog):
    """Configuration dialog for Add Recent Tags addon."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Recent Tags - Configuration")
        self.setMinimumWidth(400)
        
        # Load current config
        self.config = mw.addonManager.getConfig(__name__)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Number of tags setting
        tags_layout = QHBoxLayout()
        tags_label = QLabel("Number of recent tags to show:")
        self.tags_spinbox = QSpinBox()
        self.tags_spinbox.setMinimum(1)
        self.tags_spinbox.setMaximum(20)
        self.tags_spinbox.setValue(self.config.get("number_of_tags", 5))
        tags_layout.addWidget(tags_label)
        tags_layout.addWidget(self.tags_spinbox)
        tags_layout.addStretch()
        layout.addLayout(tags_layout)
        
        # Search depth setting
        depth_layout = QHBoxLayout()
        depth_label = QLabel("Number of recent notes to search:")
        depth_label.setToolTip("How many recent notes to check for tags")
        self.depth_spinbox = QSpinBox()
        self.depth_spinbox.setMinimum(10)
        self.depth_spinbox.setMaximum(500)
        self.depth_spinbox.setValue(self.config.get("search_depth", 50))
        depth_layout.addWidget(depth_label)
        depth_layout.addWidget(self.depth_spinbox)
        depth_layout.addStretch()
        layout.addLayout(depth_layout)
        
        # Restore defaults button
        restore_btn = QPushButton("Restore Defaults")
        restore_btn.clicked.connect(self.restore_defaults)
        layout.addWidget(restore_btn)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_config)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def restore_defaults(self):
        """Restore default configuration values."""
        self.tags_spinbox.setValue(5)
        self.depth_spinbox.setValue(50)
    
    def save_config(self):
        """Save configuration and close dialog."""
        self.config["number_of_tags"] = self.tags_spinbox.value()
        self.config["search_depth"] = self.depth_spinbox.value()
        mw.addonManager.writeConfig(__name__, self.config)
        self.accept()


def show_config_dialog():
    """Show the configuration dialog."""
    dialog = ConfigDialog(mw)
    dialog.exec()