import argparse

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
    args = parser.parse_args()

    if args.import_reference_data:
        CommunityAPIProvider(ShipReferenceStore()).refresh()
        LocationDataProvider(LocationReferenceStore()).refresh()
        return

    if not args.ship:
        parser.error("--ship is required unless --import-reference-data is passed")

    ui = ConsoleUIProvider() if args.console_ui else TkinterUIProvider()
    run(ship_name=args.ship, ui=ui)


if __name__ == "__main__":
    main()
