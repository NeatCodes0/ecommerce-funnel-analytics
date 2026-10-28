# Milestone 4: Segmentation & Statistical Hypothesis Testing

## 1. Two-Proportion Z-Test: Visitor Loyalty (New vs. Returning)
- **Null Hypothesis (H0):** The cart-to-purchase conversion rate of first-time visitors is identical to returning visitors ($p_1 = p_2$).
- **Alternative Hypothesis (H1):** The conversion rates are significantly different ($p_1 \neq p_2$).
- **Significance Level ($\alpha$):** 0.05
- **Result:** $p < 0.001 \implies$ Reject H0. Returning visitors show significantly higher cart commitment and purchasing intent compared to first-time visitors.

## 2. Chi-Square Test of Independence: Session Duration vs. Purchase Conversion
- **Null Hypothesis (H0):** Session duration bracket and purchase completion are completely independent variables.
- **Alternative Hypothesis (H1):** Session duration bracket significantly influences purchase likelihood.
- **Degrees of Freedom:** 3
- **Chi-Square Statistic:** 80,635.69
- **p-value:** < 0.0001 (Reject H0)
- **Conclusion:** Duration is a primary predictive signal of purchase intent. High-engagement sessions (>5 minutes) represent the highest return-on-investment cohort for on-site cart incentives.