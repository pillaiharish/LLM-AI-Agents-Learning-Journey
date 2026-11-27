# ML Assessment Playbook

Use this when the model or library is unfamiliar.

```text
DATASET
   ↓
What is y?
   ↓
continuous / binary / count / multiclass?
   ↓
What model and library are requested?
   ↓
What preprocessing is needed?
   ↓
Need API help?
pip list → dir() → help() → inspect.signature() → pydoc
   ↓
fit → predict → appropriate metric → baseline → interpretation
```

## Rapid checklist

1. Read the task twice; underline the target, model, library, and metric.
2. Inspect the dataframe:

   ```python
   df.head()
   df.shape
   df.dtypes
   df.isnull().sum()
   df[target].describe()
   df[target].nunique()
   df[target].unique()[:20]
   ```

3. Build `X` and `y` without target leakage.
4. Split before fitting preprocessing or the model.
5. Fit only on training data.
6. Predict the correct partition.
7. Use a metric appropriate for the target.
8. Compare with a simple baseline.
9. Sanity-check shapes, missing values, and suspiciously perfect scores.
10. Explain what the score means.

| Target clue | Starting direction | Common metrics |
|---|---|---|
| Continuous number | Regression | R², MAE, RMSE |
| Binary 0/1 or two labels | Classification | Precision, Recall, F1, ROC-AUC |
| Multiple labels | Multiclass classification | Accuracy or macro/weighted F1 |
| Non-negative counts | Poisson/count model | Deviance and count-model diagnostics |

These are clues, not universal rules.

## Scikit-learn skeleton

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

model = SomeModel(...)
model.fit(X_train, y_train)

pred = model.predict(X_test)
score = some_metric(y_test, pred)
```

Inspect unknown names instead of guessing:

```python
import inspect

print(inspect.signature(SomeModel))
help(SomeModel.fit)
help(some_metric)
```

## Statsmodels skeleton

```python
import statsmodels.api as sm

X_design = sm.add_constant(X, has_constant="add")

model = sm.GLM(
    y,
    X_design,
    family=...,
)

result = model.fit()
pred = result.predict(X_design)
```

For predictive evaluation, split first and add the constant to both training
and test design matrices. Fit on training rows and predict test rows.

## Baseline reminders

- Continuous regression: predict the training target mean or median.
- Binary classification: predict the majority class or its training prevalence.
- Count prediction: start with a constant training-count mean when appropriate.

The baseline must use training information only. A negative held-out R² means
the regression predictions were worse than the constant comparator used by the
R² definition; it does not mean the code necessarily crashed.

## Offline API discovery

```bash
python --version
python -m pip list
python -m pydoc package.module.Object
```

```python
dir(module)
help(Object)
inspect.signature(Object)
[name for name in dir(module) if "useful_word" in name.lower()]
```

Remember the stable skeleton:

```text
prepare → split → fit → predict → evaluate → compare → interpret
```

Discover exact constructors, optional arguments, and metric function names from
the environment. Follow assessment rules and never inspect hidden evaluator
infrastructure.
