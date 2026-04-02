#!/usr/bin/env bash

pip install -r requirements.txt
python -m spacy download en_core_web_sm

streamlit run app.py --server.port=$PORT --server.address=0.0.0.0