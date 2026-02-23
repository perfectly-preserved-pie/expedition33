# filepath: pages/about.py
from dash import html
from helpers.utils import make_info_card

layout = html.Div(
    [
        html.H1("About"),
        make_info_card("This is an example about page."),
    ]
)

from dash import register_page
register_page(__name__, path="/about", name="About", layout=layout)
