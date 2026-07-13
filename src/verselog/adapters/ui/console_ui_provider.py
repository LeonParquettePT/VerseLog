from verselog.core.contract import Contract
from verselog.core.legality_checker import LegalityRisk
from verselog.core.missing_prerequisite import MissingPrerequisite
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

    def select_ship(self, ship_names: list[str]) -> str | None:
        if not ship_names:
            print("No ships found - run VerseLog with --import-reference-data first.")
            return None

        for index, name in enumerate(ship_names, start=1):
            print(f"{index}. {name}")

        answer = input("Select your ship (number): ")
        try:
            choice = int(answer) - 1
        except ValueError:
            return None
        if 0 <= choice < len(ship_names):
            return ship_names[choice]
        return None

    def warn_missing_prerequisites(self, missing: list[MissingPrerequisite]) -> None:
        for item in missing:
            print(f"Missing prerequisite: {item.name} - install it from {item.install_instructions}")
