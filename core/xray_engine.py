"""
Motor d'Anàlisi d'Exposició de Cartera (Portfolio X-Ray).
Analitza la distribució geogràfica (països/regions), sectorial (indústries)
i el solapament de les principals accions individuals (Top Holdings Overlap).
"""

from typing import Dict, List, Tuple, Any
import yfinance as yf
from core.portfolio import Portfolio


# Base de dades preconfigurada de composició dels ETFs més populars
# Garanteix velocitat màxima i independència de formats de l'API pública de Yahoo
CURATED_ETF_EXPOSURE = {
    # MSCI WORLD / ALL-WORLD
    "IWDA.AS": {
        "name": "iShares Core MSCI World (Acc)",
        "countries": {"Estats Units": 70.5, "Japó": 5.4, "Regne Unit": 3.7, "França": 3.0, "Canadà": 3.0, "Suïssa": 2.5, "Alemanya": 2.2, "Altres": 9.7},
        "sectors": {"Tecnologia": 25.5, "Serveis Financers": 15.2, "Salut": 12.1, "Consum Cíclic": 10.4, "Indústria": 10.2, "Serveis de Comunicació": 8.1, "Consum Defensiu": 6.3, "Energia": 4.1, "Materials": 3.6, "Altres": 4.5},
        "top_holdings": {"Microsoft Corp": 4.6, "Apple Inc": 4.2, "NVIDIA Corp": 4.1, "Amazon.com Inc": 2.6, "Meta Platforms": 1.7, "Alphabet Inc (A)": 1.4, "Alphabet Inc (C)": 1.3, "Broadcom Inc": 1.2, "Eli Lilly & Co": 1.0, "Berkshire Hathaway": 1.0}
    },
    "VWCE.DE": {
        "name": "Vanguard FTSE All-World (Acc)",
        "countries": {"Estats Units": 62.8, "Japó": 5.8, "Regne Unit": 3.6, "Xina": 2.9, "França": 2.6, "Índia": 2.5, "Canadà": 2.5, "Taiwan": 2.2, "Suïssa": 2.1, "Alemanya": 1.9, "Altres": 11.1},
        "sectors": {"Tecnologia": 24.2, "Serveis Financers": 15.6, "Consum Cíclic": 11.2, "Indústria": 11.0, "Salut": 10.8, "Serveis de Comunicació": 7.8, "Consum Defensiu": 6.2, "Energia": 4.5, "Materials": 4.2, "Altres": 4.5},
        "top_holdings": {"Microsoft Corp": 4.1, "Apple Inc": 3.8, "NVIDIA Corp": 3.6, "Amazon.com Inc": 2.3, "Meta Platforms": 1.5, "Alphabet Inc (A)": 1.3, "Alphabet Inc (C)": 1.1, "TSMC": 1.0, "Broadcom Inc": 0.9, "Eli Lilly & Co": 0.9}
    },
    "URTH": {
        "name": "iShares MSCI World ETF",
        "countries": {"Estats Units": 71.0, "Japó": 5.3, "Regne Unit": 3.7, "Canadà": 3.1, "França": 2.9, "Suïssa": 2.4, "Alemanya": 2.1, "Altres": 9.5},
        "sectors": {"Tecnologia": 25.8, "Serveis Financers": 15.1, "Salut": 12.0, "Consum Cíclic": 10.3, "Indústria": 10.1, "Serveis de Comunicació": 8.2, "Consum Defensiu": 6.2, "Energia": 4.1, "Materials": 3.7, "Altres": 4.5},
        "top_holdings": {"Microsoft Corp": 4.7, "Apple Inc": 4.3, "NVIDIA Corp": 4.1, "Amazon.com Inc": 2.6, "Meta Platforms": 1.7, "Alphabet Inc (A)": 1.4, "Alphabet Inc (C)": 1.3, "Broadcom Inc": 1.2, "Eli Lilly & Co": 1.0, "Berkshire Hathaway": 1.0}
    },

    # S&P 500
    "CSPX.AS": {
        "name": "iShares Core S&P 500 (Acc)",
        "countries": {"Estats Units": 99.0, "Altres": 1.0},
        "sectors": {"Tecnologia": 31.8, "Serveis Financers": 13.2, "Salut": 11.5, "Consum Cíclic": 10.1, "Serveis de Comunicació": 9.2, "Indústria": 8.3, "Consum Defensiu": 5.9, "Energia": 3.7, "Materials": 2.3, "Altres": 4.0},
        "top_holdings": {"Microsoft Corp": 6.9, "Apple Inc": 6.5, "NVIDIA Corp": 6.1, "Amazon.com Inc": 3.8, "Meta Platforms": 2.5, "Alphabet Inc (A)": 2.1, "Alphabet Inc (C)": 1.8, "Berkshire Hathaway": 1.7, "Broadcom Inc": 1.6, "Eli Lilly & Co": 1.5}
    },
    "VUAA.L": {
        "name": "Vanguard S&P 500 (Acc)",
        "countries": {"Estats Units": 99.0, "Altres": 1.0},
        "sectors": {"Tecnologia": 31.8, "Serveis Financers": 13.2, "Salut": 11.5, "Consum Cíclic": 10.1, "Serveis de Comunicació": 9.2, "Indústria": 8.3, "Consum Defensiu": 5.9, "Energia": 3.7, "Materials": 2.3, "Altres": 4.0},
        "top_holdings": {"Microsoft Corp": 6.9, "Apple Inc": 6.5, "NVIDIA Corp": 6.1, "Amazon.com Inc": 3.8, "Meta Platforms": 2.5, "Alphabet Inc (A)": 2.1, "Alphabet Inc (C)": 1.8, "Berkshire Hathaway": 1.7, "Broadcom Inc": 1.6, "Eli Lilly & Co": 1.5}
    },
    "SPY": {
        "name": "SPDR S&P 500 ETF Trust",
        "countries": {"Estats Units": 99.0, "Altres": 1.0},
        "sectors": {"Tecnologia": 31.8, "Serveis Financers": 13.2, "Salut": 11.5, "Consum Cíclic": 10.1, "Serveis de Comunicació": 9.2, "Indústria": 8.3, "Consum Defensiu": 5.9, "Energia": 3.7, "Materials": 2.3, "Altres": 4.0},
        "top_holdings": {"Microsoft Corp": 6.9, "Apple Inc": 6.5, "NVIDIA Corp": 6.1, "Amazon.com Inc": 3.8, "Meta Platforms": 2.5, "Alphabet Inc (A)": 2.1, "Alphabet Inc (C)": 1.8, "Berkshire Hathaway": 1.7, "Broadcom Inc": 1.6, "Eli Lilly & Co": 1.5}
    },

    # NASDAQ 100
    "QQQ": {
        "name": "Invesco QQQ (Nasdaq 100)",
        "countries": {"Estats Units": 97.2, "Altres": 2.8},
        "sectors": {"Tecnologia": 50.8, "Serveis de Comunicació": 15.4, "Consum Cíclic": 13.2, "Salut": 6.4, "Consum Defensiu": 4.9, "Indústria": 4.8, "Altres": 4.5},
        "top_holdings": {"Apple Inc": 8.9, "Microsoft Corp": 8.2, "NVIDIA Corp": 7.8, "Amazon.com Inc": 5.4, "Broadcom Inc": 4.8, "Meta Platforms": 4.6, "Alphabet Inc (A)": 2.5, "Alphabet Inc (C)": 2.4, "Costco Wholesale": 2.5, "Tesla Inc": 2.4}
    },
    "EQAC.DE": {
        "name": "iShares Nasdaq 100 UCITS",
        "countries": {"Estats Units": 97.2, "Altres": 2.8},
        "sectors": {"Tecnologia": 50.8, "Serveis de Comunicació": 15.4, "Consum Cíclic": 13.2, "Salut": 6.4, "Consum Defensiu": 4.9, "Indústria": 4.8, "Altres": 4.5},
        "top_holdings": {"Apple Inc": 8.9, "Microsoft Corp": 8.2, "NVIDIA Corp": 7.8, "Amazon.com Inc": 5.4, "Broadcom Inc": 4.8, "Meta Platforms": 4.6, "Alphabet Inc (A)": 2.5, "Alphabet Inc (C)": 2.4, "Costco Wholesale": 2.5, "Tesla Inc": 2.4}
    },
    "EXXT.DE": {
        "name": "iShares Nasdaq 100 UCITS (DE)",
        "countries": {"Estats Units": 97.2, "Altres": 2.8},
        "sectors": {"Tecnologia": 50.8, "Serveis de Comunicació": 15.4, "Consum Cíclic": 13.2, "Salut": 6.4, "Consum Defensiu": 4.9, "Indústria": 4.8, "Altres": 4.5},
        "top_holdings": {"Apple Inc": 8.9, "Microsoft Corp": 8.2, "NVIDIA Corp": 7.8, "Amazon.com Inc": 5.4, "Broadcom Inc": 4.8, "Meta Platforms": 4.6, "Alphabet Inc (A)": 2.5, "Alphabet Inc (C)": 2.4, "Costco Wholesale": 2.5, "Tesla Inc": 2.4}
    },

    # EUROPA
    "MEUD.PA": {
        "name": "Amundi STOXX Europe 600",
        "countries": {"Regne Unit": 22.4, "França": 16.8, "Suïssa": 15.1, "Alemanya": 13.2, "Països Baixos": 7.8, "Suècia": 5.3, "Dinamarca": 4.8, "Espanya": 4.2, "Itàlia": 3.9, "Altres": 6.5},
        "sectors": {"Serveis Financers": 18.2, "Salut": 15.8, "Indústria": 15.6, "Consum Cíclic": 10.9, "Consum Defensiu": 9.2, "Tecnologia": 8.1, "Materials": 6.9, "Energia": 5.2, "Altres": 10.1},
        "top_holdings": {"Novo Nordisk": 3.6, "ASML Holding": 3.2, "Nestle SA": 2.8, "SAP SE": 2.4, "AstraZeneca PLC": 2.1, "Novartis AG": 2.0, "Roche Holding": 1.9, "LVMH Moet Hennessy": 1.8, "Shell PLC": 1.7, "TotalEnergies SE": 1.4}
    },
    "EXSA.DE": {
        "name": "iShares STOXX Europe 600 (DE)",
        "countries": {"Regne Unit": 22.4, "França": 16.8, "Suïssa": 15.1, "Alemanya": 13.2, "Països Baixos": 7.8, "Suècia": 5.3, "Dinamarca": 4.8, "Espanya": 4.2, "Itàlia": 3.9, "Altres": 6.5},
        "sectors": {"Serveis Financers": 18.2, "Salut": 15.8, "Indústria": 15.6, "Consum Cíclic": 10.9, "Consum Defensiu": 9.2, "Tecnologia": 8.1, "Materials": 6.9, "Energia": 5.2, "Altres": 10.1},
        "top_holdings": {"Novo Nordisk": 3.6, "ASML Holding": 3.2, "Nestle SA": 2.8, "SAP SE": 2.4, "AstraZeneca PLC": 2.1, "Novartis AG": 2.0, "Roche Holding": 1.9, "LVMH Moet Hennessy": 1.8, "Shell PLC": 1.7, "TotalEnergies SE": 1.4}
    },
    "EUNK.DE": {
        "name": "iShares Core MSCI Europe (DE)",
        "countries": {"Regne Unit": 22.5, "França": 17.5, "Suïssa": 15.0, "Alemanya": 13.5, "Països Baixos": 7.5, "Dinamarca": 5.0, "Suècia": 4.5, "Espanya": 4.2, "Itàlia": 4.0, "Altres": 6.3},
        "sectors": {"Serveis Financers": 18.5, "Salut": 16.2, "Indústria": 15.5, "Consum Cíclic": 10.8, "Consum Defensiu": 9.5, "Tecnologia": 8.0, "Materials": 6.8, "Energia": 5.2, "Altres": 9.5},
        "top_holdings": {"Novo Nordisk": 3.6, "ASML Holding": 3.2, "Nestle SA": 2.8, "SAP SE": 2.4, "AstraZeneca PLC": 2.1, "Novartis AG": 2.0, "Roche Holding": 1.9, "LVMH": 1.8, "Shell PLC": 1.7, "TotalEnergies": 1.4}
    },
    "VGK": {
        "name": "Vanguard FTSE Europe ETF",
        "countries": {"Regne Unit": 23.0, "França": 16.5, "Suïssa": 14.8, "Alemanya": 13.5, "Països Baixos": 7.5, "Suècia": 5.2, "Dinamarca": 4.7, "Espanya": 4.3, "Itàlia": 3.9, "Altres": 6.6},
        "sectors": {"Serveis Financers": 18.5, "Indústria": 16.0, "Salut": 15.5, "Consum Cíclic": 10.5, "Consum Defensiu": 9.0, "Tecnologia": 8.0, "Materials": 7.0, "Energia": 5.3, "Altres": 10.2},
        "top_holdings": {"Novo Nordisk": 3.5, "ASML Holding": 3.1, "Nestle SA": 2.7, "SAP SE": 2.3, "AstraZeneca PLC": 2.1, "Novartis AG": 2.0, "Roche Holding": 1.8, "LVMH": 1.7, "Shell PLC": 1.6, "HSBC Holdings": 1.4}
    },

    # SMALL CAP GLOBAL
    "IUSN.DE": {
        "name": "iShares MSCI World Small Cap (DE)",
        "countries": {"Estats Units": 60.5, "Japó": 11.2, "Regne Unit": 5.2, "Canadà": 4.1, "Austràlia": 3.5, "Alemanya": 2.2, "Suècia": 2.1, "Altres": 11.2},
        "sectors": {"Indústria": 20.5, "Serveis Financers": 14.8, "Tecnologia": 13.2, "Consum Cíclic": 12.4, "Salut": 10.5, "Béns Immobiliaris": 7.8, "Materials": 6.5, "Altres": 14.3},
        "top_holdings": {"MicroStrategy Inc": 0.6, "Pure Storage": 0.4, "Saia Inc": 0.3, "Comfort Systems": 0.3, "Embraer SA": 0.3, "Sprouts Farmers Market": 0.3, "FTAI Aviation": 0.3, "Nutanix Inc": 0.3}
    },

    # EMERGENTS
    "EIMI.AS": {
        "name": "iShares Core MSCI Emerging Markets",
        "countries": {"Xina": 24.5, "Índia": 19.8, "Taiwan": 18.2, "Corea del Sud": 11.4, "Brasil": 4.9, "Aràbia Saudita": 3.8, "Sud-àfrica": 2.9, "Mèxic": 2.4, "Altres": 12.1},
        "sectors": {"Tecnologia": 24.8, "Serveis Financers": 22.1, "Consum Cíclic": 12.8, "Serveis de Comunicació": 8.9, "Materials": 7.1, "Indústria": 6.8, "Energia": 5.2, "Consum Defensiu": 5.1, "Altres": 7.2},
        "top_holdings": {"TSMC": 8.6, "Tencent Holdings": 4.2, "Samsung Electronics": 3.8, "Alibaba Group": 2.4, "Reliance Industries": 1.6, "SK Hynix": 1.3, "PDD Holdings": 1.1, "Meituan": 1.0, "ICICI Bank": 0.9, "Infosys Ltd": 0.9}
    },
    "EMIM.AS": {
        "name": "iShares Core MSCI Emerging Markets",
        "countries": {"Xina": 24.5, "Índia": 19.8, "Taiwan": 18.2, "Corea del Sud": 11.4, "Brasil": 4.9, "Aràbia Saudita": 3.8, "Sud-àfrica": 2.9, "Mèxic": 2.4, "Altres": 12.1},
        "sectors": {"Tecnologia": 24.8, "Serveis Financers": 22.1, "Consum Cíclic": 12.8, "Serveis de Comunicació": 8.9, "Materials": 7.1, "Indústria": 6.8, "Energia": 5.2, "Consum Defensiu": 5.1, "Altres": 7.2},
        "top_holdings": {"TSMC": 8.6, "Tencent Holdings": 4.2, "Samsung Electronics": 3.8, "Alibaba Group": 2.4, "Reliance Industries": 1.6, "SK Hynix": 1.3, "PDD Holdings": 1.1, "Meituan": 1.0, "ICICI Bank": 0.9, "Infosys Ltd": 0.9}
    },
    "IS3N.DE": {
        "name": "iShares Core MSCI EM IMI (DE)",
        "countries": {"Xina": 24.5, "Índia": 19.8, "Taiwan": 18.2, "Corea del Sud": 11.4, "Brasil": 4.9, "Aràbia Saudita": 3.8, "Sud-àfrica": 2.9, "Mèxic": 2.4, "Altres": 12.1},
        "sectors": {"Tecnologia": 24.8, "Serveis Financers": 22.1, "Consum Cíclic": 12.8, "Serveis de Comunicació": 8.9, "Materials": 7.1, "Indústria": 6.8, "Energia": 5.2, "Consum Defensiu": 5.1, "Altres": 7.2},
        "top_holdings": {"TSMC": 8.6, "Tencent Holdings": 4.2, "Samsung Electronics": 3.8, "Alibaba Group": 2.4, "Reliance Industries": 1.6, "SK Hynix": 1.3, "PDD Holdings": 1.1, "Meituan": 1.0, "ICICI Bank": 0.9, "Infosys Ltd": 0.9}
    },
    "VWO": {
        "name": "Vanguard FTSE Emerging Markets",
        "countries": {"Xina": 26.0, "Índia": 21.0, "Taiwan": 19.0, "Brasil": 5.2, "Aràbia Saudita": 4.1, "Sud-àfrica": 3.1, "Mèxic": 2.6, "Altres": 19.0},
        "sectors": {"Tecnologia": 24.5, "Serveis Financers": 22.0, "Consum Cíclic": 13.0, "Serveis de Comunicació": 9.0, "Materials": 7.0, "Indústria": 6.5, "Energia": 5.5, "Altres": 12.5},
        "top_holdings": {"TSMC": 8.9, "Tencent Holdings": 4.3, "Alibaba Group": 2.5, "Reliance Industries": 1.6, "PDD Holdings": 1.2, "Meituan": 1.0, "ICICI Bank": 0.9, "Infosys Ltd": 0.9, "China Construction Bank": 0.8}
    },

    # CRIPTOACTIUS
    "BTC-EUR": {
        "name": "Bitcoin (EUR)",
        "countries": {"Criptoactius / Global": 100.0},
        "sectors": {"Criptoactius / Actius Digitals": 100.0},
        "top_holdings": {"Bitcoin (BTC)": 100.0}
    },
    "BTC-USD": {
        "name": "Bitcoin (USD)",
        "countries": {"Criptoactius / Global": 100.0},
        "sectors": {"Criptoactius / Actius Digitals": 100.0},
        "top_holdings": {"Bitcoin (BTC)": 100.0}
    },

    # RENDA FIXA
    "AGGH.AS": {
        "name": "iShares Global Aggregate Bond EUR Hedged",
        "countries": {"Estats Units": 38.5, "Japó": 12.2, "França": 8.1, "Alemanya": 7.2, "Regne Unit": 6.4, "Itàlia": 5.2, "Canadà": 3.9, "Altres": 18.5},
        "sectors": {"Deute Sobirà Governamental": 62.0, "Deute Corporatiu": 24.5, "Titulitzacions i Agències": 13.5},
        "top_holdings": {"Bo Tresor EUA 10A": 3.2, "Bo Federal Alemany (Bund)": 2.5, "Bo Govern Japonès": 2.1, "Bo Tresor Francès (OAT)": 1.8, "Gilt Regne Unit": 1.5}
    },
    "VAGF.DE": {
        "name": "Vanguard Global Aggregate Bond EUR Hedged",
        "countries": {"Estats Units": 38.0, "Japó": 12.0, "França": 8.0, "Alemanya": 7.0, "Regne Unit": 6.5, "Itàlia": 5.0, "Canadà": 4.0, "Altres": 19.5},
        "sectors": {"Deute Sobirà Governamental": 61.5, "Deute Corporatiu": 25.0, "Titulitzacions i Agències": 13.5},
        "top_holdings": {"Bo Tresor EUA 10A": 3.1, "Bo Federal Alemany": 2.4, "Bo Govern Japó": 2.0, "Bo Tresor França": 1.7, "Gilt Regne Unit": 1.5}
    },
    "BND": {
        "name": "Vanguard Total Bond Market ETF",
        "countries": {"Estats Units": 99.0, "Altres": 1.0},
        "sectors": {"Deute Sobirà Governamental": 68.0, "Deute Corporatiu": 26.0, "Titulitzacions": 6.0},
        "top_holdings": {"Bo Tresor EUA 2Y": 3.8, "Bo Tresor EUA 5Y": 3.5, "Bo Tresor EUA 10Y": 3.2, "Bo Tresor EUA 30Y": 2.6}
    },
    "EUNH.DE": {
        "name": "iShares Euro Aggregate Bond",
        "countries": {"França": 22.5, "Alemanya": 19.8, "Itàlia": 14.2, "Espanya": 12.1, "Països Baixos": 5.4, "Bèlgica": 5.1, "Altres": 20.9},
        "sectors": {"Deute Sobirà Governamental": 74.0, "Deute Corporatiu": 18.0, "Agències": 8.0},
        "top_holdings": {"Bo Tresor Francès OAT": 4.2, "Bo Federal Alemany": 3.8, "BTP Itàlia": 3.2, "Bonos de l'Estat Espanyol": 2.9}
    },

    # OR I MATÈRIES PRIMERES
    "GLD": {
        "name": "SPDR Gold Shares",
        "countries": {"Or Físic / Custòdia Global": 100.0},
        "sectors": {"Matèries Primeres / Or": 100.0},
        "top_holdings": {"Or Físic": 100.0}
    },
    "SGLD.L": {
        "name": "Invesco Physical Gold",
        "countries": {"Or Físic / Custòdia Global": 100.0},
        "sectors": {"Matèries Primeres / Or": 100.0},
        "top_holdings": {"Or Físic": 100.0}
    }
}


