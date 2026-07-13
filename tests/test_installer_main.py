from verselog_installer import __main__ as installer_main
from verselog_installer.steps.benchmark_step import BenchmarkStep
from verselog_installer.steps.component_selection_step import ComponentSelectionStep
from verselog_installer.steps.finish_step import FinishStep
from verselog_installer.steps.welcome_step import WelcomeStep


class _SpyWizard:
    instances: list["_SpyWizard"] = []

    def __init__(self, steps) -> None:
        self.steps = steps
        self.ran = False
        _SpyWizard.instances.append(self)

    def run(self) -> None:
        self.ran = True


def test_main_builds_the_wizard_with_all_four_steps_in_order_and_runs_it(monkeypatch):
    _SpyWizard.instances.clear()
    monkeypatch.setattr(installer_main, "InstallerWizard", _SpyWizard)

    installer_main.main()

    assert len(_SpyWizard.instances) == 1
    wizard = _SpyWizard.instances[0]
    assert wizard.ran is True
    assert isinstance(wizard.steps[0], WelcomeStep)
    assert isinstance(wizard.steps[1], BenchmarkStep)
    assert isinstance(wizard.steps[2], ComponentSelectionStep)
    assert isinstance(wizard.steps[3], FinishStep)


def test_component_selection_step_shares_the_same_benchmark_step_instance(monkeypatch):
    _SpyWizard.instances.clear()
    monkeypatch.setattr(installer_main, "InstallerWizard", _SpyWizard)

    installer_main.main()

    wizard = _SpyWizard.instances[0]
    benchmark_step, component_step = wizard.steps[1], wizard.steps[2]
    assert component_step._benchmark_step is benchmark_step
