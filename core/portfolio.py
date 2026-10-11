"""
Model de dades de Cartera d'Inversió.
"""

from typing import Dict, Any, Optional
import math


class Portfolio:
    def __init__(
        self,
        name: str,
        allocations: Dict[str, float],
        initial_capital: float = 10000.0,
        rebalance_freq: str = "yearly",
        description: str = ""
    ):
        self.name = name.strip()
        self.description = description.strip()
        # Normalitzar claus de tickers a majúscules
        self.allocations = {t.strip().upper(): float(w) for t, w in allocations.items() if float(w) > 0}
        self.initial_capital = float(initial_capital)
        self.rebalance_freq = rebalance_freq.lower()

    @property
    def total_weight(self) -> float:
        """Retorna la suma total dels percentatges (hauria de ser 100.0)."""
        return sum(self.allocations.values())

    @property
    def is_valid(self) -> bool:
        """Comprova si la cartera té actius i la suma és aproximadament 100%."""
        if not self.allocations:
            return False
        return math.isclose(self.total_weight, 100.0, abs_tol=0.5)

    def normalized_weights(self) -> Dict[str, float]:
        """
        Retorna els pesos normalitzats sumant exactament 1.0 (decimals).
        Si la suma no és 100, redistribueix proporcionalment.
        """
        tot = self.total_weight
        if tot <= 0:
            return {}
        return {ticker: weight / tot for ticker, weight in self.allocations.items()}

    def to_dict(self) -> Dict[str, Any]:
        """Converteix la cartera a diccionari per desar com a JSON."""
        return {
            "name": self.name,
            "description": self.description,
            "allocations": self.allocations,
            "initial_capital": self.initial_capital,
            "rebalance_freq": self.rebalance_freq,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Portfolio":
        """Reconstrueix una instància de Portfolio a partir d'un diccionari."""
        return cls(
            name=data.get("name", "Cartera Sense Nom"),
            allocations=data.get("allocations", {}),
            initial_capital=float(data.get("initial_capital", 10000.0)),
            rebalance_freq=data.get("rebalance_freq", "yearly"),
            description=data.get("description", ""),
        )

    def __repr__(self) -> str:
        return f"<Portfolio '{self.name}' ({len(self.allocations)} actius, {self.initial_capital:,.2f} €)>"
