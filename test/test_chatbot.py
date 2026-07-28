import pytest
from unittest.mock import patch, MagicMock


class _AttrDict(dict):
    """Mimic Streamlit session_state: supports ``\"key\" in state`` and ``state.messages``."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(key) from e

    def __setattr__(self, key, value):
        self[key] = value


from modules import chatbot as app


def test_get_response_keywords():
    response = app.get_response("I feel dizzy")
    # Response uses "dizziness", which does not contain the substring "dizzy".
    assert "dizziness" in response.lower()

def test_detect_sentiment():
    label, style = app.detect_sentiment("I feel healthy and great")
    assert label == "😊 Positive"


def test_detect_sentiment_concerned_when_negative_dominates():
    label, _ = app.detect_sentiment("I feel sick and awful and in pain")
    assert label == "😔 Concerned"


def test_detect_sentiment_neutral():
    label, _ = app.detect_sentiment("The weather is cloudy today")
    assert label == "😐 Neutral"


@pytest.mark.parametrize(
    "text, expected_state",
    [
        ("I feel stressed at work", "Stress"),
        ("panic attack last night", "Anxiety"),
        ("I feel hopeless", "Depressive mood"),
        ("just checking symptoms", "No clear emotional distress detected"),
    ],
)
def test_detect_emotional_state(text, expected_state):
    assert app.detect_emotional_state(text) == expected_state


@pytest.mark.parametrize(
    "user_input, expected_substring",
    [
        ("hello there", "nlp-medora"),
        ("I have a migraine", "headache"),
        ("bye for now", "goodbye"),
        ("unknown xyz symptom zzz", "i'm not sure"),
    ],
)
def test_get_response_routed_topics(user_input, expected_substring):
    out = app.get_response(user_input).lower()
    assert expected_substring in out

@patch("streamlit.chat_input")
@patch("streamlit.chat_message")
@patch("streamlit.session_state", new_callable=_AttrDict)
def test_chatbot_ui_no_crash(mock_session, mock_message, mock_input):
    """
    Session state must support both dict checks (``\"messages\" in st.session_state``)
    and attribute access (``st.session_state.messages``).
    """
    mock_input.return_value = "Hello"

    try:
        app.show()
    except Exception as e:
        pytest.fail(f"Chatbot UI crashed: {e}")

def test_session_history_logic():
    """Verify that messages are correctly appended to the history list."""
    mock_history = []
    # Logic simulation
    prompt = "I have a headache"
    mock_history.append({"role": "user", "content": prompt})
    
    response = app.get_response(prompt)
    mock_history.append({"role": "assistant", "content": response})
    
    assert len(mock_history) == 2
    assert "rest" in mock_history[1]["content"].lower()