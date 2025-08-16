"""
The definitions file is used for detection of assets, sensors, jobs, and resources within a code location.
"""


from pathlib import Path

from dagster import definitions, load_from_defs_folder

# This is a boilerplate function automatically created along with a new dagster project.
@definitions
def defs():
    return load_from_defs_folder(project_root=Path(__file__).parent.parent)

