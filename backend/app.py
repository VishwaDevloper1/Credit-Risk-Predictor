from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib, pandas as pd, io, os, numpy as np
from sqlalchemy import create_engine, Column, Integer, Float, String, MetaData, Table
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
DB_PATH = os.path.join(BASE_DIR, "predictions.db")

app = Flask(__name__)
CORS(app)

# setup sqlite
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={'check_same_thread': False})
metadata = MetaData()

predictions = Table('predictions', metadata,
    Column('id', Integer, primary_key=True),
    Column('income', Integer),
    Column('loan_amount', Float),
    Column('credit_history', Integer),
    Column('age', Integer),
    Column('gender', String),
    Column('married', String),
    Column('education', String),
    Column('self_employed', String),
    Column('dependents', String),
    Column('property_area', String),
    Column('loan_term', Integer),
    Column('dti', Float),
    Column('lta', Float),
    Column('risk_score', Float),
    Column('decision', String)
)

metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def ensure_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    # train small synthetic model fast
    from sklearn.ensemble import RandomForestClassifier
    rng = np.random.default_rng(1)
    n = 400
    df = pd.DataFrame({
        'Income': rng.integers(2000,12000,n),
        'LoanAmount': rng.integers(50,500,n),
        'Credit_History': rng.integers(0,2,n),
        'Age': rng.integers(21,60,n),
        'Gender': rng.choice(['Male','Female'], size=n),
        'Married': rng.choice(['Yes','No'], size=n),
        'Education': rng.choice(['Graduate','Not Graduate'], size=n),
        'Self_Employed': rng.choice(['No','Yes'], size=n),
        'Dependents': rng.choice(['0','1','2','3+'], size=n),
        'Property_Area': rng.choice(['Urban','Semiurban','Rural'], size=n),
        'Loan_Amount_Term': rng.integers(60,480,n)
    })
    score = 0.4*(df['Income']/df['Income'].max()) + 0.3*df['Credit_History'] + 0.2*(1-df['LoanAmount']/df['LoanAmount'].max())
    prob = (score - score.min())/(score.max()-score.min())
    df['Loan_Status'] = (prob > 0.5).astype(int)
    df['dti'] = df['LoanAmount'] / df['Income']
    df['lta'] = df['LoanAmount'] / df['Age']
    X = df[['Income','LoanAmount','Credit_History','Age','dti','lta']]
    X = pd.concat([X, pd.get_dummies(df[['Gender','Married','Education','Self_Employed','Dependents','Property_Area']], drop_first=True)], axis=1)
    y = df['Loan_Status']
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    return model

model = ensure_model()

def add_engineered_features(df):
    df = df.copy()
    df['dti'] = df['LoanAmount'] / df['Income'].replace(0, pd.NA)
    df['lta'] = df['LoanAmount'] / df['Age'].replace(0, pd.NA)
    df['dti'] = df['dti'].fillna(0.0)
    df['lta'] = df['lta'].fillna(0.0)
    return df

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    df = pd.DataFrame([data])
    df.rename(columns={'income':'Income','loan_amount':'LoanAmount','credit_history':'Credit_History','age':'Age','gender':'Gender','married':'Married','education':'Education','self_employed':'Self_Employed','dependents':'Dependents','property_area':'Property_Area','loan_term':'Loan_Amount_Term'}, inplace=True)
    df = add_engineered_features(df)
    order = ['Income','LoanAmount','Credit_History','Age','Gender','Married','Education','Self_Employed','Dependents','Property_Area','Loan_Amount_Term','dti','lta']
    X = df[order]
    # convert to model input: create dummies similar to training
    X_proc = pd.get_dummies(X, drop_first=True)
    # align columns with model if possible
    try:
        model_cols = model.feature_names_in_
    except Exception:
        model_cols = X_proc.columns
    for c in model_cols:
        if c not in X_proc.columns:
            X_proc[c] = 0
    X_proc = X_proc[model_cols]
    proba = model.predict_proba(X_proc)[:,1][0]
    decision = 'Approved' if proba >= 0.5 else 'Rejected'
    # store in DB
    conn = engine.connect()
    ins = predictions.insert().values(
        income=int(df['Income'].iloc[0]), loan_amount=float(df['LoanAmount'].iloc[0]), credit_history=int(df['Credit_History'].iloc[0]), age=int(df['Age'].iloc[0]),
        gender=str(df['Gender'].iloc[0]), married=str(df['Married'].iloc[0]), education=str(df['Education'].iloc[0]), self_employed=str(df['Self_Employed'].iloc[0]),
        dependents=str(df['Dependents'].iloc[0]), property_area=str(df['Property_Area'].iloc[0]), loan_term=int(df['Loan_Amount_Term'].iloc[0]), dti=float(df['dti'].iloc[0]), lta=float(df['lta'].iloc[0]),
        risk_score=float(proba), decision=decision
    )
    conn.execute(ins)
    conn.close()
    return jsonify({'risk_score': float(proba), 'decision': decision})

@app.route('/history', methods=['GET'])
def history():
    conn = engine.connect()
    res = conn.execute(predictions.select().order_by(predictions.c.id.desc()).limit(200))
    rows = [dict(r) for r in res.fetchall()]
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
