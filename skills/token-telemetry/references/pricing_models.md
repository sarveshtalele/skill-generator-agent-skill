# 💰 Multi-Model Pricing Catalog & Dual-Currency Formulas (USD & INR)

This reference documents the official per-million token rates in both **USD ($)** and **INR (₹)** based on the standard conversion rate of **1 USD = 87.50 INR**.

---

## 📊 Standard Unit Rates (per 1,000,000 Tokens)

### 🟣 Anthropic Claude Family

| Model Name | Model Identifier | Input Rate ($ / ₹) | Output Rate ($ / ₹) | Cache Read Rate ($ / ₹) | Cache Write Rate ($ / ₹) |
|:---|:---|:---:|:---:|:---:|:---:|
| **Claude 3.7 Sonnet** | `claude-3-7-sonnet` | **$3.00** *(₹262.50)* | **$15.00** *(₹1,312.50)* | **$0.30** *(₹26.25)* | **$3.75** *(₹328.13)* |
| **Claude 3.5 Sonnet** | `claude-3-5-sonnet` | **$3.00** *(₹262.50)* | **$15.00** *(₹1,312.50)* | **$0.30** *(₹26.25)* | **$3.75** *(₹328.13)* |
| **Claude 3.5 Haiku** | `claude-3-5-haiku` | **$0.80** *(₹70.00)* | **$4.00** *(₹350.00)* | **$0.08** *(₹7.00)* | **$1.00** *(₹87.50)* |
| **Claude 3 Opus** | `claude-3-opus` | **$15.00** *(₹1,312.50)* | **$75.00** *(₹6,562.50)* | **$1.50** *(₹131.25)* | **$18.75** *(₹1,640.63)* |

---

### 🟢 Google Gemini Family (Antigravity)

| Model Name | Model Identifier | Input Rate ($ / ₹) | Output Rate ($ / ₹) | Cache Read Rate ($ / ₹) | Cache Write Rate ($ / ₹) |
|:---|:---|:---:|:---:|:---:|:---:|
| **Gemini 2.0 Pro** | `gemini-2-0-pro` | **$1.25** *(₹109.38)* | **$5.00** *(₹437.50)* | **$0.31** *(₹27.13)* | **$1.25** *(₹109.38)* |
| **Gemini 2.0 Flash** | `gemini-2-0-flash` | **$0.10** *(₹8.75)* | **$0.40** *(₹35.00)* | **$0.025** *(₹2.19)* | **$0.10** *(₹8.75)* |
| **Gemini 1.5 Pro** | `gemini-1-5-pro` | **$1.25** *(₹109.38)* | **$5.00** *(₹437.50)* | **$0.31** *(₹27.13)* | **$1.25** *(₹109.38)* |

---

### 🔵 OpenAI GPT Family

| Model Name | Model Identifier | Input Rate ($ / ₹) | Output Rate ($ / ₹) | Cache Read Rate ($ / ₹) | Cache Write Rate ($ / ₹) |
|:---|:---|:---:|:---:|:---:|:---:|
| **GPT-4o** | `gpt-4o` | **$2.50** *(₹218.75)* | **$10.00** *(₹875.00)* | **$1.25** *(₹109.38)* | **$2.50** *(₹218.75)* |
| **GPT-4o mini** | `gpt-4o-mini` | **$0.15** *(₹13.13)* | **$0.60** *(₹52.50)* | **$0.075** *(₹6.56)* | **$0.15** *(₹13.13)* |

---

### 🔴 Nous Research Hermes Agent

| Model Name | Model Identifier | Input Rate ($ / ₹) | Output Rate ($ / ₹) | Cache Read Rate ($ / ₹) | Cache Write Rate ($ / ₹) |
|:---|:---|:---:|:---:|:---:|:---:|
| **Hermes 3 405B** | `hermes-3-llama-3-1-405b` | **$1.50** *(₹131.25)* | **$3.00** *(₹262.50)* | **$0.50** *(₹43.75)* | **$1.50** *(₹131.25)* |
| **Hermes 3 70B** | `hermes-3-llama-3-1-70b` | **$0.40** *(₹35.00)* | **$0.80** *(₹70.00)* | **$0.10** *(₹8.75)* | **$0.40** *(₹35.00)* |

---

## 🧮 Cost Calculation Formulas

### USD Calculation:
$$\text{Cost}_{\text{USD}} = \left(\frac{T_{\text{in}}}{10^6} \times P_{\text{in}}\right) + \left(\frac{T_{\text{out}}}{10^6} \times P_{\text{out}}\right) + \left(\frac{T_{\text{read}}}{10^6} \times P_{\text{read}}\right) + \left(\frac{T_{\text{write}}}{10^6} \times P_{\text{write}}\right)$$

### INR Calculation:
$$\text{Cost}_{\text{INR}} = \text{Cost}_{\text{USD}} \times R_{\text{INR/USD}}$$
*(where $R_{\text{INR/USD}} = 87.50$ by default).*
