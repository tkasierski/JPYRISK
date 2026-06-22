# JPYRISK

A Streamlit app for monitoring Japan equity and exporter risk using market and macro indicators.

The app pulls data from Yahoo Finance and FRED, computes percentile-based risk tripwires, builds headline indices, generates an executive narrative, and exports a PDF report.

## Indicators

- Nikkei 225 3-month realized volatility
- Nikkei 225 drawdown versus 1-year rolling peak
- USDJPY 3-month realized volatility
- USDJPY 1-month absolute move
- Japan 10-year yield 3-month change
- China versus Japan export growth spread
- China versus Japan REER spread 3-month change
- Japan REER level

## Headline indices

- Exporter Pressure Index
- Macro Stress Index

Both are scaled from 0 to 100, where higher values indicate greater stress or pressure.

## Streamlit deployment

Use these settings in Streamlit Community Cloud:

```text
Repository: tkasierski/JPYRISK
Branch: main
Main file path: streamlit_app.py
```

## Local usage

```bash
git clone https://github.com/tkasierski/JPYRISK.git
cd JPYRISK
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Data notes

Yahoo Finance and FRED data can revise, lag, or occasionally fail to return observations. The app reports unavailable indicators as `GRAY` rather than forcing a risk classification.