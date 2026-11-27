# Linear Regression: From One Line to an Assessment Strategy

This lesson builds intuition before API memorization. The executable example is
in [linear_regression_statsmodels.ipynb](linear_regression_statsmodels.ipynb).

The goal is to recognize the operation you need:

```text
data → features X and target y → fit → predict → metric → baseline → interpret
```

Once that is clear, the exact library API can be discovered from the installed
Python environment.

## 1. Start with one feature and one prediction

Imagine predicting salary from years of experience:

```text
experience → salary
```

A straight-line model writes this relationship as:

```text
y_hat = b0 + b1*x
```

- `x` is the input feature, such as years of experience.
- `y` is the actual observed salary.
- `y_hat` is the model's prediction.
- `b0` is the intercept: the prediction when `x = 0`.
- `b1` is the coefficient: the predicted change in salary for one extra unit of `x`.
- The residual is `y - y_hat`, the prediction error for one observation.

Linear regression learns `b0` and `b1` so the line passes as close as possible
to the observed points.

## 2. Why square the residuals?

For every row:

```text
residual = actual - prediction
```

Simply adding residuals is not useful because positive and negative errors can
cancel. Squaring makes every contribution non-negative and penalizes large
mistakes more strongly:

```text
Residual Sum of Squares = sum((y - y_hat)^2)
```

OLS means **Ordinary Least Squares**:

> Choose the coefficients that minimize the sum of squared residuals.

That is the fitting objective. RMSE and MAE are evaluation summaries; they are
not additional coefficients learned by OLS.

## 3. R-squared is a baseline comparison

Before fitting a useful model, imagine a deliberately simple rule:

```text
ignore every feature
always predict mean(y)
```

R² compares the regression model's squared errors with that constant-mean
comparator:

```text
R² = 1 - SS_res / SS_tot

SS_res = sum((actual - model prediction)^2)
SS_tot = sum((actual - mean(actual))^2)
```

- `R² = 1`: predictions are perfect.
- `R² = 0`: squared error matches the mean comparator.
- `R² < 0`: predictions are worse than that comparator.

There is an important context distinction:

- For **in-sample OLS with an intercept**, R² is between 0 and 1. The fitted
  model can reproduce the intercept-only mean solution, so training it cannot
  do worse on the same rows.
- For **held-out/test predictions**, R² can be negative. Coefficients learned
  from the training rows may generalize worse than the constant comparator on
  unseen rows.

The notebook calculates training R² manually so `SS_res` and `SS_tot` are
visible, then uses `r2_score` on a held-out set. R² is a regression metric; it
is not a generic metric for classification.

For a real held-out baseline, predict the **training target mean**. This avoids
looking at test labels. Its test R² may be slightly above or below zero because
the mathematical zero-point in `r2_score` uses the test target mean.

## 4. From one feature to six

Adding features does not change the central idea:

```text
y_hat = b0 + b1*x1
```

becomes:

```text
y_hat = b0 + b1*x1 + b2*x2 + ... + b6*x6
```

In a dataframe:

```python
X = df[feature_columns]  # inputs used to make predictions
y = df[target_column]    # value the model should predict
```

The notebook uses six synthetic feature columns and a continuous label. Each
coefficient estimates the contribution of one feature while holding the other
included features constant.

## 5. Why an assessment may use Statsmodels

Scikit-learn emphasizes prediction workflows. Statsmodels also exposes
statistical information such as:

- coefficients and standard errors;
- t statistics and p-values;
- confidence intervals;
- R² and adjusted R²;
- residual and model diagnostics.

That makes `statsmodels` common in applied statistics and assessments that ask
you to interpret a fitted relationship, not only produce predictions.

The matrix API follows this pattern:

```python
model = sm.OLS(endog=y, exog=X)
result = model.fit()
prediction = result.predict(X_new)
```

## 6. Why `sm.add_constant()` matters

Statsmodels matrix APIs do not automatically add an intercept:

```python
X = sm.add_constant(X, has_constant="add")
```

The added column contains ones:

