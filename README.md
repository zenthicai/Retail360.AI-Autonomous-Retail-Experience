
# 🛍️ Retail360.AI: Smart Retail Face Recognition App

Retail360.AI is an intelligent retail entry system built using **Streamlit** and **DeepFace** that recognizes customers via facial recognition, greets them with personalized messages and voice, displays their past purchases, and recommends offers — all in real-time.

---

## 🚀 Features

- 👤 Real-time Face Capture using Webcam
- 🔍 Face Matching with Stored Customer Data (DeepFace)
- 📄 Auto Fetch Customer Profile from MySQL
- 💬 Personalized Greeting with Text & Voice (gTTS + pygame)
- 🛒 Show Last 5 Purchases from Purchase History
- 🎁 Personalized Offers based on Last Purchase Categories
- 📊 Insights:
  - Bar Chart of Purchase Frequency (Plotly)
  - Gauge Chart of Total Spend
- ✍️ New Customer Registration via Webcam

---

## 🗂️ Project Structure

```
Retail360-App/
│
├── data/                   # Csv files (e.g., customers.csv,orders.csv)
|   └── ...
├── face_images/            # Stored face images (e.g., 1_face.jpg)
│    └── ...
├── sample_outputs/         # Sample outputs for Recognition and Registration
│    └── ...
├── app.py                  # Main Streamlit app
├── requirements.txt        # Required Python packages
├── retail360degree.sql     # SQL Script
└── README.md               # Project documentation
```

---

## ⚙️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python + MySQL
- **Face Recognition**: DeepFace
- **Voice Output**: gTTS + pygame
- **Charts**: Plotly
- **Database**: MySQL

---

## 📸 Face Image Format

Face images are stored in the `face_images/` folder with the naming convention:

```
<customer_id>_face.jpg
```

Example:
```
1_face.jpg, 2_face.jpg, ...
```

---

## 🧪 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/zenthicai/Retail360.AI-Autonomous-Retail-Experience
cd Retail360-App
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create MySQL Database & Tables

Create a MySQL database named `retail` and include required tables like:
- `customers`
- `purchases`
- `offers`
- `purchases_data_model` (view with joined data)

> **Note**: Ensure the structure matches `app.py` expectations.

### 4. Run the App
```bash
streamlit run app.py
```

---

## 📢 Acknowledgements

- [Streamlit](https://streamlit.io/)
- [DeepFace](https://github.com/serengil/deepface)
- [MySQL](https://www.mysql.com/)
- [Plotly](https://plotly.com/)
- [gTTS](https://pypi.org/project/gTTS/)

---

