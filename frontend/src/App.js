import React, { useState } from "react";
import "./index.css";

const API_BASE = process.env.REACT_APP_API_BASE; // Must be set in Vercel dashboard

function App() {
  const [form, setForm] = useState({
    income: 5000,
    loan_amount: 150,
    credit_history: 1,
    age: 30,
    gender: "Male",
    married: "Yes",
    education: "Graduate",
    self_employed: "No",
    dependents: "0",
    property_area: "Urban",
    loan_term: 360,
  });

  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const numericFields = ["income", "loan_amount", "credit_history", "age", "loan_term"];
    setForm((prev) => ({
      ...prev,
      [name]: numericFields.includes(name) ? parseFloat(value) || 0 : value,
    }));
  };

  const predict = async () => {
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error("Network response not ok");
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Prediction error:", err);
      alert("Error connecting to backend!");
    }
  };

  return (
    <div className="container">
      <h2>💳 Credit Risk Predictor</h2>
      <div className="form-container">
        <div className="form-section">
          <label>Income:</label>
          <input type="number" name="income" value={form.income} onChange={handleChange} />

          <label>Loan Amount:</label>
          <input type="number" name="loan_amount" value={form.loan_amount} onChange={handleChange} />

          <label>Credit History:</label>
          <select name="credit_history" value={form.credit_history} onChange={handleChange}>
            <option value={1}>1</option>
            <option value={0}>0</option>
          </select>

          <label>Age:</label>
          <input type="number" name="age" value={form.age} onChange={handleChange} />

          <label>Gender:</label>
          <select name="gender" value={form.gender} onChange={handleChange}>
            <option>Male</option>
            <option>Female</option>
          </select>

          <label>Married:</label>
          <select name="married" value={form.married} onChange={handleChange}>
            <option>Yes</option>
            <option>No</option>
          </select>

          <label>Education:</label>
          <select name="education" value={form.education} onChange={handleChange}>
            <option>Graduate</option>
            <option>Not Graduate</option>
          </select>

          <label>Self Employed:</label>
          <select name="self_employed" value={form.self_employed} onChange={handleChange}>
            <option>No</option>
            <option>Yes</option>
          </select>

          <label>Dependents:</label>
          <select name="dependents" value={form.dependents} onChange={handleChange}>
            <option>0</option>
            <option>1</option>
            <option>2</option>
            <option>3+</option>
          </select>

          <label>Property Area:</label>
          <select name="property_area" value={form.property_area} onChange={handleChange}>
            <option>Urban</option>
            <option>Semiurban</option>
            <option>Rural</option>
          </select>

          <label>Loan Term (months):</label>
          <input type="number" name="loan_term" value={form.loan_term} onChange={handleChange} />

          <button className="btn" onClick={predict}>🚀 Predict</button>
        </div>
      </div>

      {result && (
        <div className="result-card">
          <h3>Result</h3>
          <p><strong>Decision:</strong> {result.decision}</p>
          <p><strong>Risk Score:</strong> {result.risk_score.toFixed(3)}</p>
        </div>
      )}
    </div>
  );
}

export default App;
