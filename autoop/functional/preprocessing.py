from typing import List, Tuple
from autoop.core.ml.feature import Feature
from autoop.core.ml.dataset import Dataset
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
import pandas as pd
import io


def preprocess_features(features: List[Feature], dataset: Dataset
                        ) -> List[Tuple[str, np.ndarray, dict]]:
    """Preprocess features.
    Args:
        features (List[Feature]): List of features.
        dataset (Dataset): Dataset object.
    Returns:
        List[str, Tuple[np.ndarray, dict]]: List of preprocessed features.
        Each ndarray of shape (N, ...)
    """
    results = []
    raw = pd.read_csv(io.BytesIO(dataset.read()))

    for feature in features:
        if feature.type == "categorical":
            # to convert categorical feature to integer indices
            label_encoder = LabelEncoder()
            raw[feature.name + '_encoded'] = label_encoder.fit_transform(
                raw[feature.name])

            encoder = OneHotEncoder()
            data = encoder.fit_transform(raw[feature.name].values.reshape(-1, 1)).toarray()
            artifact = {"type": "OneHotEncoder", "encoder": encoder.get_params()}

            results.append((feature.name, data, artifact))

        if feature.type == "numerical":

            scaler = StandardScaler()
            data = scaler.fit_transform(raw[feature.name].values.reshape(-1, 1))
            artifact = {"type": "StandardScaler", "scaler": scaler.get_params()}
            results.append((feature.name, data, artifact))
 
    # Sort for consistency
    results = list(sorted(results, key=lambda x: x[0]))
    return results
