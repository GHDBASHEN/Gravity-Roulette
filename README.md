# 🎰 Gravity-Roulette Predictor 🔮

## 🧩 Project Overview

The **Gravity-Roulette Predictor** is a desktop application designed to assist in making **speculative next-bet predictions** for the roulette game, focusing on the simple outcomes:

- 🔴 **Red**
- ⚫ **Black** (referred to as *White* in some contexts)
- 🟢 **Zero (Green)**

The application employs a **dual-analysis approach**:
1. A simple **pattern-based heuristic** (Gambler’s Fallacy logic).
2. A more sophisticated **LSTM (Long Short-Term Memory)** machine learning model that searches for possible non-random patterns in historical spin data.

All spin data is persistently stored in an external Excel file.

---

<img width="1876" height="840" alt="image" src="https://github.com/user-attachments/assets/cdcb9be4-b3f7-4d69-9014-fa41f0209c40" />

## ✨ Features

### 🧠 Dual Prediction System

<img width="551" height="578" alt="image" src="https://github.com/user-attachments/assets/8362eb68-0def-464e-bc26-656f4fb738b9" />

#### 1. Pattern Bias Prediction
- Performs a quick analysis of the **last 20 spins**.
- Recommends a color **only** when one outcome is significantly underrepresented.
- **Bias threshold:** ≥ 4 difference between color counts.

#### 2. LSTM Machine Learning Prediction
- Uses a **sequence-based neural network** to predict the next probable color.
- Trains on the entire recorded history for accuracy and consistency.

### 💾 Persistent Data Storage
- All spin results (number, color, timestamp) are saved to and loaded from `roulette_history.xlsx`.

### 🔁 Consistent ML Results
- Fixed random seeds ensure **consistent predictions** across restarts with identical data.

### ⚙️ Modular Architecture
- Heavy ML training runs in **separate scripts** to keep the GUI responsive and smooth.

---

## 🧱 Prerequisites

Before running the application, ensure you have **Python** installed, then install the required libraries:

```bash
pip install pandas openpyxl numpy tensorflow scikit-learn
