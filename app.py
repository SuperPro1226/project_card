from fastapi import FastAPI
from fastapi.responses import Response, RedirectResponse
from jinja2 import Environment, FileSystemLoader
from urllib.request import urlopen, Request
from src.themes import THEMES
from json import loads
from src.formatters import *
from os import environ
app = FastAPI()
renderer = Environment(loader=FileSystemLoader('templates'))

templates = {
    "project_card": renderer.get_template('project_card.svg'),
}
default_theme = 'dark-blue'

GITHUB_TOKEN = environ.get('GITHUB_TOKEN')


@app.get('/')
async def index():
    return RedirectResponse('/docs')


@app.get("/{template_name}/{user}/{repo}")
async def get_project_card(user: str, repo: str, template_name: str, theme: str = default_theme):
    """
    Get a project card for a given user and repo.
    """
    # Fetch the data from github
    try:
        print(GITHUB_TOKEN)
        req = Request(f"https://api.github.com/repos/{user}/{repo}")
        req.add_header("Authorization",
                       f"token {GITHUB_TOKEN}")
        data = urlopen(req).read()

    except Exception as e:
        return {"error": str(e)}
    data = loads(data)

    # Loads the template
    template = templates.get(template_name, None)
    if not template:
        return {"error": "template not found"}

    # Loads the theme
    theme = THEMES.get(theme, None)
    if not theme:
        return {"error": "theme not found"}

    # Assembles the data
    if template_name == "project_card":
        template_data = {
            "name": format_title(data["name"]),


            "stars": format_number(data["stargazers_count"]),
            "forks": format_number(data["forks_count"]),
            "watch": format_number(data["watchers"]),

            "size": format_file(data["size"]),
            "issues": data["open_issues"],
            "lang": data["language"],
            "license": format_license(data["license"]["name"]) if data["license"] else "Unknown",

            "created": format_date(data["created_at"]),
            "updated": format_date(data["updated_at"]),
        }
        template_data["desc1"], template_data["desc2"], template_data["desc3"] = format_desc(
            data["description"] if data["description"] else "~")
        template_data.update(theme)
        svg = template.render(template_data)
        return Response(svg, media_type="image/svg+xml")
