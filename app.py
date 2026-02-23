from dash import html
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

# create the Dash app with the builtin pages support
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    #suppress_callback_exceptions=True,
)

app.layout = dmc.MantineProvider(
    dbc.Container(
        [
            dbc.NavbarSimple(
                children=[
                    dbc.NavItem(dbc.NavLink(page["name"], href=page["path"]))
                    for page in dash.page_registry.values()
                ],
                brand="Multi‑Page Demo",
                color="dark",
                dark=True,
            ),
            html.Hr(),
            dash.page_container,
        ],
        fluid=True,
    )
)

if __name__ == "__main__":
    app.run(debug=True)
