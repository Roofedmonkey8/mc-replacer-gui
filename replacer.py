import customtkinter as ctk
from tkinter import messagebox
import pyperclip

# === Blocks ===

# Base blocks (all wool + concrete)
base_blocks = [
    # Concrete
    "white_concrete", "orange_concrete", "magenta_concrete", "light_blue_concrete",
    "yellow_concrete", "lime_concrete", "pink_concrete", "gray_concrete",
    "light_gray_concrete", "cyan_concrete", "purple_concrete", "blue_concrete",
    "brown_concrete", "green_concrete", "red_concrete", "black_concrete",
    
    # Wool
    "white_wool", "orange_wool", "magenta_wool", "light_blue_wool",
    "yellow_wool", "lime_wool", "pink_wool", "gray_wool",
    "light_gray_wool", "cyan_wool", "purple_wool", "blue_wool",
    "brown_wool", "green_wool", "red_wool", "black_wool"
]

# Replacement blocks mapped by structure type
structure_to_blocks = {
    "Normal Block": [
        "mossy_cobblestone", "cobblestone", "mossy_stone_bricks",
        "cracked_stone_bricks", "stone_bricks"
    ],
    "Slab": [
        "stone_brick_slab", "mossy_cobblestone_slab", "mossy_stone_brick_slab", "cobblestone_slab"
    ],
    "Wall": [
        "stone_brick_wall", "mossy_cobblestone_wall", "mossy_stone_brick_wall", "cobblestone_wall"
    ],
    "Stair": [
        "stone_brick_stairs", "mossy_cobblestone_stairs", "mossy_stone_brick_stairs", "cobblestone_stairs"
    ],
    "Upside Down Stair": [
        "stone_brick_stairs", "mossy_cobblestone_stairs", "mossy_stone_brick_stairs", "cobblestone_stairs"
    ]
}

stair_directions = ["north", "south", "east", "west"]
structure_types = list(structure_to_blocks.keys())

# === UI Setup ===

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Minecraft Replace Command Generator")
app.geometry("700x650")

# Functions for dynamic slider handling
def clear_sliders():
    for row in slider_rows:
        row.destroy()
    slider_rows.clear()
    replace_sliders.clear()
    replace_labels.clear()
    percent_labels.clear()

def slider_callback_factory(label):
    def callback(value):
        label.configure(text=f"{int(value)}%")
    return callback

def build_sliders_for_structure(structure_type):
    clear_sliders()
    blocks = structure_to_blocks.get(structure_type, [])
    for block in blocks:
        row = ctk.CTkFrame(replace_frame)
        row.pack(fill="x", padx=10, pady=2)
        slider_rows.append(row)

        name_label = ctk.CTkLabel(row, text=block, width=200, anchor="w")
        name_label.pack(side="left")

        percent_label = ctk.CTkLabel(row, text="25%", width=50, anchor="e")
        percent_label.pack(side="right", padx=(5, 0))
        percent_labels.append(percent_label)

        slider = ctk.CTkSlider(row, from_=0, to=100, number_of_steps=100,
                               command=slider_callback_factory(percent_label))
        slider.set(25)
        slider.pack(side="right", fill="x", expand=True)

        replace_labels.append(block)
        replace_sliders.append(slider)

# Dropdowns
base_block_label = ctk.CTkLabel(app, text="Base Block:")
base_block_label.pack(pady=(10, 0))
base_block_menu = ctk.CTkOptionMenu(app, values=base_blocks)
base_block_menu.pack()

structure_label = ctk.CTkLabel(app, text="Structure Type:")
structure_label.pack(pady=(10, 0))

# Structure menu with dynamic update
structure_menu = ctk.CTkOptionMenu(app, values=structure_types, command=build_sliders_for_structure)
structure_menu.pack()

# Reusable UI lists
replace_labels = []
replace_sliders = []
percent_labels = []
slider_rows = []

# Facing and Half dropdowns
facing_label = ctk.CTkLabel(app, text="Facing Direction (if applicable):")
facing_label.pack(pady=(10, 0))
facing_menu = ctk.CTkOptionMenu(app, values=["", *stair_directions])
facing_menu.pack()

half_label = ctk.CTkLabel(app, text="Half (for slabs/upside-down stairs):")
half_label.pack(pady=(10, 0))
half_menu = ctk.CTkOptionMenu(app, values=["", "bottom", "top"])
half_menu.pack()

# Frame for dynamic sliders
replace_frame = ctk.CTkFrame(app)
replace_frame.pack(pady=(20, 10), fill="x")
ctk.CTkLabel(replace_frame, text="Replacement Blocks and Percentages").pack(pady=5)

# Output box
output_box = ctk.CTkTextbox(app, height=100)
output_box.pack(pady=10, padx=10, fill="both", expand=False)

# Generate command
def generate_command():
    base = base_block_menu.get()
    structure = structure_menu.get()
    facing = facing_menu.get()
    half = half_menu.get()

    parts = []
    for block, slider in zip(replace_labels, replace_sliders):
        percent = int(slider.get())
        if percent > 0:
            props = []
            if "Stair" in structure:
                if facing:
                    props.append(f"facing={facing}")
                if structure == "Upside Down Stair":
                    props.append("half=top")
            elif structure == "Slab" and half:
                props.append(f"type={half}")
            prop_str = f"[{','.join(props)}]" if props else ""
            parts.append(f"{percent}%{block}{prop_str}")

    if not parts:
        messagebox.showwarning("Empty", "You must assign at least one non-zero percent block.")
        return

    cmd = f"//replace {base} {','.join(parts)}"
    output_box.delete("1.0", "end")
    output_box.insert("end", cmd)

# Copy to clipboard
def copy_command():
    pyperclip.copy(output_box.get("1.0", "end").strip())
    messagebox.showinfo("Copied", "Command copied to clipboard!")

# Buttons
btn_generate = ctk.CTkButton(app, text="Generate Command", command=generate_command)
btn_generate.pack(pady=5)

btn_copy = ctk.CTkButton(app, text="Copy to Clipboard", command=copy_command)
btn_copy.pack(pady=5)

# Run app
app.mainloop()