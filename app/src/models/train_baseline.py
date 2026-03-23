from __future__ import annotations

from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import ClassifierChain, MultiOutputClassifier


def build_logistic_regression_model(random_seed: int = 42) -> MultiOutputClassifier:
    return MultiOutputClassifier(
        LogisticRegression(max_iter=2000, solver="liblinear", random_state=random_seed)
    )


def build_classifier_chain_model(random_seed: int = 42) -> ClassifierChain:
    return ClassifierChain(
        LogisticRegression(max_iter=2000, solver="liblinear", random_state=random_seed),
        random_state=random_seed,
    )
