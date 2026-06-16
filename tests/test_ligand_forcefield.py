"""Unit tests for ligand forcefield module"""

import pytest
from pathlib import Path
from grogui.pipeline.ligand_forcefield import (
    LigandForceFieldSelector,
    LigandTopologyGenerator,
    LIGAND_FORCEFIELDS,
    CHARGE_METHODS
)


class TestLigandForceFieldSelector:
    """Test LigandForceFieldSelector"""

    @pytest.fixture
    def selector(self):
        """Create selector instance"""
        return LigandForceFieldSelector()

    def test_list_all_forcefields(self, selector):
        """Test listing all ligand forcefields"""
        ffs = selector.list_all_ligand_forcefields()
        assert len(ffs) > 10
        assert 'gaff' in ffs
        assert 'cgenff' in ffs

    def test_list_by_category(self, selector):
        """Test filtering by category"""
        organic = selector.list_forcefields_by_category('organic-ligand')
        assert len(organic) > 0
        assert 'gaff' in organic

    def test_list_by_use_case(self, selector):
        """Test filtering by use case"""
        drug_ffs = selector.list_forcefields_by_use_case('drug-like molecules')
        assert len(drug_ffs) > 0
        assert 'gaff' in drug_ffs or 'gaff2' in drug_ffs

    def test_get_forcefield_info(self, selector):
        """Test getting forcefield info"""
        info = selector.get_forcefield_info('gaff')
        assert info is not None
        assert 'name' in info
        assert 'charge_methods' in info

    def test_recommend_forcefields(self, selector):
        """Test recommendations"""
        recs = selector.recommend_forcefields(
            protein_forcefield='amber99sb-ildn',
            system_type='drug-like'
        )
        assert len(recs) > 0
        assert recs[0][1] > 0  # Has compatibility score

    def test_compare_forcefields(self, selector):
        """Test comparison"""
        comparison = selector.compare_forcefields(['gaff', 'cgenff'])
        assert len(comparison) == 2
        assert 'gaff' in comparison
        assert 'cgenff' in comparison


class TestLigandTopologyGenerator:
    """Test LigandTopologyGenerator"""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create generator instance"""
        return LigandTopologyGenerator(
            forcefield='gaff',
            charge_method='AM1-BCC',
            project_dir=tmp_path
        )

    def test_initialization(self, generator):
        """Test initialization"""
        assert generator.forcefield == 'gaff'
        assert generator.charge_method == 'AM1-BCC'

    def test_get_recommended_tools(self, generator):
        """Test getting tools"""
        tools = generator.get_recommended_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_get_workflow_instructions(self, generator):
        """Test workflow instructions"""
        instructions = generator.get_workflow_instructions()
        assert isinstance(instructions, str)
        assert 'Step' in instructions
        assert 'GAFF' in instructions


class TestLigandForceFieldDatabase:
    """Test ligand forcefield database"""

    def test_ligand_forcefields_count(self):
        """Test number of ligand forcefields"""
        assert len(LIGAND_FORCEFIELDS) >= 12

    def test_forcefield_structure(self):
        """Test forcefield data structure"""
        ff = LIGAND_FORCEFIELDS['gaff']
        assert 'name' in ff
        assert 'category' in ff
        assert 'best_for' in ff
        assert 'tools' in ff
        assert isinstance(ff['best_for'], list)

    def test_charge_methods_count(self):
        """Test number of charge methods"""
        assert len(CHARGE_METHODS) >= 5

    def test_charge_method_info(self):
        """Test charge method info"""
        method = CHARGE_METHODS['AM1-BCC']
        assert 'description' in method
        assert 'accuracy' in method
        assert 'speed' in method
        assert 'tools' in method
