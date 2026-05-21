#!/usr/bin/env python3
"""Entry point for Pokémon Sleep skill trigger tracker."""

import sys
import traceback


def main() -> int:
    try:
        from app.application import PokemonSleepApp

        app = PokemonSleepApp()
        from app import strings as S

        print(S.APP_STARTED_HINT, flush=True)
        return app.run()
    except Exception:
        traceback.print_exc()
        input("按 Enter 键退出…")
        return 1


if __name__ == "__main__":
    sys.exit(main())
