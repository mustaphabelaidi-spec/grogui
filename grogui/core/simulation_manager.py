"""Central simulation management and workflow orchestration"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass, asdict

from grogui.core.gromacs_interface import GromacsInterface
from grogui.utils.logger import setup_logger

logger = logging.getLogger(__name__)


@dataclass
class SimulationConfig:
    """Simulation configuration"""
    project_name: str
    structure_file: str
    forcefield: str = "amber99sb-ildn"
    water_model: str = "tip3p"
    temperature: float = 300
    pressure: float = 1.0
    box_type: str = "cubic"
    box_distance: float = 1.0


class SimulationManager:
    """Main simulation management class"""

    def __init__(
        self,
        project_name: str,
        project_dir: Optional[str] = None,
        gmx_path: Optional[str] = None,
        gpu: bool = False,
        threads: int = 4
    ):
        """
        Initialize simulation manager.
        
        Args:
            project_name: Name of the project
            project_dir: Project directory (default: ./projects/{project_name})
            gmx_path: Path to GROMACS executable
            gpu: Enable GPU acceleration
            threads: Number of CPU threads
        """
        self.project_name = project_name
        self.project_dir = Path(project_dir or f"./projects/{project_name}")
        self.gmx = GromacsInterface(gmx_path=gmx_path, gpu=gpu, threads=threads)
        
        # Setup directories
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.input_dir = self.project_dir / "input"
        self.output_dir = self.project_dir / "output"
        self.analysis_dir = self.project_dir / "analysis"
        
        for d in [self.input_dir, self.output_dir, self.analysis_dir]:
            d.mkdir(exist_ok=True)
        
        self.config: Optional[SimulationConfig] = None
        self.pipeline_steps: List[str] = []
        self.logger = setup_logger(
            "SimulationManager",
            self.project_dir / "simulation.log"
        )
        
        self.logger.info(f"Initialized SimulationManager for project: {project_name}")

    def load_config(self, config_file: str) -> None:
        """Load configuration from JSON file"""
        with open(config_file, 'r') as f:
            config_dict = json.load(f)
        self.config = SimulationConfig(**config_dict)
        self.logger.info(f"Loaded configuration from {config_file}")

    def save_config(self, config_file: Optional[str] = None) -> None:
        """Save current configuration to JSON file"""
        if not self.config:
            raise ValueError("No configuration to save")
        
        filepath = config_file or (self.project_dir / "config.json")
        with open(filepath, 'w') as f:
            json.dump(asdict(self.config), f, indent=2)
        self.logger.info(f"Saved configuration to {filepath}")

    def add_step(self, step_name: str) -> None:
        """Add step to pipeline"""
        if step_name not in self.pipeline_steps:
            self.pipeline_steps.append(step_name)
            self.logger.info(f"Added step: {step_name}")

    def remove_step(self, step_name: str) -> None:
        """Remove step from pipeline"""
        if step_name in self.pipeline_steps:
            self.pipeline_steps.remove(step_name)
            self.logger.info(f"Removed step: {step_name}")

    def get_pipeline(self) -> List[str]:
        """Get current pipeline steps"""
        return self.pipeline_steps.copy()

    def run_step(self, step_name: str) -> bool:
        """Execute a specific pipeline step"""
        self.logger.info(f"Starting step: {step_name}")
        try:
            # Step execution logic will be implemented in submodules
            self.logger.info(f"Completed step: {step_name}")
            return True
        except Exception as e:
            self.logger.error(f"Step failed: {step_name} - {e}")
            return False

    def run_pipeline(self) -> bool:
        """Execute full simulation pipeline"""
        if not self.config:
            raise ValueError("No configuration loaded")
        
        self.logger.info(f"Starting pipeline with {len(self.pipeline_steps)} steps")
        
        for step in self.pipeline_steps:
            if not self.run_step(step):
                self.logger.error(f"Pipeline failed at step: {step}")
                return False
        
        self.logger.info("Pipeline completed successfully")
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get project status"""
        return {
            "project_name": self.project_name,
            "project_dir": str(self.project_dir),
            "config_loaded": self.config is not None,
            "pipeline_steps": self.pipeline_steps,
            "completed_steps": [],  # Track completed steps
            "last_updated": datetime.now().isoformat(),
        }

    def get_input_file(self, filename: str) -> Path:
        """Get input file path"""
        return self.input_dir / filename

    def get_output_file(self, filename: str) -> Path:
        """Get output file path"""
        return self.output_dir / filename

    def get_analysis_file(self, filename: str) -> Path:
        """Get analysis file path"""
        return self.analysis_dir / filename
