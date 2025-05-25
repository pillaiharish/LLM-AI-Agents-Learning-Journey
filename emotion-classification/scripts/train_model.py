import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.svm import LinearSVC
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import pandas as pd

# --- 1. Load features and labels ---
X_tfidf = np.load('data/processed/X_tfidf.npy')
y = np.load('data/processed/y.npy', allow_pickle=True)

# --- 2. Remove rare classes (labels with <2 samples) ---
unique, counts = np.unique(y, return_counts=True)
label_counts = dict(zip(unique, counts))
rare_labels = [label for label, count in label_counts.items() if count < 2]
if rare_labels:
    print(f"Removing rare labels with <2 samples: {rare_labels}")
    mask = ~np.isin(y, rare_labels)
    X_tfidf = X_tfidf[mask]
    y = y[mask]

# --- 3. Split data ---
X_train, X_test, y_train, y_test = train_test_split(
    X_tfidf, y, test_size=0.2, random_state=42, stratify=y
)

# --- 4. Train and save models ---
os.makedirs('models/logistic_regression', exist_ok=True)
os.makedirs('models/svm', exist_ok=True)

logreg = LogisticRegression(max_iter=200, class_weight='balanced')
logreg.fit(X_train, y_train)
joblib.dump(logreg, 'models/logistic_regression/logreg_model.joblib')

svm = LinearSVC(class_weight='balanced', max_iter=1000)
svm.fit(X_train, y_train)
joblib.dump(svm, 'models/svm/svm_model.joblib')

# --- 5. Predictions ---
y_pred_logreg = logreg.predict(X_test)
y_pred_svm = svm.predict(X_test)

print("Logistic Regression Results:\n")
print(classification_report(y_test, y_pred_logreg))

print("SVM Results:\n")
print(classification_report(y_test, y_pred_svm))

# --- 6. Plot confusion matrices ---
import os

def plot_conf_matrix(y_true, y_pred, labels, title, save_path, top_n=10, show=False):
    from collections import Counter
    import numpy as np

    # Only keep top_n most frequent labels
    top_labels = [x for x, _ in Counter(y_true).most_common(top_n)]
    mask = np.isin(y_true, top_labels) & np.isin(y_pred, top_labels)
    y_true_top = np.array(y_true)[mask]
    y_pred_top = np.array(y_pred)[mask]
    
    cm = confusion_matrix(y_true_top, y_pred_top, labels=top_labels)
    plt.figure(figsize=(2 + top_n, 2 + top_n))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=top_labels, yticklabels=top_labels)
    plt.title(title + f" (Top {top_n} Classes)")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)
    print(f"Confusion matrix saved to {save_path}")
    if show:
        plt.show()
    else:
        plt.close()



labels = np.unique(y)
plot_conf_matrix(
    y_test, y_pred_logreg, labels, 
    title="Confusion Matrix: Logistic Regression", 
    save_path="eda/plots/conf_matrix_logreg.png",
    top_n=10,
    show=False
)

plot_conf_matrix(
    y_test, y_pred_svm, labels, 
    title="Confusion Matrix: SVM", 
    save_path="eda/plots/conf_matrix_svm.png",
    top_n=10,
    show=False
)


cm = confusion_matrix(y_test, y_pred_logreg, labels=labels)
cm_df = pd.DataFrame(cm, index=labels, columns=labels)
cm_df.to_csv("data/processed/confusion_matrix_logreg.csv")
