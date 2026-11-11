"""Native Jevotron labels; uncertainty is distinct from a normal assessment."""

from jevotron import Config

config = Config(
    labels=["NORMAL", "ANOMALY", "UNKNOWN"],
    criteria={
        "NORMAL": "The supplied evidence is sufficient to establish no issue under this field's guidance.",
        "ANOMALY": "The supplied evidence shows a concrete issue under this field's guidance that merits review.",
        "UNKNOWN": "Missing, truncated, opaque or insufficient evidence prevents a confident assessment.",
    },
    anomaly_label="ANOMALY",
    model="jev-1.13.0",
    threshold=0.5,
)
