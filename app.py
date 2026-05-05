"""
 MACRO DASHBOARD — ESCUELA AUSTRIACA DE ECONOMÍA 
 Ciclo Económico, Liquidez & Asset Allocation 
 Datos en vivo vía FRED API + fuentes complementarias 

Instrucciones:
  1. Obtén una API key gratuita en https://fred.stlouisfed.org/docs/api/api_key.html
  2. Configúrala en el sidebar o como variable de entorno FRED_API_KEY
  3. Ejecuta: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import json
import os
from functools import lru_cache
import time

# CONFIGURACIÓN DE PÁGINA

st.set_page_config(
    page_title="Macro Dashboard · Escuela Austriaca",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# THEME & CSS

st.markdown("""
<style>
    /* Dark theme overrides */
    .stApp { background-color: #0a0f1a; }
    
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem;
    }
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header .subtitle {
        font-size: 0.75rem;
        color: #64748b;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .main-header .update-time {
        font-size: 0.75rem;
        color: #475569;
        font-family: monospace;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(15,23,42,0.7);
        border: 1px solid rgba(100,116,139,0.2);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        position: relative;
        overflow: hidden;
        height: 100%;
    }
    .metric-card .bar {
        position: absolute; top: 0; left: 0;
        width: 4px; height: 100%;
        border-radius: 12px 0 0 12px;
    }
    .metric-card .label {
        font-size: 0.68rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-family: monospace;
    }
    .metric-card .value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 2px 0;
    }
    .metric-card .detail {
        font-size: 0.7rem;
        color: #64748b;
    }
    .metric-card .trend-up { color: #22c55e; }
    .metric-card .trend-down { color: #ef4444; }
    .metric-card .trend-flat { color: #f59e0b; }
    
    /* Regime badge */
    .regime-badge {
        background: linear-gradient(135deg, rgba(239,68,68,0.12), rgba(245,158,11,0.12));
        border: 1px solid rgba(239,68,68,0.25);
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1.5rem;
    }
    .regime-badge .tag {
        font-size: 0.7rem;
        font-weight: 600;
        color: #fbbf24;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-family: monospace;
    }
    .regime-badge .regime-name {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0.3rem 0;
    }
    .regime-badge .regime-desc {
        font-size: 0.82rem;
        color: #cbd5e1;
        line-height: 1.6;
    }
    
    /* Section titles */
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #e2e8f0;
        margin: 1.5rem 0 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(100,116,139,0.2);
    }
    
    /* Allocation bar */
    .alloc-item {
        background: rgba(15,23,42,0.6);
        border: 1px solid rgba(100,116,139,0.2);
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.5rem;
    }
    .alloc-item .name {
        font-weight: 600;
        color: #f1f5f9;
        font-size: 0.9rem;
    }
    .alloc-item .pct {
        font-weight: 700;
        font-family: monospace;
        font-size: 0.9rem;
    }
    .alloc-item .reason {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.2rem;
    }
    
    /* Analysis box */
    .analysis-box {
        background: rgba(15,23,42,0.6);
        border: 1px solid rgba(100,116,139,0.2);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-top: 1rem;
        font-size: 0.85rem;
        color: #cbd5e1;
        line-height: 1.7;
    }
    .analysis-box h4 {
        color: #e2e8f0;
        margin: 0 0 0.5rem;
        font-size: 0.9rem;
    }
    
    /* Risk cards */
    .risk-card {
        border-radius: 10px;
        padding: 1rem 1.2rem;
    }
    .risk-bear {
        background: rgba(239,68,68,0.08);
        border: 1px solid rgba(239,68,68,0.2);
    }
    .risk-bull {
        background: rgba(34,197,94,0.08);
        border: 1px solid rgba(34,197,94,0.2);
    }
    
    /* Phase card */
    .phase-card {
        background: rgba(15,23,42,0.6);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        position: relative;
        overflow: hidden;
    }
    
    /* Disclaimer */
    .disclaimer {
        text-align: center;
        padding: 1rem;
        margin-top: 2rem;
        background: rgba(100,116,139,0.06);
        border-radius: 10px;
        font-size: 0.7rem;
        color: #475569;
        font-family: monospace;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(15,23,42,0.6);
        border-radius: 8px;
        color: #94a3b8;
        padding: 8px 16px;
        font-size: 0.8rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(100,116,139,0.2) !important;
        color: #f1f5f9 !important;
    }
</style>
""", unsafe_allow_html=True)

# DATA FETCHING — FRED API

REMOVED_FRED_SERIES = {
    "GOLDAMGBD228NLBM",
}

class FREDClient:
    """Cliente ligero para la API de FRED (Federal Reserve Economic Data)."""
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_series(self, series_id: str, start_date: str = None, limit: int = 60) -> pd.DataFrame:
        """Obtiene datos de una serie FRED."""
        if series_id in REMOVED_FRED_SERIES:
            return pd.DataFrame()

        if not start_date:
            start_date = (datetime.now() - timedelta(days=365 * 3)).strftime("%Y-%m-%d")
        
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start_date,
            "sort_order": "desc",
            "limit": limit,
        }
        try:
            resp = requests.get(f"{self.BASE_URL}/series/observations", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json().get("observations", [])
            df = pd.DataFrame(data)
            if not df.empty:
                df["date"] = pd.to_datetime(df["date"])
                df["value"] = pd.to_numeric(df["value"], errors="coerce")
                df = df.dropna(subset=["value"])
                df = df.sort_values("date")
            return df
        except Exception as e:
            st.warning(f"⚠️ Error obteniendo {series_id}: {e}")
            return pd.DataFrame()
    
    def get_latest(self, series_id: str) -> float | None:
        """Obtiene el último valor de una serie."""
        df = self.get_series(series_id, limit=5)
        if not df.empty:
            return df["value"].iloc[-1]
        return None

# SERIES FRED — Mapeo de indicadores

FRED_SERIES = {
    # Tipos de interés
    "fed_funds": "EFFR",              # Effective Federal Funds Rate
    "yield_10y": "DGS10",             # 10-Year Treasury
    "yield_2y": "DGS2",               # 2-Year Treasury
    "yield_3m": "DGS3MO",             # 3-Month Treasury
    "yield_30y": "DGS30",             # 30-Year Treasury
    "yield_5y": "DGS5",               # 5-Year Treasury
    "yield_1y": "DGS1",               # 1-Year Treasury
    "spread_10y2y": "T10Y2Y",         # 10Y-2Y Spread
    "spread_10y3m": "T10Y3M",         # 10Y-3M Spread
    
    # Masa monetaria
    "m2": "M2SL",                     # M2 Money Stock
    "m1": "M1SL",                     # M1 Money Stock
    "monetary_base": "BOGMBASE",      # Monetary Base
    "m2_velocity": "M2V",             # Velocity of M2
    
    # Inflación
    "cpi": "CPIAUCSL",                # CPI All Urban
    "core_cpi": "CPILFESL",           # Core CPI
    "pce": "PCEPI",                   # PCE Price Index
    "core_pce": "PCEPILFE",           # Core PCE
    "breakeven_5y": "T5YIE",          # 5Y Breakeven Inflation
    "breakeven_10y": "T10YIE",        # 10Y Breakeven Inflation
    
    # Empleo
    "unemployment": "UNRATE",          # Unemployment Rate
    "nfp": "PAYEMS",                  # Total Nonfarm Payrolls
    "participation": "CIVPART",        # Labor Force Participation
    "initial_claims": "ICSA",          # Initial Jobless Claims
    "jolts": "JTSJOL",               # Job Openings
    
    # Actividad
    "ism_mfg": "MANEMP",             # Manufacturing Employment (proxy)
    "industrial_prod": "INDPRO",       # Industrial Production
    "retail_sales": "RSAFS",           # Retail Sales
    "housing_starts": "HOUST",         # Housing Starts
    "lei": "USSLIND",                 # Leading Economic Index
    
    # Mercados financieros
    "sp500": "SP500",                 # S&P 500
    "vix": "VIXCLS",                  # VIX
    "dxy": "DTWEXBGS",               # Trade Weighted Dollar Index
    "baa_spread": "BAA10Y",           # Baa Corp Bond Spread over 10Y
    "ted_spread": "TEDRATE",          # TED Spread
    
    # Balance Fed
    "fed_assets": "WALCL",            # Fed Total Assets
    "fed_treasuries": "TREAST",       # Fed Treasury Holdings
    
    # Commodities (proxies disponibles en FRED)
    "oil_wti": "DCOILWTICO",         # WTI Crude Oil
    "gold": "GOLDAMGBD228NLBM",       # Gold London Fix (removido en FRED, se usa fallback si falla)
    
    # Crédito
    "consumer_credit": "TOTALSL",     # Total Consumer Credit
    "bank_lending": "TOTLL",          # Bank Lending
}
# DATOS FALLBACK (cuando no hay API key)

FALLBACK_DATA = {
    "fed_funds": 3.625,
    "yield_10y": 4.43,
    "yield_2y": 3.91,
    "yield_3m": 3.65,
    "yield_5y": 4.15,
    "yield_1y": 3.78,
    "yield_30y": 4.98,
    "spread_10y2y": 0.55,
    "m2_latest": 22686.0,
    "m2_yoy": 4.6,
    "cpi_yoy": 3.3,
    "core_cpi_yoy": 2.6,
    "unemployment": 4.3,
    "participation": 61.9,
    "sp500": 7124,
    "vix": 18.55,
    "dxy": 98.73,
    "oil_wti": 107.14,
    "gold": 4554,
    "ism_pmi": 52.7,
    "ism_prices": 78.3,
    "ism_new_orders": 53.5,
    "nfp_change": 178,
    "breakeven_5y": 2.85,
    "breakeven_10y": 2.62,
    "baa_spread": 2.10,
    "fed_assets": 7200,
}

# Historical data for charts when API unavailable
FALLBACK_HISTORY = {
    "m2_yoy": [
        {"date": "2025-04", "yoy": 3.8}, {"date": "2025-07", "yoy": 3.5},
        {"date": "2025-10", "yoy": 4.0}, {"date": "2025-12", "yoy": 4.3},
        {"date": "2026-01", "yoy": 4.3}, {"date": "2026-02", "yoy": 4.9},
        {"date": "2026-03", "yoy": 4.6},
    ],
    "cpi_yoy": [
        {"date": "2025-06", "yoy": 2.0}, {"date": "2025-08", "yoy": 2.1},
        {"date": "2025-09", "yoy": 2.1}, {"date": "2025-10", "yoy": 2.0},
        {"date": "2025-11", "yoy": 2.2}, {"date": "2025-12", "yoy": 2.3},
        {"date": "2026-01", "yoy": 2.4}, {"date": "2026-02", "yoy": 2.4},
        {"date": "2026-03", "yoy": 3.3},
    ],
    "core_cpi_yoy": [
        {"date": "2025-06", "yoy": 2.2}, {"date": "2025-08", "yoy": 2.3},
        {"date": "2025-09", "yoy": 2.3}, {"date": "2025-10", "yoy": 2.3},
        {"date": "2025-11", "yoy": 2.4}, {"date": "2025-12", "yoy": 2.4},
        {"date": "2026-01", "yoy": 2.5}, {"date": "2026-02", "yoy": 2.5},
        {"date": "2026-03", "yoy": 2.6},
    ],
    "ism": [
        {"date": "2025-07", "value": 46.5, "prices": 52.0, "orders": 44.8},
        {"date": "2025-08", "value": 46.2, "prices": 53.5, "orders": 44.2},
        {"date": "2025-09", "value": 46.8, "prices": 54.0, "orders": 45.2},
        {"date": "2025-10", "value": 46.8, "prices": 54.0, "orders": 45.2},
        {"date": "2025-11", "value": 47.2, "prices": 55.5, "orders": 46.0},
        {"date": "2025-12", "value": 47.9, "prices": 58.5, "orders": 47.4},
        {"date": "2026-01", "value": 52.6, "prices": 59.0, "orders": 57.1},
        {"date": "2026-02", "value": 52.4, "prices": 70.5, "orders": 55.8},
        {"date": "2026-03", "value": 52.7, "prices": 78.3, "orders": 53.5},
    ],
    "yield_curve": [
        {"maturity": "1M", "yield": 3.62, "months": 1/12},
        {"maturity": "3M", "yield": 3.65, "months": 0.25},
        {"maturity": "6M", "yield": 3.70, "months": 0.5},
        {"maturity": "1Y", "yield": 3.78, "months": 1},
        {"maturity": "2Y", "yield": 3.91, "months": 2},
        {"maturity": "5Y", "yield": 4.15, "months": 5},
        {"maturity": "7Y", "yield": 4.28, "months": 7},
        {"maturity": "10Y", "yield": 4.43, "months": 10},
        {"maturity": "20Y", "yield": 4.72, "months": 20},
        {"maturity": "30Y", "yield": 4.98, "months": 30},
    ],
}

# DATA MANAGER — Orquesta la obtención de datos

class MacroDataManager:
    def __init__(self, fred_client: FREDClient | None = None):
        self.fred = fred_client
        self.data = {}
        self.history = {}
        self.last_update = None
    
    def fetch_all(self):
        """Obtiene todos los datos, usando FRED si disponible, fallback si no."""
        if self.fred:
            self._fetch_from_fred()
        else:
            self._use_fallback()
        self.last_update = datetime.now()
        self._compute_derived()
    
    def _fetch_from_fred(self):
        """Obtiene datos en vivo de FRED."""
        with st.spinner("📡 Obteniendo datos de FRED..."):
            # Latest values
            for key, series_id in FRED_SERIES.items():
                val = self.fred.get_latest(series_id)
                if val is not None:
                    self.data[key] = val
            
            # Historical series for charts
            series_to_fetch = {
                "m2": "M2SL",
                "cpi_index": "CPIAUCSL",
                "core_cpi_index": "CPILFESL",
                "sp500_hist": "SP500",
                "vix_hist": "VIXCLS",
                "spread_hist": "T10Y2Y",
                "oil_hist": "DCOILWTICO",
                "gold_hist": "GOLDAMGBD228NLBM",
                "unemployment_hist": "UNRATE",
                "fed_assets_hist": "WALCL",
                "breakeven_5y_hist": "T5YIE",
                "yield_10y_hist": "DGS10",
                "yield_2y_hist": "DGS2",
                "m2v_hist": "M2V",
                "industrial_hist": "INDPRO",
            }
            for key, series_id in series_to_fetch.items():
                if series_id in REMOVED_FRED_SERIES:
                    continue
                df = self.fred.get_series(series_id, limit=120)
                if not df.empty:
                    self.history[key] = df
            
            # Compute YoY for CPI from index
            if "cpi_index" in self.history and len(self.history["cpi_index"]) > 12:
                df = self.history["cpi_index"].copy()
                df["yoy"] = df["value"].pct_change(12) * 100
                self.history["cpi_yoy"] = df.dropna(subset=["yoy"])
                if not df["yoy"].dropna().empty:
                    self.data["cpi_yoy"] = df["yoy"].dropna().iloc[-1]
            
            if "core_cpi_index" in self.history and len(self.history["core_cpi_index"]) > 12:
                df = self.history["core_cpi_index"].copy()
                df["yoy"] = df["value"].pct_change(12) * 100
                self.history["core_cpi_yoy"] = df.dropna(subset=["yoy"])
                if not df["yoy"].dropna().empty:
                    self.data["core_cpi_yoy"] = df["yoy"].dropna().iloc[-1]
            
            # M2 YoY
            if "m2" in self.history and len(self.history["m2"]) > 12:
                df = self.history["m2"].copy()
                df["yoy"] = df["value"].pct_change(12) * 100
                self.history["m2_yoy"] = df.dropna(subset=["yoy"])
                if not df["yoy"].dropna().empty:
                    self.data["m2_yoy"] = df["yoy"].dropna().iloc[-1]
                    self.data["m2_latest"] = df["value"].iloc[-1]
        
        # Fill gaps with fallback
        for key, val in FALLBACK_DATA.items():
            if key not in self.data:
                self.data[key] = val
    
    def _use_fallback(self):
        """Usa datos estáticos como fallback."""
        self.data = FALLBACK_DATA.copy()
        # Convert fallback history to DataFrames
        for key, records in FALLBACK_HISTORY.items():
            self.history[key] = pd.DataFrame(records)
    
    def _compute_derived(self):
        """Calcula métricas derivadas para el análisis austriaco."""
        d = self.data
        
        # ─── Austrian Cycle Scores ───
        # 1. Expansión crediticia (0-100)
        m2_growth = d.get("m2_yoy", 4.6)
        fed_rate = d.get("fed_funds", 3.625)
        credit_score = min(100, max(0, 
            (m2_growth / 6) * 40 +  # M2 growth component
            ((5 - fed_rate) / 5) * 20 +  # Rate component (lower = more expansive)
            30  # Base for active QE ($40B/mo Treasuries)
        ))
        
        # 2. Malinversión (0-100)
        cape = d.get("cape", 38.93) if "cape" in d else 38.93
        malinv_score = min(100, max(0,
            (cape / 50) * 60 +  # Valuation stretch
            (d.get("vix", 18.55) / 40) * 20 +  # Complacency
            15  # Base for AI capex bubble
        ))
        
        # 3. Inflación de precios (0-100)
        cpi = d.get("cpi_yoy", 3.3)
        ism_prices = d.get("ism_prices", 78.3)
        inflation_score = min(100, max(0,
            (cpi / 4) * 35 +  # CPI component
            (ism_prices / 85) * 40 +  # ISM Prices component
            15  # Energy shock base
        ))
        
        # 4. Corrección / Bust (0-100)
        unemp = d.get("unemployment", 4.3)
        spread = d.get("spread_10y2y", 0.55)
        bust_score = min(100, max(0,
            (unemp / 8) * 30 +  # Unemployment
            max(0, (1 - spread) * 30) +  # Yield curve flatness
            10  # Base for employment contraction signals
        ))
        
        self.data["cycle_scores"] = {
            "Expansión Crediticia": round(credit_score),
            "Malinversión": round(malinv_score),
            "Inflación de Precios": round(inflation_score),
            "Corrección / Bust": round(bust_score),
        }
        
        # ─── Regime determination ───
        if inflation_score > 70 and bust_score > 50:
            self.data["regime"] = "Estanflación"
            self.data["regime_color"] = "#ef4444"
        elif inflation_score > 70 and credit_score > 60:
            self.data["regime"] = "Estanflación Incipiente + Shock de Oferta"
            self.data["regime_color"] = "#f59e0b"
        elif credit_score > 70 and inflation_score < 40:
            self.data["regime"] = "Expansión Artificial (Boom)"
            self.data["regime_color"] = "#22c55e"
        elif bust_score > 70:
            self.data["regime"] = "Contracción / Recesión"
            self.data["regime_color"] = "#8b5cf6"
        else:
            self.data["regime"] = "Transición / Incertidumbre"
            self.data["regime_color"] = "#f59e0b"
        
        # Radar data
        self.data["radar"] = {
            "Expansión M2": min(100, m2_growth * 15),
            "Presión Precios": min(100, cpi * 20 + 10),
            "Curva Tipos": min(100, max(0, (2 - d.get("spread_10y2y", 0.55)) * 35)),
            "Actividad Real": min(100, d.get("ism_pmi", 52.7) * 1.2),
            "Empleo": min(100, (6 - unemp) * 30),
            "Riesgo Geopolítico": 85,  # Iran war — manual assessment
        }
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def get_history(self, key):
        return self.history.get(key, pd.DataFrame())

# CHART BUILDERS

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,15,26,0.8)",
    font=dict(color="#94a3b8", size=11),
    margin=dict(l=50, r=20, t=40, b=40),
    xaxis=dict(gridcolor="rgba(100,116,139,0.12)", zerolinecolor="rgba(100,116,139,0.12)"),
    yaxis=dict(gridcolor="rgba(100,116,139,0.12)", zerolinecolor="rgba(100,116,139,0.12)"),
    hovermode="x unified",
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
)


def chart_m2_yoy(mgr: MacroDataManager):
    """Gráfico M2 YoY %."""
    df = mgr.get_history("m2_yoy")
    if df.empty:
        df = pd.DataFrame(FALLBACK_HISTORY["m2_yoy"])
        x, y = df["date"], df["yoy"]
    else:
        df = df.tail(36)
        x, y = df["date"], df["yoy"]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines+markers",
        name="M2 YoY %",
        line=dict(color="#22c55e", width=2.5),
        marker=dict(size=5),
        fill="tozeroy",
        fillcolor="rgba(34,197,94,0.1)",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(239,68,68,0.4)")
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Oferta Monetaria M2 — Crecimiento YoY %", font=dict(size=14, color="#e2e8f0")),
        yaxis_title="%",
        height=320,
    )
    return fig


def chart_cpi(mgr: MacroDataManager):
    """CPI Headline vs Core."""
    df_h = mgr.get_history("cpi_yoy")
    df_c = mgr.get_history("core_cpi_yoy")
    
    fig = go.Figure()
    
    if not df_h.empty:
        df_h = df_h.tail(24)
        fig.add_trace(go.Scatter(x=df_h["date"], y=df_h["yoy"], name="Headline CPI",
                                  line=dict(color="#ef4444", width=2.5), mode="lines+markers", marker=dict(size=4)))
    else:
        fb = pd.DataFrame(FALLBACK_HISTORY["cpi_yoy"])
        fig.add_trace(go.Scatter(x=fb["date"], y=fb["yoy"], name="Headline CPI",
                                  line=dict(color="#ef4444", width=2.5), mode="lines+markers", marker=dict(size=4)))
    
    if not df_c.empty:
        df_c = df_c.tail(24)
        fig.add_trace(go.Scatter(x=df_c["date"], y=df_c["yoy"], name="Core CPI",
                                  line=dict(color="#3b82f6", width=2, dash="dash"), mode="lines+markers", marker=dict(size=3)))
    else:
        fb = pd.DataFrame(FALLBACK_HISTORY["core_cpi_yoy"])
        fig.add_trace(go.Scatter(x=fb["date"], y=fb["yoy"], name="Core CPI",
                                  line=dict(color="#3b82f6", width=2, dash="dash"), mode="lines+markers", marker=dict(size=3)))
    
    fig.add_hline(y=2, line_dash="dot", line_color="rgba(34,197,94,0.4)",
                  annotation_text="Target Fed 2%", annotation_font_color="#22c55e")
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Inflación CPI — Headline vs Core (YoY %)", font=dict(size=14, color="#e2e8f0")),
        yaxis_title="%", height=340,
    )
    return fig


def chart_yield_curve(mgr: MacroDataManager):
    """Curva de rendimientos."""
    # Build from individual series or fallback
    maturities_map = {
        "3M": "yield_3m", "1Y": "yield_1y", "2Y": "yield_2y",
        "5Y": "yield_5y", "10Y": "yield_10y", "30Y": "yield_30y"
    }
    
    labels, yields = [], []
    for mat, key in maturities_map.items():
        val = mgr.get(key)
        if val is not None:
            labels.append(mat)
            yields.append(val)
    
    if not labels:
        fb = pd.DataFrame(FALLBACK_HISTORY["yield_curve"])
        labels = fb["maturity"].tolist()
        yields = fb["yield"].tolist()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=yields, mode="lines+markers",
        line=dict(color="#6366f1", width=2.5),
        marker=dict(size=7, color="#6366f1"),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.08)",
        name="Yield"
    ))
    ff = mgr.get("fed_funds", 3.625)
    fig.add_hline(y=ff, line_dash="dash", line_color="#ef4444",
                  annotation_text=f"Fed Funds {ff:.2f}%", annotation_font_color="#ef4444")
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Curva de Rendimiento US Treasury", font=dict(size=14, color="#e2e8f0")),
        yaxis_title="Yield %", height=320,
    )
    return fig


def chart_ism(mgr: MacroDataManager):
    """ISM Manufacturing components."""
    fb = pd.DataFrame(FALLBACK_HISTORY["ism"])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fb["date"], y=fb["value"], name="PMI",
                              line=dict(color="#3b82f6", width=2.5), mode="lines+markers", marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=fb["date"], y=fb["prices"], name="Precios Pagados",
                              line=dict(color="#ef4444", width=2), mode="lines+markers", marker=dict(size=4)))
    fig.add_trace(go.Scatter(x=fb["date"], y=fb["orders"], name="New Orders",
                              line=dict(color="#22c55e", width=2), mode="lines+markers", marker=dict(size=4)))
    fig.add_hline(y=50, line_dash="dash", line_color="rgba(245,158,11,0.4)",
                  annotation_text="50 = Neutral", annotation_font_color="#f59e0b")
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="ISM Manufacturing — PMI, Precios & New Orders", font=dict(size=14, color="#e2e8f0")),
        height=340,
    )
    return fig


def chart_oil_gold(mgr: MacroDataManager):
    """Oil and Gold dual axis."""
    df_oil = mgr.get_history("oil_hist")
    df_gold = mgr.get_history("gold_hist")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if not df_oil.empty:
        df_oil = df_oil.tail(120)
        fig.add_trace(go.Scatter(x=df_oil["date"], y=df_oil["value"], name="WTI Crude ($/bbl)",
                                  line=dict(color="#f97316", width=2)), secondary_y=False)
    
    if not df_gold.empty:
        df_gold = df_gold.tail(120)
        fig.add_trace(go.Scatter(x=df_gold["date"], y=df_gold["value"], name="Gold ($/oz)",
                                  line=dict(color="#d4a017", width=2)), secondary_y=True)
    
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Commodities — Petróleo WTI & Oro", font=dict(size=14, color="#e2e8f0")),
        height=340,
    )
    fig.update_yaxes(title_text="WTI $/bbl", secondary_y=False, gridcolor="rgba(100,116,139,0.12)")
    fig.update_yaxes(title_text="Gold $/oz", secondary_y=True, gridcolor="rgba(100,116,139,0.06)")
    return fig


def chart_spread_history(mgr: MacroDataManager):
    """10Y-2Y Spread history."""
    df = mgr.get_history("spread_hist")
    if df.empty:
        return None
    
    df = df.tail(250)
    colors = ["#22c55e" if v >= 0 else "#ef4444" for v in df["value"]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["value"], mode="lines",
        line=dict(color="#6366f1", width=2),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.08)",
        name="10Y-2Y Spread"
    ))
    fig.add_hline(y=0, line_dash="solid", line_color="rgba(239,68,68,0.5)")
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Spread 10Y-2Y Treasury — Señal de Recesión", font=dict(size=14, color="#e2e8f0")),
        yaxis_title="%", height=300,
    )
    return fig


def chart_radar(mgr: MacroDataManager):
    """Radar chart for Austrian framework."""
    radar = mgr.get("radar", {})
    if not radar:
        return None
    
    categories = list(radar.keys())
    values = list(radar.values())
    values.append(values[0])  # close the polygon
    categories.append(categories[0])
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories,
        fill="toself",
        fillcolor="rgba(245,158,11,0.15)",
        line=dict(color="#f59e0b", width=2),
        marker=dict(size=6, color="#f59e0b"),
        name="Score"
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(10,15,26,0.8)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(100,116,139,0.15)",
                           tickfont=dict(size=9, color="#64748b")),
            angularaxis=dict(gridcolor="rgba(100,116,139,0.15)",
                            tickfont=dict(size=10, color="#94a3b8")),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        title=dict(text="Radar Macroeconómico Austriaco", font=dict(size=14, color="#e2e8f0")),
        height=400,
        margin=dict(t=60, b=40, l=60, r=60),
        showlegend=False,
    )
    return fig


def chart_fed_balance(mgr: MacroDataManager):
    """Fed balance sheet."""
    df = mgr.get_history("fed_assets_hist")
    if df.empty:
        return None
    df = df.tail(200)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["value"] / 1e6, mode="lines",
        line=dict(color="#8b5cf6", width=2),
        fill="tozeroy", fillcolor="rgba(139,92,246,0.08)",
        name="Fed Total Assets"
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="Balance de la Fed — Activos Totales ($T)", font=dict(size=14, color="#e2e8f0")),
        yaxis_title="Trillones $", height=300,
    )
    return fig


def chart_sp500_vix(mgr: MacroDataManager):
    """S&P 500 with VIX overlay."""
    df_sp = mgr.get_history("sp500_hist")
    df_vix = mgr.get_history("vix_hist")
    
    if df_sp.empty and df_vix.empty:
        return None
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if not df_sp.empty:
        df_sp = df_sp.tail(250)
        fig.add_trace(go.Scatter(x=df_sp["date"], y=df_sp["value"], name="S&P 500",
                                  line=dict(color="#8b5cf6", width=2)), secondary_y=False)
    
    if not df_vix.empty:
        df_vix = df_vix.tail(250)
        fig.add_trace(go.Scatter(x=df_vix["date"], y=df_vix["value"], name="VIX",
                                  line=dict(color="#f59e0b", width=1.5)), secondary_y=True)
    
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="S&P 500 & VIX — Riesgo de Mercado", font=dict(size=14, color="#e2e8f0")),
        height=340,
    )
    fig.update_yaxes(title_text="S&P 500", secondary_y=False, gridcolor="rgba(100,116,139,0.12)")
    fig.update_yaxes(title_text="VIX", secondary_y=True, gridcolor="rgba(100,116,139,0.06)")
    return fig


def chart_allocation():
    """Asset allocation donut chart."""
    alloc = [
        ("Oro y Metales", 20, "#d4a017"),
        ("Commodities Energía", 15, "#f97316"),
        ("TIPS / Bonos Indexados", 15, "#06b6d4"),
        ("T-Bills Corto Plazo", 15, "#64748b"),
        ("Acciones Value / Dividendo", 15, "#8b5cf6"),
        ("Acciones Energía", 10, "#ef4444"),
        ("Cash / Liquidez", 10, "#94a3b8"),
    ]
    
    names = [a[0] for a in alloc]
    values = [a[1] for a in alloc]
    colors = [a[2] for a in alloc]
    
    fig = go.Figure(data=[go.Pie(
        labels=names, values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="rgba(10,15,26,1)", width=2)),
        textinfo="label+percent",
        textfont=dict(size=10, color="#e2e8f0"),
        hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>",
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        title=dict(text="Asignación Recomendada — Régimen Estanflación", font=dict(size=14, color="#e2e8f0")),
        height=420,
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color="#94a3b8")),
        margin=dict(t=60, b=20, l=20, r=20),
        annotations=[dict(text="Anti-<br>Estanflación", x=0.5, y=0.5,
                         font=dict(size=14, color="#f59e0b", family="monospace"),
                         showarrow=False)]
    )
    return fig

# HELPER — Metric card HTML

def metric_card_html(label, value, color="#6366f1", detail="", trend=""):
    trend_class = "trend-up" if trend == "up" else "trend-down" if trend == "down" else "trend-flat"
    arrow = "▲" if trend == "up" else "▼" if trend == "down" else "●" if trend else ""
    return f"""
    <div class="metric-card">
        <div class="bar" style="background:{color}"></div>
        <div class="label">{label}</div>
        <div class="value">{value} <span class="{trend_class}" style="font-size:0.8rem">{arrow}</span></div>
        <div class="detail">{detail}</div>
    </div>
    """

# MAIN APP

def main():
    # ─── SIDEBAR ───
    with st.sidebar:
        st.markdown("### 🏛️ Configuración")
        st.markdown("---")
        
        api_key = st.text_input(
            "🔑 FRED API Key",
            value=os.environ.get("FRED_API_KEY", ""),
            type="password",
            help="Obtén tu key gratuita en https://fred.stlouisfed.org/docs/api/api_key.html"
        )
        
        if api_key:
            st.success("✅ API Key configurada")
        else:
            st.info("ℹ️ Sin API key se usarán datos estáticos (Abr 2026). Configura tu key para datos en vivo.")
        
        st.markdown("---")
        auto_refresh = st.selectbox("⏱️ Auto-refresh", ["Desactivado", "5 min", "15 min", "30 min", "1 hora"])
        
        if st.button("🔄 Actualizar datos ahora", use_container_width=True, type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📚 Framework Teórico")
        st.markdown("""
        **Escuela Austriaca**  
        - Mises — Teoría del ciclo crediticio  
        - Hayek — Estructura de producción  
        - Rothbard — True Money Supply  
        - Böhm-Bawerk — Preferencia temporal  
        - Salerno — TMS metric  
        """)
        
        st.markdown("---")
        st.markdown("### 📡 Fuentes de Datos")
        st.markdown("""
        - **FRED** — Federal Reserve Economic Data  
        - **BLS** — Bureau of Labor Statistics  
        - **ISM** — Institute for Supply Management  
        - **Mises Institute** — TMS analysis  
        """)
        
        st.markdown("---")
        st.markdown("""
        <div style="font-size:0.65rem; color:#475569; text-align:center; padding:0.5rem">
        ⚠️ Esto no constituye asesoramiento financiero. 
        Análisis basado en principios teóricos de la 
        Escuela Austriaca de Economía.
        </div>
        """, unsafe_allow_html=True)
    
    # ─── INIT DATA MANAGER ───
    fred_client = FREDClient(api_key) if api_key else None
    
    @st.cache_data(ttl=300, show_spinner=False)
    def load_data(_has_key: bool, _key: str = ""):
        mgr = MacroDataManager(FREDClient(_key) if _has_key and _key else None)
        mgr.fetch_all()
        return mgr
    
    mgr = load_data(bool(api_key), api_key)
    
    # ─── AUTO REFRESH ───
    refresh_map = {"5 min": 300, "15 min": 900, "30 min": 1800, "1 hora": 3600}
    if auto_refresh in refresh_map:
        st.markdown(f"""
        <meta http-equiv="refresh" content="{refresh_map[auto_refresh]}">
        """, unsafe_allow_html=True)
    
    # ─── HEADER ───
    update_str = mgr.last_update.strftime("%d/%m/%Y %H:%M") if mgr.last_update else "N/A"
    source = "🟢 FRED API (Live)" if api_key else "🟡 Datos estáticos (Abr 2026)"
    
    st.markdown(f"""
    <div class="main-header">
        <div class="subtitle">Escuela Austriaca · Macro Dashboard</div>
        <h1>Ciclo Económico & Liquidez</h1>
        <div class="update-time">{source} · Última actualización: {update_str}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # TABS
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "◉ Panel General",
        "◈ Liquidez & Crédito",
        "◆ Precios & Inflación",
        "◇ Ciclo Austriaco",
        "◐ Asset Allocation",
    ])
    
    # TAB 1: PANEL GENERAL
    with tab1:
        # Regime badge
        regime = mgr.get("regime", "Transición")
        st.markdown(f"""
        <div class="regime-badge">
            <div class="tag">🔴 Régimen Actual</div>
            <div class="regime-name">{regime}</div>
            <div class="regime-desc">
                La economía muestra señales de estanflación: inflación acelerándose (CPI {mgr.get('cpi_yoy', 3.3):.1f}%) impulsada 
                por shock energético, mientras el mercado laboral se debilita y la Fed permanece inmovilizada en {mgr.get('fed_funds', 3.625):.2f}%. 
                M2 crece al {mgr.get('m2_yoy', 4.6):.1f}% YoY con QE renovado, pero la velocidad del dinero permanece deprimida.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">📊 Indicadores Clave en Tiempo Real</div>', unsafe_allow_html=True)
        
        # Row 1: Rates & Policy
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(metric_card_html("Fed Funds Rate", f"{mgr.get('fed_funds', 3.625):.2f}%", "#6366f1", "3ª pausa consecutiva", "flat"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card_html("CPI Headline", f"{mgr.get('cpi_yoy', 3.3):.1f}%", "#ef4444", "Máx. desde May 2024", "up"), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card_html("Core CPI", f"{mgr.get('core_cpi_yoy', 2.6):.1f}%", "#f97316", "Excl. food & energy", "up"), unsafe_allow_html=True)
        with c4:
            st.markdown(metric_card_html("M2 YoY", f"{mgr.get('m2_yoy', 4.6):.1f}%", "#22c55e", "QE $40B/mes Treasuries", "up"), unsafe_allow_html=True)
        
        # Row 2: Employment & Activity
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(metric_card_html("Desempleo", f"{mgr.get('unemployment', 4.3):.1f}%", "#3b82f6", "Participación 61.9%", "down"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card_html("ISM Mfg PMI", f"{mgr.get('ism_pmi', 52.7):.1f}", "#3b82f6", "3er mes en expansión", "up"), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card_html("ISM Precios", f"{mgr.get('ism_prices', 78.3):.1f}", "#ef4444", "Máximo 4 años", "up"), unsafe_allow_html=True)
        with c4:
            st.markdown(metric_card_html("Spread 10Y-2Y", f"{mgr.get('spread_10y2y', 0.55):.2f}%", "#f59e0b", "Se estrecha"), unsafe_allow_html=True)
        
        # Row 3: Markets
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(metric_card_html("Oro", f"${mgr.get('gold', 4554):,.0f}/oz", "#d4a017", "+39% YoY", "down"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card_html("WTI Crudo", f"${mgr.get('oil_wti', 107.14):.1f}/bbl", "#f97316", "Ormuz cerrado", "up"), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card_html("DXY Dólar", f"{mgr.get('dxy', 98.73):.1f}", "#64748b", "Bajo nivel 100", "down"), unsafe_allow_html=True)
        with c4:
            st.markdown(metric_card_html("S&P 500", f"{mgr.get('sp500', 7124):,.0f}", "#8b5cf6", "CAPE ~39", "down"), unsafe_allow_html=True)
        
        # Row 4: More
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(metric_card_html("VIX", f"{mgr.get('vix', 18.55):.1f}", "#f59e0b", "Volatilidad implícita", "up"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card_html("10Y Yield", f"{mgr.get('yield_10y', 4.43):.2f}%", "#06b6d4", "Treasury 10 años", "up"), unsafe_allow_html=True)
        with c3:
            be5 = mgr.get("breakeven_5y", 2.85)
            st.markdown(metric_card_html("Breakeven 5Y", f"{be5:.2f}%", "#ef4444", "Expectativas inflación", "up"), unsafe_allow_html=True)
        with c4:
            baa = mgr.get("baa_spread", 2.10)
            st.markdown(metric_card_html("Baa Spread", f"{baa:.2f}%", "#8b5cf6", "Riesgo crédito corp.", "up"), unsafe_allow_html=True)
    
    # TAB 2: LIQUIDEZ & CRÉDITO
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(chart_m2_yoy(mgr), use_container_width=True)
        with col2:
            st.plotly_chart(chart_yield_curve(mgr), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fig_spread = chart_spread_history(mgr)
            if fig_spread:
                st.plotly_chart(fig_spread, use_container_width=True)
            else:
                st.info("Spread history requiere FRED API key")
        with col2:
            fig_fed = chart_fed_balance(mgr)
            if fig_fed:
                st.plotly_chart(fig_fed, use_container_width=True)
            else:
                st.info("Balance Fed requiere FRED API key")
        
        st.markdown("""
        <div class="analysis-box">
            <h4>🏦 Análisis Austriaco de Liquidez</h4>
            <p><strong style="color:#22c55e">Expansión monetaria activa:</strong> La Fed ha retomado compras de 
            Treasuries por $40B/mes (QE encubierto) mientras mantiene tipos en 3.5–3.75%. El TMS (True Money Supply 
            de Rothbard-Salerno) supera los $20.4 billones, con ~30% creado desde enero 2020. En solo 7 meses 
            (Jul 2025–Feb 2026) se ha creado $1 billón adicional.</p>
            <p><strong style="color:#f59e0b">Señal de curva:</strong> El spread 10Y-2Y en +55pb indica que la inversión 
            previa se ha deshecho, pero su estrechez sugiere escepticismo del mercado sobre el crecimiento futuro. Los 
            rendimientos largos suben por expectativas inflacionarias, no por crecimiento real — la distorsión hayekiana 
            de la estructura temporal de tipos.</p>
            <p><strong style="color:#ef4444">Riesgo:</strong> Esta combinación — expansión monetaria + inflación de 
            costes + tipos elevados — es el patrón clásico austriaco de «crack-up boom» en fase temprana, donde el 
            dinero nuevo fluye hacia activos reales y commodities en lugar de inversiones productivas.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # TAB 3: PRECIOS & INFLACIÓN
    with tab3:
        st.plotly_chart(chart_cpi(mgr), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(chart_ism(mgr), use_container_width=True)
        with col2:
            st.plotly_chart(chart_oil_gold(mgr), use_container_width=True)
        
        st.markdown(f"""
        <div class="analysis-box">
            <h4>📈 Lectura Austriaca de la Inflación</h4>
            <p><strong style="color:#ef4444">Inflación de costes vs monetaria:</strong> El salto del CPI de 2.4% a 
            {mgr.get('cpi_yoy', 3.3):.1f}% es primariamente un shock de oferta (energía +12.5% por el cierre del 
            Estrecho de Ormuz), pero el core CPI subiendo a {mgr.get('core_cpi_yoy', 2.6):.1f}% muestra que la 
            transmisión a precios subyacentes ha comenzado. Desde la perspectiva de Mises, toda inflación de precios 
            tiene su origen último en la expansión de la oferta monetaria — el shock de oferta solo determina <em>dónde</em> 
            aparecen primero los precios más altos.</p>
            <p><strong style="color:#f59e0b">ISM Precios Pagados en {mgr.get('ism_prices', 78.3):.1f}:</strong> El mayor 
            nivel desde junio 2022 confirma que los costes de inputs se están disparando. La divergencia entre precios 
            ({mgr.get('ism_prices', 78.3):.1f}) y new orders ({mgr.get('ism_new_orders', 53.5):.1f}, cayendo) es la 
            señal clásica austriaca de compresión de márgenes que precede una corrección del ciclo.</p>
            <p><strong style="color:#8b5cf6">Efecto Cantillon:</strong> El dinero nuevo creado por la Fed no entra 
            uniformemente en la economía. Los primeros receptores (sector financiero, gobierno) se benefician a 
            expensas de los últimos (consumidores, ahorradores). El oro (+39% YoY) y el petróleo reflejan la 
            devaluación real del dólar que las estadísticas oficiales infraestiman.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # TAB 4: CICLO AUSTRIACO
    with tab4:
        scores = mgr.get("cycle_scores", {})
        phase_colors = {"Expansión Crediticia": "#22c55e", "Malinversión": "#f59e0b",
                       "Inflación de Precios": "#ef4444", "Corrección / Bust": "#8b5cf6"}
        
        st.markdown('<div class="section-title">🔄 Reloj del Ciclo Austriaco (Mises-Hayek)</div>', unsafe_allow_html=True)
        
        cols = st.columns(4)
        for i, (phase, score) in enumerate(scores.items()):
            color = phase_colors.get(phase, "#6366f1")
            with cols[i]:
                st.markdown(f"""
                <div class="phase-card" style="border: 1px solid {color}33">
                    <div style="font-size:0.65rem; color:#94a3b8; text-transform:uppercase; 
                                letter-spacing:0.5px; font-family:monospace">Fase {i+1}</div>
                    <div style="font-size:0.85rem; font-weight:600; color:{color}; margin-top:4px">{phase}</div>
                    <div style="font-size:1.5rem; font-weight:700; color:#f1f5f9; margin-top:4px">
                        {score}<span style="font-size:0.75rem; color:#64748b">/100</span>
                    </div>
                    <div style="margin-top:8px; height:4px; background:rgba(100,116,139,0.15); border-radius:2px">
                        <div style="height:100%; width:{score}%; background:{color}; border-radius:2px"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            fig_radar = chart_radar(mgr)
            if fig_radar:
                st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            fig_spvix = chart_sp500_vix(mgr)
            if fig_spvix:
                st.plotly_chart(fig_spvix, use_container_width=True)
            else:
                st.info("S&P 500 / VIX chart requiere FRED API key")
        
        st.markdown("""
        <div class="analysis-box">
            <h4>📖 Diagnóstico del Ciclo — Marco Mises-Hayek</h4>
            <p><strong style="color:#22c55e">1. Expansión crediticia:</strong> La Fed retomó QE con $40B/mes en compras 
            de Treasuries y recortó tipos 175pb en 2025. El TMS supera $20.4T. El tipo natural de interés (Wickselliano) 
            se encuentra muy por encima del tipo de mercado, manteniendo el desajuste intertemporal.</p>
            <p><strong style="color:#f59e0b">2. Malinversión:</strong> Las inversiones masivas en IA (data centers, chips) 
            muestran señales de sobreinversión. El CAPE en ~39 (2x la media histórica) refleja valoraciones infladas por 
            crédito barato. La producción real sigue expandiéndose (ISM 52.7), retrasando la corrección.</p>
            <p><strong style="color:#ef4444">3. Inflación de precios:</strong> Fase más avanzada. El shock energético ha 
            acelerado la transmisión de la inflación monetaria a precios reales. ISM Precios en 78.3, CPI saltando a 3.3%. 
            La divergencia precios-demanda es la señal hayekiana clásica de distorsión en la estructura de producción.</p>
            <p><strong style="color:#8b5cf6">4. Corrección / Bust:</strong> Aún en fase temprana. La Fed no ha endurecido 
            agresivamente, los mercados laborales resisten. Pero las señales adelantadas (ISM New Orders cayendo, empleo 
            ISM en contracción, participación laboral descendiendo) sugieren que la corrección se está gestando.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # TAB 5: ASSET ALLOCATION
    with tab5:
        st.markdown(f"""
        <div class="regime-badge">
            <div class="tag">◐ Cartera Defensiva</div>
            <div class="regime-name">Anti-Estanflación · Shock de Oferta</div>
            <div class="regime-desc">
                En un régimen de estanflación con shock de oferta energético, la asignación prioriza: 
                (1) activos reales que preserven poder adquisitivo, (2) exposición a la escasez energética, 
                (3) duración corta en renta fija, y (4) liquidez para oportunidades post-corrección. 
                Basado en el framework de Mises-Hayek y la estructura de producción de Böhm-Bawerk.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.plotly_chart(chart_allocation(), use_container_width=True)
        
        with col2:
            allocation = [
                ("Oro y Metales", 20, "#d4a017", "Protección ante debasement monetario y riesgo geopolítico"),
                ("Commodities Energía", 15, "#f97316", "Escasez por conflicto Irán, Estrecho de Ormuz"),
                ("TIPS / Bonos Indexados", 15, "#06b6d4", "Protección inflacionaria con rendimiento real"),
                ("T-Bills Corto Plazo", 15, "#64748b", "Liquidez defensiva, yield 3.6%+ con bajo riesgo"),
                ("Acciones Value / Dividendo", 15, "#8b5cf6", "Empresas con pricing power, baja duración"),
                ("Acciones Energía", 10, "#ef4444", "Beneficiarias directas del shock de oferta"),
                ("Cash / Liquidez", 10, "#94a3b8", "Opcionalidad ante corrección bursátil (CAPE ~39)"),
            ]
            
            for name, pct, color, reason in allocation:
                st.markdown(f"""
                <div class="alloc-item">
                    <div style="display:flex; justify-content:space-between; align-items:center">
                        <span class="name" style="border-left:3px solid {color}; padding-left:8px">{name}</span>
                        <span class="pct" style="color:{color}">{pct}%</span>
                    </div>
                    <div class="reason">{reason}</div>
                    <div style="margin-top:6px; height:3px; background:rgba(100,116,139,0.12); border-radius:2px">
                        <div style="height:100%; width:{pct*5}%; background:{color}; border-radius:2px"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Risk cards
        st.markdown('<div class="section-title">⚠️ Riesgos y Catalizadores</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="risk-card risk-bear">
                <div style="font-weight:600; color:#ef4444; margin-bottom:8px">Riesgos Bajistas</div>
                <div style="font-size:0.82rem; color:#cbd5e1; line-height:1.7">
                    • Escalada guerra Irán → CPI >4%<br>
                    • Fed forzada a subir tipos<br>
                    • CAPE ~39 → corrección 20-30% en renta variable<br>
                    • Crack-up boom si M2 acelera aún más<br>
                    • Recesión en bienes si ISM New Orders cae bajo 50
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="risk-card risk-bull">
                <div style="font-weight:600; color:#22c55e; margin-bottom:8px">Catalizadores Alcistas</div>
                <div style="font-size:0.82rem; color:#cbd5e1; line-height:1.7">
                    • Alto el fuego Irán → petróleo -30%<br>
                    • Fed recorta → boost de liquidez<br>
                    • IA mantiene productividad y márgenes<br>
                    • Warsh como Chair → reforma y credibilidad Fed<br>
                    • Apertura Estrecho de Ormuz → CPI normaliza
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="analysis-box">
            <h4>📚 Lógica Austriaca del Asset Allocation</h4>
            <p><strong style="color:#d4a017">Oro (20%):</strong> En el framework Mises-Rothbard, el oro es el dinero por 
            excelencia. Con $1T de masa monetaria creada en 7 meses y compras de bancos centrales a ~60t/mes, el oro 
            protege contra el debasement activo del dólar. JPMorgan target: $6,300/oz.</p>
            <p><strong style="color:#f97316">Energía (25% total):</strong> El Estrecho de Ormuz cerrado ha cortado ~20% 
            del suministro mundial de petróleo. Desde la perspectiva austriaca, los bienes de primer orden (consumo 
            directo) son los primeros en reflejar la escasez real vs. la abundancia monetaria artificial.</p>
            <p><strong style="color:#06b6d4">TIPS (15%):</strong> Los bonos indexados a inflación ofrecen protección 
            directa. Con breakevens a 5Y en ~{mgr.get('breakeven_5y', 2.85):.1f}%, el mercado aún infravalora el riesgo 
            inflacionario — oportunidad de posicionarse antes de que se reprecie.</p>
            <p><strong style="color:#94a3b8">Liquidez (25% entre cash y T-Bills):</strong> Böhm-Bawerk enfatizó que la 
            preferencia temporal alta exige mantener opcionalidad. Con CAPE en ~39 y la corrección de malinversiones aún 
            por materializarse, el cash es la pólvora seca para comprar activos productivos cuando los precios reflejen 
            sus fundamentales reales.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # FOOTER
    st.markdown("""
    <div class="disclaimer">
        ⚠️ Esto no constituye asesoramiento financiero. Análisis basado en principios teóricos 
        de la Escuela Austriaca de Economía aplicados a datos macro actuales. 
        Consulte con un asesor financiero cualificado antes de tomar decisiones de inversión.<br><br>
        Fuentes: FRED · BLS · ISM · Federal Reserve · Mises Institute<br>
        Framework: Mises · Hayek · Rothbard · Böhm-Bawerk · Salerno
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
