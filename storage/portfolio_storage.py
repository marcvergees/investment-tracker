"""
Gestió de persistència de carteres d'inversió (desar, carregar i suprimir fitxers JSON).
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from config import PORTFOLIOS_DIR
from core.portfolio import Portfolio


def sanitize_filename(name: str) -> str:
    """Neteja un nom perquè sigui vàlid com a nom de fitxer."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    cleaned = cleaned.strip().replace(" ", "_")
    return cleaned or "cartera"


class PortfolioStorage:
    def __init__(self, storage_dir: Path = PORTFOLIOS_DIR):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(exist_ok=True)
        self._ensure_sample_portfolios()

    def _ensure_sample_portfolios(self):
        """Crea o actualitza carteres d'exemple típiques amb tickers d'alta liquiditat i ampli històric."""
        sample_portfolios = [
            Portfolio(
                name="Proposta Banc A (Dinàmic 80/20)",
                allocations={"SPY": 50.0, "QQQ": 20.0, "EMIM.AS": 10.0, "EUNH.DE": 20.0},
                initial_capital=10000.0,
                rebalance_freq="yearly",
                description="Proposta bancària de perfil dinàmic: 50% S&P 500, 20% Nasdaq 100, 10% Mercats Emergents i 20% Renda Fixa Euro."
            ),
            Portfolio(
                name="Proposta Banc B (Moderat 60/40)",
                allocations={"IWDA.AS": 40.0, "EXSA.DE": 20.0, "EUNH.DE": 40.0},
                initial_capital=10000.0,
                rebalance_freq="yearly",
                description="Estratègia moderada equilibrada: 40% MSCI World, 20% STOXX Europe 600 i 40% Renda Fixa Europea."
            ),
            Portfolio(
                name="Cartera Indexada Global 90/10",
                allocations={"IWDA.AS": 80.0, "EMIM.AS": 10.0, "EUNH.DE": 10.0},
                initial_capital=10000.0,
                rebalance_freq="yearly",
                description="Cartera passiva global indexada a l'economia mundial: 80% països desenvolupats, 10% emergents i 10% bons."
            ),
            Portfolio(
                name="Cartera Tecnològica i Mega-Caps",
                allocations={"QQQ": 50.0, "AAPL": 15.0, "MSFT": 15.0, "NVDA": 10.0, "GOOGL": 10.0},
                initial_capital=10000.0,
                rebalance_freq="yearly",
                description="Cartera de creixement agressiu concentrada en gegants tecnològics mundials."
            )
        ]

        # Desar si no existeixen
        for p in sample_portfolios:
            f_path = self.storage_dir / f"{sanitize_filename(p.name)}.json"
            if not f_path.exists():
                self.save_portfolio(p)
            else:
                # Comprovar si tenia tickers antics com EIMI.AS o MEUD.PA i actualitzar-los
                try:
                    with open(f_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    allocs = data.get("allocations", {})
                    if "EIMI.AS" in allocs or "MEUD.PA" in allocs or "AGGH.AS" in allocs:
                        self.save_portfolio(p)
                except Exception:
                    self.save_portfolio(p)

    def save_portfolio(self, portfolio: Portfolio) -> Path:
        """Guarda la cartera en format JSON."""
        filename = f"{sanitize_filename(portfolio.name)}.json"
        target_path = self.storage_dir / filename
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(portfolio.to_dict(), f, ensure_ascii=False, indent=2)
        return target_path

    def load_portfolio(self, name_or_path: str) -> Optional[Portfolio]:
        """Carrega una cartera pel seu nom o camí de fitxer."""
        p = Path(name_or_path)
        if not p.exists():
            p = self.storage_dir / f"{sanitize_filename(name_or_path)}.json"
        if not p.exists():
            return None

        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Portfolio.from_dict(data)

    def list_portfolios(self) -> List[Portfolio]:
        """Llista totes les carteres desades."""
        portfolios = []
        for file in sorted(self.storage_dir.glob("*.json")):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                portfolios.append(Portfolio.from_dict(data))
            except Exception:
                continue
        return portfolios

    def delete_portfolio(self, name: str) -> bool:
        """Elimina una cartera desada."""
        filename = f"{sanitize_filename(name)}.json"
        target_path = self.storage_dir / filename
        if target_path.exists():
            target_path.unlink()
            return True
        return False

    def rename_portfolio(self, old_name: str, new_name: str) -> bool:
        """Canvia el nom d'una cartera desada."""
        portfolio = self.load_portfolio(old_name)
        if portfolio is None:
            return False
        # Eliminar l'arxiu antic
        self.delete_portfolio(old_name)
        # Desar amb el nom nou
        portfolio.name = new_name
        self.save_portfolio(portfolio)
        return True
