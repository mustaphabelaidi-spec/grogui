"""GroGUI - GROMACS Molecular Dynamics Simulation Runner & Analysis Tool"""

__version__ = "2.0.0"
__author__ = "Mustapha Belaidi"
__email__ = "mustapha.belaidi@example.com"

from grogui.core.simulation_manager import SimulationManager
from grogui.core.gromacs_interface import GromacsInterface

__all__ = [
    "SimulationManager",
    "GromacsInterface",
]
