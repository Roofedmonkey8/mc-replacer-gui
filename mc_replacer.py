from rapidfuzz import process
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QSlider, QPushButton,
    QTextEdit, QHBoxLayout, QMessageBox, QGroupBox, QFileDialog, QCheckBox,
    QDialog, QLineEdit, QDialogButtonBox, QScrollArea, QCompleter, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt
import pyperclip
import json
import os
import sys

def to_readable(name):
    return name.replace("_", " ").title()

class AddBlockDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Block to blocks.json")
        self.setMinimumWidth(400)
        self.layout = QVBoxLayout(self)

        self.block_id_input = QLineEdit()
        self.layout.addWidget(QLabel("Block ID:"))
        self.layout.addWidget(self.block_id_input)

        self.props_layout = QVBoxLayout()
        self.layout.addLayout(self.props_layout)

        self.property_rows = []
        self.add_property_row()

        add_prop_button = QPushButton("+ Add Property")
        add_prop_button.clicked.connect(self.add_property_row)
        self.layout.addWidget(add_prop_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def add_property_row(self):
        row = QHBoxLayout()
        key_input = QLineEdit()
        val_input = QLineEdit()
        key_input.setPlaceholderText("Property name")
        val_input.setPlaceholderText("val1,val2,...")
        row.addWidget(key_input)
        row.addWidget(val_input)
        self.props_layout.addLayout(row)
        self.property_rows.append((key_input, val_input))

    def get_block_data(self):
        block_id = self.block_id_input.text().strip()
        if not block_id:
            return None, None
        props = {}
        for key_input, val_input in self.property_rows:
            key = key_input.text().strip()
            values = [v.strip() for v in val_input.text().split(",") if v.strip()]
            if key and values:
                props[key] = values
        return block_id, props

def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None: 
            clear_layout(item.layout())

class FuzzyCompleter(QCompleter):
    def __init__(self, items, parent=None):
        super().__init__(items, parent)
        self.all_items = items
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterMode(Qt.MatchContains)

    def updateModel(self, text):  # optional: move this to top if used often
        matches = [x[0] for x in process.extract(text, self.all_items, limit=10) if x[1] > 60]
        self.model().setStringList(matches)

    def setWidget(self, widget):
        super().setWidget(widget)
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(self.updateModel)


class ReplaceCommandApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minecraft Replace Command Generator")
        self.setMinimumSize(850, 800)

        self.accent_color = "#4f8cc9"
        self.theme_mode = "dark"
        self.show_icons = True
        self.blocks = {}
        self.filtered_blocks = []

        self.replacement_rows = []
        self.replacement_state_menus = []

        # Initialize all replacement-related lists early
        self.replacement_rows = []
        self.replacement_dropdowns = []
        self.replacement_sliders = []
        self.replacement_labels = []
        self.replacement_state_menus = []

        self.init_ui()               
        self.load_blocks()           
        self.apply_theme()

    def init_ui(self):
        layout = QVBoxLayout()

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["dark", "light"])
        self.theme_selector.currentTextChanged.connect(self.set_theme)
        layout.addWidget(QLabel("Theme:"))
        layout.addWidget(self.theme_selector)

        self.accent_selector = QComboBox()
        self.accent_selector.addItems(["blue", "green", "pink", "orange", "red"])
        self.accent_selector.currentTextChanged.connect(self.set_accent)
        layout.addWidget(QLabel("Accent Color:"))
        layout.addWidget(self.accent_selector)

        self.icon_checkbox = QCheckBox("Show Icons")
        self.icon_checkbox.setChecked(True)
        self.icon_checkbox.stateChanged.connect(self.toggle_icons)
        layout.addWidget(self.icon_checkbox)

        self.base_block_menu = QComboBox()
        self.base_block_menu.setEditable(True)
        layout.addWidget(QLabel("Base Block:"))
        layout.addWidget(self.base_block_menu)

        self.structure_menu = QComboBox()
        self.structure_menu.addItems(["Normal Block", "Slab", "Wall", "Stair", "Upside Down Stair"])
        self.structure_menu.currentTextChanged.connect(self.update_replacement_options)
        layout.addWidget(QLabel("Structure Type:"))
        layout.addWidget(self.structure_menu)

        self.replacement_count_menu = QComboBox()
        self.replacement_count_menu.addItems([str(i) for i in range(1, 11)])
        self.replacement_count_menu.currentTextChanged.connect(self.update_replacement_count)
        layout.addWidget(QLabel("Number of Replacement Blocks:"))
        layout.addWidget(self.replacement_count_menu)

        # Scrollable area for replacements
        self.replacement_group = QGroupBox("Replacement Blocks and Percentages")
        self.replacement_layout = QVBoxLayout()
        self.replacement_group.setLayout(self.replacement_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.replacement_group)
        layout.addWidget(scroll_area)

        self.output_box = QTextEdit()
        self.output_box.setFont(QFont("Consolas", 11))
        self.output_box.setFixedHeight(110)
        layout.addWidget(self.output_box)

        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Command")
        self.generate_button.clicked.connect(self.generate_command)
        button_layout.addWidget(self.generate_button)

        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_command)
        button_layout.addWidget(self.copy_button)

        self.save_button = QPushButton("Save to File")
        self.save_button.clicked.connect(self.save_command)
        button_layout.addWidget(self.save_button)
        
        self.project_save_button = QPushButton("Save Project")
        self.project_save_button.clicked.connect(self.save_project)
        button_layout.addWidget(self.project_save_button)

        self.project_load_button = QPushButton("Load Project")
        self.project_load_button.clicked.connect(self.load_project)
        button_layout.addWidget(self.project_load_button)
        layout.addLayout(button_layout)

        self.add_block_button = QPushButton("Add New Block to blocks.json")
        self.add_block_button.clicked.connect(self.show_add_block_dialog)
        layout.addWidget(self.add_block_button)
        
        # self.preset_button = QPushButton("Load Preset Template")
        # self.preset_button.clicked.connect(self.load_preset)
        # layout.addWidget(self.preset_button)

        self.view_blocks_button = QPushButton("View/Edit Blocks")
        self.view_blocks_button.clicked.connect(lambda: BlockEditorDialog().exec())
        layout.addWidget(self.view_blocks_button)

        self.setLayout(layout)
        self.update_replacement_options()

    def show_add_block_dialog(self):
        dialog = AddBlockDialog(self)
        if dialog.exec():
            block_id, props = dialog.get_block_data()
            if block_id:
                self.blocks[block_id] = props
                with open("blocks.json", "w") as f:
                    json.dump(self.blocks, f, indent=2)
                QMessageBox.information(self, "Saved", f"Block '{block_id}' added.")
                self.load_blocks()
                self.update_replacement_options()

    def load_blocks(self):
        try:
            print("Loading blocks into base_block_menu...")
            with open("blocks.json", "r") as f:
                self.blocks = json.load(f)

            # Only populate base block menu if it already exists
            if hasattr(self, "base_block_menu"):
                self.base_block_menu.clear()
                readable_blocks = []
                for block in self.blocks:
                    print(f" → Adding base block: {block}")
                    readable = to_readable(block)
                    icon_path = f"icons/blocks/{block}.png"
                    icon = QIcon(icon_path) if self.show_icons and os.path.exists(icon_path) else QIcon("icon.png")
                    self.base_block_menu.addItem(icon, readable, userData=block)
                    readable_blocks.append(readable)

                fuzzy = FuzzyCompleter(readable_blocks)
                self.base_block_menu.setCompleter(fuzzy)
                print("Base block menu items:")
                for i in range(self.base_block_menu.count()):
                    print(f" - {self.base_block_menu.itemText(i)} ({self.base_block_menu.itemData(i)})")


        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load blocks.json:\n{e}")
            self.blocks = {}

    def update_replacement_options(self):
        structure = self.structure_menu.currentText()
        if structure == "Normal Block":
            # Exclude known special suffixes
            self.filtered_blocks = [
                b for b in self.blocks
                if not any(b.endswith(suffix) for suffix in ("_slab", "_stairs", "_wall"))
            ]
        else:
            suffix = {
                "Slab": "_slab",
                "Wall": "_wall",
                "Stair": "_stairs",
                "Upside Down Stair": "_stairs"
            }.get(structure, "")
            self.filtered_blocks = [b for b in self.blocks if b.endswith(suffix)]

        print("Filtered blocks for structure:", structure)
        print(self.filtered_blocks)

        self.update_replacement_count(self.replacement_count_menu.currentText())

    def rebuild_state_selectors(self):
        for i, dropdown in enumerate(self.replacement_dropdowns):
            block_id = dropdown.currentData()
            if not block_id:
                continue
            layout = self.replacement_state_menus[i]
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            states = self.blocks.get(block_id, {})
            for key, values in states.items():
                layout.addWidget(QLabel(f"{key}:"))
                state_menu = QComboBox()
                state_menu.setProperty("key", key)
                state_menu.addItems(values)
                layout.addWidget(state_menu)

    def update_replacement_count(self, count_str):
        print(f"Rebuilding UI for {count_str} replacements. Filtered: {self.filtered_blocks}")
        for row in self.replacement_rows:
            clear_layout(row)
            self.replacement_layout.removeItem(row)
            del row  # ✅ ensure layout gets deleted

        self.replacement_rows.clear()
        self.replacement_dropdowns.clear()
        self.replacement_sliders.clear()
        self.replacement_labels.clear()
        self.replacement_state_menus.clear()

        # Force UI to refresh
        QApplication.processEvents()


        count = int(count_str)
        pct = 100 // count

        for _ in range(count):
            row = QHBoxLayout()
            state_layout = QHBoxLayout()
            row_wrapper = QVBoxLayout()

            combo = QComboBox()
            combo.setEditable(True)
            combo.clear()  # (safe redundancy)

            for block in self.filtered_blocks:
                readable = to_readable(block)
                icon_path = f"icons/blocks/{block}.png"
                icon = QIcon(icon_path) if self.show_icons and os.path.exists(icon_path) else QIcon("icon.png")
                combo.addItem(icon, readable, userData=block)
                print(f"   Added to dropdown: {block}")


            fuzzy = FuzzyCompleter([to_readable(b) for b in self.filtered_blocks])
            combo.setCompleter(fuzzy)

            self.replacement_dropdowns.append(combo)
            row.addWidget(combo)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(pct)
            slider.valueChanged.connect(self.rebalance_sliders)
            self.replacement_sliders.append(slider)
            row.addWidget(slider)

            label = QLabel(f"{pct}%")
            self.replacement_labels.append(label)
            row.addWidget(label)

            row_wrapper.addLayout(row)
            row_wrapper.addLayout(state_layout)

            self.replacement_state_menus.append(state_layout)
            self.replacement_rows.append(row_wrapper)
            self.replacement_layout.addLayout(row_wrapper)

        self.rebuild_state_selectors()

    def rebalance_sliders(self):
        total = sum(slider.value() for slider in self.replacement_sliders)
        if total == 0:
            return
        for slider, label in zip(self.replacement_sliders, self.replacement_labels):
            pct = int(round(slider.value() * 100 / total))
            label.setText(f"{pct}%")

    def generate_command(self):
        total = sum(slider.value() for slider in self.replacement_sliders)
        if total == 0:
            QMessageBox.warning(self, "Empty", "Total percent is 0.")
            return

        base_block = self.base_block_menu.currentData() or self.base_block_menu.currentText().replace(" ", "_").lower()

        parts = []
        for combo, slider, layout in zip(self.replacement_dropdowns, self.replacement_sliders, self.replacement_state_menus):
            block = combo.currentData() or combo.currentText().replace(" ", "_").lower()
            pct = int(round(slider.value() * 100 / total))
            props = []
            for j in range(layout.count()):
                w = layout.itemAt(j).widget()
                if isinstance(w, QComboBox):
                    key = w.property("key")
                    props.append(f"{key}={w.currentText()}")
            prop_str = f"[{','.join(props)}]" if props else ""
            parts.append(f"{pct}%{block}{prop_str}")

        self.output_box.setPlainText(f"//replace {base_block} " + ",".join(parts))

    def copy_command(self):
        pyperclip.copy(self.output_box.toPlainText().strip())
        QMessageBox.information(self, "Copied", "Command copied to clipboard!")

    def save_command(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save File", "replace_command.txt", "Text Files (*.txt)")
        if fname:
            with open(fname, "w") as f:
                f.write(self.output_box.toPlainText().strip())
            QMessageBox.information(self, "Saved", "Command saved successfully!")
    

    # def load_preset(self):
    #     fname, _ = QFileDialog.getOpenFileName(self, "Load Preset", "presets", "JSON Files (*.json)")
    #     if fname:
    #         self.load_project_from_file(fname)

    # def load_project_from_file(self, path):
    #     try:
    #         with open(path, "r") as f:
    #             data = json.load(f)
    #         self.theme_selector.setCurrentText(data.get("theme", "dark"))
    #         self.accent_selector.setCurrentText(data.get("accent", "blue"))
    #         self.icon_checkbox.setChecked(data.get("icons", True))
    #         self.structure_menu.setCurrentText(data.get("structure", "Normal Block"))
    #         self.base_block_menu.setCurrentText(data.get("base", ""))
    #         self.replacement_count_menu.setCurrentText(data.get("count", "1"))

    #         self.update_replacement_count(data["count"])
    #         for i, entry in enumerate(data["replacements"]):
    #             self.replacement_dropdowns[i].setCurrentText(entry["block"])
    #             self.replacement_sliders[i].setValue(entry["percent"])
    #             for j in range(self.replacement_state_menus[i].count()):
    #                 w = self.replacement_state_menus[i].itemAt(j).widget()
    #                 if isinstance(w, QComboBox):
    #                     k = w.property("key")
    #                     if k in entry["states"]:
    #                         w.setCurrentText(entry["states"][k])
    #         self.rebalance_sliders()
    #     except Exception as e:
    #         QMessageBox.critical(self, "Error", f"Failed to load preset:\n{e}")

    def save_project(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save Project", "project.json", "JSON Files (*.json)")
        if not fname:
            return
        data = {
            "theme": self.theme_selector.currentText(),
            "accent": self.accent_selector.currentText(),
            "icons": self.show_icons,
            "structure": self.structure_menu.currentText(),
            "base": self.base_block_menu.currentText(),
            "count": self.replacement_count_menu.currentText(),
            "replacements": []
        }
        for combo, slider, layout in zip(self.replacement_dropdowns, self.replacement_sliders, self.replacement_state_menus):
            entry = {
                "block": combo.currentText(),
                "percent": slider.value(),
                "states": {}
            }
            for j in range(layout.count()):
                w = layout.itemAt(j).widget()
                if isinstance(w, QComboBox):
                    k = w.property("key")
                    entry["states"][k] = w.currentText()
            data["replacements"].append(entry)

        with open(fname, "w") as f:
            json.dump(data, f, indent=2)
        QMessageBox.information(self, "Saved", "Project saved.")

    def load_project(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "JSON Files (*.json)")
        if not fname:
            return
        try:
            with open(fname, "r") as f:
                data = json.load(f)
            self.theme_selector.setCurrentText(data.get("theme", "dark"))
            self.accent_selector.setCurrentText(data.get("accent", "blue"))
            self.icon_checkbox.setChecked(data.get("icons", True))
            self.structure_menu.setCurrentText(data.get("structure", "Normal Block"))
            self.base_block_menu.setCurrentText(data.get("base", ""))
            self.replacement_count_menu.setCurrentText(data.get("count", "1"))

            self.update_replacement_count(data["count"])
            for i, entry in enumerate(data["replacements"]):
                self.replacement_dropdowns[i].setCurrentText(entry["block"])
                self.replacement_sliders[i].setValue(entry["percent"])
                for j in range(self.replacement_state_menus[i].count()):
                    w = self.replacement_state_menus[i].itemAt(j).widget()
                    if isinstance(w, QComboBox):
                        k = w.property("key")
                        if k in entry["states"]:
                            w.setCurrentText(entry["states"][k])
            self.rebalance_sliders()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load project:\n{e}")

    def toggle_icons(self):
        self.show_icons = self.icon_checkbox.isChecked()
        self.update_replacement_options()

    def set_theme(self, mode):
        self.theme_mode = mode
        self.apply_theme()

    def set_accent(self, color):
        self.accent_color = color
        self.apply_theme()

    def apply_theme(self):
        accent = {
            "blue": "#4f8cc9", "green": "#4fc98d", "pink": "#d25cb0",
            "orange": "#f4a261", "red": "#f75c5c"
        }.get(self.accent_selector.currentText(), "#4f8cc9")

        dark = self.theme_mode == "dark"
        bg = "#2b2b2b" if dark else "#f0f0f0"
        fg = "#ffffff" if dark else "#000000"
        field = "#3a3a3a" if dark else "#ffffff"
        border = "#444" if dark else "#cccccc"

        self.setStyleSheet(f"""
        QWidget {{
            background-color: {bg};
            color: {fg};
            font-family: "Segoe UI";
        }}
        QGroupBox {{
            border: 1px solid {border};
            border-radius: 8px;
            margin-top: 10px;
            padding: 10px;
        }}
        QComboBox, QTextEdit, QPushButton {{
            background-color: {field};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 5px;
        }}
        QScrollArea {{
            background-color: transparent;
        }}
        QSlider::groove:horizontal {{
            height: 10px;
            background: #444;
            border-radius: 5px;
        }}
        QSlider::handle:horizontal {{
            background: {accent};
            border: 1px solid #ccc;
            width: 14px;
            margin: -4px 0;
            border-radius: 7px;
        }}
        QPushButton:hover {{
            background-color: {accent};
            color: white;
        }}
        """)
class BlockEditorDialog(QDialog):
    def __init__(self, block_file="blocks.json"):
        super().__init__()
        self.setWindowTitle("Block Data Viewer/Editor")
        self.setMinimumSize(700, 500)
        self.block_file = block_file
        self.original_data = {}
        self.current_data = {}

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Block ID", "Property", "Values"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSortingEnabled(True)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search block ID, property, or values...")
        self.search_bar.textChanged.connect(self.filter_table)

        button_layout = QHBoxLayout()
        self.add_row_btn = QPushButton("Add Row")
        self.del_row_btn = QPushButton("Delete Selected")
        self.revert_btn = QPushButton("Undo/Revert")
        self.save_btn = QPushButton("Save")
        button_layout.addWidget(self.add_row_btn)
        button_layout.addWidget(self.del_row_btn)
        button_layout.addWidget(self.revert_btn)
        button_layout.addWidget(self.save_btn)

        self.add_row_btn.clicked.connect(self.add_empty_row)
        self.del_row_btn.clicked.connect(self.delete_selected_row)
        self.revert_btn.clicked.connect(self.revert_changes)
        self.save_btn.clicked.connect(self.save_changes)

        layout = QVBoxLayout(self)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        self.load_data()

    def load_data(self):
        try:
            with open(self.block_file, "r") as f:
                self.original_data = json.load(f)
                self.current_data = json.loads(json.dumps(self.original_data))
                self.populate_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def populate_table(self):
        self.table.setRowCount(0)
        for block_id, props in self.current_data.items():
            if not props:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(block_id))
            else:
                for prop, values in props.items():
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(block_id))
                    self.table.setItem(row, 1, QTableWidgetItem(prop))
                    self.table.setItem(row, 2, QTableWidgetItem(",".join(values)))

    def filter_table(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            visible = any(text in (self.table.item(row, col).text().lower() if self.table.item(row, col) else "") for col in range(3))
            self.table.setRowHidden(row, not visible)

    def add_empty_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col in range(3):
            self.table.setItem(row, col, QTableWidgetItem(""))

    def delete_selected_row(self):
        selected = self.table.selectedItems()
        if selected:
            rows = {item.row() for item in selected}
            for r in sorted(rows, reverse=True):
                self.table.removeRow(r)

    def revert_changes(self):
        self.current_data = json.loads(json.dumps(self.original_data))
        self.populate_table()

    def save_changes(self):
        updated = {}
        for row in range(self.table.rowCount()):
            bid = self.table.item(row, 0)
            prop = self.table.item(row, 1)
            vals = self.table.item(row, 2)
            if not bid:
                continue
            block_id = bid.text().strip()
            if block_id not in updated:
                updated[block_id] = {}
            if prop and prop.text().strip():
                updated[block_id][prop.text().strip()] = [v.strip() for v in vals.text().split(",")] if vals else []
        try:
            with open(self.block_file, "w") as f:
                json.dump(updated, f, indent=2)
            QMessageBox.information(self, "Saved", "blocks.json updated.")
            self.original_data = json.loads(json.dumps(updated))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReplaceCommandApp()
    window.show()
    sys.exit(app.exec())