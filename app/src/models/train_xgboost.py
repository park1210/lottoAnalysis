from __future__ import annotations

from sklearn.multioutput import MultiOutputClassifier
from xgboost import XGBClassifier


def build_xgboost_model(random_seed: int = 42) -> MultiOutputClassifier:
    return MultiOutputClassifier(
        XGBClassifier(
            n_estimators=80,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=random_seed,
            n_jobs=1,
            verbosity=0,
        )
    )
