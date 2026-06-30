"""Unit tests for actur.categorize — no live config or OpenAI calls required."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_FAKE_KEY = "sk-test-key-123"


@pytest.fixture(autouse=True)
def _reset_cached_client():
    """classify_by_title caches its AsyncOpenAI client at module scope; clear it
    between tests so each test's AsyncOpenAI patch takes effect."""
    from actur import categorize

    categorize._client = None
    yield
    categorize._client = None


def _make_openai_mock(reply_content="US Politics"):
    """Return a mock AsyncOpenAI instance whose chat.completions.create coroutine
    resolves to a response with the given content string."""
    message = MagicMock()
    message.content = reply_content

    choice = MagicMock()
    choice.message = message

    response = MagicMock()
    response.choices = [choice]

    client = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=response)
    return client


def _run(coro):
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# classify_by_title — return value
# ---------------------------------------------------------------------------


def test_classify_by_title_returns_openai_reply():
    mock_client = _make_openai_mock("Finance")
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}), \
         patch("actur.categorize.AsyncOpenAI", return_value=mock_client):
        from actur import categorize
        result = _run(categorize.classify_by_title("Markets rally on inflation data"))
    assert result == "Finance"


def test_classify_by_title_returns_raw_reply_without_validation():
    """categorize makes no effort to validate the reply against the category list."""
    mock_client = _make_openai_mock("NotARealCategory")
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}), \
         patch("actur.categorize.AsyncOpenAI", return_value=mock_client):
        from actur import categorize
        result = _run(categorize.classify_by_title("anything"))
    assert result == "NotARealCategory"


def test_classify_by_title_returns_none_when_reply_is_none():
    """If the model returns None content, the function should return None."""
    mock_client = _make_openai_mock(None) # type: ignore
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}), \
         patch("actur.categorize.AsyncOpenAI", return_value=mock_client):
        from actur import categorize
        result = _run(categorize.classify_by_title("Some title"))
    assert result is None


# ---------------------------------------------------------------------------
# classify_by_title — API key handling
# ---------------------------------------------------------------------------


def test_classify_by_title_reads_api_key_from_config():
    mock_client = _make_openai_mock("Tech")
    openai_ctor = MagicMock(return_value=mock_client)
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}) as mock_conf, \
         patch("actur.categorize.AsyncOpenAI", openai_ctor):
        from actur import categorize
        _run(categorize.classify_by_title("New AI chip released"))
    mock_conf.assert_called_once_with("openai")


def test_classify_by_title_passes_api_key_to_async_openai():
    mock_client = _make_openai_mock("Tech")
    openai_ctor = MagicMock(return_value=mock_client)
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}), \
         patch("actur.categorize.AsyncOpenAI", openai_ctor):
        from actur import categorize
        _run(categorize.classify_by_title("New AI chip released"))
    openai_ctor.assert_called_once_with(api_key=_FAKE_KEY)


# ---------------------------------------------------------------------------
# classify_by_title — model and messages
# ---------------------------------------------------------------------------


def test_classify_by_title_uses_gpt4o_mini_model():
    mock_client = _make_openai_mock("Science")
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}), \
         patch("actur.categorize.AsyncOpenAI", return_value=mock_client):
        from actur import categorize
        _run(categorize.classify_by_title("CRISPR breakthrough"))
    call_kwargs = mock_client.chat.completions.create.call_args
    assert call_kwargs.kwargs["model"] == "gpt-4o-mini"


def test_classify_by_title_sends_two_messages():
    mock_client = _make_openai_mock("Health")
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}), \
         patch("actur.categorize.AsyncOpenAI", return_value=mock_client):
        from actur import categorize
        _run(categorize.classify_by_title("Vaccine trial results"))
    messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert len(messages) == 2


def test_classify_by_title_first_message_is_system():
    mock_client = _make_openai_mock("Health")
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}), \
         patch("actur.categorize.AsyncOpenAI", return_value=mock_client):
        from actur import categorize
        _run(categorize.classify_by_title("Vaccine trial results"))
    messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are a helpful assistant"


def test_classify_by_title_second_message_is_user():
    mock_client = _make_openai_mock("Health")
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}), \
         patch("actur.categorize.AsyncOpenAI", return_value=mock_client):
        from actur import categorize
        _run(categorize.classify_by_title("Vaccine trial results"))
    messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert messages[1]["role"] == "user"


def test_classify_by_title_user_message_contains_title():
    title = "Parliament votes on budget bill"
    mock_client = _make_openai_mock("UK Politics")
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}), \
         patch("actur.categorize.AsyncOpenAI", return_value=mock_client):
        from actur import categorize
        _run(categorize.classify_by_title(title))
    messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert title in messages[1]["content"]


def test_classify_by_title_user_message_contains_category_list():
    """Spot-check that several expected categories appear in the prompt."""
    mock_client = _make_openai_mock("War")
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}), \
         patch("actur.categorize.AsyncOpenAI", return_value=mock_client):
        from actur import categorize
        _run(categorize.classify_by_title("Conflict in border region"))
    user_content = mock_client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
    for category in ("US Politics", "Finance", "Climate", "War", "Other"):
        assert category in user_content, f"Expected category '{category}' in prompt"


def test_classify_by_title_user_message_instructs_reply_format():
    mock_client = _make_openai_mock("Sports")
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}), \
         patch("actur.categorize.AsyncOpenAI", return_value=mock_client):
        from actur import categorize
        _run(categorize.classify_by_title("World Cup final preview"))
    user_content = mock_client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
    assert "solely of category" in user_content


# ---------------------------------------------------------------------------
# classify_by_title — propagates exceptions
# ---------------------------------------------------------------------------


def test_classify_by_title_propagates_openai_error():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=RuntimeError("API timeout"))
    with patch("actur.categorize.get_conf_by_key", return_value={"secret_key": _FAKE_KEY}), \
         patch("actur.categorize.AsyncOpenAI", return_value=mock_client):
        from actur import categorize
        with pytest.raises(RuntimeError, match="API timeout"):
            _run(categorize.classify_by_title("Some title"))


def test_classify_by_title_propagates_config_error():
    with patch("actur.categorize.get_conf_by_key", side_effect=KeyError("openai")):
        from actur import categorize
        with pytest.raises(KeyError):
            _run(categorize.classify_by_title("Some title"))
