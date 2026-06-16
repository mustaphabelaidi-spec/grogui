"""GROMACS command interface and wrapper"""

import subprocess
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class GromacsInterface:
    """Interface to GROMACS commands"""

    def __init__(self, gmx_path: Optional[str] = None, gpu: bool = False, threads: int = 4):
        """
        Initialize GROMACS interface.
        
        Args:
            gmx_path: Path to GROMACS executable (default: 'gmx')
            gpu: Enable GPU acceleration
            threads: Number of CPU threads to use
        """
        self.gmx_path = gmx_path or "gmx"
        self.gpu = gpu
        self.threads = threads
        self._verify_installation()

    def _verify_installation(self) -> bool:
        """Verify GROMACS is installed and accessible"""
        try:
            result = subprocess.run(
                [self.gmx_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"GROMACS found: {result.stdout.split(chr(10))[0]}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.error(f"GROMACS not found at {self.gmx_path}: {e}")
            raise RuntimeError(f"GROMACS installation not found at {self.gmx_path}")
        return False

    def run_command(
        self,
        command: str,
        input_file: Optional[str] = None,
        output_file: Optional[str] = None,
        args: Optional[List[str]] = None,
        working_dir: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """
        Run a GROMACS command.
        
        Args:
            command: GROMACS command (e.g., 'editconf', 'grompp', 'mdrun')
            input_file: Input file path
            output_file: Output file path
            args: Additional arguments
            working_dir: Working directory
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        cmd = [self.gmx_path, command]
        
        if input_file:
            cmd.extend(["-f", input_file])
        if output_file:
            cmd.extend(["-o", output_file])
        
        if args:
            cmd.extend(args)
        
        # Add threading options
        cmd.extend(["-nt", str(self.threads)])
        
        if self.gpu:
            cmd.extend(["-gpu_id", "0"])
        
        logger.info(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=3600
            )
            
            if result.returncode != 0:
                logger.error(f"Command failed: {result.stderr}")
            else:
                logger.info(f"Command succeeded: {command}")
            
            return result.returncode, result.stdout, result.stderr
        
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {command}")
            raise RuntimeError(f"GROMACS command timeout: {command}")
        except Exception as e:
            logger.error(f"Command error: {e}")
            raise

    def editconf(self, structure: str, output: str, **kwargs) -> bool:
        """Edit structure file (PDB to GRO conversion, box setup, etc.)"""
        args = []
        if "box" in kwargs:
            args.extend(["-box"] + list(map(str, kwargs["box"])))
        if "center" in kwargs and kwargs["center"]:
            args.append("-center")
        
        returncode, _, _ = self.run_command(
            "editconf",
            input_file=structure,
            output_file=output,
            args=args
        )
        return returncode == 0

    def genbox(self, structure: str, topology: str, output_gro: str, output_top: str, **kwargs) -> bool:
        """Generate simulation box with solvent"""
        args = ["-cs", kwargs.get("water_model", "spc216.gro")]
        if "distance" in kwargs:
            args.extend(["-d", str(kwargs["distance"])])
        
        returncode, _, _ = self.run_command(
            "genbox",
            input_file=structure,
            output_file=output_gro,
            args=args + ["-p", topology, "-o", output_top]
        )
        return returncode == 0

    def grompp(
        self,
        structure: str,
        topology: str,
        mdp: str,
        output_tpr: str,
        **kwargs
    ) -> bool:
        """Pre-process topology and run parameters"""
        args = []
        if "maxwarn" in kwargs:
            args.extend(["-maxwarn", str(kwargs["maxwarn"])])
        
        returncode, _, _ = self.run_command(
            "grompp",
            input_file=structure,
            args=["-p", topology, "-f", mdp, "-o", output_tpr] + args
        )
        return returncode == 0

    def mdrun(
        self,
        tpr_file: str,
        output_prefix: str,
        **kwargs
    ) -> bool:
        """Run molecular dynamics simulation"""
        args = [
            "-s", tpr_file,
            "-o", f"{output_prefix}.trr",
            "-x", f"{output_prefix}.xtc",
            "-e", f"{output_prefix}.edr",
            "-g", f"{output_prefix}.log",
            "-c", f"{output_prefix}.gro",
        ]
        
        if "checkpoint" in kwargs:
            args.extend(["-cpi", kwargs["checkpoint"]])
        
        if self.gpu:
            args.extend(["-nb", "gpu"])
        
        returncode, _, _ = self.run_command(
            "mdrun",
            args=args
        )
        return returncode == 0

    def trjconv(
        self,
        trajectory: str,
        structure: str,
        output: str,
        **kwargs
    ) -> bool:
        """Convert trajectory format"""
        args = []
        if "skip" in kwargs:
            args.extend(["-skip", str(kwargs["skip"])])
        if "fit" in kwargs:
            args.extend(["-fit", kwargs["fit"]])
        
        returncode, _, _ = self.run_command(
            "trjconv",
            input_file=trajectory,
            args=["-s", structure, "-o", output] + args
        )
        return returncode == 0

    def energy(
        self,
        edr_file: str,
        output: str,
        groups: Optional[List[str]] = None
    ) -> bool:
        """Extract energy data from EDR file"""
        args = ["-f", edr_file, "-o", output]
        
        if groups:
            args.extend(["-groups", " ".join(groups)])
        
        returncode, _, _ = self.run_command(
            "energy",
            args=args
        )
        return returncode == 0

    def get_version(self) -> str:
        """Get GROMACS version"""
        try:
            result = subprocess.run(
                [self.gmx_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.split("\n")[0] if result.returncode == 0 else "Unknown"
        except Exception:
            return "Unknown"
