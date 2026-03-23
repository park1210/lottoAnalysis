from __future__ import annotations

import numpy as np
import pandas as pd


def create_gap_feature(one_hot: pd.DataFrame) -> pd.DataFrame:
    gap = pd.DataFrame(0, index=one_hot.index, columns=one_hot.columns, dtype=float)
    last_seen = {i: -1 for i in one_hot.columns}

    for i in range(len(one_hot)):
        for num in one_hot.columns:
            if last_seen[num] == -1:
                gap.loc[i, num] = np.nan
            else:
                gap.loc[i, num] = i - last_seen[num]

        for num in one_hot.columns:
            if one_hot.loc[i, num] == 1:
                last_seen[num] = i

    return gap
