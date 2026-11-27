# Offline Python and `.venv` Model Discovery

In a timed assessment, separate the conceptual question from the API question:

```text
What operation do I need?
        ↓
How does the installed library express it?
```

You do not need to memorize every constructor and metric. You do need to
recognize operations such as fit, predict, and evaluate, then know how to
inspect the environment.

## Assessment boundary

Use these techniques only when the assessment permits normal inspection of
installed libraries, documentation, examples, tests, and source code.

Do not access hidden assessment test cases, inspect protected evaluator
infrastructure, bypass restrictions, or use resources prohibited by the
assessment instructions.

## 1. Discover the environment

Start with facts:

```bash
pwd
ls -la
which python
python --version
python -m pip list
```

If the project supplies a virtual environment on macOS or Linux:

```bash
source .venv/bin/activate
```

Then find likely ML libraries:

```bash
python -m pip list | grep -Ei \
  'statsmodels|pandas|numpy|scikit|scipy'
```

Before recalling an API, verify which packages and versions actually exist.

## 2. Inspect an unfamiliar model

Statsmodels GLM is a useful example:

```bash
python
```

```python
import inspect
import statsmodels.api as sm

dir(sm)
help(sm.GLM)
print(inspect.signature(sm.GLM))
```

The signature exposes terms such as:

- `endog`: target or dependent variable;
- `exog`: features or design matrix;
- `family`: target distribution and default link behavior.

Discover available families:

```python
dir(sm.families)
help(sm.families.Gaussian)
```

Look for `Gaussian`, `Binomial`, `Poisson`, `Gamma`, and
`NegativeBinomial`. Their presence does not automatically make them suitable;
target type and task requirements still guide the choice.

## 3. Discover how to fit

If the conceptual requirement is “train the model,” search for fit-like names:

```python
[
    name
    for name in dir(sm.GLM)
    if "fit" in name.lower()
]

help(sm.GLM.fit)
print(inspect.signature(sm.GLM.fit))
```

That is enough to reconstruct the common pattern:

```python
model = sm.GLM(...)
result = model.fit()
```

## 4. Discover prediction methods

After fitting:

```python
[
    name
    for name in dir(result)
    if "predict" in name.lower()
]

help(result.predict)
```

Keep the mapping explicit:

```text
concept: I need predictions
mechanism: find and inspect predict-like methods
```

## 5. Discover evaluation metrics

If the assessment requests R²:

```python
import sklearn.metrics as metrics

[
    name
    for name in dir(metrics)
    if "r2" in name.lower()
]

help(metrics.r2_score)
```

Then reconstruct:

```python
score = metrics.r2_score(y_test, y_pred)
```

Repeat with search words such as `error`, `mean`, `precision`, `recall`, or
`f1`. First confirm the metric matches the task: R² is for regression, while
precision, recall, and F1 are classification metrics.

## 6. Use `pydoc` without a browser

```bash
python -m pydoc statsmodels.api.GLM
python -m pydoc sklearn.metrics.r2_score
python -m pydoc sklearn.linear_model.LogisticRegression
```

For long output:

```bash
python -m pydoc statsmodels.api.GLM | less
```

Inside `less`:

```text
/Parameters
/Examples
/Returns
n    next match
N    previous match
q    quit
```

## 7. Locate installed source and examples

Find the package and class source locations:

```bash
python -c \
  "import statsmodels; print(statsmodels.__file__)"

python -c \
  "import inspect, statsmodels.api as sm; print(inspect.getfile(sm.GLM))"
```

Inspect a method from Python:

```python
import inspect

print(inspect.getsource(sm.GLM.fit))
```

Search installed examples or tests when assessment rules allow:

```bash
PACKAGE=$(python -c \
  'import pathlib, statsmodels; print(pathlib.Path(statsmodels.__file__).parent)')

find "$PACKAGE" -iname '*glm*'
grep -R -n "GLM(" "$PACKAGE" --include="*.py" | head -30
```

Source is a fallback when signatures and help do not answer the question. Start
with the smallest, clearest inspection tool.

## 8. Use Jupyter and IPython discovery

Where IPython syntax is supported:

```python
sm.GLM?
sm.GLM??
sm.GLM.fit?
```

Also use:

- `Tab` for completion;
- `Shift+Tab` for call tips;
- `%pdoc` for documentation;
- `%psource` for source.

## Unknown-model drills

For every drill, use the same loop:

```text
understand problem
→ inspect installed package
→ discover constructor and fit/predict API
→ implement the minimum solution
→ choose the requested metric
→ compare with a baseline
```

Do not search the web. Use `pip list`, `dir()`, `help()`,
`inspect.signature()`, and `pydoc`.

### Drill 1: Random forest regression

```text
Use RandomForestRegressor.
Predict a continuous target.
Evaluate with RMSE.
```

Hints:

```python
import sklearn.ensemble as ensemble

[name for name in dir(ensemble) if "forest" in name.lower()]
help(ensemble.RandomForestRegressor)
```

### Drill 2: Logistic regression

```text
Use LogisticRegression for a binary target.
Evaluate with F1.
```

Hints:

```python
import sklearn.linear_model as linear_model
import sklearn.metrics as metrics

[name for name in dir(linear_model) if "logistic" in name.lower()]
[name for name in dir(metrics) if "f1" in name.lower()]
```

### Drill 3: Poisson GLM

```text
Use a statsmodels Poisson GLM for a count target.
```

Hints:

```python
import inspect
import statsmodels.api as sm

print(inspect.signature(sm.GLM))
help(sm.families.Poisson)
```

Remember to inspect whether the matrix API expects you to add a constant.

### Drill 4: Ridge regression

```text
Use Ridge regression.
Evaluate with R².
```

Hints:

```python
import sklearn.linear_model as linear_model

[name for name in dir(linear_model) if "ridge" in name.lower()]
help(linear_model.Ridge)
```

### Drill 5: A less familiar regressor

```text
Use HistGradientBoostingRegressor.
Predict a continuous target.
Choose an appropriate regression metric.
```

Hints:

```python
import sklearn.ensemble as ensemble

[name for name in dir(ensemble) if "hist" in name.lower()]
help(ensemble.HistGradientBoostingRegressor)
```

The drills intentionally stop before complete solutions. The transferable
skill is reconstructing the solution from concepts and installed APIs.
