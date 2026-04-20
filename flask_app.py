from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
from dotenv import load_dotenv
from db_manager import DBManager

load_dotenv()

app = Flask(__name__)

# ─── Load ML Model ───
def load_model():
    try:
        model  = joblib.load('models/ensemble_model.pkl')
        scaler = joblib.load('models/scaler.pkl')
        return model, scaler
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None

model, scaler = load_model()

# ─── Database ───
db = DBManager(
    host=os.getenv("DB_HOST", "localhost"),
    database=os.getenv("DB_NAME", "postgres"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "1234")
)
db.connect()
db.init_db()

# ─── Routes ───
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = {
            'duration':           float(data.get('duration', 0)),
            'src_bytes':          float(data.get('src_bytes', 0)),
            'dst_bytes':          float(data.get('dst_bytes', 0)),
            'hot':                float(data.get('hot', 0)),
            'num_failed_logins':  float(data.get('num_failed_logins', 0)),
            'logged_in':          float(data.get('logged_in', 0)),
            'num_compromised':    float(data.get('num_compromised', 0)),
            'num_file_creations': float(data.get('num_file_creations', 0)),
            'num_shells':         float(data.get('num_shells', 0)),
            'num_access_files':   float(data.get('num_access_files', 0)),
            'is_guest_login':     float(data.get('is_guest_login', 0)),
            'count':              float(data.get('count', 0)),
        }

        # Add hidden defaults the model expects
        full_features = features.copy()
        full_features.update({
            'land': 0.0, 'wrong_fragment': 0.0, 'urgent': 0.0,
            'root_shell': 0.0, 'su_attempted': 0.0, 'num_root': 0.0,
            'num_outbound_cmds': 0.0, 'is_host_login': 0.0
        })

        expected_order = [
            'duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment',
            'urgent', 'hot', 'num_failed_logins', 'logged_in',
            'num_compromised', 'root_shell', 'su_attempted', 'num_root',
            'num_file_creations', 'num_shells', 'num_access_files',
            'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count'
        ]
        ordered = {k: full_features[k] for k in expected_order}

        input_df = pd.DataFrame([ordered])
        input_scaled = scaler.transform(input_df)
        pred = int(model.predict(input_scaled)[0])
        prob = model.predict_proba(input_scaled)[0].tolist()

        # Log to database
        db_status = "ok"
        try:
            db.log_prediction(features, pred, prob[1])
        except Exception:
            db_status = "failed"

        return jsonify({
            'prediction': pred,
            'probability': prob,
            'confidence': round(max(prob) * 100, 1),
            'db_status': db_status
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def history():
    try:
        limit = request.args.get('limit', 20, type=int)
        rows = db.get_history(limit)
        result = []
        for row in rows:
            result.append({
                'id':           row[0],
                'timestamp':    str(row[1]),
                'duration':     row[2],
                'src_bytes':    row[3],
                'dst_bytes':    row[4],
                'hot':          row[5],
                'failed_logins':row[6],
                'logged_in':    row[7],
                'compromised':  row[8],
                'file_creations':row[9],
                'shells':       row[10],
                'access_files': row[11],
                'guest':        row[12],
                'count':        row[13],
                'prediction':   row[14],
                'probability':  row[15],
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("  CyberShield AI — Flask Server")
    print("=" * 50)
    app.run(debug=True, port=5000)
