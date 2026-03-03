import dash_bootstrap_components as dbc
from dash import html

def make_info_card(text: str) -> dbc.Card:
    """Build a simple informational Bootstrap card.

    Args:
        text: The paragraph text rendered inside the card body.

    Returns:
        A Bootstrap card containing the supplied text.
    """

    return dbc.Card(dbc.CardBody(html.P(text)))
