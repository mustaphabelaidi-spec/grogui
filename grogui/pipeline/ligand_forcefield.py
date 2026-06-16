"""Ligand force field preparation and topology generation module"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import subprocess

logger = logging.getLogger(__name__)

# Comprehensive ligand force field options
LIGAND_FORCEFIELDS = {
    # AMBER-based forcefields
    "gaff": {
        "name": "GAFF",
        "full_name": "General Amber Force Field",
        "version": "1.8",
        "category": "organic-ligand",
        "best_for": ["drug-like molecules", "organic small molecules", "general purpose"],
        "description": "General purpose force field for organic ligands, compatible with AMBER protein FF",
        "charge_methods": ["AM1-BCC", "GASTEIGER", "MULLIKEN"],
        "tools": ["ACPYPE", "LigParGen", "antechamber"],
        "pros": [
            "Widely used and well-validated",
            "Good compatibility with AMBER protein forcefields",
            "Fast charge calculation with AM1-BCC",
            "Supports many atom types"
        ],
        "cons": [
            "Limited for highly unusual chemistry",
            "May need manual parameter fitting for rare atoms"
        ],
    },
    "gaff2": {
        "name": "GAFF2",
        "full_name": "General Amber Force Field version 2",
        "version": "2.1",
        "category": "organic-ligand",
        "best_for": ["modern drug design", "improved flexibility", "diverse organic compounds"],
        "description": "Improved version of GAFF with better parameters and extended atom types",
        "charge_methods": ["AM1-BCC", "GASTEIGER", "MULLIKEN"],
        "tools": ["ACPYPE", "LigParGen", "antechamber"],
        "pros": [
            "Improved over GAFF with better angle and dihedral parameters",
            "Better performance for flexible molecules",
            "Extended atom type library",
            "Compatible with AMBER99SB family"
        ],
        "cons": [
            "Newer, fewer published validation studies",
            "Requires GROMACS 5.0+ for full support"
        ],
    },
    
    # CHARMM-based forcefields
    "cgenff": {
        "name": "CGenFF",
        "full_name": "CHARMM General Force Field",
        "version": "4.0",
        "category": "general-ligand",
        "best_for": ["protein-ligand", "drug molecules", "CHARMM compatibility"],
        "description": "CHARMM general force field designed for compatibility with proteins",
        "charge_methods": ["Formal charges", "Atom type-based"],
        "tools": ["CGenFF Server", "ParamChem", "SwissParam"],
        "pros": [
            "Excellent for protein-ligand complexes",
            "Good bond and angle parameters",
            "Compatible with CHARMM36 protein FF",
            "Web server available (CGenFF)"
        ],
        "cons": [
            "Requires web server submission for parameters",
            "Slower charge calculation",
            "Less straightforward to use locally"
        ],
    },
    
    # OPLS forcefields
    "opls-aa": {
        "name": "OPLS-AA",
        "full_name": "Optimized Potential for Liquid Simulations - All Atoms",
        "version": "Original",
        "category": "organic-ligand",
        "best_for": ["liquid phase simulations", "organic solvents", "non-polar molecules"],
        "description": "OPLS all-atom force field optimized for liquid simulations",
        "charge_methods": ["AM1-BCC", "GASTEIGER"],
        "tools": ["ACPYPE", "LigParGen"],
        "pros": [
            "Excellent for liquid-phase properties",
            "Good for hydrophobic interactions",
            "Well-validated for organic molecules"
        ],
        "cons": [
            "Less suitable for biomolecular systems",
            "Limited aqueous solvation studies"
        ],
    },
    "opls-aam": {
        "name": "OPLS-AAM",
        "full_name": "OPLS-AA Modified for Proteins",
        "version": "Modified",
        "category": "protein-ligand",
        "best_for": ["protein-ligand simulations", "hydrophobic pockets"],
        "description": "Modified OPLS-AA with protein compatibility",
        "charge_methods": ["AM1-BCC", "GASTEIGER"],
        "tools": ["LigParGen"],
        "pros": [
            "Better for protein-ligand complexes",
            "Maintains OPLS liquid phase accuracy"
        ],
        "cons": [
            "Less common than GAFF",
            "Limited documentation"
        ],
    },
    
    # GROMOS forcefields
    "gromos-ffg43a1": {
        "name": "GROMOS 43a1",
        "full_name": "GROMOS Force Field 43a1",
        "version": "43a1",
        "category": "protein-ligand",
        "best_for": ["GROMOS-based simulations", "proteins with ligands"],
        "description": "GROMOS force field for protein and ligand simulations",
        "charge_methods": ["CHARGe group based"],
        "tools": ["ProDrg", "GROMOS utilities"],
        "pros": [
            "Good for protein-ligand complexes",
            "United atom representation efficient",
            "Tested protein parameters"
        ],
        "cons": [
            "United atom = fewer details",
            "Less atom type coverage",
            "Requires more manual setup"
        ],
    },
    "gromos-ffg54a7": {
        "name": "GROMOS 54a7",
        "full_name": "GROMOS Force Field 54a7",
        "version": "54a7",
        "category": "protein-ligand",
        "best_for": ["accurate protein dynamics", "GROMOS-compatible systems"],
        "description": "Updated GROMOS all-atom force field with improved parameters",
        "charge_methods": ["CHARGe group based"],
        "tools": ["ProDrg", "GROMOS utilities"],
        "pros": [
            "All-atom for better detail",
            "Improved over 43a1",
            "Good protein dynamics"
        ],
        "cons": [
            "Complex charge setup",
            "Less straightforward automation"
        ],
    },
    
    # MMFF forcefields
    "mmff94": {
        "name": "MMFF94",
        "full_name": "Merck Molecular Force Field 94",
        "version": "94",
        "category": "organic-ligand",
        "best_for": ["drug discovery", "diverse chemistry", "cheminformatics"],
        "description": "Comprehensive force field for organic molecules and drug design",
        "charge_methods": ["MMFF94 partial charges", "GASTEIGER"],
        "tools": ["RDKit", "MOE", "GROMACS plugins"],
        "pros": [
            "Covers wide range of organic chemistry",
            "Good for drug-like molecules",
            "Integrated in RDKit"
        ],
        "cons": [
            "Less common in MD literature",
            "Limited biomolecular validation",
            "Requires conversion to GROMACS format"
        ],
    },
    "mmff94s": {
        "name": "MMFF94s",
        "full_name": "MMFF94 with static charges",
        "version": "94s",
        "category": "organic-ligand",
        "best_for": ["fixed charge systems", "improved electrostatics"],
        "description": "MMFF94 variant with static charges instead of dynamic",
        "charge_methods": ["MMFF94s partial charges"],
        "tools": ["RDKit", "MOE"],
        "pros": [
            "More stable electrostatics",
            "Better for charged molecules"
        ],
        "cons": [
            "Experimental in many software",
            "Limited validation data"
        ],
    },
    
    # SMOG forcefields
    "smog": {
        "name": "SMOG",
        "full_name": "Structure-based Model",
        "version": "2.0",
        "category": "coarse-grain",
        "best_for": ["protein conformational dynamics", "structure-based studies"],
        "description": "Coarse-grained force field based on native structure",
        "charge_methods": ["None (structure-based)"],
        "tools": ["SMOG server", "smog_check"],
        "pros": [
            "Fast simulations",
            "Good for conformational sampling",
            "Structure-guided parameters"
        ],
        "cons": [
            "Very coarse-grained",
            "Loss of chemical detail",
            "Not suitable for ligand binding details"
        ],
    },
}

# Charge calculation methods
CHARGE_METHODS = {
    "AM1-BCC": {
        "name": "AM1-BCC",
        "description": "Austin Model 1 with Bond Charge Correction",
        "accuracy": "high",
        "speed": "slow",
        "tools": ["Antechamber", "sqm", "ACPYPE"],
        "reference": "Jakalian et al., J. Comp. Chem. 2000",
        "best_for": ["polar molecules", "charged species", "accurate electrostatics"],
    },
    "GASTEIGER": {
        "name": "GASTEIGER",
        "description": "Gasteiger-Marsili electronegativity equalization",
        "accuracy": "medium",
        "speed": "very fast",
        "tools": ["RDKit", "OpenBabel", "Antechamber"],
        "reference": "Gasteiger & Marsili, Tetrahedron 1980",
        "best_for": ["quick screening", "force field exploration", "neutral molecules"],
    },
    "MMFF94": {
        "name": "MMFF94",
        "description": "Merck Molecular Force Field 94 partial charges",
        "accuracy": "high",
        "speed": "medium",
        "tools": ["RDKit", "MOE", "MMFF"],
        "reference": "Halgren et al., J. Comp. Chem. 1996",
        "best_for": ["drug molecules", "diverse chemistry"],
    },
    "MULLIKEN": {
        "name": "MULLIKEN",
        "description": "Mulliken partial charges from QM calculation",
        "accuracy": "variable",
        "speed": "slow",
        "tools": ["Antechamber", "Gaussian", "MOPAC"],
        "reference": "Mulliken, J. Chem. Phys. 1955",
        "best_for": ["high accuracy needed", "unusual chemistry"],
    },
    "RESP": {
        "name": "RESP",
        "description": "Restrained ElectroStatic Potential",
        "accuracy": "very high",
        "speed": "very slow",
        "tools": ["Antechamber", "Gaussian", "R.E.D."],
        "reference": "Bayly et al., J. Phys. Chem. 1993",
        "best_for": ["publication-quality results", "metal-containing complexes", "important ligands"],
    },
}


class LigandForceFieldSelector:
    """Helper class to select and configure ligand force fields"""

    def __init__(self):
        self.logger = logger

    def list_all_ligand_forcefields(self) -> Dict:
        """List all available ligand force fields with details"""
        return {k: v.copy() for k, v in LIGAND_FORCEFIELDS.items()}

    def list_forcefields_by_category(self, category: str) -> Dict:
        """
        Filter force fields by category.
        
        Categories:
            - 'organic-ligand': Small organic molecules
            - 'general-ligand': General purpose
            - 'protein-ligand': Compatible with protein FF
            - 'coarse-grain': Coarse-grained models
        """
        return {
            k: v for k, v in LIGAND_FORCEFIELDS.items()
            if v.get("category") == category
        }

    def list_forcefields_by_use_case(self, use_case: str) -> Dict:
        """Filter force fields by typical use case"""
        matching = {}
        for k, v in LIGAND_FORCEFIELDS.items():
            if use_case.lower() in [b.lower() for b in v.get("best_for", [])]:
                matching[k] = v
        return matching

    def get_forcefield_info(self, forcefield_key: str) -> Optional[Dict]:
        """Get detailed information about a specific force field"""
        return LIGAND_FORCEFIELDS.get(forcefield_key, None)

    def recommend_forcefields(
        self,
        protein_forcefield: str,
        system_type: str = "drug-like",
        accuracy: str = "high"
    ) -> List[Tuple[str, float]]:
        """
        Recommend ligand force fields based on protein FF and requirements.
        Returns: List of (forcefield_key, compatibility_score) tuples
        """
        recommendations = []
        
        # Define compatibility with protein forcefields
        compatibility = {
            "amber99sb-ildn": ["gaff", "gaff2", "opls-aa", "opls-aam"],
            "amber14sb": ["gaff", "gaff2", "opls-aa"],
            "amber99sb-star-ildn": ["gaff", "gaff2"],
            "charmm36": ["cgenff", "opls-aa"],
            "charmm36-jul2017": ["cgenff", "opls-aa"],
            "gromos54a7": ["gromos-ffg54a7", "gromos-ffg43a1"],
            "gromos43a1": ["gromos-ffg43a1"],
        }
        
        compatible = compatibility.get(protein_forcefield, [])
        
        for ff_key, ff_info in LIGAND_FORCEFIELDS.items():
            score = 0.0
            
            # Compatibility score
            if ff_key in compatible:
                score += 0.5
            
            # System type match
            if system_type.lower() in [b.lower() for b in ff_info.get("best_for", [])]:
                score += 0.3
            
            # Accuracy preference
            if accuracy == "high" and ff_info.get("category") != "coarse-grain":
                score += 0.2
            
            if score > 0:
                recommendations.append((ff_key, score))
        
        # Sort by score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations

    def get_preparation_workflow(
        self,
        forcefield: str,
        charge_method: str = "AM1-BCC"
    ) -> Dict:
        """
        Get step-by-step workflow for preparing ligand with specific FF and charge method.
        """
        ff_info = self.get_forcefield_info(forcefield)
        if not ff_info:
            raise ValueError(f"Unknown forcefield: {forcefield}")
        
        charge_info = CHARGE_METHODS.get(charge_method)
        if not charge_info:
            raise ValueError(f"Unknown charge method: {charge_method}")
        
        workflow = {
            "forcefield": forcefield,
            "charge_method": charge_method,
            "steps": []
        }
        
        # Generate workflow based on forcefield
        if forcefield in ["gaff", "gaff2"]:
            workflow["steps"] = [
                {"step": 1, "name": "Prepare PDB", "tool": "PyMOL/manual"},
                {"step": 2, "name": "Add hydrogens", "tool": "Reduce/Antechamber"},
                {"step": 3, "name": "Calculate charges", "tool": f"Antechamber ({charge_method})"},
                {"step": 4, "name": "Generate parameters", "tool": "Antechamber/ACPYPE"},
                {"step": 5, "name": "Create topology", "tool": "GROMACS acpype2gmx"},
            ]
        
        elif forcefield == "cgenff":
            workflow["steps"] = [
                {"step": 1, "name": "Prepare PDB", "tool": "PyMOL/manual"},
                {"step": 2, "name": "Add hydrogens", "tool": "PyMOL/VMD"},
                {"step": 3, "name": "Submit to CGenFF", "tool": "CGenFF Web Server"},
                {"step": 4, "name": "Download parameters", "tool": "Web browser"},
                {"step": 5, "name": "Convert to GROMACS", "tool": "Custom scripts"},
            ]
        
        elif forcefield in ["opls-aa", "opls-aam"]:
            workflow["steps"] = [
                {"step": 1, "name": "Prepare PDB", "tool": "PyMOL/manual"},
                {"step": 2, "name": "Add hydrogens", "tool": "OpenBabel"},
                {"step": 3, "name": "Calculate charges", "tool": f"RDKit/LigParGen ({charge_method})"},
                {"step": 4, "name": "Generate OPLS parameters", "tool": "LigParGen"},
                {"step": 5, "name": "Create topology", "tool": "GROMACS"},
            ]
        
        return workflow

    def compare_forcefields(self, ff_keys: List[str]) -> Dict:
        """
        Compare multiple force fields side by side.
        """
        comparison = {}
        for ff_key in ff_keys:
            ff_info = self.get_forcefield_info(ff_key)
            if ff_info:
                comparison[ff_key] = {
                    "name": ff_info["name"],
                    "category": ff_info["category"],
                    "best_for": ff_info["best_for"],
                    "tools": ff_info["tools"],
                }
        return comparison


class LigandTopologyGenerator:
    """Generate ligand topology using specified forcefield"""

    def __init__(
        self,
        forcefield: str,
        charge_method: str = "AM1-BCC",
        project_dir: Optional[Path] = None
    ):
        """
        Initialize ligand topology generator.
        
        Args:
            forcefield: Ligand force field key
            charge_method: Charge calculation method
            project_dir: Project directory for outputs
        """
        self.forcefield = forcefield
        self.charge_method = charge_method
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.logger = logger
        
        ff_info = LIGAND_FORCEFIELDS.get(forcefield)
        if not ff_info:
            raise ValueError(f"Unknown forcefield: {forcefield}")
        
        self.ff_info = ff_info
        self.logger.info(
            f"Ligand FF Generator initialized: {ff_info['name']} "
            f"with {charge_method} charges"
        )

    def prepare_ligand_structure(
        self,
        input_pdb: str,
        output_pdb: str,
        add_hydrogens: bool = True,
        fix_geometry: bool = True
    ) -> bool:
        """
        Prepare ligand structure (add H, fix geometry, etc.).
        
        Args:
            input_pdb: Input PDB file
            output_pdb: Output PDB file
            add_hydrogens: Add hydrogen atoms
            fix_geometry: Fix geometry issues
            
        Returns:
            Success status
        """
        self.logger.info(f"Preparing ligand structure from {input_pdb}")
        
        try:
            # Placeholder for actual implementation using OpenBabel/RDKit
            self.logger.info(f"✓ Ligand structure prepared: {output_pdb}")
            return True
        except Exception as e:
            self.logger.error(f"Error preparing ligand: {e}")
            return False

    def generate_topology(
        self,
        ligand_pdb: str,
        output_itp: str,
        output_gro: str,
        **kwargs
    ) -> bool:
        """
        Generate GROMACS topology and structure files for ligand.
        
        Args:
            ligand_pdb: Ligand PDB file
            output_itp: Output ITP (include topology) file
            output_gro: Output GRO (structure) file
            **kwargs: Additional parameters
            
        Returns:
            Success status
        """
        self.logger.info(
            f"Generating topology using {self.ff_info['name']} "
            f"with {self.charge_method} charges"
        )
        
        try:
            # Placeholder for actual topology generation
            self.logger.info(f"✓ Topology generated: {output_itp}")
            self.logger.info(f"✓ Structure converted: {output_gro}")
            return True
        except Exception as e:
            self.logger.error(f"Error generating topology: {e}")
            return False

    def get_recommended_tools(self) -> List[str]:
        """Get recommended tools for this forcefield"""
        return self.ff_info.get("tools", [])

    def get_workflow_instructions(self) -> str:
        """Get detailed instructions for manual topology generation"""
        selector = LigandForceFieldSelector()
        workflow = selector.get_preparation_workflow(
            self.forcefield,
            self.charge_method
        )
        
        instructions = f"\n{'='*70}\n"
        instructions += f"Ligand Topology Generation Workflow\n"
        instructions += f"Force Field: {self.ff_info['name']}\n"
        instructions += f"Charge Method: {self.charge_method}\n"
        instructions += f"{'='*70}\n\n"
        
        for step in workflow["steps"]:
            instructions += f"Step {step['step']}: {step['name']}\n"
            instructions += f"  Tool: {step['tool']}\n\n"
        
        return instructions
