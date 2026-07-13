import argparse

import mss

from verselog.adapters.datasource.community_api_provider import CommunityAPIProvider
from verselog.adapters.datasource.location_data_provider import LocationDataProvider
from verselog.adapters.ui.console_ui_provider import ConsoleUIProvider
from verselog.adapters.ui.tkinter_ui_provider import TkinterUIProvider
from verselog.app import run
from verselog.core.location_reference_store import LocationReferenceStore
from verselog.core.ship_reference_store import ShipReferenceStore


def main() -> None:
    parser = argparse.ArgumentParser(prog="verselog")
    parser.add_argument("--ship", help="ship name to compute route/loading cost for")
    parser.add_argument(
        "--import-reference-data",
        action="store_true",
        help="bulk-import ship and location reference data, then exit",
    )
    parser.add_argument(
        "--console-ui",
        action="store_true",
        help="show results in the console instead of the Tkinter results window",
    )
    parser.add_argument(
        "--monitor",
        type=int,
        help="monitor index to capture (0 = all screens combined, the default; 1, 2, ... = a specific screen)",
    )
    args = parser.parse_args()

    if args.import_reference_data:
        CommunityAPIProvider(ShipReferenceStore()).refresh()
        LocationDataProvider(LocationReferenceStore()).refresh()
        return

    if not args.ship and args.console_ui:
        parser.error("--ship is required when using --console-ui")

    if args.monitor is not None:
        with mss.mss() as sct:
            monitor_count = len(sct.monitors)
        if not (0 <= args.monitor < monitor_count):
            parser.error(f"--monitor must be between 0 and {monitor_count - 1} (0 = all screens combined)")

    ui = ConsoleUIProvider() if args.console_ui else TkinterUIProvider()
    run(ship_name=args.ship, ui=ui, monitor_index=args.monitor)


if __name__ == "__main__":
    main()
