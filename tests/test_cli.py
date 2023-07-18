#!/usr/bin/env python

"""Tests for `actur` package."""

from click.testing import CliRunner

from actur import actu_cli


# @pytest.fixture
# def response():
#     """Sample pytest fixture.

#     See more at: http://doc.pytest.org/en/latest/fixture.html
#     """
#     # import requests
#     # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


# def test_content(response):
#     """Sample pytest test function with the pytest fixture as an argument."""
#     # from bs4 import BeautifulSoup
#     # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(actu_cli.cli)
    assert result.exit_code == 0  # nosec
    # assert "actur.show_news.main" in result.output  # nosec
    help_result = runner.invoke(actu_cli.cli, ["--help"])
    assert help_result.exit_code == 0  # nosec
    print(help_result.output)
    assert "--help" in help_result.output  # nosec
