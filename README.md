# ⚡ Subnet Calculator Pro (Routing Engine)

A comprehensive, interactive web-based toolkit built with **Streamlit** for networking professionals and students. This project simplifies complex Computer Networks (CN) operations like Subnetting, Variable Length Subnet Masking (VLSM), Route Summarization (Supernetting), IPv6 calculations, and various IP conversions.

## ✨ Features

- **📡 Basic Subnet Calculator**: Calculate Network Address, Broadcast Address, Host Range, Subnet Mask, and total usable hosts from a given IP and CIDR.
- **✂️ Subnet Divider / VLSM**: Flexibly divide a major network into multiple smaller subnets based on custom host requirements per subnet using VLSM to optimize IP allocation without waste.
- **🔗 Supernet / Route Summarization**: Combine multiple contiguous subnets into a single optimized supernet routing entry.
- **🔄 IP Converter**: Seamlessly convert IP configurations:
  - IPv4 to Binary and vice-versa
  - IPv4 to Hexadecimal and vice-versa
  - CIDR to Decimal Subnet Mask and vice-versa
- **🌐 IPv6 Support**: Comprehensive support for IPv6 address calculations and manipulations.
- **📊 Interactive Visualizations**: Explore data dynamically with informative charts and graphs rendered using Plotly.

## 🛠️ Technology Stack

- **Frontend / Framework**: [Streamlit](https://streamlit.io/)
- **Programming Language**: Python 3.x
- **Data Manipulation**: Pandas
- **Interactive Graphs**: Plotly Express & Plotly Graph Objects
- **Networking Logic**: Python `ipaddress` module and custom utility scripts

## 📂 Project Structure

```bash
📦 CN Project
├── 📜 app.py               # Main Streamlit Application entry file
├── 📜 requirements.txt     # Python dependencies required to run the app
├── 📜 README.md            # Project documentation (this file)
├── 📂 styles/              
│   └── 🎨 style.css        # Custom CSS for UI styling and overrides
└── 📂 utils/               # Core logic and networking calculations
    ├── ⚙️ ip_converter.py  # Functions for Binary/Hex/CIDR conversions
    ├── ⚙️ ipv6.py          # IPv6 logic and calculations
    ├── ⚙️ subnet_calc.py   # Basic IPv4 subnet calculations
    └── ⚙️ vlsm.py          # Variable Length Subnet Mask logic
```

## 🚀 Installation & Setup

1. **Clone or Download the Repository**
   Keep all the files within a single folder.

2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv .venv
   ```

3. **Activate the Virtual Environment**
   - On **Windows**:
     ```powershell
     .\.venv\Scripts\activate
     ```
   - On **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Dependencies**
   Run the following command to install required packages (like `streamlit`, `pandas`, `plotly`):
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## 💻 Usage

Once you run the application, Streamlit will automatically open a new tab in your default web browser (typically at `http://localhost:8501`). 

Use the **Sidebar Navigation** on the left to switch between different networking tools:
1. Basic Subnet Calculator
2. Subnet Divider / VLSM
3. Supernet / Summarization
4. IP Converter
5. IPv6 Capabilities 

Simply input your IP addresses in standard formats (e.g., `192.168.1.0/24`) and let the application instantly compute the required ranges, masks, and summaries!

## 👩‍💻 Team Members

**Class / Batch:** INFT B

| Name | Roll Number |
| :--- | :--- |
| Priyanshu Gupta | 24101B0037 |
| Atharv Raut | 24101B0052 |
| Ronak Boddu | 24101B0044 |

*(Created for Computer Networks Project)*
