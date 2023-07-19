#!/usr/bin/env python

"""Tests for `actur` package."""

from click.testing import CliRunner

from actur import actu_cli

# from actur.utils import dbif


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(actu_cli.cli)
    assert result.exit_code == 0  # nosec
    help_result = runner.invoke(actu_cli.cli, ["--help"])
    assert help_result.exit_code == 0  # nosec
    assert "--help" in help_result.output  # nosec


def test_show_list():
    runner = CliRunner()
    res = runner.invoke(actu_cli.cli, ["show", "--list"])
    assert "LeMonde" in res.output  # nosec B101
    assert res.exit_code == 0  # nosec B101
