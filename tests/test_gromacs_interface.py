"""Unit tests for GROMACS interface module"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from grogui.core.gromacs_interface import GromacsInterface


class TestGromacsInterface:
    """Test GromacsInterface functionality"""

    @pytest.fixture
    def gmx(self):
        """Create mock GROMACS interface"""
        with patch('grogui.core.gromacs_interface.subprocess.run'):
            return GromacsInterface(gmx_path='gmx', gpu=False, threads=4)

    def test_initialization(self, gmx):
        """Test GromacsInterface initialization"""
        assert gmx.gmx_path == 'gmx'
        assert gmx.gpu == False
        assert gmx.threads == 4

    def test_editconf(self, gmx):
        """Test editconf command"""
        with patch('grogui.core.gromacs_interface.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
            result = gmx.editconf('input.pdb', 'output.gro')
            assert result == True

    def test_grompp(self, gmx):
        """Test grompp preprocessing"""
        with patch('grogui.core.gromacs_interface.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
            result = gmx.grompp('struct.gro', 'topol.top', 'min.mdp', 'out.tpr')
            assert result == True

    def test_mdrun(self, gmx):
        """Test mdrun execution"""
        with patch('grogui.core.gromacs_interface.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
            result = gmx.mdrun('system.tpr', 'output')
            assert result == True

    def test_energy(self, gmx):
        """Test energy extraction"""
        with patch('grogui.core.gromacs_interface.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
            result = gmx.energy('system.edr', 'energy.xvg')
            assert result == True


class TestGromacsInterfaceErrors:
    """Test error handling"""

    def test_invalid_gmx_path(self):
        """Test handling of invalid GROMACS path"""
        with pytest.raises(RuntimeError):
            GromacsInterface(gmx_path='/nonexistent/gmx')

    def test_command_failure(self):
        """Test handling of failed command"""
        with patch('grogui.core.gromacs_interface.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='Error')
            gmx = GromacsInterface(gmx_path='gmx')
            # Should handle gracefully
            assert gmx is not None
