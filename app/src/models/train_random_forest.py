from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier


def build_random_forest_model(random_seed: int = 42) -> MultiOutputClassifier:
    return MultiOutputClassifier(
        RandomForestClassifier(
            n_estimators=120,
            max_depth=6,
            min_samples_leaf=2,
            random_state=random_seed,
            n_jobs=-1,
        )
    )
