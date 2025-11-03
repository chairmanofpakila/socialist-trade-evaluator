"""Streamlit entrypoint wrapper.

Many Streamlit hosts default to looking for `streamlit_app.py`.
This wrapper just imports `app.py`, which renders the UI at import time.
"""

import app  # noqa: F401

