# GroGUI - GROMACS Molecular Dynamics Simulation Runner & Analysis Tool

**Complete automation and analysis platform for GROMACS MD simulations**

## Overview

GroGUI is a comprehensive Python-based GUI application that automates the entire molecular dynamics simulation workflow with GROMACS, from setup through complete analysis.

## Features

### 🚀 Simulation Pipeline
- **Automated Setup**: Structure preparation, topology generation, box setup
- **Energy Minimization**: Steepest descent and conjugate gradient methods
- **Equilibration**: NVT and NPT ensemble equilibration
- **Production MD**: Long-timescale MD simulations with various ensembles
- **Checkpoint Management**: Automatic restart from checkpoints
- **Resource Monitoring**: Real-time CPU/GPU usage tracking

### 📊 Analysis Module
- **Trajectory Analysis**: RMSD, RMSF, Radius of Gyration (Rg)
- **Structural Analysis**: Secondary structure, hydrogen bonding
- **Dynamics**: Principal Component Analysis (PCA), Clustering
- **Thermodynamics**: Free energy calculations, Energy decomposition
- **Interaction Networks**: Protein-protein, protein-ligand interactions
- **Advanced Metrics**: Solvent accessibility, contact maps

### 🎨 User Interface
- **Interactive Dashboard**: Real-time simulation monitoring
- **Workflow Designer**: Visual pipeline configuration
- **Results Viewer**: Integrated trajectory and data visualization
- **Project Management**: Multi-project support with metadata

### ⚙️ Automation
- **Job Queuing**: Queue and schedule simulations
- **Parallel Execution**: Multiple simulations simultaneously
- **Error Handling**: Automatic recovery and logging
- **Batch Processing**: Process multiple systems

## Project Structure

```
grogui/
├── grogui/                          # Main package
│   ├── __init__.py
│   ├── core/                        # Core simulation logic
│   │   ├── __init__.py
│   │   ├── gromacs_interface.py     # GROMACS wrapper
│   │   ├── simulation_manager.py    # Simulation lifecycle
│   │   └── job_queue.py             # Job management
│   │
│   ├── pipeline/                    # Simulation workflows
│   │   ├── __init__.py
│   │   ├── setup.py                 # Structure/topology prep
│   │   ├── minimization.py          # Energy minimization
│   │   ├── equilibration.py         # NVT/NPT equilibration
│   │   └── production.py            # Production MD
│   │
│   ├── analysis/                    # Analysis framework
│   │   ├── __init__.py
│   │   ├── trajectory.py            # RMSD, RMSF, Rg
│   │   ├── structure.py             # Structural analysis
│   │   ├── dynamics.py              # PCA, clustering
│   │   ├── thermodynamics.py        # Energy/FE analysis
│   │   └── interactions.py          # Interaction networks
│   │
│   ├── visualization/               # Data visualization
│   │   ├── __init__.py
│   │   ├── trajectory_viewer.py     # Structure/trajectory display
│   │   ├── analysis_plots.py        # Analysis result plots
│   │   └── dashboard.py             # Real-time monitoring
│   │
│   ├── gui/                         # User interface
│   │   ├── __init__.py
│   │   ├── main_window.py           # Main application window
│   │   ├── widgets/                 # Custom widgets
│   │   │   ├── __init__.py
│   │   │   ├── simulation_setup.py
│   │   │   ├── analysis_panel.py
│   │   │   ├── dashboard_widget.py
│   │   │   └── results_viewer.py
│   │   ├── dialogs/                 # Dialog windows
│   │   │   ├── __init__.py
│   │   │   ├── project_dialog.py
│   │   │   ├── settings_dialog.py
│   │   │   └── results_export.py
│   │   └── styles/                  # UI themes
│   │       └── dark_theme.qss
│   │
│   ├── config/                      # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py              # App settings
│   │   └── defaults.py              # Default parameters
│   │
│   ├── utils/                       # Utilities
│   │   ├── __init__.py
│   │   ├── file_handler.py          # File operations
│   │   ├── logger.py                # Logging
│   │   └── validators.py            # Input validation
│   │
│   └── data/                        # Data management
│       ├── __init__.py
│       ├── database.py              # Project database
│       └── export.py                # Results export
│
├── tests/                           # Unit tests
│   ├── __init__.py
│   ├── test_gromacs_interface.py
│   ├── test_simulation_manager.py
│   ├── test_analysis.py
│   └── test_pipeline.py
│
├── examples/                        # Example projects
│   ├── protein_md.py
│   ├── protein_ligand_md.py
│   └── sample_data/
│
├── docs/                            # Documentation
│   ├── index.md
│   ├── installation.md
│   ├── quick_start.md
│   ├── pipeline_guide.md
│   ├── analysis_guide.md
│   └── api_reference.md
│
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package setup
├── LICENSE
└── .gitignore
```

## Installation

### Requirements
- Python 3.8+
- GROMACS 2020 or later
- PyQt6 (for GUI)
- MDAnalysis
- NumPy, SciPy, Pandas
- Matplotlib, PyVis

### Quick Install

```bash
git clone https://github.com/mustaphabelaidi-spec/grogui.git
cd grogui
pip install -r requirements.txt
python -m grogui.gui.main_window
```

## Quick Start

### Via GUI
1. Launch the application
2. Create a new project
3. Upload structure file (PDB/GRO)
4. Configure simulation parameters
5. Click "Run Pipeline"
6. View results in Analysis tab

### Via Python API

```python
from grogui.core import SimulationManager
from grogui.pipeline import MinimizationStep, EquilibrationStep, ProductionStep

# Create simulation manager
sim = SimulationManager('my_protein')

# Add pipeline steps
sim.add_step(MinimizationStep(steps=5000))
sim.add_step(EquilibrationStep(temperature=300, time=100))
sim.add_step(ProductionStep(temperature=300, time=1000))

# Run simulation
sim.run()

# Analyze results
from grogui.analysis import TrajectoryAnalysis
analysis = TrajectoryAnalysis('my_protein')
rmsd = analysis.calculate_rmsd()
rg = analysis.calculate_radius_gyration()
```

## Configuration

Create a `config.yaml` in your project directory:

```yaml
gromacs:
  path: /usr/bin/gmx
  gpu: true
  num_threads: 4

simulation:
  forcefield: amber99sb-ildn
  water_model: tip3p
  default_temperature: 300
  default_pressure: 1.0

analysis:
  trajectory_stride: 1000
  reference_frame: 0
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file

## Citation

If you use GroGUI in your research, please cite:
```
Belaid, M. (2026). GroGUI: Automated Molecular Dynamics Simulation and Analysis. 
https://github.com/mustaphabelaidi-spec/grogui
```

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

- Built on [GROMACS](http://www.gromacs.org/)
- Analysis powered by [MDAnalysis](https://www.mdanalysis.org/)
- GUI framework: [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
