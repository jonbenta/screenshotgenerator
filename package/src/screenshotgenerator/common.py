from __future__ import annotations
import json

from .screenshot import Screenshot

def write_pool_report(report_path: str, sorted_screenshots: list[Screenshot]):
    if not report_path:
        return
    
    with open(report_path, "w") as pool_list_file:
        pool_list_file.write(json.dumps(sorted_screenshots, indent=4, default=vars))