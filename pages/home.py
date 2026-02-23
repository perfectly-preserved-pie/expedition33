# filepath: pages/home.py
from dash import html

layout = html.Div(
    [
        html.H1("Home"),
        html.P("Welcome to the home page of the multi‑page Dash app."),
    ]
)

# register the page
from dash import register_page

register_page(__name__, path="/", name="Home", layout=layout)
