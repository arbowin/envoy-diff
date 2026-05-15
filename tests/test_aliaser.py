"""Tests for envoy_diff.aliaser and envoy_diff.alias_reporter."""
import json
import pytest

from envoy_diff.aliaser import (
    AliasError,
    AliasRule,
    apply_aliases,
)
from envoy_diff.alias_reporter import (
    format_alias_json,
    format_alias_markdown,
    format_alias_text,
    render_alias,
)


@pytest.fixture()
def rules():
    return [
        AliasRule(canonical="DATABASE_URL", aliases=["DB_URL", "DATABASE_URI"]),
        AliasRule(canonical="SECRET_KEY", aliases=["APP_SECRET", "DJANGO_SECRET"]),
    ]


@pytest.fixture()
def env_with_aliases():
    return {"DB_URL": "postgres://localhost/db", "APP_SECRET": "s3cr3t", "PORT": "8080"}


def test_apply_aliases_replaces_alias_key(rules, env_with_aliases):
    result = apply_aliases(env_with_aliases, rules)
    assert "DATABASE_URL" in result.resolved
    assert result.resolved["DATABASE_URL"] == "postgres://localhost/db"
    assert "DB_URL" not in result.resolved


def test_apply_aliases_records_match(rules, env_with_aliases):
    result = apply_aliases(env_with_aliases, rules)
    originals = [m.original_key for m in result.matches]
    assert "DB_URL" in originals
    assert "APP_SECRET" in originals


def test_apply_aliases_canonical_takes_precedence(rules):
    env = {"DB_URL": "alias_value", "DATABASE_URL": "canonical_value"}
    result = apply_aliases(env, rules)
    assert result.resolved["DATABASE_URL"] == "canonical_value"
    assert len([m for m in result.matches if m.original_key == "DB_URL"]) == 0


def test_non_alias_keys_pass_through(rules, env_with_aliases):
    result = apply_aliases(env_with_aliases, rules)
    assert "PORT" in result.resolved
    assert result.resolved["PORT"] == "8080"


def test_no_rules_returns_original_env(env_with_aliases):
    result = apply_aliases(env_with_aliases, [])
    assert result.resolved == env_with_aliases
    assert not result.has_matches


def test_duplicate_canonical_raises():
    bad_rules = [
        AliasRule(canonical="KEY", aliases=["OLD_KEY"]),
        AliasRule(canonical="KEY", aliases=["LEGACY_KEY"]),
    ]
    with pytest.raises(AliasError):
        apply_aliases({"OLD_KEY": "v"}, bad_rules)


def test_text_no_matches():
    from envoy_diff.aliaser import AliasResult
    result = AliasResult(resolved={"PORT": "8080"})
    text = format_alias_text(result)
    assert "No alias" in text


def test_text_shows_substitutions(rules, env_with_aliases):
    result = apply_aliases(env_with_aliases, rules)
    text = format_alias_text(result)
    assert "DB_URL" in text
    assert "DATABASE_URL" in text


def test_json_is_valid(rules, env_with_aliases):
    result = apply_aliases(env_with_aliases, rules)
    data = json.loads(format_alias_json(result))
    assert "substitutions" in data
    assert isinstance(data["substitutions"], list)


def test_markdown_contains_table_header(rules, env_with_aliases):
    result = apply_aliases(env_with_aliases, rules)
    md = format_alias_markdown(result)
    assert "| Original Key |" in md
    assert "`DB_URL`" in md


def test_render_alias_delegates_format(rules, env_with_aliases):
    result = apply_aliases(env_with_aliases, rules)
    assert render_alias(result, "json") == format_alias_json(result)
    assert render_alias(result, "markdown") == format_alias_markdown(result)
    assert render_alias(result, "text") == format_alias_text(result)
