# Scoring Formulas — 8-Dimension Quality Assessment

Reference document for understanding and computing the composite quality score. Load this file when interpreting scorecard results or debugging dimension scores.

## Composite Score

$$\text{Score}_{\text{overall}} = \sum_{d \in \text{dimensions}} W_d \times S_d$$

Where $W_d$ is the weight and $S_d$ is the dimension score (0-100).

## Dimension Weights

| # | Dimension | Weight | Target |
|:--|:--|:--|:--|
| 1 | Specification Compliance | 10% | 0 errors |
| 2 | Content Quality | 15% | < 500 lines, examples present |
| 3 | Functional Correctness | 25% | ≥ 80% pass rate |
| 4 | Skill Lift Delta | 15% | Positive lift over baseline |
| 5 | Trigger Quality (F1) | 10% | F1 ≥ 0.80 |
| 6 | Reliability | 5% | 0 failures, 0 timeouts |
| 7 | Efficiency | 5% | < 8000 tokens, < 60s |
| 8 | Security | 15% | 0 Critical, 0 High |

## Individual Dimension Formulas

### 1. Specification Compliance (10%)

$$S_1 = \max(0,\; 100 - 25 \times E)$$

Where $E$ = number of spec errors (missing frontmatter, invalid name, broken references).

### 2. Content Quality (15%)

$$S_2 = 100 - D_{\text{length}} - D_{\text{examples}} - D_{\text{disclosure}}$$

| Deduction | Condition | Points |
|:--|:--|:--|
| $D_{\text{length}}$ | SKILL.md > 500 lines | -20 |
| $D_{\text{examples}}$ | No worked examples or code blocks | -10 |
| $D_{\text{disclosure}}$ | No progressive disclosure (no references/ or scripts/) | -10 |

### 3. Functional Correctness (25%)

$$S_3 = \frac{\text{passed assertions}}{\text{total assertions}} \times 100$$

Hard-block trigger: $S_3 < 80$ forces gate = BLOCK regardless of overall score.

### 4. Skill Lift Delta (15%)

$$S_4 = \text{clamp}\!\left(\frac{\Delta_{\text{pass\_rate}} + 0.20}{0.70} \times 100,\; 0,\; 100\right)$$

Where $\Delta_{\text{pass\_rate}} = \text{with\_skill\_pass\_rate} - \text{without\_skill\_pass\_rate}$.

- A skill that matches baseline ($\Delta = 0$) scores 28.6
- A skill that adds 0.50 lift scores 100
- A skill worse than baseline ($\Delta < -0.20$) scores 0

### 5. Trigger Quality — F1 Score (10%)

$$S_5 = F_1 \times 100$$

$$F_1 = 2 \times \frac{P \times R}{P + R}$$

Where:
- $P$ (Precision) = true triggers / (true triggers + false triggers)
- $R$ (Recall) = true triggers / (true triggers + missed triggers)

### 6. Reliability (5%)

$$S_6 = 100 - 50F - 25T$$

Where $F$ = number of execution failures, $T$ = number of timeouts.

### 7. Efficiency (5%)

$$S_7 = 100 - D_{\text{tokens}} - D_{\text{time}}$$

| Deduction | Condition | Points |
|:--|:--|:--|
| $D_{\text{tokens}}$ | Total tokens > 8000 | -30 |
| $D_{\text{time}}$ | Wall-clock time > 60s | -20 |

### 8. Security (15%)

$$S_8 = \max(0,\; 100 - 100C - 40H - 15M)$$

Where $C$ = Critical findings, $H$ = High findings, $M$ = Medium findings.

Hard-block trigger: Any Critical finding forces gate = BLOCK regardless of overall score.

## Quality Gate Decision

| Gate | Condition |
|:--|:--|
| ✅ **PASS** | $\text{Score} \geq 95$ AND no Critical/High security AND functional ≥ 80% |
| ⚠️ **WARN** | $75 \leq \text{Score} < 95$ AND no Critical security |
| ❌ **BLOCK** | $\text{Score} < 75$ OR any Critical security OR functional < 80% |