# Mapeig de traducció de noms de sectors en català
SECTOR_TRANSLATIONS = {
    "technology": "Tecnologia",
    "information technology": "Tecnologia",
    "financial services": "Serveis Financers",
    "financials": "Serveis Financers",
    "healthcare": "Salut",
    "health care": "Salut",
    "consumer cyclical": "Consum Cíclic",
    "consumer discretionary": "Consum Cíclic",
    "industrials": "Indústria",
    "communication services": "Serveis de Comunicació",
    "communication": "Serveis de Comunicació",
    "consumer defensive": "Consum Defensiu",
    "consumer staples": "Consum Defensiu",
    "energy": "Energia",
    "materials": "Materials",
    "basic materials": "Materials",
    "real estate": "Béns Immobiliaris",
    "utilities": "Serveis Públics (Utilities)",
}


class XRayEngine:
    @staticmethod
    def get_asset_exposure(ticker: str) -> Dict[str, Any]:
        """
        Obté el perfil d'exposició per a un sol actiu (països, sectors, accions principals).
        Combina la base de coneixement precarregada i consultes en viu a yfinance.
        """
        ticker = ticker.strip().upper()

        # 1. Si és un dels nostres ETFs o fons curats, retornem la informació directament
        if ticker in CURATED_ETF_EXPOSURE:
            return CURATED_ETF_EXPOSURE[ticker]

        # 2. Si no, consultem yfinance per veure si és una acció individual o un altre ETF
        try:
            yf_t = yf.Ticker(ticker)
            info = yf_t.info or {}
            quote_type = info.get("quoteType", "").upper()
            short_name = info.get("shortName") or info.get("longName") or ticker

            if quote_type == "EQUITY":
                # És una acció individual (com AAPL, SAN.MC, ITX.MC, etc.)
                raw_sector = info.get("sector", "Altres").lower()
                sector_cat = SECTOR_TRANSLATIONS.get(raw_sector, info.get("sector", "Altres"))
                country = info.get("country", "Desconegut")

                # Normalitzar països freqüents al català
                country_map = {
                    "United States": "Estats Units",
                    "Spain": "Espanya",
                    "Germany": "Alemanya",
                    "France": "França",
                    "United Kingdom": "Regne Unit",
                    "Japan": "Japó",
                    "China": "Xina",
                    "Switzerland": "Suïssa",
                    "Netherlands": "Països Baixos"
                }
                country_cat = country_map.get(country, country)

                return {
                    "name": short_name,
                    "countries": {country_cat: 100.0},
                    "sectors": {sector_cat: 100.0},
                    "top_holdings": {short_name: 100.0}
                }

            # Si és un ETF o fons no catalogat prèviament:
            # Provem d'obtenir dades de fons de yfinance
            sectors = {}
            top_holdings = {}
            countries = {"Global / Sense desglossar": 100.0}

            try:
                funds_data = getattr(yf_t, "funds_data", None)
                if funds_data:
                    # Sectors
                    sec_w = getattr(funds_data, "sector_weightings", {}) or {}
                    for k, v in sec_w.items():
                        cat_name = SECTOR_TRANSLATIONS.get(k.lower(), k.capitalize())
                        sectors[cat_name] = round(float(v) * 100.0, 2)
                    
                    # Top holdings
                    th_df = getattr(funds_data, "top_holdings", None)
                    if th_df is not None and hasattr(th_df, "iterrows"):
                        for _, row in th_df.iterrows():
                            h_name = row.get("Holding Name") or row.get("Symbol") or "Actiu"
                            h_pct = float(row.get("Holding Percent", 0.0)) * 100.0
                            top_holdings[str(h_name)] = round(h_pct, 2)
            except Exception:
                pass

            if not sectors:
                sectors = {"Fons Mixt / Altres": 100.0}
            if not top_holdings:
                top_holdings = {short_name: 100.0}

            return {
                "name": short_name,
                "countries": countries,
                "sectors": sectors,
                "top_holdings": top_holdings
            }

        except Exception:
            # Fallback segur
            return {
                "name": ticker,
                "countries": {"Altres": 100.0},
                "sectors": {"Altres": 100.0},
                "top_holdings": {ticker: 100.0}
            }

    @staticmethod
    def calculate_portfolio_xray(portfolio: Portfolio) -> Dict[str, Any]:
        """
        Calcula l'exposició agregada ponderada de tota la cartera per:
        - Països / Regions
        - Sectors / Indústries
        - Principals accions individuals (solapament entre ETFs)
        """
        norm_weights = portfolio.normalized_weights()
        if not norm_weights:
            return {"countries": {}, "sectors": {}, "top_holdings": {}, "raw_assets": {}}

        agg_countries: Dict[str, float] = {}
        agg_sectors: Dict[str, float] = {}
        agg_holdings: Dict[str, float] = {}
        raw_assets: Dict[str, Any] = {}

        for ticker, weight in norm_weights.items():
            exposure = XRayEngine.get_asset_exposure(ticker)
            raw_assets[ticker] = exposure

            # Països
            for country, c_pct in exposure.get("countries", {}).items():
                effective_weight = weight * c_pct
                agg_countries[country] = agg_countries.get(country, 0.0) + effective_weight

            # Sectors
            for sector, s_pct in exposure.get("sectors", {}).items():
                effective_weight = weight * s_pct
                agg_sectors[sector] = agg_sectors.get(sector, 0.0) + effective_weight

            # Top Holdings
            for holding, h_pct in exposure.get("top_holdings", {}).items():
                effective_weight = weight * h_pct
                agg_holdings[holding] = agg_holdings.get(holding, 0.0) + effective_weight

        # Normalitzar i ordenar de major a menor
        sorted_countries = dict(sorted(agg_countries.items(), key=lambda item: item[1], reverse=True))
        sorted_sectors = dict(sorted(agg_sectors.items(), key=lambda item: item[1], reverse=True))
        sorted_holdings = dict(sorted(agg_holdings.items(), key=lambda item: item[1], reverse=True))

        # Arrodonir percentatges
        sorted_countries = {k: round(v, 2) for k, v in sorted_countries.items() if round(v, 2) > 0.1}
        sorted_sectors = {k: round(v, 2) for k, v in sorted_sectors.items() if round(v, 2) > 0.1}
        sorted_holdings = {k: round(v, 2) for k, v in sorted_holdings.items() if round(v, 2) > 0.1}

        return {
            "portfolio_name": portfolio.name,
            "countries": sorted_countries,
            "sectors": sorted_sectors,
            "top_holdings": sorted_holdings,
            "raw_assets": raw_assets,
        }
