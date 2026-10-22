"""Tests that the frontend is served and each page has its content."""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    ("path", "expected_text"),
    [
        ("/", "Hi, I'm Alex."),
        ("/index.html", "Explore this site"),
        ("/about.html", "Biography"),
        ("/portfolio.html", "Portfolio"),
        ("/contact.html", "Contact"),
        ("/todos.html", "ToDo List"),
    ],
)
def test_page_responds_with_expected_content(client: TestClient, path: str, expected_text: str):
    response = client.get(path)

    assert response.status_code == 200
    assert expected_text in response.text
    assert response.headers["content-type"].startswith("text/html")


def test_homepage_links_to_the_other_pages(client: TestClient):
    html = client.get("/").text

    for href in ("/about.html", "/portfolio.html", "/contact.html"):
        assert href in html


def test_every_page_has_navigation(client: TestClient):
    for path in ("/", "/about.html", "/portfolio.html", "/contact.html"):
        html = client.get(path).text
        assert 'class="site-nav"' in html
        assert "data-page=" in html


def test_about_page_has_all_sections(client: TestClient):
    html = client.get("/about.html").text

    for heading in ("Biography", "Education", "Skills", "Interests"):
        assert f"<h2 id=\"{heading.lower()}\">{heading}</h2>" in html


def test_contact_page_has_mailto_and_no_form(client: TestClient):
    html = client.get("/contact.html").text

    assert "mailto:" in html
    assert "<form" not in html


def test_portfolio_lists_projects_with_technologies(client: TestClient):
    html = client.get("/portfolio.html").text

    assert html.count('class="project"') >= 2
    assert "Technologies used" in html
    assert "javascript" in html.lower()


def test_portfolio_contains_project_without_link(client: TestClient):
    html = client.get("/portfolio.html").text
    cards = re.findall(r'<article class="project">(.*?)</article>', html, re.DOTALL)

    assert cards, "expected at least one project card"
    assert any("project-link" not in card for card in cards)


def test_unknown_path_returns_404_page(client: TestClient):
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert "Page not found" in response.text


def test_api_is_not_shadowed_by_static_mount(client: TestClient):
    response = client.get("/api/todos")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
