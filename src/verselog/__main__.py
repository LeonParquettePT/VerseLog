import argparse

from verselog.adapters.datasource.community_api_provider import CommunityAPIProvider
from verselog.adapters.datasource.location_data_provider import LocationDataProvider
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
    args = parser.parse_args()

    if args.import_reference_data:
        CommunityAPIProvider(ShipReferenceStore()).refresh()
        LocationDataProvider(LocationReferenceStore()).refresh()
        return

    if not args.ship:
        parser.error("--ship is required unless --import-reference-data is passed")

    run(ship_name=args.ship)


if __name__ == "__main__":
    main()
