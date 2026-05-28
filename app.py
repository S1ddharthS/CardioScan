from flask import Flask, render_template, request, jsonify
import os
import random
import re
import csv
import tempfile
from pdf2image import convert_from_path
import pytesseract

app = Flask(__name__)

# Try to start MATLAB Engine
try:
    import matlab.engine  # type: ignore
    import matlab  # type: ignore
    print("Initializing MATLAB Engine...")
    eng = matlab.engine.start_matlab()
    MATLAB_AVAILABLE = True
except ImportError:
    print("WARNING: MATLAB Engine API not found. Running in Simulation Mode.")
    eng = None
    MATLAB_AVAILABLE = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Read heart.csv and return full dataset statistics including per-biomarker averages for low/high risk."""
    try:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heart.csv')
        if not os.path.exists(csv_path):
            return jsonify({'success': False, 'error': 'heart.csv not found'})
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        total = len(rows)
        if total == 0:
            return jsonify({'success': False, 'error': 'Dataset is empty'})
        # Identify target column
        target_col = None
        for col in ['target', 'num', 'condition', 'output']:
            if col in rows[0]:
                target_col = col
                break
        if not target_col:
            target_col = list(rows[0].keys())[-1]

        biomarker_cols = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
                          'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']

        def compute_group(group_rows):
            count = len(group_rows)
            if count == 0:
                return {'count': 0, 'biomarkers': {c: 0 for c in biomarker_cols}}
            bio = {}
            for col in biomarker_cols:
                vals = []
                for r in group_rows:
                    try:
                        vals.append(float(r.get(col, 0)))
                    except (ValueError, TypeError):
                        pass
                bio[col] = round(sum(vals) / len(vals), 2) if vals else 0
            return {'count': count, 'biomarkers': bio}

        low_rows = [r for r in rows if float(r[target_col]) == 0]
        high_rows = [r for r in rows if float(r[target_col]) >= 1]
        low_stats = compute_group(low_rows)
        high_stats = compute_group(high_rows)
        overall = compute_group(rows)

        positive = len(high_rows)
        negative = len(low_rows)
        columns = list(rows[0].keys())

        return jsonify({
            'success': True,
            'total_records': total,
            'positive_cases': positive,
            'negative_cases': negative,
            'risk_rate': round((positive / total) * 100, 1),
            'avg_age': overall['biomarkers'].get('age', 0),
            'avg_cholesterol': overall['biomarkers'].get('chol', 0),
            'avg_blood_pressure': overall['biomarkers'].get('trestbps', 0),
            'low_risk': low_stats,
            'high_risk': high_stats,
            'overall': overall,
            'columns': columns,
            'model_available': MATLAB_AVAILABLE
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dataset', methods=['GET'])
def get_dataset():
    """Return heart.csv data as JSON for the Labs view."""
    try:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heart.csv')
        if not os.path.exists(csv_path):
            return jsonify({'success': False, 'error': 'heart.csv not found'})
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        clean_rows = []
        for row in rows:
            clean = {}
            for k, v in row.items():
                try:
                    clean[k] = round(float(v), 2)
                except (ValueError, TypeError):
                    clean[k] = v
            clean_rows.append(clean)
        return jsonify({
            'success': True,
            'columns': list(rows[0].keys()) if rows else [],
            'data': clean_rows,
            'total': len(clean_rows)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Collect values from the HTML form
        raw_data = [
            float(request.form['age']),
            float(request.form['sex']),
            float(request.form['cp']),
            float(request.form['trestbps']),
            float(request.form['chol']),
            float(request.form['fbs']),
            float(request.form['restecg']),
            float(request.form['thalach']),
            float(request.form['exang']),
            float(request.form['oldpeak']),
            float(request.form['slope']),
            float(request.form['ca']),
            float(request.form['thal'])
        ]
        
        if MATLAB_AVAILABLE:
            # Convert to MATLAB double array
            ml_data = matlab.double(raw_data)
            # Call the MATLAB function
            out = eng.predict_heart(ml_data)
            risk = out[0][0]
            confidence = out[0][1]
        else:
            # Simulation Mode
            print("SIMULATION MODE: Generating diagnostic risk score...")
            risk_base = float(raw_data[0]) * 0.4 + float(raw_data[3]) * 0.1
            risk = min(99.0, max(5.0, risk_base + random.uniform(-10, 10)))
            confidence = min(99.0, max(60.0, 75.0 + random.uniform(-10, 20)))
        
        return jsonify({
            'success': True, 
            'risk': round(risk, 2),
            'confidence': round(confidence, 1)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'})
            
        # Optional: Set Tesseract Path if needed based on standard Windows installation
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Save temp PDF
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, 'scan.pdf')
        file.save(pdf_path)
        
        # 1. OCR Image Processing
        # (Requires Poppler to be in PATH or specified)
        images = convert_from_path(pdf_path)
        full_text = ""
        for img in images:
            text = pytesseract.image_to_string(img)
            full_text += text + "\n"
            
        # Clean up
        os.remove(pdf_path)
        os.rmdir(temp_dir)
        
        # 2. Information Extraction via Regex Mapping
        # We will extract basic numbers if we find the keywords.
        # This is a simplified regex extractor tailored for medical vitals.
        text_lower = full_text.lower()
        
        def extract_val(pattern, default=0.0):
            match = re.search(pattern, text_lower)
            if match:
                try:
                    return float(match.group(1))
                except:
                    return default
            return default
            
        age = extract_val(r'age\s*[:\-]?\s*(\d+)')
        sex = 1.0 if 'male' in text_lower and 'female' not in text_lower else 0.0 # simplified
        trestbps = extract_val(r'blood pressure\s*[:\-]?\s*(\d+)', default=120)
        chol = extract_val(r'cholesterol\s*[:\-]?\s*(\d+)', default=200)
        thalach = extract_val(r'max\s*hr\s*[:\-]?\s*(\d+)', default=150)
        oldpeak = extract_val(r'oldpeak\s*[:\-]?\s*([\d\.]+)', default=1.0)
        ca = extract_val(r'major vessels\s*[:\-]?\s*(\d)', default=0)
        
        # Categoricals (heuristics)
        fbs = 1.0 if extract_val(r'fasting blood sugar\s*[:\-]?\s*(\d+)') > 120 else 0.0
        
        restecg = 0.0
        if 'st-t' in text_lower: restecg = 1.0
        elif 'hypertrophy' in text_lower: restecg = 2.0
        
        cp = 0.0
        if 'atypical' in text_lower: cp = 1.0
        elif 'non-anginal' in text_lower: cp = 2.0
        elif 'asymptomatic' in text_lower: cp = 3.0
        
        exang = 1.0 if 'exercise induced angina: yes' in text_lower else 0.0
        
        slope = 1.0
        if 'upsloping' in text_lower: slope = 0.0
        elif 'downsloping' in text_lower: slope = 2.0
        
        thal = 3.0
        if 'normal thal' in text_lower: thal = 1.0
        elif 'fixed defect' in text_lower: thal = 2.0
        
        raw_data = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
        
        # 3. Model Inference
        if MATLAB_AVAILABLE:
            ml_data = matlab.double(raw_data)
            out = eng.predict_heart(ml_data)
            risk = out[0][0]
            confidence = out[0][1]
        else:
            risk_base = age * 0.4 + trestbps * 0.1
            risk = min(99.0, max(5.0, risk_base + random.uniform(-10, 10)))
            confidence = min(99.0, max(60.0, 75.0 + random.uniform(-10, 20)))
            
        return jsonify({
            'success': True,
            'risk': round(risk, 2),
            'confidence': round(confidence, 1),
            'extracted': {
                'age': age, 'sex': sex, 'cp': cp, 'trestbps': trestbps,
                'chol': chol, 'fbs': fbs, 'restecg': restecg, 'thalach': thalach,
                'exang': exang, 'oldpeak': oldpeak, 'slope': slope, 'ca': ca, 'thal': thal
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
