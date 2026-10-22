"""Optional build profiling: stack output every minute, no extra dependency."""
import faulthandler

from mkdocs.__main__ import cli

faulthandler.dump_traceback_later(60, repeat=True)
try:
    cli(["build", "-f", "mkdocs.zh-TW.yml"])
finally:
    faulthandler.cancel_dump_traceback_later()
