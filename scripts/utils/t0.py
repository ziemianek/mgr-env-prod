
import pandas as pd

STRESS_T0_MAP = {
    # AKS
    "aks_stress01": pd.Timestamp("2025-10-26 14:16:00"),
    "aks_stress02": pd.Timestamp("2025-10-26 20:20:30"),
    "aks_stress03": pd.Timestamp("2025-10-27 07:18:30"),

    # EKS
    "eks_stress01": pd.Timestamp("2025-11-08 10:57:30"),
    "eks_stress02": pd.Timestamp("2025-11-08 17:58:00"),
    "eks_stress03": pd.Timestamp("2025-11-08 19:18:00"),

    # GKE
    "gke_stress01": pd.Timestamp("2025-10-17 20:09:30"),
    "gke_stress02": pd.Timestamp("2025-10-18 07:36:00"),
    "gke_stress03": pd.Timestamp("2025-10-18 8:51:00"),
}

SOAK_T0_MAP = {
    # AKS
    "aks_soak01": pd.Timestamp("2025-10-26 13:29:30"),
    "aks_soak02": pd.Timestamp("2025-10-26 06:36:00"),

    # # EKS
    # "eks_stress01": pd.Timestamp("2025-10-17 19:59:00"),
    # "eks_soak02": pd.Timestamp("2025-10-18 09:25:30"),

    # GKE
    "gke_soak01": pd.Timestamp("2025-10-14 08:17:30"),
    "gke_soak02": pd.Timestamp("2025-10-18 10:07:00"),
}
