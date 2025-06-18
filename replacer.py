import customtkinter as ctk


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.geometry("750x650")
app.title("Replace Command Generator")

# ==== Header ====
header_frame = ctk.CTkFrame(app)
header_frame.pack(pady=(10, 0), fill="x")

base_block_btn = ctk.CTkButton(header_frame, text="Base Block", width=300, height=40, font=("Arial", 19))
base_block_btn.pack(pady=(10))
# ==== Main layout ====
main_frame = ctk.CTkFrame(app)
main_frame.pack(expand=True, fill="both", padx=20, pady=10)

left_frame = ctk.CTkFrame(main_frame, width=500)
left_frame.pack(side="left", expand=True, fill="both", padx=(0, 10))

right_frame = ctk.CTkFrame(main_frame)
right_frame.pack(side="right", expand=True, fill="both")

new_block_btn = ctk.CTkButton(left_frame, text="New Block ➡", font=("Arial", 16))
new_block_btn.pack(pady=10)

block_listbox = ctk.CTkScrollableFrame(left_frame, label_text="Blocks")
block_listbox.pack(expand=True, fill="both", pady=10)

# Example block entry
for _ in range(3):
    row = ctk.CTkFrame(block_listbox)
    row.pack(fill="x", pady=2, padx=5)

    dot = ctk.CTkLabel(row, text="●", width=10)
    dot.pack(side="left")

    name = ctk.CTkLabel(row, text="stone_brick_stairs", anchor="w")
    name.pack(side="left", expand=True)

    delete = ctk.CTkButton(row, text="🗑", width=25)
    delete.pack(side="right")

# ==== Right Column: Properties ====
ctk.CTkLabel(right_frame, text="Properties", font=("Arial", 20, "bold")).pack(pady=5)

dropdowns = {}
for prop in ["Waterlog", "Facing", "Shape", "Half"]:
    label = ctk.CTkLabel(right_frame, text=prop)
    label.pack(pady=(5, 0))
    dropdown = ctk.CTkOptionMenu(right_frame, values=["", "value1", "value2"])
    dropdown.pack()
    dropdowns[prop.lower()] = dropdown

# Slider
ctk.CTkLabel(right_frame, text="50%").pack(pady=(10, 0))
slider = ctk.CTkSlider(right_frame, from_=0, to=100)
slider.set(50)
slider.pack()

# ==== Bottom Buttons ====
button_row = ctk.CTkFrame(app)
button_row.pack(pady=10)

generate_btn = ctk.CTkButton(button_row, text="Generate Code", width=120)
generate_btn.pack(side="left", padx=5)

load_btn = ctk.CTkButton(button_row, text="Load", width=80)
load_btn.pack(side="left", padx=5)

save_btn = ctk.CTkButton(button_row, text="Save", width=80)
save_btn.pack(side="left", padx=5)

app.mainloop()