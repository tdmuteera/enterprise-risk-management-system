"""
JSON utilities for audit trail diffs.

Provides JSON diff computation for audit logging.
"""

from typing import Any, Dict


def compute_json_diff(
    previous_values: Dict[str, Any],
    new_values: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compute JSON diff showing only changed fields.

    Returns a dict with keys: "added", "removed", "modified"

    Args:
        previous_values: Old state
        new_values: New state

    Returns:
        Diff dict with only changed fields
    """
    diff = {
        "added": {},
        "removed": {},
        "modified": {},
    }

    # Find removed fields
    for key in previous_values:
        if key not in new_values:
            diff["removed"][key] = previous_values[key]

    # Find added and modified fields
    for key in new_values:
        if key not in previous_values:
            diff["added"][key] = new_values[key]
        elif previous_values[key] != new_values[key]:
            diff["modified"][key] = {
                "from": previous_values[key],
                "to": new_values[key],
            }

    return diff
