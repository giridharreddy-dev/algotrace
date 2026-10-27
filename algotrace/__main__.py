"""Run the web lab, or execute a reproducible trace from the command line."""

import argparse
import json

from .algorithms import CATALOG, compare_sorts, run_algorithm
from .server import make_server


def main():
    parser = argparse.ArgumentParser(description="AlgoTrace — an offline Python algorithm lab")
    sub = parser.add_subparsers(dest="command")
    serve = sub.add_parser("serve", help="Start the browser lab on 127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    run = sub.add_parser("run", help="Print a JSON result and trace")
    run.add_argument("algorithm", choices=CATALOG)
    run.add_argument("--values", default="12,7,19,3,15,8,2,11")
    run.add_argument("--target", type=int)
    run.add_argument("--compare", action="store_true", help="Compare all four sorts on this input")
    args = parser.parse_args()
    if args.command == "run":
        try:
            values = [] if not args.values.strip() else [int(part.strip()) for part in args.values.split(",")]
            result = compare_sorts(values) if args.compare else run_algorithm(args.algorithm, values, args.target)
        except ValueError as error:
            parser.error(str(error))
        print(json.dumps(result, indent=2))
        return
    port = getattr(args, "port", 8765)
    if not 0 <= port <= 65535:
        parser.error("Port must be from 0 to 65535.")
    try:
        server = make_server(port)
    except OSError as error:
        parser.exit(1, f"Could not start AlgoTrace: {error}\nTry: python -m algotrace serve --port 8766\n")
    print(f"AlgoTrace is ready: http://127.0.0.1:{server.server_port}", flush=True)
    print("Local only. Stop with Ctrl+C. No external services or accounts needed.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
