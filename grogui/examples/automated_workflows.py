"""Automated workflow and command execution examples"""

from pathlib import Path
from grogui.core.command_executor import AutomatedCommandExecutor


def example_full_simulation_workflow():
    """
    Example: Complete simulation workflow automation.
    Demonstrates how to run a full MD simulation pipeline automatically.
    """
    project_dir = Path("./projects/example_simulation")
    project_dir.mkdir(parents=True, exist_ok=True)
    
    executor = AutomatedCommandExecutor(project_dir, verbose=True)
    
    # Simulate minimization workflow
    print("\n1. Running Minimization...")
    min_results = executor.simulate_minimization(
        structure="protein.gro",
        topology="topol.top",
        mdp_file="minimize.mdp",
        output_prefix="min"
    )
    
    # Simulate NVT equilibration
    print("\n2. Running NVT Equilibration (100ps)...")
    nvt_results = executor.simulate_equilibration(
        structure="min.gro",
        topology="topol.top",
        mdp_file="nvt.mdp",
        output_prefix="nvt",
        ensemble="nvt"
    )
    
    # Simulate NPT equilibration
    print("\n3. Running NPT Equilibration (100ps)...")
    npt_results = executor.simulate_equilibration(
        structure="nvt.gro",
        topology="topol.top",
        mdp_file="npt.mdp",
        output_prefix="npt",
        ensemble="npt"
    )
    
    # Simulate production run (100ns)
    print("\n4. Running Production MD (100ns)...")
    prod_results = executor.simulate_production(
        structure="npt.gro",
        topology="topol.top",
        mdp_file="production.mdp",
        output_prefix="prod"
    )
    
    # Run analysis
    print("\n5. Running Trajectory Analysis...")
    analysis_results = executor.run_analysis_workflow(
        trajectory="prod.xtc",
        structure="prod.gro",
        analyses=["RMSD", "RMSF", "GYRATE", "SASA"]
    )
    
    # Save execution log
    executor.save_execution_log(str(project_dir / "execution.log.json"))
    executor.print_summary()


def example_custom_workflow():
    """
    Example: Custom command workflow.
    Demonstrates how to create and execute custom workflows.
    """
    project_dir = Path("./projects/custom_workflow")
    project_dir.mkdir(parents=True, exist_ok=True)
    
    executor = AutomatedCommandExecutor(project_dir, verbose=True)
    
    # Define custom workflow
    custom_workflow = [
        {
            "workflow_name": "Custom Analysis Workflow",
            "name": "Convert trajectory format",
            "gmx_command": "trjconv",
            "args": ["-f", "prod.xtc", "-s", "prod.gro", "-o", "prod_fit.xtc", "-fit", "rotxy"]
        },
        {
            "name": "Extract center of mass",
            "gmx_command": "traj",
            "args": ["-f", "prod_fit.xtc", "-s", "prod.gro", "-o", "com.xvg"]
        },
        {
            "name": "Calculate energy landscape",
            "gmx_command": "angle",
            "args": ["-f", "prod.xtc", "-s", "prod.gro", "-o", "angle.xvg"]
        }
    ]
    
    results = executor.run_workflow(custom_workflow)
    executor.print_summary()
    
    return results


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 GROGUI AUTOMATED COMMAND EXECUTION EXAMPLES")
    print("="*80 + "\n")
    
    print("Example 1: Full Simulation Workflow")
    print("-" * 80)
    try:
        example_full_simulation_workflow()
    except Exception as e:
        print(f"Note: This is a demonstration. In real use: {e}")
    
    print("\n\nExample 2: Custom Workflow")
    print("-" * 80)
    try:
        example_custom_workflow()
    except Exception as e:
        print(f"Note: This is a demonstration. In real use: {e}")
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80 + "\n")
