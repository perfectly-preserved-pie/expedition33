# filepath: pages/contact.py
from dash import html, dcc

layout = html.Div(
    [
        html.H1("Contact"),
        html.P("You can reach us at:"),
        dcc.Input(type="email", placeholder="your@email.com"),
    ]
)

from dash import register_page
register_page(__name__, path="/contact", name="Contact", layout=layout)
