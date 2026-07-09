from dataclasses import dataclass, field

from verselog.core.contract import Contract
from verselog.core.loading_plan_calculator import LoadingPlan
from verselog.core.route_cost_calculator import RouteCost


@dataclass
class ScanResult:
    contract: Contract | None
    route_cost: RouteCost | None
    loading_plan: LoadingPlan | None
    quarantine_reasons: list[str] = field(default_factory=list)
