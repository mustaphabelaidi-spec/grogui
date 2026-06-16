"""Unit tests for simulation manager"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from grogui.core.simulation_manager import SimulationManager, SimulationConfig


class TestSimulationManager:
    """Test SimulationManager functionality"""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for tests"""
        return tmp_path / "test_project"

    @pytest.fixture
    def manager(self, temp_dir):
        """Create SimulationManager instance"""
        with patch('grogui.core.gromacs_interface.GromacsInterface'):
            return SimulationManager('test_project', project_dir=str(temp_dir))

    def test_initialization(self, manager, temp_dir):
        """Test manager initialization"""
        assert manager.project_name == 'test_project'
        assert manager.project_dir == temp_dir
        assert manager.input_dir.exists()
        assert manager.output_dir.exists()
        assert manager.analysis_dir.exists()

    def test_config_creation(self):
        """Test configuration creation"""
        config = SimulationConfig(
            project_name='test',
            structure_file='protein.pdb',
            forcefield='amber99sb-ildn',
            temperature=300
        )
        assert config.project_name == 'test'
        assert config.temperature == 300

    def test_add_step(self, manager):
        """Test adding pipeline steps"""
        manager.add_step('minimization')
        manager.add_step('equilibration')
        assert 'minimization' in manager.pipeline_steps
        assert 'equilibration' in manager.pipeline_steps

    def test_remove_step(self, manager):
        """Test removing pipeline steps"""
        manager.add_step('minimization')
        manager.remove_step('minimization')
        assert 'minimization' not in manager.pipeline_steps

    def test_get_pipeline(self, manager):
        """Test getting pipeline"""
        manager.add_step('step1')
        manager.add_step('step2')
        pipeline = manager.get_pipeline()
        assert len(pipeline) == 2
        assert 'step1' in pipeline

    def test_file_paths(self, manager):
        """Test file path generation"""
        input_file = manager.get_input_file('structure.pdb')
        output_file = manager.get_output_file('result.gro')
        analysis_file = manager.get_analysis_file('rmsd.xvg')
        
        assert input_file.name == 'structure.pdb'
        assert output_file.name == 'result.gro'
        assert analysis_file.name == 'rmsd.xvg'

    def test_get_status(self, manager):
        """Test getting project status"""
        status = manager.get_status()
        assert status['project_name'] == 'test_project'
        assert 'last_updated' in status
        assert status['config_loaded'] == False
