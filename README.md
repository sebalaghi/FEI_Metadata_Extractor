# FEI EMI & SER Metadata Extractor

A Python GUI application for extracting and saving microscopy metadata from FEI `.emi` and `.ser` files.

---

## 🛠 Features
- Match `.emi` and `.ser` files by base filename
- Extract XML metadata from `.emi`
- Extract pixel size & image dimensions directly from `.ser` via HyperSpy
- Display results in a GUI and save to `.txt` file
- Designed for TIA FEI file formats

---

## 📦 Requirements

Install dependencies using pip:

```bash
pip install hyperspy
```

---

## 🚀 Running the App

Run from the terminal:

```bash
python fei_metadata_extractor.py
```

---

## 💾 Output

Generates `.txt` files containing:
- Microscope & acquisition settings
- Image dimensions
- Pixel size (in nm, pm, etc)

---

## ✨ Credits

Designed and implemented by **Esmael Balaghi** @FischerLab.

---

## 🧭 License

Licensed under the MIT License.
