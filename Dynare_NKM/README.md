# Small Open Economy New Keynesian Model

A linearized small open economy New Keynesian (SOE-NK) model implemented in Dynare to analyze the transmission of domestic and foreign shocks under different exchange rate regimes.

## 🎯 Project Overview

This project implements a workhorse SOE-NK model following Galí & Monacelli (2005) to study:

1. **Q1:** Benchmark impulse response analysis to domestic and foreign shocks
2. **Q2:** Comparison with a closed-economy NK foreign block
3. **Q3:** GFC-like shock scenarios under alternative exchange rate regimes:
   - Pure floating (φₑ = 0)
   - Managed floating (φₑ = 0.80)
   - Fixed exchange rate (eᶜ = 0)

## 🏗️ Model Features

- **Habit formation** in consumption (parameter `h`)
- **Calvo pricing** with backward indexation (parameters `θH`, `ιH`)
- **UIP condition** with endogenous risk premium
- **Taylor rule** with optional FX response
- **7 structural shocks:** monetary, preference, cost-push, risk premium, foreign output/inflation/rate
