"""Unit tests for trajectory analysis module"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock
from grogui.analysis.trajectory import (
    SimulationTimeController,
    TrajectoryAnalysis,
    TRAJECTORY_ANALYSIS_PRESETS
)


class TestSimulationTimeController:
    """Test SimulationTimeController"""

    @pytest.fixture
    def controller(self):
        """Create controller instance"""
        return SimulationTimeController()

    def test_available_time_scales(self, controller):
        """Test available time scales"""
        scales = controller.get_available_time_scales()
        assert '1ns' in scales
        assert '5ns' in scales
        assert '10ns' in scales
        assert '50ns' in scales
        assert '100ns' in scales
        assert '200ns' in scales
        assert '300ns' in scales
        assert '500ns' in scales
        assert '1000ns' in scales

    def test_select_time_scale(self, controller):
        """Test selecting time scale"""
        success, msg = controller.select_time_scale('100ns')
        assert success == True
        assert '100ns' in msg
        assert controller.selected_time == '100ns'

    def test_select_invalid_time_scale(self, controller):
        """Test selecting invalid time scale"""
        success, msg = controller.select_time_scale('999ns')
        assert success == False
        assert 'Invalid' in msg

    def test_validate_simulation_time(self, controller):
        """Test validating simulation time"""
        # Valid times
        for time_ns in [1, 5, 10, 50, 100, 200, 300, 500, 1000]:
            is_valid, msg = controller.validate_simulation_time(time_ns)
            assert is_valid == True
            assert str(time_ns) in msg

    def test_validate_invalid_time(self, controller):
        """Test invalid time validation"""
        is_valid, msg = controller.validate_simulation_time(42)
        assert is_valid == False

    def test_time_scale_info(self, controller):
        """Test getting time scale info"""
        info = controller.get_time_scale_info('100ns')
        assert info is not None
        assert info['time_ns'] == 100
        assert info['time_ps'] == 100000

    def test_recommended_analysis(self, controller):
        """Test recommended analysis"""
        # 1ns should recommend quick_check
        info = controller.get_time_scale_info('1ns')
        assert info['recommended_analysis'] == 'quick_check'
        
        # 100ns should recommend standard
        info = controller.get_time_scale_info('100ns')
        assert info['recommended_analysis'] == 'standard'
        
        # 500ns should recommend extended
        info = controller.get_time_scale_info('500ns')
        assert info['recommended_analysis'] == 'extended'
        
        # 1000ns should recommend production
        info = controller.get_time_scale_info('1000ns')
        assert info['recommended_analysis'] == 'production'

    def test_list_time_scales_formatted(self, controller):
        """Test formatted time scale listing"""
        output = controller.list_all_time_scales_formatted()
        assert isinstance(output, str)
        assert '1ns' in output
        assert '1000ns' in output
        assert 'ultrashort' in output
        assert 'long' in output


class TestTrajectoryAnalysis:
    """Test TrajectoryAnalysis"""

    @pytest.fixture
    def analysis(self, tmp_path):
        """Create analysis instance"""
        return TrajectoryAnalysis(
            'test_project',
            tmp_path,
            'trajectory.xtc',
            'structure.gro'
        )

    def test_initialization(self, analysis):
        """Test initialization"""
        assert analysis.project_name == 'test_project'
        assert analysis.trajectory_file == 'trajectory.xtc'
        assert analysis.structure_file == 'structure.gro'

    def test_calculate_rmsd(self, analysis):
        """Test RMSD calculation"""
        result = analysis.calculate_rmsd()
        assert result['metric'] == 'RMSD'
        assert result['status'] == 'completed'

    def test_calculate_rmsf(self, analysis):
        """Test RMSF calculation"""
        result = analysis.calculate_rmsf()
        assert result['metric'] == 'RMSF'
        assert result['per_residue'] == True

    def test_calculate_radius_gyration(self, analysis):
        """Test Rg calculation"""
        result = analysis.calculate_radius_gyration()
        assert result['metric'] == 'Radius of Gyration'
        assert 'mean' in result

    def test_calculate_sasa(self, analysis):
        """Test SASA calculation"""
        result = analysis.calculate_sasa()
        assert result['metric'] == 'SASA'
        assert 'probe_radius' in result

    def test_hydrogen_bonds(self, analysis):
        """Test hydrogen bond analysis"""
        result = analysis.analyze_hydrogen_bonds()
        assert result['metric'] == 'Hydrogen Bonds'
        assert 'total_hbonds' in result

    def test_clustering(self, analysis):
        """Test clustering analysis"""
        result = analysis.clustering_analysis()
        assert result['metric'] == 'Clustering'
        assert result['method'] == 'kmeans'

    def test_pca(self, analysis):
        """Test PCA analysis"""
        result = analysis.pca_analysis()
        assert result['metric'] == 'PCA'
        assert 'explained_variance' in result

    def test_analysis_recommendations(self, analysis):
        """Test getting analysis recommendations"""
        recs = analysis.get_analysis_recommendations(100)
        assert recs['simulation_time_ns'] == 100
        assert 'recommended_preset' in recs
        assert 'recommended_analyses' in recs


class TestAnalysisPresets:
    """Test analysis presets"""

    def test_presets_exist(self):
        """Test that presets are defined"""
        assert 'quick_check' in TRAJECTORY_ANALYSIS_PRESETS
        assert 'standard' in TRAJECTORY_ANALYSIS_PRESETS
        assert 'extended' in TRAJECTORY_ANALYSIS_PRESETS
        assert 'production' in TRAJECTORY_ANALYSIS_PRESETS

    def test_preset_structure(self):
        """Test preset structure"""
        preset = TRAJECTORY_ANALYSIS_PRESETS['standard']
        assert 'name' in preset
        assert 'analyses' in preset
        assert isinstance(preset['analyses'], list)
        assert len(preset['analyses']) > 0

    def test_preset_time_ranges(self):
        """Test preset time ranges"""
        quick = TRAJECTORY_ANALYSIS_PRESETS['quick_check']
        assert quick['min_time'] <= 10
        
        prod = TRAJECTORY_ANALYSIS_PRESETS['production']
        assert prod['min_time'] >= 500
