from verselog.core.contract import Contract
from verselog.core.legality_checker import LegalityRisk
from verselog.core.ports.ui_port import UIPort
from verselog.core.scan_result import ScanResult


class ConsoleUIProvider(UIPort):
    """Plain console UIPort - a real, working adapter, not a placeholder for a future one."""

    def show_results(self, results: list[ScanResult]) -> None:
        for result in results:
            print(result.describe())

    def confirm_risky_contract(self, contract: Contract, risk: LegalityRisk) -> bool:
        print(f"{contract.departure} -> {contract.arrival}: {contract.scu} SCU, {contract.reward:,.0f} reward")
        print(f"  Risk: {risk.reason}")
        answer = input("Proceed anyway? [y/N]: ")
        return answer.strip().lower() in ("y", "yes")
