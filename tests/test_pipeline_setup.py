"""Unit tests for pipeline setup module"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from grogui.pipeline.setup import (
    SetupStep,
    SUPPORTED_FORCEFIELDS,
    WATER_MODELS,
    PL_SYSTEM_PRESETS
)


class TestSetupStep:
    """Test SetupStep functionality"""

    @pytest.fixture
    def setup(self, tmp_path):
        """Create SetupStep instance"""
        gmx = MagicMock()
        return SetupStep(gmx, tmp_path, forcefield='charmm36', water_model='tip3p')

    def test_initialization(self, setup):
        """Test SetupStep initialization"""
        assert setup.forcefield == 'charmm36'
        assert setup.water_model == 'tip3p'

    def test_invalid_forcefield(self, tmp_path):
        """Test handling of invalid forcefield"""
        gmx = MagicMock()
        with pytest.raises(ValueError):
            SetupStep(gmx, tmp_path, forcefield='invalid_ff')

    def test_invalid_water_model(self, tmp_path):
        """Test handling of invalid water model"""
        gmx = MagicMock()
        with pytest.raises(ValueError):
            SetupStep(gmx, tmp_path, water_model='invalid_water')

    def test_forcefield_water_compatibility(self, setup):
        """Test forcefield-water compatibility check"""
        is_compatible = setup.validate_forcefield_water_compatibility()
        assert is_compatible == True

    def test_get_forcefield_info(self, setup):
        """Test getting forcefield info"""
        info = setup.get_forcefield_info()
        assert 'name' in info
        assert 'category' in info
        assert info['supports_protein'] == True

    def test_get_water_model_info(self, setup):
        """Test getting water model info"""
        info = setup.get_water_model_info()
        assert 'name' in info
        assert 'molecules' in info
        assert info['molecules'] == 3  # tip3p has 3 sites

    def test_list_available_forcefields(self, setup):
        """Test listing forcefields"""
        ffs = setup.list_available_forcefields()
        assert 'amber99sb-ildn' in ffs
        assert 'charmm36' in ffs
        assert len(ffs) > 5

    def test_list_system_presets(self, setup):
        """Test listing system presets"""
        presets = setup.list_system_presets()
        assert 'protein-small-ligand' in presets
        assert 'protein-peptide-ligand' in presets

    def test_recommend_forcefield(self, setup):
        """Test forcefield recommendation"""
        ff = setup.recommend_forcefields_for_system('protein-small-ligand')
        assert ff is not None


class TestForceFieldDatabase:
    """Test forcefield database"""

    def test_supported_forcefields(self):
        """Test supported forcefields list"""
        assert len(SUPPORTED_FORCEFIELDS) > 5
        assert 'amber99sb-ildn' in SUPPORTED_FORCEFIELDS
        assert 'charmm36' in SUPPORTED_FORCEFIELDS

    def test_water_models(self):
        """Test water models"""
        assert len(WATER_MODELS) > 3
        assert 'tip3p' in WATER_MODELS
        assert 'tip4p' in WATER_MODELS

    def test_system_presets(self):
        """Test system presets"""
        assert len(PL_SYSTEM_PRESETS) > 2
        assert 'protein-small-ligand' in PL_SYSTEM_PRESETS

    def test_forcefield_properties(self):
        """Test forcefield properties"""
        ff = SUPPORTED_FORCEFIELDS['amber99sb-ildn']
        assert ff['protein'] == True
        assert isinstance(ff['water'], list)
        assert len(ff['water']) > 0
