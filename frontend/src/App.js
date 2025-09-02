import React, { useState } from "react";
import "./index.css";

const API_BASE = process.env.REACT_APP_API_BASE; // This should now be your Render backend URL

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
        {/* Form sections */}
        <div className="form-section">
          <label>Income:</label>
          <input type="number" name="income" value={form.income} onChange={handleChange} />
          <label>Loan Amount:</label>
          <input type="number" name="loan_amount" value={form.loan_amount} onChange={handleChange} />
          <label>Credit History:</label>
          <select name="credit_history" value={form.credit_history} onChange={handleChange}>
            <option value={1}>1</option>
            <option value={0
