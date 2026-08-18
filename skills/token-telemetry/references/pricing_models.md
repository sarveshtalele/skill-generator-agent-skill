# 💰 Anthropic Claude Model Pricing Catalog & Cost Calculation Formulas

This document defines the official pricing rates and formula models for Claude 3, 3.5, and 3.7 families.

---

## 📊 Standard Rates (USD per Million Tokens)

| Model Family | Model Key | Base Input ($/1M) | Output / Completion ($/1M) | Prompt Cache Read ($/1M) | Prompt Cache Write ($/1M) |
|:---|:---|:---:|:---:|:---:|:---:|
| **Claude 3.7 Sonnet** | `claude-3-7-sonnet` | **$3.00** | **$15.00** | **$0.30** *(90% off)* | **$3.75** *(1.25x base)* |
| **Claude 3.5 Sonnet** | `claude-3-5-sonnet` | **$3.00** | **$15.00** | **$0.30** *(90% off)* | **$3.75** *(1.25x base)* |
| **Claude 3.5 Haiku** | `claude-3-5-haiku` | **$0.80** | **$4.00** | **$0.08** *(90% off)* | **$1.00** *(1.25x base)* |
| **Claude 3 Opus** | `claude-3-opus` | **$15.00** | **$75.00** | **$1.50** *(90% off)* | **$18.75** *(1.25x base)* |

---

## 🧮 Mathematical Cost Formula

$$\text{Total Cost} = \left(\frac{T_{\text{in}}}{10^6} \times P_{\text{in}}\right) + \left(\frac{T_{\text{out}}}{10^6} \times P_{\text{out}}\right) + \left(\frac{T_{\text{read}}}{10^6} \times P_{\text{read}}\right) + \left(\frac{T_{\text{write}}}{10^6} \times P_{\text{write}}\right)$$

Where:
- $T_{\text{in}}$: Non-cached prompt tokens
- $T_{\text{out}}$: Generated completion tokens
- $T_{\text{read}}$: Cache read tokens (90% cost savings)
- $T_{\text{write}}$: Cache creation tokens (5-minute TTL)

---

## 📈 Cache Hit Efficiency Metric

$$\text{Cache Hit Ratio (\%)} = \frac{T_{\text{read}}}{T_{\text{in}} + T_{\text{read}}} \times 100$$
