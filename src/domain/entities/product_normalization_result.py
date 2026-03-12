from dataclasses import dataclass


@dataclass
class ProductNormalizationResult:
    canonical_name: str
    confidence: float
    brand: str | None = None
    category: str | None = None
    normalization_rule_applied: str | None = None