```text
constant column of 1s → model can learn b0
```

Without that column, the fitted relationship is forced through the origin
unless the design matrix already contains an intercept-like column.

## 7. Training fit versus generalization

Training metrics answer:

> How closely did the model fit rows it already saw?

Test metrics answer:

> How well did the learned relationship work on unseen rows?

A typical workflow is:

```python
X_fit, X_test, y_fit, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

result = sm.OLS(y_fit, sm.add_constant(X_fit)).fit()
prediction = result.predict(sm.add_constant(X_test))
```

Use the same split for the trained model and its baseline. Compare R² for
relative fit and RMSE/MAE for error magnitude in target units.

The fixed random seeds make dataset generation and the numerical
model/evaluation results repeatable across executions. The saved notebook is
not byte-for-byte deterministic because `full_ols_results.summary()` includes its
execution Date/Time and notebook execution metadata may also contain
timestamps.

## From OLS to GLM

Linear regression is a natural starting point for a continuous target. A
Generalized Linear Model asks two broader questions:

1. Which distribution family is appropriate for `y`?
2. Which link function connects the expected response to the linear predictor?

The conventional GLM relationship is:

```text
g(E[Y | X]) = Xβ
```

The link function `g` maps the expected response, or conditional mean, to the
linear predictor `Xβ`. The inverse link goes in the direction needed for
prediction: it maps `Xβ` back to the expected target. For logistic regression,
the inverse-logit turns an unrestricted linear predictor into a probability
between 0 and 1.

Three target shapes make the progression concrete:

```text
continuous salary: 12.5, 18.2, 25.1
binary fraud:       0, 1, 0, 1
request counts:     0, 4, 2, 13
```

```text
Linear Regression
        ↓
Multiple Linear Regression
        ↓
Statsmodels OLS
        ↓
Generalized Linear Model
```

| Target clue | First model direction | Typical evaluation |
|---|---|---|
| Continuous values such as salary | Gaussian / linear regression | R², MAE, RMSE |
| Binary values such as fraud 0/1 | Binomial / logistic-style classification | Precision, Recall, F1, ROC-AUC |
| Non-negative counts such as requests | Poisson-style count model | Deviance and count-model diagnostics |

This is a first-pass assessment heuristic, not a complete real-world
model-selection rule. Data generation, class imbalance, exposure, dispersion,
and assessment instructions still matter.

## How to approach an unfamiliar ML assessment

1. Load the dataset.
2. Inspect its rows, shape, types, and missing values.
3. Identify target `y` and feature matrix `X`.
4. Determine whether `y` appears continuous, binary, count, or multiclass.
5. Identify the requested model and library.
6. Decide what preprocessing is required.
7. Split train/test when the task is predictive.
8. Fit on training data.
9. Predict on the appropriate data.
10. Evaluate using a target-appropriate metric.
11. Compare with a simple baseline.
12. Interpret the result in context.

Useful first checks:

```python
df.head()
df.shape
df.dtypes
df.isnull().sum()
df[target].describe()
df[target].nunique()
df[target].unique()[:20]
```

These values are clues, not rigid rules:

```text
[0, 1]                  → probably binary classification
[12.7, 18.4, 31.2, ...] → probably continuous regression
[0, 1, 2, 5, 8, ...]    → potentially count data
```

If the model API is unfamiliar, use the
[terminal and virtual-environment discovery guide](../terminal-venv-model-discovery.md).
For a shorter timed-assessment checklist, use the
[assessment playbook](../ASSESSMENT_PLAYBOOK.md).

## Learning ladder

```text
01 Linear Regression intuition
        ↓
02 Multiple Linear Regression
        ↓
03 Statsmodels OLS
        ↓
04 Train/test evaluation
        ↓
05 Gaussian GLM
        ↓
06 Binomial GLM / Logistic Regression
        ↓
07 Poisson GLM
        ↓
08 Unknown-model discovery drills
```

This PR establishes the foundation and bridge. Later lessons can explore each
GLM family and model type in greater depth.
