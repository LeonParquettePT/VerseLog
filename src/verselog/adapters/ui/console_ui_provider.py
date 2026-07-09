from verselog.core.contract import Contract
from verselog.core.legality_checker import LegalityRisk
from verselog.core.ports.ui_port import UIPort
from verselog.core.scan_result import ScanResult


class ConsoleUIProvider(UIPort):
    """Plain console UIPort - a real, working adapter, not a placeholder for a future one."""

    def show_results(self, results: list[ScanResult]) -> None:
        for result in results:
            if result.contract is None:
                print("No trustworthy contract this scan:")
                for reason in result.quarantine_reasons:
                    print(f"  - {reason}")
                continue

            print(self._format_contract(result.contract))
            if result.route_cost is not None:
                cost = result.route_cost
                print(
                    f"  Route: {cost.distance_meters:,.0f} m, "
                    f"{cost.travel_time_seconds:,.0f} s, {cost.fuel_cost:,.2f} fuel"
                )
            if result.loading_plan is not None:
                for step in result.loading_plan.steps:
                    print(f"  {step.action} {step.scu} SCU @ {step.location}")

    def confirm_risky_contract(self, contract: Contract, risk: LegalityRisk) -> bool:
        print(self._format_contract(contract))
        print(f"  Risk: {risk.reason}")
        answer = input("Proceed anyway? [y/N]: ")
        return answer.strip().lower() in ("y", "yes")

    def _format_contract(self, contract: Contract) -> str:
        return (
            f"{contract.departure} -> {contract.arrival}: "
            f"{contract.scu} SCU, {contract.reward:,.0f} reward"
        )
