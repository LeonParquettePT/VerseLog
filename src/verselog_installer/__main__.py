from verselog_installer.steps.benchmark_step import BenchmarkStep
from verselog_installer.steps.component_selection_step import ComponentSelectionStep
from verselog_installer.steps.finish_step import FinishStep
from verselog_installer.steps.welcome_step import WelcomeStep
from verselog_installer.wizard import InstallerWizard


def main() -> None:
    benchmark_step = BenchmarkStep()
    wizard = InstallerWizard(
        [WelcomeStep(), benchmark_step, ComponentSelectionStep(benchmark_step), FinishStep()]
    )
    wizard.run()


if __name__ == "__main__":
    main()
