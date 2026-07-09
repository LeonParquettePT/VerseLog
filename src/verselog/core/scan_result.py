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

    def describe(self) -> str:
        if self.contract is None:
            lines = ["No trustworthy contract this scan:"]
            lines.extend(f"  - {reason}" for reason in self.quarantine_reasons)
            return "\n".join(lines)

        lines = [
            f"{self.contract.departure} -> {self.contract.arrival}: "
            f"{self.contract.scu} SCU, {self.contract.reward:,.0f} reward"
        ]
        if self.route_cost is not None:
            cost = self.route_cost
            lines.append(
                f"  Route: {cost.distance_meters:,.0f} m, "
                f"{cost.travel_time_seconds:,.0f} s, {cost.fuel_cost:,.2f} fuel"
            )
        if self.loading_plan is not None:
            for step in self.loading_plan.steps:
                lines.append(f"  {step.action} {step.scu} SCU @ {step.location}")
        return "\n".join(lines)
