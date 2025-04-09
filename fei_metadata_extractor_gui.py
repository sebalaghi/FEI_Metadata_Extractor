import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET
import hyperspy.api as hs

class FEIExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FEI EMI & SER Metadata Extractor")
        self.root.geometry("750x600")
        self.root.configure(bg="#f0f0f0")

        ttk.Label(self.root, text="Designed by Esmael Balaghi", font=("Arial", 12, "bold"), background="#f0f0f0", foreground="blue").pack(pady=5)
        ttk.Label(self.root, text="FEI Metadata Extractor", font=("Arial", 16, "bold"), background="#f0f0f0").pack(pady=10)

        ttk.Label(self.root, text="Select EMI Files:", background="#f0f0f0").pack(pady=5)
        self.emi_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE, width=80, height=6)
        self.emi_listbox.pack(pady=5)
        ttk.Button(self.root, text="Browse", command=self.select_emi_files).pack(pady=5)

        ttk.Label(self.root, text="Select SER Files:", background="#f0f0f0").pack(pady=5)
        self.ser_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE, width=80, height=6)
        self.ser_listbox.pack(pady=5)
        ttk.Button(self.root, text="Browse", command=self.select_ser_files).pack(pady=5)

        ttk.Label(self.root, text="Select Save Directory:", background="#f0f0f0").pack(pady=5)
        self.save_dir_entry = ttk.Entry(self.root, width=60)
        self.save_dir_entry.pack(pady=5)
        ttk.Button(self.root, text="Browse", command=self.select_directory).pack(pady=5)

        self.extract_button = ttk.Button(self.root, text="Extract Metadata", command=self.process_files)
        self.extract_button.pack(pady=20)

        self.output_text = tk.Text(self.root, height=12, width=90, bg="white", fg="black", font=("Arial", 10))
        self.output_text.pack(pady=10)

        footer_label = ttk.Label(self.root, text="Designed by Esmael Balaghi @FischerLab", font=("Arial", 10, "italic"), background="#f0f0f0", foreground="gray")
        footer_label.pack(pady=10)

    def select_emi_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("EMI Files", "*.emi")])
        if file_paths:
            self.emi_listbox.delete(0, tk.END)
            for file in file_paths:
                self.emi_listbox.insert(tk.END, file)

    def select_ser_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("SER Files", "*.ser")])
        if file_paths:
            self.ser_listbox.delete(0, tk.END)
            for file in file_paths:
                self.ser_listbox.insert(tk.END, file)

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir_entry.delete(0, tk.END)
            self.save_dir_entry.insert(tk.END, directory)

    def process_files(self):
        emi_files = self.emi_listbox.get(0, tk.END)
        ser_files = self.ser_listbox.get(0, tk.END)
        save_dir = self.save_dir_entry.get()

        if not emi_files or not ser_files:
            messagebox.showerror("Error", "Please select EMI and SER files.")
            return

        if not os.path.isdir(save_dir):
            messagebox.showerror("Error", "Please select a valid save directory.")
            return

        matched_files = {}
        for emi_file in emi_files:
            base_name = os.path.basename(emi_file).replace(".emi", "")
            for ser_file in ser_files:
                ser_base_name = os.path.basename(ser_file).replace(".ser", "").replace("_1", "")
                if ser_base_name == base_name:
                    matched_files[emi_file] = ser_file
                    break

        if not matched_files:
            messagebox.showerror("Error", "No matching EMI and SER files found!")
            return

        for emi_file, ser_file in matched_files.items():
            metadata = self.extract_emi_metadata(emi_file)
            if metadata:
                ser_metadata = self.extract_ser_metadata(ser_file)
                if ser_metadata:
                    metadata.update(ser_metadata)
                self.display_metadata(metadata)
                self.save_metadata(emi_file, metadata, save_dir)

        messagebox.showinfo("Success", "Metadata extraction completed successfully!")

    def extract_emi_metadata(self, file_path):
        try:
            with open(file_path, "rb") as file:
                binary_data = file.read()

            text_data = binary_data.decode(errors='ignore')
            start_idx = text_data.find("<ObjectInfo>")
            end_idx = text_data.find("</ObjectInfo>") + len("</ObjectInfo>")

            if start_idx == -1 or end_idx == -1:
                return {}

            xml_content = text_data[start_idx:end_idx]
            metadata_dict = {}
            try:
                root = ET.fromstring(xml_content)
                for data in root.findall(".//Data"):
                    label = data.find("Label").text if data.find("Label") is not None else "Unknown"
                    value = data.find("Value").text if data.find("Value") is not None else "N/A"
                    metadata_dict[label] = value
            except ET.ParseError:
                return {}

            return metadata_dict

        except Exception:
            return {}

    def extract_ser_metadata(self, file_path):
        try:
            ser_data = hs.load(file_path, lazy=True)
            image_size_x = ser_data.data.shape[1]
            image_size_y = ser_data.data.shape[0]

            pixel_size_x = ser_data.axes_manager[1].scale
            pixel_size_y = ser_data.axes_manager[0].scale
            pixel_unit_x = ser_data.axes_manager[1].units or "units"
            pixel_unit_y = ser_data.axes_manager[0].units or "units"

            return {
                "Image Size (X)": image_size_x,
                "Image Size (Y)": image_size_y,
                "Pixel Size (X)": f"{pixel_size_x:.3f} {pixel_unit_x}",
                "Pixel Size (Y)": f"{pixel_size_y:.3f} {pixel_unit_y}"
            }

        except Exception:
            return {}

    def display_metadata(self, metadata):
        self.output_text.delete("1.0", tk.END)
        for key, value in metadata.items():
            self.output_text.insert(tk.END, f"{key}: {value}\n")

    def save_metadata(self, file_path, metadata, save_dir):
        output_file = os.path.join(save_dir, os.path.basename(file_path).replace(".emi", "_metadata.txt"))
        with open(output_file, "w", encoding="utf-8") as f:
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = FEIExtractorApp(root)
    root.mainloop()