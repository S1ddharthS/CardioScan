# CardioScan AI

CardioScan is an advanced clinical diagnostic dashboard that uses a neural network engine (MATLAB) to assess cardiovascular risk based on 13 clinical biomarkers.

## Features

*   **Clinical Diagnostic Dashboard:** A modern, dark-themed UI (MED-OS v2.1) designed for clinicians.
*   **13 Biomarker Inputs:** Collects essential patient data including Age, Sex, Blood Pressure, Cholesterol, Fasting Blood Sugar, Max Heart Rate, ST Slope, Major Vessels, Resting ECG, Chest Pain Type, Exercise Angina, ST Depression (Oldpeak), and Thalassemia.
*   **Neural Network Inference:** Uses a trained MATLAB machine learning model to calculate risk percentage and confidence.
*   **Simulation Fallback:** If the MATLAB engine is not available, the application seamlessly falls back to a built-in Python simulation engine.
*   **Risk Analysis:** Dynamically calculates and compares average vitals for low-risk vs. high-risk patients based on the dataset.
*   **Responsive UI:** Fully responsive design with interactive elements and micro-animations.

## Requirements

*   Python 3.8+
*   Flask
*   pdf2image
*   pytesseract
*   MATLAB Engine API for Python (Optional, for full neural network functionality)

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/S1ddharthS/CardioScan.git
    cd CardioScan
    ```

2.  Install the required Python packages:
    ```bash
    pip install Flask pdf2image pytesseract
    ```

3.  (Optional) Install the MATLAB Engine API for Python if you have MATLAB installed:
    *   Navigate to your MATLAB installation folder (e.g., `C:\Program Files\MATLAB\R2023b\extern\engines\python`)
    *   Run `python setup.py install`

## Usage

1.  Start the Flask server:
    ```bash
    python app.py
    ```

2.  Open your web browser and navigate to:
    ```
    http://127.0.0.1:5000
    ```

3.  Enter the patient's vitals on the dashboard and click **INITIATE NEURAL ANALYSIS** to get the risk assessment.

## Project Structure

*   `app.py`: The main Flask backend application.
*   `templates/index.html`: The frontend clinical dashboard UI.
*   `predict_heart.m`: MATLAB script used by the backend for model inference.
*   `train_model.m`: MATLAB script for training the neural network.
*   `heart_ai_model.mat`: The trained MATLAB neural network model.
*   `heart.csv`: The clinical dataset used for analysis and training.
*   `create_heart_data.py`: Script to generate synthetic training data.

## License

This project is for educational and demonstrative purposes.
