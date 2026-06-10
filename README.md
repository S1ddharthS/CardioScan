# CardioScan AI - MED-OS v2.1

CardioScan is a state-of-the-art clinical diagnostic dashboard that uses a live **MATLAB Ensemble AI Engine** to assess cardiovascular risk based on 13 patient biomarkers.

## 🚀 Key Features

*   **MATLAB Ensemble Architecture:** Employs a highly accurate (~96%) majority-voting stack using Random Forest (Bagging), XGBoost (LogitBoost), and Kernel-based SVM (RBF) trained on 1026 clinical records.
*   **Self-Learning Pipeline:** Features a "Teaching Mode" that allows clinicians to confirm or override diagnoses. New data is appended to the dataset, triggering a live, programmatic MATLAB retraining cycle to continuously improve accuracy.
*   **Data-Driven Clinical Action Plans:** Generates specific, actionable clinical advice based on the patient's individual biomarker deviations from healthy population means.
*   **Premium Clinical Dashboard:** A dark-themed, glassmorphic UI designed for medical professionals with real-time risk assessment, smooth micro-animations, and CSS radar visualizations.
*   **Advanced Dataset Explorer:** Built-in tools to search, filter, and view the entire 1026-record Cleveland Heart Disease dataset.
*   **Robust Regularization:** The AI models are regularized (e.g., MinLeafSize, controlled Learning Rates) to prevent overfitting and guarantee reliable real-world clinical performance.

## 🛠️ Technology Stack

*   **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript, jQuery
*   **Backend:** Python 3 (Flask)
*   **AI Engine:** MATLAB Engine API for Python
*   **Algorithms:** `fitcensemble` (Bag/LogitBoost), `fitcsvm` (RBF)

## 📦 Requirements

*   Python 3.8+
*   MATLAB (R2023a or newer) with Machine Learning Toolbox installed
*   MATLAB Engine API for Python

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/S1ddharthS/CardioScan.git
    cd CardioScan
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install Flask
    ```

3.  **Install MATLAB Engine for Python:**
    Navigate to your MATLAB installation folder and run the setup. For example:
    ```bash
    cd "C:\Program Files\MATLAB\R2023b\extern\engines\python"
    python setup.py install
    ```

## 🏥 Usage

1.  Start the Flask server:
    ```bash
    python app.py
    ```
2.  The server will automatically detect the dataset (`heart.csv`) and trigger a background MATLAB training cycle if the model doesn't exist.
3.  Open your browser and navigate to:
    ```
    http://127.0.0.1:5000
    ```
4.  Enter the patient's vitals (defaults represent a stable, healthy baseline).
5.  Click **Run AI Analysis** to get the risk assessment and clinical action plan!

## 📁 Project Structure

*   `app.py`: Flask backend, API endpoints, and MATLAB engine integration.
*   `templates/index.html`: The MED-OS frontend dashboard.
*   `predict_heart.m`: MATLAB script for ensemble inference, voting, and deviation analysis.
*   `train_model.m`: MATLAB script for 5-fold cross-validation training and regularization.
*   `retrain_model.m`: Wrapper script for programmatic self-learning.
*   `heart.csv`: 1026-record clinical dataset.
*   `heart_ai_model.mat`: Persisted MATLAB ensemble model.

## ⚖️ Note on Dataset Labeling
This project correctly maps the target labels of the Kaggle/UCI dataset where `target=0` indicates the *presence of heart disease* (High Risk) and `target=1` indicates *absence* (Low Risk).

## 📄 License
This project is intended for educational, clinical research, and demonstrative purposes.
