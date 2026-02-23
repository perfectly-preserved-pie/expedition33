# filepath: helpers/utils.py
from dash import html, dbc

def make_info_card(text: str):
    """return a simple bootstrap card with the given text"""
    return dbc.Card(dbc.CardBody(html.P(text)))
