"""Launch the Copilot UI tailored for the Tracks & Fields workflow."""

from __future__ import annotations

from typing import Any

from agency_swarm.ui.demos.copilot import CopilotDemoLauncher

from tf_agents.agents import create_tf_agency


def launch_copilot(**launcher_kwargs: Any) -> None:
    """Start the Copilot UI preloaded with the TF agency.

    Parameters
    ----------
    **launcher_kwargs: Any
        Optional keyword arguments forwarded to :class:`CopilotDemoLauncher`.
    """

    agency = create_tf_agency()
    launcher = CopilotDemoLauncher(**launcher_kwargs)
    launcher.start(agency)


if __name__ == "__main__":
    launch_copilot()
