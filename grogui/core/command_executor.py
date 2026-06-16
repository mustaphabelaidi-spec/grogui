"""Automated command execution and workflow orchestration"""

import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of command execution"""
    command: str
    return_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timestamp: str
    success: bool

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "command": self.command,
            "return_code": self.return_code,
            "stdout": self.stdout[:500],  # First 500 chars
            "stderr": self.stderr[:500],
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
            "success": self.success,
        }


class AutomatedCommandExecutor:
    """Execute GROMACS and simulation commands automatically"""

    def __init__(
        self,
        project_dir: Path,
        gmx_path: str = "gmx",
        verbose: bool = True,
    ):
        """
        Initialize command executor.
        
        Args:
            project_dir: Project directory
            gmx_path: Path to GROMACS executable
            verbose: Print command output
        """
        self.project_dir = Path(project_dir)
        self.gmx_path = gmx_path
        self.verbose = verbose
        self.logger = logger
        self.execution_history: List[CommandResult] = []
        self.working_dir = self.project_dir

    def execute_command(
        self,
        command: str,
        args: Optional[List[str]] = None,
        input_file: Optional[str] = None,
        output_file: Optional[str] = None,
        cwd: Optional[Path] = None,
        **kwargs
    ) -> CommandResult:
        """
        Execute a system command.
        
        Args:
            command: Command to execute
            args: Command arguments
            input_file: Input file for command
            output_file: Output file for command
            cwd: Working directory
            **kwargs: Additional keyword arguments
            
        Returns:
            CommandResult object
        """
        import time
        
        # Build full command
        cmd = [command]
        
        if input_file:
            cmd.extend(["-f", input_file])
        if output_file:
            cmd.extend(["-o", output_file])
        if args:
            cmd.extend(args)
        
        working_dir = cwd or self.working_dir
        full_cmd = " ".join(cmd)
        
        self.logger.info(f"Executing: {full_cmd}")
        if self.verbose:
            print(f"\n>>> {full_cmd}")
        
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=kwargs.get("timeout", 3600)
            )
            duration = time.time() - start_time
            
            cmd_result = CommandResult(
                command=full_cmd,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_seconds=duration,
                timestamp=datetime.now().isoformat(),
                success=result.returncode == 0
            )
            
            self.execution_history.append(cmd_result)
            
            if result.returncode == 0:
                self.logger.info(
                    f"✓ Command succeeded in {duration:.2f}s"
                )
                if self.verbose and result.stdout:
                    print(result.stdout[:200])
            else:
                self.logger.error(
                    f"✗ Command failed with code {result.returncode}"
                )
                if self.verbose and result.stderr:
                    print(f"Error: {result.stderr[:200]}")
            
            return cmd_result
        
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timeout: {full_cmd}")
            raise RuntimeError(f"Command timeout after {kwargs.get('timeout')}s")
        except Exception as e:
            self.logger.error(f"Command error: {e}")
            raise

    def execute_gromacs_command(
        self,
        gmx_command: str,
        args: Optional[List[str]] = None,
        **kwargs
    ) -> CommandResult:
        """
        Execute GROMACS command.
        
        Args:
            gmx_command: GROMACS subcommand (e.g., 'editconf', 'grompp')
            args: Additional arguments
            **kwargs: Keyword arguments
            
        Returns:
            CommandResult object
        """
        cmd = [self.gmx_path, gmx_command]
        if args:
            cmd.extend(args)
        
        return self.execute_command(
            cmd[0],
            args=cmd[1:],
            **kwargs
        )

    def run_workflow(
        self,
        workflow: List[Dict],
        stop_on_error: bool = True,
    ) -> Dict:
        """
        Execute a workflow of commands.
        
        Args:
            workflow: List of command dictionaries with 'name' and 'command' keys
            stop_on_error: Stop execution on first error
            
        Returns:
            Workflow execution results
        """
        self.logger.info(f"Starting workflow with {len(workflow)} steps")
        
        results = {
            "workflow_name": workflow[0].get("workflow_name", "unnamed"),
            "steps_total": len(workflow),
            "steps_completed": 0,
            "steps_failed": 0,
            "results": [],
        }
        
        for i, step in enumerate(workflow, 1):
            step_name = step.get("name", f"Step {i}")
            self.logger.info(f"\n[{i}/{len(workflow)}] {step_name}")
            
            try:
                # Execute step command
                if "command" in step:
                    cmd_result = self.execute_command(
                        step["command"],
                        args=step.get("args"),
                        cwd=step.get("cwd")
                    )
                elif "gmx_command" in step:
                    cmd_result = self.execute_gromacs_command(
                        step["gmx_command"],
                        args=step.get("args")
                    )
                
                results["results"].append({
                    "step": step_name,
                    "success": cmd_result.success,
                    "duration": cmd_result.duration_seconds,
                })
                
                if cmd_result.success:
                    results["steps_completed"] += 1
                    self.logger.info(f"✓ {step_name} completed")
                else:
                    results["steps_failed"] += 1
                    self.logger.error(f"✗ {step_name} failed")
                    
                    if stop_on_error:
                        self.logger.error("Stopping workflow on error")
                        break
            
            except Exception as e:
                self.logger.error(f"Workflow error in {step_name}: {e}")
                results["steps_failed"] += 1
                
                if stop_on_error:
                    break
        
        self.logger.info(
            f"\nWorkflow completed: {results['steps_completed']}/{results['steps_total']} steps"
        )
        
        return results

    def simulate_minimization(
        self,
        structure: str,
        topology: str,
        mdp_file: str,
        output_prefix: str,
    ) -> Dict:
        """
        Run full minimization workflow.
        
        Args:
            structure: Structure file (GRO)
            topology: Topology file (TOP)
            mdp_file: MDP parameters file
            output_prefix: Output file prefix
            
        Returns:
            Workflow results
        """
        workflow = [
            {
                "workflow_name": "Energy Minimization",
                "name": "Preprocessing (grompp)",
                "gmx_command": "grompp",
                "args": ["-f", mdp_file, "-p", topology, "-c", structure, "-o", f"{output_prefix}.tpr"]
            },
            {
                "name": "Energy Minimization (mdrun)",
                "gmx_command": "mdrun",
                "args": ["-s", f"{output_prefix}.tpr", "-o", f"{output_prefix}.trr", "-e", f"{output_prefix}.edr", "-g", f"{output_prefix}.log"]
            }
        ]
        
        return self.run_workflow(workflow)

    def simulate_equilibration(
        self,
        structure: str,
        topology: str,
        mdp_file: str,
        output_prefix: str,
        ensemble: str = "nvt",
    ) -> Dict:
        """
        Run full equilibration workflow (NVT or NPT).
        
        Args:
            structure: Structure file
            topology: Topology file
            mdp_file: MDP file
            output_prefix: Output prefix
            ensemble: "nvt" or "npt"
            
        Returns:
            Workflow results
        """
        workflow = [
            {
                "workflow_name": f"{ensemble.upper()} Equilibration",
                "name": "Preprocessing",
                "gmx_command": "grompp",
                "args": ["-f", mdp_file, "-p", topology, "-c", structure, "-o", f"{output_prefix}.tpr"]
            },
            {
                "name": "Running simulation",
                "gmx_command": "mdrun",
                "args": ["-s", f"{output_prefix}.tpr", "-c", f"{output_prefix}.gro", "-e", f"{output_prefix}.edr", "-g", f"{output_prefix}.log"]
            }
        ]
        
        return self.run_workflow(workflow)

    def simulate_production(
        self,
        structure: str,
        topology: str,
        mdp_file: str,
        output_prefix: str,
        checkpoint: Optional[str] = None,
    ) -> Dict:
        """
        Run production MD simulation.
        
        Args:
            structure: Structure file
            topology: Topology file
            mdp_file: MDP file
            output_prefix: Output prefix
            checkpoint: Checkpoint file for restart
            
        Returns:
            Workflow results
        """
        workflow = [
            {
                "workflow_name": "Production MD",
                "name": "Preprocessing",
                "gmx_command": "grompp",
                "args": ["-f", mdp_file, "-p", topology, "-c", structure, "-o", f"{output_prefix}.tpr"]
            },
            {
                "name": "Production run",
                "gmx_command": "mdrun",
                "args": ["-s", f"{output_prefix}.tpr", "-x", f"{output_prefix}.xtc", "-e", f"{output_prefix}.edr", "-g", f"{output_prefix}.log"]
            }
        ]
        
        return self.run_workflow(workflow)

    def run_analysis_workflow(
        self,
        trajectory: str,
        structure: str,
        analyses: List[str],
    ) -> Dict:
        """
        Run trajectory analysis workflow.
        
        Args:
            trajectory: Trajectory file
            structure: Structure file
            analyses: List of analyses to run
            
        Returns:
            Analysis workflow results
        """
        workflow = [
            {"workflow_name": "Trajectory Analysis"}
        ]
        
        for analysis in analyses:
            if analysis.upper() == "RMSD":
                workflow.append({
                    "name": "RMSD Analysis",
                    "gmx_command": "rms",
                    "args": ["-f", trajectory, "-s", structure, "-o", "rmsd.xvg"]
                })
            elif analysis.upper() == "RMSF":
                workflow.append({
                    "name": "RMSF Analysis",
                    "gmx_command": "rmsf",
                    "args": ["-f", trajectory, "-s", structure, "-o", "rmsf.xvg"]
                })
            elif analysis.upper() == "GYRATE":
                workflow.append({
                    "name": "Radius of Gyration",
                    "gmx_command": "gyrate",
                    "args": ["-f", trajectory, "-s", structure, "-o", "gyrate.xvg"]
                })
            elif analysis.upper() == "SASA":
                workflow.append({
                    "name": "SASA Analysis",
                    "gmx_command": "sasa",
                    "args": ["-f", trajectory, "-s", structure, "-o", "sasa.xvg"]
                })
        
        return self.run_workflow(workflow)

    def get_execution_history(self) -> List[Dict]:
        """Get execution history"""
        return [cmd.to_dict() for cmd in self.execution_history]

    def save_execution_log(self, filepath: str) -> None:
        """Save execution log to file"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "total_commands": len(self.execution_history),
            "successful": sum(1 for cmd in self.execution_history if cmd.success),
            "failed": sum(1 for cmd in self.execution_history if not cmd.success),
            "commands": self.get_execution_history()
        }
        
        with open(filepath, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        self.logger.info(f"Execution log saved to {filepath}")

    def print_summary(self) -> None:
        """Print execution summary"""
        total = len(self.execution_history)
        successful = sum(1 for cmd in self.execution_history if cmd.success)
        failed = total - successful
        total_time = sum(cmd.duration_seconds for cmd in self.execution_history)
        
        print("\n" + "="*80)
        print("EXECUTION SUMMARY")
        print("="*80)
        print(f"Total commands executed: {total}")
        print(f"Successful: {successful} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success rate: {(successful/total*100):.1f}%")
        print(f"Total execution time: {total_time:.2f}s")
        print("="*80 + "\n")
