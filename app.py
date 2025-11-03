from __future__ import annotations

import datetime as _dt
from typing import List, Dict

import streamlit as st

# Reuse your existing logic from starter.py
from starter import search_players, last_n_averages


def _default_season() -> str:
    """Return an NBA season string like '2024-25' based on today."""
    today = _dt.date.today()
    year = today.year
    # NBA seasons roll over in October; Oct–Dec are the start of a new season
    if today.month >= 10:
        start = year
        end = (year + 1) % 100
    else:
        start = year - 1
        end = (year) % 100
    return f"{start}-{end:02d}"


st.set_page_config(page_title="NBA Recent Averages", page_icon="🏀", layout="wide")

st.title("NBA Player Recent Averages 🏀")
st.caption("Search a player and view last N games per-game stats and shooting percentages.")


@st.cache_data(ttl=900)
def _cached_search(q: str) -> List[dict]:
    return search_players(q)


@st.cache_data(ttl=600)
def _cached_averages(name: str, season: str, n: int) -> Dict[str, float]:
    return last_n_averages(name, season, n)


with st.sidebar:
    st.header("Filters")
    season = st.text_input("Season (e.g. 2024-25)", value=_default_season())
    n_games = st.slider("Last N games", min_value=1, max_value=20, value=10)

    st.divider()
    query = st.text_input("Search player", placeholder="Type at least 3 characters...")
    matches: List[dict] = []
    sel_idx = 0
    if query and len(query.strip()) >= 3:
        with st.spinner("Searching players..."):
            try:
                matches = _cached_search(query.strip())[:50]
            except Exception as e:
                st.error(f"Search failed: {e}")
                matches = []

    names = [f"{m.get('full_name')}" + (" (ACTIVE)" if m.get('is_active') else "") for m in matches]
    selection = st.selectbox("Select player", options=["—"] + names, index=0)


def _render_metrics(avg: Dict[str, float]) -> None:
    st.subheader("Per-game averages (last window)")
    st.caption(f"Computed over {int(avg.get('games_used', 0))} games.")

    cols = st.columns(6)
    cols[0].metric("PTS", f"{avg.get('PTS', 0):.1f}")
    cols[1].metric("REB", f"{avg.get('REB', 0):.1f}")
    cols[2].metric("AST", f"{avg.get('AST', 0):.1f}")
    cols[3].metric("STL", f"{avg.get('STL', 0):.1f}")
    cols[4].metric("BLK", f"{avg.get('BLK', 0):.1f}")
    cols[5].metric("TOV", f"{avg.get('TOV', 0):.1f}")

    cols2 = st.columns(4)
    cols2[0].metric("3PM", f"{avg.get('3PM', 0):.1f}")
    cols2[1].metric("FG%", f"{avg.get('FG%', 0)*100:.1f}%")
    cols2[2].metric("FT%", f"{avg.get('FT%', 0)*100:.1f}%")
    cols2[3].metric("Games", f"{int(avg.get('games_used', 0))}")

    with st.expander("Advanced (makes/attempts per game)"):
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("FGM / G", f"{avg.get('FGM_pg', 0):.2f}")
        a2.metric("FGA / G", f"{avg.get('FGA_pg', 0):.2f}")
        a3.metric("FTM / G", f"{avg.get('FTM_pg', 0):.2f}")
        a4.metric("FTA / G", f"{avg.get('FTA_pg', 0):.2f}")


placeholder = st.empty()

if selection and selection != "—":
    i = names.index(selection)
    chosen = matches[i]
    player_name = str(chosen.get("full_name", ""))
    st.subheader(player_name)
    st.caption("Regular season only; pulled from nba_api PlayerGameLog.")

    with st.spinner("Fetching last N game averages..."):
        try:
            averages = _cached_averages(player_name, season, n_games)
        except Exception as e:
            st.error(f"Failed to fetch game log for {player_name}: {e}")
        else:
            _render_metrics(averages)
else:
    placeholder.info("Use the sidebar to search and select a player.")

