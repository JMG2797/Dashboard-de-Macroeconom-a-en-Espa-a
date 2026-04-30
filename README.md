# 🏛️ Macro Dashboard — Escuela Austriaca de Economía

Dashboard financiero macroeconómico que recopila variables adelantadas para predecir el ciclo económico y bursátil de liquidez, determina el régimen macroeconómico actual, y recomienda asset allocation óptimo — todo basado en principios de la Escuela Austriaca de Economía.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Obtener API Key de FRED (Gratuita)

1. Ve a [https://fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html)
2. Crea una cuenta gratuita
3. Solicita tu API key

### 3. Ejecutar

```bash
# Opción A: Configurar key como variable de entorno
export FRED_API_KEY="tu_api_key_aqui"
streamlit run app.py

# Opción B: Introducir la key en el sidebar de la app
streamlit run app.py
```

---

## 📊 Paneles del Dashboard

### ◉ Panel General
- 16 métricas macro en tiempo real con tendencias
- Determinación automática del régimen macroeconómico
- Fed Funds, CPI, M2, ISM, Oro, Petróleo, DXY, S&P 500, VIX, Breakevens, etc.

### ◈ Liquidez & Crédito
- Gráfico M2 YoY con datos históricos
- Curva de rendimientos del Treasury completa
- Spread 10Y-2Y (señal de recesión)
- Balance de la Fed (activos totales)
- Análisis austriaco de la expansión monetaria

### ◆ Precios & Inflación
- CPI Headline vs Core con target de la Fed
- ISM Manufacturing: PMI, Precios Pagados & New Orders
- Commodities: Petróleo WTI & Oro
- Análisis del Efecto Cantillon y transmisión de precios

### ◇ Ciclo Austriaco
- Reloj de 4 fases Mises-Hayek con scoring automático
- Radar macroeconómico con 6 dimensiones
- S&P 500 vs VIX overlay
- Diagnóstico completo del ciclo crediticio

### ◐ Asset Allocation
- Donut chart con asignación recomendada
- 7 clases de activos con justificación teórica
- Riesgos bajistas y catalizadores alcistas
- Lógica de Böhm-Bawerk para preferencia temporal

---

## 📡 Fuentes de Datos

| Fuente | Tipo | Series |
|--------|------|--------|
| **FRED API** | En vivo | M2, CPI, Yields, Unemployment, S&P 500, VIX, Oil, Gold, Fed Balance, etc. |
| **Fallback** | Estático | Datos de Abril 2026 cuando no hay API key |

### Series FRED utilizadas (30+)

- **Tipos**: EFFR, DGS10, DGS2, DGS3MO, DGS5, DGS30, DGS1, T10Y2Y, T10Y3M
- **Monetarias**: M2SL, M1SL, BOGMBASE, M2V
- **Inflación**: CPIAUCSL, CPILFESL, PCEPI, PCEPILFE, T5YIE, T10YIE
- **Empleo**: UNRATE, PAYEMS, CIVPART, ICSA, JTSJOL
- **Actividad**: INDPRO, RSAFS, HOUST, USSLIND
- **Mercados**: SP500, VIXCLS, DTWEXBGS, BAA10Y
- **Fed**: WALCL, TREAST
- **Commodities**: DCOILWTICO, GOLDAMGBD228NLBM

---

## 🔧 Configuración Avanzada

### Auto-refresh
Selecciona el intervalo de actualización en el sidebar (5 min, 15 min, 30 min, 1 hora).

### Variables de entorno
```bash
FRED_API_KEY=tu_key_aqui    # API key de FRED
```

### Despliegue en Streamlit Cloud
1. Sube el repo a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repo
4. Añade `FRED_API_KEY` en Secrets:
   ```toml
   FRED_API_KEY = "tu_key_aqui"
   ```

---

## 📚 Framework Teórico

### Escuela Austriaca de Economía
- **Ludwig von Mises** — Teoría del ciclo crediticio
- **Friedrich Hayek** — Estructura de producción y precios relativos
- **Murray Rothbard** — True Money Supply (TMS)
- **Eugen von Böhm-Bawerk** — Preferencia temporal
- **Joseph Salerno** — Métricas monetarias austriacas

### Determinación del Régimen
El dashboard clasifica automáticamente el régimen macroeconómico en base a 4 scores:

1. **Expansión Crediticia** (0-100): M2 growth, Fed Funds rate, QE
2. **Malinversión** (0-100): CAPE ratio, VIX, AI capex bubble
3. **Inflación de Precios** (0-100): CPI, ISM Prices Paid
4. **Corrección / Bust** (0-100): Unemployment, yield curve, leading indicators

### Regímenes posibles:
- 🟢 **Expansión Artificial (Boom)** — Crédito alto, inflación baja
- 🟡 **Estanflación Incipiente** — Inflación alta, crédito activo
- 🔴 **Estanflación** — Inflación alta, actividad cayendo
- 🟣 **Contracción / Recesión** — Bust score alto

---

## ⚠️ Disclaimer

Esto no constituye asesoramiento financiero. Análisis basado en principios teóricos de la Escuela Austriaca de Economía aplicados a datos macroeconómicos. Consulte con un asesor financiero cualificado antes de tomar decisiones de inversión.
