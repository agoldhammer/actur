#!/usr/bin/env python

"""Tests for `actur` package."""

from click.testing import CliRunner

from actur import actu_cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(actu_cli.cli)
    assert result.exit_code == 0  # nosec
    # assert "actur.show_news.main" in result.output  # nosec
    help_result = runner.invoke(actu_cli.cli, ["--help"])
    assert help_result.exit_code == 0  # nosec
    # print(help_result.output)
    assert "--help" in help_result.output  # nosec


def test_show_list(mocker):
    runner = CliRunner()
    res = runner.invoke(actu_cli.cli, ["show", "--list"])
    assert res.exit_code == 0  # nosec B101
