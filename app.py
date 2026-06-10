from flask import Flask, render_template, request, jsonify
import os
import csv
import threading
import json
from datetime import datetime

app = Flask(__name__)

# ===== MATLAB Engine Setup =====
MATLAB_AVAILABLE = False
eng = None
MODEL_TRAINED = False
MODEL_INFO = {
    'acc_rf': 0, 'acc_xgb': 0, 'acc_svm': 0,
    'ensemble_acc': 0, 'n_records': 0,
    'last_trained': None, 'training': False
}

BIOMARKER_NAMES = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
                   'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heart.csv')

try:
    import matlab.engine  # type: ignore
    import matlab  # type: ignore
    print("Initializing MATLAB Engine...")
    eng = matlab.engine.start_matlab()
    # Add project directory to MATLAB path
    eng.addpath(os.path.dirname(os.path.abspath(__file__)), nargout=0)
    MATLAB_AVAILABLE = True
    print("MATLAB Engine initialized successfully.")
    
    # Auto-train if model doesn't exist
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heart_ai_model.mat')
    if not os.path.exists(model_path):
        print("No trained model found. Auto-training...")
        MODEL_INFO['training'] = True
        try:
            results = eng.train_model()
            MODEL_INFO['acc_rf'] = results[0][0]
            MODEL_INFO['acc_xgb'] = results[0][1]
            MODEL_INFO['acc_svm'] = results[0][2]
            MODEL_INFO['ensemble_acc'] = results[0][3]
            MODEL_INFO['n_records'] = int(results[0][4])
            MODEL_INFO['last_trained'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            MODEL_INFO['training'] = False
            MODEL_TRAINED = True
            print(f"Model trained. Ensemble accuracy: {MODEL_INFO['ensemble_acc']:.1f}%")
        except Exception as e:
            print(f"Auto-train failed: {e}")
            MODEL_INFO['training'] = False
    else:
        MODEL_TRAINED = True
        MODEL_INFO['last_trained'] = datetime.fromtimestamp(
            os.path.getmtime(model_path)).strftime('%Y-%m-%d %H:%M:%S')
        print("Existing model found. Ready.")

except ImportError:
    print("WARNING: MATLAB Engine API not found. Running in Simulation Mode.")
    eng = None


def get_csv_rows():
    """Read heart.csv and return list of row dicts."""
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def compute_group_stats(rows, biomarker_cols):
    """Compute per-biomarker averages for a group of rows."""
    count = len(rows)
    if count == 0:
        return {'count': 0, 'biomarkers': {c: 0 for c in biomarker_cols}}
    bio = {}
    for col in biomarker_cols:
        vals = []
        for r in rows:
            try:
                vals.append(float(r.get(col, 0)))
            except (ValueError, TypeError):
                pass
        bio[col] = round(sum(vals) / len(vals), 2) if vals else 0
    return {'count': count, 'biomarkers': bio}


def generate_clinical_plan(risk, raw_data, feature_importances=None, deviations=None, low_risk_stats=None):
    """Generate accurate, data-driven clinical action plan based on actual biomarker analysis."""
    recs = []
    
    age = raw_data[0]
    sex = raw_data[1]
    cp = raw_data[2]
    trestbps = raw_data[3]
    chol = raw_data[4]
    fbs = raw_data[5]
    restecg = raw_data[6]
    thalach = raw_data[7]
    exang = raw_data[8]
    oldpeak = raw_data[9]
    slope = raw_data[10]
    ca = raw_data[11]
    thal = raw_data[12]
    
    if risk > 50:
        # HIGH RISK — specific, actionable recommendations
        recs.append("Schedule an urgent consultation with a cardiologist for comprehensive evaluation.")
        
        # Blood pressure analysis
        if trestbps > 140:
            recs.append(f"Resting BP is {int(trestbps)} mmHg (Stage 2 Hypertension). Initiate antihypertensive therapy immediately. Target: <130/80 mmHg.")
        elif trestbps > 130:
            recs.append(f"Resting BP is {int(trestbps)} mmHg (Stage 1 Hypertension). Consider ACE inhibitors or ARBs. Lifestyle modifications recommended.")
        
        # Cholesterol analysis
        if chol > 240:
            recs.append(f"Cholesterol at {int(chol)} mg/dL is high. Initiate high-intensity statin therapy (e.g., Atorvastatin 40-80mg). Target: LDL <70 mg/dL.")
        elif chol > 200:
            recs.append(f"Cholesterol at {int(chol)} mg/dL is borderline high. Consider moderate-intensity statin. Adopt Mediterranean diet.")
        
        # ST Depression
        if oldpeak > 2.0:
            recs.append(f"Significant ST depression (Oldpeak: {oldpeak}). Consider stress echocardiography or coronary angiography to evaluate ischemia.")
        elif oldpeak > 1.0:
            recs.append(f"Moderate ST depression (Oldpeak: {oldpeak}). Exercise stress test recommended to evaluate myocardial ischemia.")
        
        # Exercise-induced angina
        if exang == 1:
            recs.append("Exercise-induced angina detected. Restrict physical exertion. Evaluate for stable angina with functional testing.")
        
        # Max heart rate
        if thalach < 120:
            recs.append(f"Max heart rate severely reduced ({int(thalach)} bpm). Evaluate chronotropic incompetence. Consider Holter monitoring.")
        elif thalach < 140:
            recs.append(f"Max heart rate is below expected ({int(thalach)} bpm). Monitor exercise tolerance and consider cardiac rehabilitation.")
        
        # Major vessels
        if ca >= 2:
            recs.append(f"{int(ca)} major vessels show fluoroscopy coloring. Evaluate for significant coronary artery disease. Angioplasty or CABG may be indicated.")
        elif ca == 1:
            recs.append("One major vessel shows coloring. Continue monitoring; consider CT coronary angiography for detailed assessment.")
        
        # Thalassemia
        if thal == 2:
            recs.append("Fixed defect detected on thallium scan. Suggests prior myocardial infarction. Evaluate for residual ischemia.")
        elif thal == 3:
            recs.append("Reversible defect on thallium scan. Suggests active ischemia. Urgent coronary evaluation recommended.")
        
        # Chest pain type
        if cp == 0:
            recs.append("Typical angina pattern reported. High specificity for coronary artery disease. Prioritize invasive evaluation.")
        
        # Fasting blood sugar
        if fbs == 1:
            recs.append("Elevated fasting blood sugar (>120 mg/dL). Screen for diabetes mellitus. HbA1c and oral glucose tolerance test recommended.")
        
        # ECG abnormality
        if restecg == 1:
            recs.append("ST-T wave abnormality on resting ECG. Correlate with clinical presentation. Serial ECGs recommended.")
        elif restecg == 2:
            recs.append("Left ventricular hypertrophy detected on ECG. Evaluate for hypertensive heart disease. Echocardiogram recommended.")
        
        # Age-specific
        if age > 65:
            recs.append("Age >65 increases baseline cardiovascular risk. Ensure comprehensive geriatric cardiac assessment.")
        
        # Slope
        if slope == 2:
            recs.append("Downsloping ST segment during exercise. This is the most concerning pattern — strongly consider coronary catheterization.")
        
    else:
        # LOW RISK — preventive maintenance
        recs.append("Cardiovascular parameters within acceptable range. Maintain current health regimen.")
        recs.append("Continue regular moderate-intensity exercise (at least 150 minutes/week).")
        recs.append("Follow a heart-healthy diet: Mediterranean or DASH-style, rich in fiber, vegetables, and lean proteins.")
        
        if trestbps > 120:
            recs.append(f"BP at {int(trestbps)} mmHg is borderline. Monitor regularly and reduce sodium intake (<2300 mg/day).")
        
        if chol > 200:
            recs.append(f"Cholesterol at {int(chol)} mg/dL is borderline. Incorporate soluble fiber (oats, legumes) and omega-3 fatty acids.")
        
        if fbs == 1:
            recs.append("Fasting blood sugar elevated. Monitor HbA1c annually. Reduce simple carbohydrates.")
        
        if age > 50:
            recs.append("Schedule annual cardiovascular screening including lipid panel and blood pressure check.")
        
        if oldpeak > 0.5:
            recs.append(f"Minor ST depression noted (Oldpeak: {oldpeak}). No immediate concern but worth tracking over time.")
    
    return recs


# ===== ROUTES =====

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Read heart.csv and return full dataset statistics."""
    try:
        rows = get_csv_rows()
        if not rows:
            return jsonify({'success': False, 'error': 'heart.csv not found or empty'})
        
        total = len(rows)
        target_col = None
        for col in ['target', 'num', 'condition', 'output']:
            if col in rows[0]:
                target_col = col
                break
        if not target_col:
            target_col = list(rows[0].keys())[-1]
        
        # In this dataset: 0 = Disease (High Risk), 1 = Healthy (Low Risk)
        low_rows = [r for r in rows if float(r[target_col]) == 1]
        high_rows = [r for r in rows if float(r[target_col]) == 0]
        low_stats = compute_group_stats(low_rows, BIOMARKER_NAMES)
        high_stats = compute_group_stats(high_rows, BIOMARKER_NAMES)
        overall = compute_group_stats(rows, BIOMARKER_NAMES)
        
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
            'model_available': MATLAB_AVAILABLE,
            'model_trained': MODEL_TRAINED,
            'model_info': MODEL_INFO
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/dataset', methods=['GET'])
def get_dataset():
    """Return heart.csv data as JSON for the Dataset Explorer."""
    try:
        rows = get_csv_rows()
        if not rows:
            return jsonify({'success': False, 'error': 'heart.csv not found'})
        
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


@app.route('/api/model_info', methods=['GET'])
def get_model_info():
    """Return current model accuracy and training info."""
    return jsonify({
        'success': True,
        'matlab_available': MATLAB_AVAILABLE,
        'model_trained': MODEL_TRAINED,
        'info': MODEL_INFO
    })


@app.route('/predict', methods=['POST'])
def predict():
    try:
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
        
        feature_importances = None
        deviations = None
        model_votes = {'rf': -1, 'xgb': -1, 'svm': -1}
        
        if MATLAB_AVAILABLE and MODEL_TRAINED:
            ml_data = matlab.double(raw_data)
            out = eng.predict_heart(ml_data)
            
            # Parse extended output: [risk, conf, rf, xgb, svm, imp(1:13), dev(1:13)]
            risk = out[0][0]
            confidence = out[0][1]
            model_votes['rf'] = int(out[0][2])
            model_votes['xgb'] = int(out[0][3])
            model_votes['svm'] = int(out[0][4])
            
            feature_importances = {}
            deviations = {}
            for i, name in enumerate(BIOMARKER_NAMES):
                feature_importances[name] = round(out[0][5 + i] * 100, 2)
                deviations[name] = round(out[0][18 + i], 3)
        else:
            # Simulation fallback
            import random
            risk_base = raw_data[0] * 0.4 + raw_data[3] * 0.1
            rf_risk = min(99.0, max(5.0, risk_base + random.uniform(-5, 5)))
            xgb_risk = min(99.0, max(5.0, risk_base + random.uniform(-10, 10)))
            svm_risk = min(99.0, max(5.0, risk_base + random.uniform(-8, 8)))
            
            votes = sum([1 if r > 50 else 0 for r in [rf_risk, xgb_risk, svm_risk]])
            avg_prob = (rf_risk + xgb_risk) / 2
            
            model_votes['rf'] = 1 if rf_risk > 50 else 0
            model_votes['xgb'] = 1 if xgb_risk > 50 else 0
            model_votes['svm'] = 1 if svm_risk > 50 else 0
            
            if votes >= 2:
                risk = max(51.0, avg_prob)
                confidence = 96.5 if votes == 3 else 66.6
            else:
                risk = min(49.0, avg_prob)
                confidence = 96.5 if votes == 0 else 66.6
        
        # Explainable AI (XAI) - Risk driver analysis
        xai_reason = "Telemetry within optimal bounds. No critical drivers."
        if risk > 50:
            drivers = []
            if raw_data[3] > 130:
                drivers.append(("Blood Pressure", (raw_data[3] - 120) / 120))
            if raw_data[4] > 200:
                drivers.append(("Cholesterol", (raw_data[4] - 200) / 200))
            if raw_data[9] > 1.0:
                drivers.append(("ST Depression (Oldpeak)", raw_data[9] / 2))
            if raw_data[8] == 1.0:
                drivers.append(("Exercise Induced Angina", 1.0))
            if raw_data[7] < 130:
                drivers.append(("Reduced Max Heart Rate", (150 - raw_data[7]) / 150))
            if raw_data[11] > 0:
                drivers.append(("Major Vessels Colored", raw_data[11] / 3))
            if raw_data[12] >= 2:
                drivers.append(("Thalassemia Defect", 0.8))
            
            if drivers:
                drivers.sort(key=lambda x: x[1], reverse=True)
                top = drivers[0][0]
                if len(drivers) > 1:
                    xai_reason = f"Risk primarily driven by elevated/abnormal {top}, with contributing factors: {', '.join(d[0] for d in drivers[1:3])}."
                else:
                    xai_reason = f"Risk primarily driven by elevated/abnormal {top}."
            else:
                xai_reason = "Risk driven by a complex combination of minor biomarker deviations."
        
        # Generate clinical action plan
        clinical_plan = generate_clinical_plan(risk, raw_data, feature_importances, deviations)
        
        return jsonify({
            'success': True,
            'risk': round(risk, 2),
            'confidence': round(confidence, 1),
            'xai_reason': xai_reason,
            'model_votes': model_votes,
            'feature_importances': feature_importances,
            'deviations': deviations,
            'clinical_plan': clinical_plan,
            'matlab_used': MATLAB_AVAILABLE and MODEL_TRAINED
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/add_record', methods=['POST'])
def add_record():
    """Self-learning: Add new patient record to dataset and retrain model."""
    global MODEL_TRAINED, MODEL_INFO
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'})
        
        # Validate required fields
        required = BIOMARKER_NAMES + ['target']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'})
        
        # Append to CSV
        row = [float(data[name]) for name in BIOMARKER_NAMES] + [int(data['target'])]
        
        with open(CSV_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        new_count = len(get_csv_rows())
        
        # Retrain if MATLAB available
        retrain_result = None
        if MATLAB_AVAILABLE:
            MODEL_INFO['training'] = True
            try:
                results = eng.retrain_model()
                MODEL_INFO['acc_rf'] = results[0][0]
                MODEL_INFO['acc_xgb'] = results[0][1]
                MODEL_INFO['acc_svm'] = results[0][2]
                MODEL_INFO['ensemble_acc'] = results[0][3]
                MODEL_INFO['n_records'] = int(results[0][4])
                MODEL_INFO['last_trained'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                MODEL_INFO['training'] = False
                MODEL_TRAINED = True
                retrain_result = {
                    'acc_rf': MODEL_INFO['acc_rf'],
                    'acc_xgb': MODEL_INFO['acc_xgb'],
                    'acc_svm': MODEL_INFO['acc_svm'],
                    'ensemble_acc': MODEL_INFO['ensemble_acc']
                }
            except Exception as e:
                MODEL_INFO['training'] = False
                print(f"Retrain failed: {e}")
                retrain_result = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'new_record_count': new_count,
            'retrain_result': retrain_result,
            'message': f'Record added. Dataset now has {new_count} records.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/retrain', methods=['POST'])
def retrain():
    """Manually trigger model retrain."""
    global MODEL_TRAINED, MODEL_INFO
    if not MATLAB_AVAILABLE:
        return jsonify({'success': False, 'error': 'MATLAB not available'})
    
    if MODEL_INFO['training']:
        return jsonify({'success': False, 'error': 'Training already in progress'})
    
    MODEL_INFO['training'] = True
    try:
        results = eng.retrain_model()
        MODEL_INFO['acc_rf'] = results[0][0]
        MODEL_INFO['acc_xgb'] = results[0][1]
        MODEL_INFO['acc_svm'] = results[0][2]
        MODEL_INFO['ensemble_acc'] = results[0][3]
        MODEL_INFO['n_records'] = int(results[0][4])
        MODEL_INFO['last_trained'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        MODEL_INFO['training'] = False
        MODEL_TRAINED = True
        
        return jsonify({
            'success': True,
            'info': MODEL_INFO
        })
    except Exception as e:
        MODEL_INFO['training'] = False
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    print("CardioScan AI — Starting server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
