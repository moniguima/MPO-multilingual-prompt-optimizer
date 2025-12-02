"""
Experiment tracking and results storage.

This module provides structured tracking of evaluation experiments,
enabling reproducibility and analysis.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ExperimentConfig:
    """Configuration for an evaluation experiment."""
    prompt_ids: List[str]
    languages: List[str]
    formality_levels: List[str]
    model: str
    temperature: float = 0.7
    max_tokens: int = 1024
    demo_mode: bool = False


@dataclass
class ExperimentRun:
    """
    Record of a complete experiment run.

    Tracks configuration, execution details, and results for reproducibility.
    """
    id: str
    name: str
    config: ExperimentConfig
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    status: str = "running"  # running, completed, failed
    results_summary: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert ExperimentConfig to dict
        if isinstance(data['config'], ExperimentConfig):
            data['config'] = asdict(data['config'])
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "ExperimentRun":
        """Create ExperimentRun from dictionary."""
        # Convert config dict back to ExperimentConfig
        if isinstance(data['config'], dict):
            data['config'] = ExperimentConfig(**data['config'])
        return cls(**data)


class ExperimentTracker:
    """
    Tracks evaluation experiments and stores results.

    Provides structured logging of experimental runs for reproducibility
    and analysis.
    """

    def __init__(self, experiments_dir: str = "data/experiments"):
        """
        Initialize experiment tracker.

        Args:
            experiments_dir: Directory for storing experiment data
        """
        self.experiments_dir = Path(experiments_dir)
        self.experiments_dir.mkdir(parents=True, exist_ok=True)

        # Index of all experiments
        self.index_file = self.experiments_dir / "experiments_index.json"
        self._load_index()

    def _load_index(self):
        """Load experiments index."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {
                "experiments": [],
                "created_at": datetime.utcnow().isoformat()
            }

    def _save_index(self):
        """Save experiments index."""
        self.index["updated_at"] = datetime.utcnow().isoformat()
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def create_experiment(
        self,
        name: str,
        config: ExperimentConfig,
        metadata: Optional[Dict] = None
    ) -> ExperimentRun:
        """
        Create a new experiment run.

        Args:
            name: Human-readable experiment name
            config: Experiment configuration
            metadata: Additional metadata

        Returns:
            ExperimentRun instance
        """
        # Generate unique ID
        exp_id = f"exp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        experiment = ExperimentRun(
            id=exp_id,
            name=name,
            config=config,
            metadata=metadata or {}
        )

        # Save experiment
        self._save_experiment(experiment)

        # Update index
        self.index["experiments"].append({
            "id": exp_id,
            "name": name,
            "started_at": experiment.started_at,
            "status": experiment.status
        })
        self._save_index()

        return experiment

    def _get_experiment_path(self, exp_id: str) -> Path:
        """Get file path for experiment data."""
        return self.experiments_dir / f"{exp_id}.json"

    def _save_experiment(self, experiment: ExperimentRun):
        """Save experiment to disk."""
        exp_path = self._get_experiment_path(experiment.id)
        with open(exp_path, 'w') as f:
            json.dump(experiment.to_dict(), f, indent=2)

    def load_experiment(self, exp_id: str) -> Optional[ExperimentRun]:
        """
        Load experiment by ID.

        Args:
            exp_id: Experiment ID

        Returns:
            ExperimentRun if found, None otherwise
        """
        exp_path = self._get_experiment_path(exp_id)
        if not exp_path.exists():
            return None

        with open(exp_path, 'r') as f:
            data = json.load(f)

        return ExperimentRun.from_dict(data)

    def update_experiment(
        self,
        experiment: ExperimentRun,
        status: Optional[str] = None,
        results_summary: Optional[Dict] = None
    ):
        """
        Update experiment status and results.

        Args:
            experiment: ExperimentRun to update
            status: New status (if changing)
            results_summary: Results summary to add/update
        """
        if status:
            experiment.status = status
            if status == "completed":
                experiment.completed_at = datetime.utcnow().isoformat()

        if results_summary:
            experiment.results_summary.update(results_summary)

        # Save updated experiment
        self._save_experiment(experiment)

        # Update index
        for exp in self.index["experiments"]:
            if exp["id"] == experiment.id:
                exp["status"] = experiment.status
                if experiment.completed_at:
                    exp["completed_at"] = experiment.completed_at
                break

        self._save_index()

    def store_result(
        self,
        exp_id: str,
        result_data: Dict,
        result_type: str = "evaluation"
    ):
        """
        Store individual result within an experiment.

        Args:
            exp_id: Experiment ID
            result_data: Result data to store
            result_type: Type of result (evaluation, metric, etc.)
        """
        # Create results subdirectory for this experiment
        results_dir = self.experiments_dir / exp_id / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        # Generate result filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
        result_file = results_dir / f"{result_type}_{timestamp}.json"

        # Save result
        with open(result_file, 'w') as f:
            json.dump({
                "type": result_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": result_data
            }, f, indent=2)

    def get_experiment_results(self, exp_id: str) -> List[Dict]:
        """
        Get all results for an experiment.

        Args:
            exp_id: Experiment ID

        Returns:
            List of result dictionaries
        """
        results_dir = self.experiments_dir / exp_id / "results"
        if not results_dir.exists():
            return []

        results = []
        for result_file in sorted(results_dir.glob("*.json")):
            with open(result_file, 'r') as f:
                results.append(json.load(f))

        return results

    def list_experiments(
        self,
        status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        List experiments with optional filtering.

        Args:
            status: Filter by status
            limit: Maximum number of experiments to return

        Returns:
            List of experiment metadata dictionaries
        """
        experiments = self.index["experiments"]

        if status:
            experiments = [e for e in experiments if e["status"] == status]

        # Sort by started_at (most recent first)
        experiments = sorted(
            experiments,
            key=lambda x: x["started_at"],
            reverse=True
        )

        if limit:
            experiments = experiments[:limit]

        return experiments

    def get_latest_experiment(self, status: Optional[str] = None) -> Optional[ExperimentRun]:
        """
        Get the most recent experiment.

        Args:
            status: Filter by status

        Returns:
            Latest ExperimentRun or None
        """
        experiments = self.list_experiments(status=status, limit=1)
        if not experiments:
            return None

        return self.load_experiment(experiments[0]["id"])

    def export_experiment(self, exp_id: str, output_path: str):
        """
        Export experiment data to a single file.

        Args:
            exp_id: Experiment ID
            output_path: Output file path
        """
        experiment = self.load_experiment(exp_id)
        if not experiment:
            raise ValueError(f"Experiment not found: {exp_id}")

        results = self.get_experiment_results(exp_id)

        export_data = {
            "experiment": experiment.to_dict(),
            "results": results,
            "exported_at": datetime.utcnow().isoformat()
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
