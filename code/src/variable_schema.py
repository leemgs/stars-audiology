"""Common STARS variable schema.

This module encodes, in code, the prespecified design decisions from the
protocol (Methods): the DAG roles of each variable, the minimal vs. extended
adjustment sets, the separated endpoints, and the cross-national measurement
comparability that governs which variables may enter the common transportable
model. Keeping these in code (not just prose) makes the analysis auditable.
"""

COMMON_SCHEMA = {
    "person_id": "unique deidentified participant identifier",
    "dataset": "KNHANES or NHANES",
    "cycle": "survey cycle or year",
    "age": "age in years",
    "sex": "sex/gender as reported",
    "education": "education level (SES axis)",
    "income": "household income where available (SES axis)",
    "race_ethnicity": "race/ethnicity (NHANES; fairness axis)",
    "employment_status": "currently employed status where available",
    "occupation_group": "harmonized occupation group where available",
    "working_hours": "weekly working hours where available",
    "shift_work": "shift-work indicator where available",
    "perceived_stress": "dataset-specific perceived-stress item (EXPOSURE)",
    "sleep_hours": "sleep duration (mediator)",
    "depression_symptoms": "depression/mood variable (mediator)",
    "occupational_noise": "workplace loud-noise exposure",
    "occupational_noise_years": "duration of occupational noise exposure",
    "recreational_noise": "non-work noise exposure",
    "firearm_noise": "firearm noise exposure",
    "hearing_protection": "use of hearing protection",
    "tinnitus_presence": "any tinnitus in past 12 months (ENDPOINT)",
    "bothersome_tinnitus": "tinnitus causing annoyance/sleep/concentration issues (ENDPOINT)",
    "hearing_difficulty": "self-reported hearing difficulty",
    "left_pta": "left-ear pure-tone average (0.5,1,2,4 kHz)",
    "right_pta": "right-ear pure-tone average (0.5,1,2,4 kHz)",
    "better_ear_pta": "minimum of left and right PTA (ENDPOINT)",
    "worse_ear_pta": "maximum of left and right PTA (ENDPOINT)",
    "hf_pta": "high-frequency PTA (3,4,6 kHz)",
    "asymmetric_loss": "interaural diff >=15 dB at >=2 adjacent frequencies (ENDPOINT)",
    "hearing_loss_pta": "binary PTA-based hearing loss at primary 25 dB HL cutoff",
    "hearing_aid_use": "hearing-aid use where available",
    "survey_weight": "analysis weight",
    "strata": "survey stratum",
    "psu": "primary sampling unit",
}

# DAG roles (see Methods, Figure: causal DAG). Depressed mood and sleep are
# treated as MEDIATORS of stress->tinnitus, not confounders.
VARIABLE_ROLES = {
    "perceived_stress": "exposure",
    "age": "confounder",
    "sex": "confounder",
    "education": "confounder",
    "occupation_group": "confounder",
    "employment_status": "confounder",
    "occupational_noise": "confounder",
    "recreational_noise": "confounder",
    "smoking": "confounder",
    "alcohol": "confounder",
    "cardiometabolic": "confounder",
    "depression_symptoms": "mediator",
    "sleep_hours": "mediator",
    "working_hours": "work_related_factor",
    "shift_work": "work_related_factor",
}

# Prespecified adjustment sets. PRIMARY analysis uses the minimal sufficient set
# only; EXTENDED adds mediators and is reported separately (mediator-adjusted).
ADJUSTMENT_SETS = {
    "minimal_sufficient": [
        "age", "sex", "education", "occupation_group", "employment_status",
        "occupational_noise",
    ],
    "extended_mediator_adjusted": [
        "age", "sex", "education", "occupation_group", "employment_status",
        "occupational_noise", "depression_symptoms", "sleep_hours",
    ],
}

# Separated endpoints (see Methods).
ENDPOINTS = [
    "tinnitus_presence",
    "bothersome_tinnitus",
    "better_ear_pta",     # continuous, and binarized at 25 dB HL
    "worse_ear_pta",
    "asymmetric_loss",
]

# Measurement comparability across KNHANES/NHANES (see harmonization table).
# LOW-comparability variables are excluded from the common transportable model
# and used only in country-specific extended models.
MEASUREMENT_COMPARABILITY = {
    "tinnitus_presence": "high",
    "bothersome_tinnitus": "medium",
    "better_ear_pta": "high",
    "worse_ear_pta": "high",
    "perceived_stress": "low",
    "depression_symptoms": "medium",
    "occupation_group": "medium",
    "occupational_noise": "medium",
    "sleep_hours": "medium",
    "age": "high",
    "sex": "high",
    "education": "high",
}

# Subgroups for fairness evaluation (adds SES and race/ethnicity per review).
FAIRNESS_SUBGROUPS = [
    "sex", "age_band", "employment_status", "occupational_noise",
    "asymmetric_loss", "education", "income", "race_ethnicity",
]


def transportable_predictors(candidate_predictors, min_comparability="medium"):
    """Return predictors eligible for the common cross-national model.

    Variables with comparability below the threshold are dropped (used only in
    country-specific models). Unknown variables are conservatively excluded.
    """
    order = {"low": 0, "medium": 1, "high": 2}
    thr = order[min_comparability]
    return [
        v for v in candidate_predictors
        if order.get(MEASUREMENT_COMPARABILITY.get(v, "low"), 0) >= thr
    ]
