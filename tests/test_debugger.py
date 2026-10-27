"""Unit tests for the Possessed Java Debugger (Phase 3)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ghostshell.client import CompletionResponse, GemmaClient, ModelServerError
from ghostshell.config import GhostConfig
from ghostshell.debugger import JavaDebugger, JavaDebugRequest, JavaDebugResult


@pytest.fixture
def mock_client() -> MagicMock:
    """Fixture providing a mocked GemmaClient."""
    client = MagicMock(spec=GemmaClient)
    client.endpoint = "http://127.0.0.1:9931/v1/chat/completions"
    client.model_name = "gemma-3-1b-it"
    return client


@pytest.fixture
def debugger(mock_client: MagicMock) -> JavaDebugger:
    """Fixture providing a JavaDebugger instance with a mocked client."""
    config = GhostConfig()
    return JavaDebugger(client=mock_client, config=config)


def test_debugger_empty_code(debugger: JavaDebugger) -> None:
    """Ensure empty code returns a graceful non-crashing result without calling the model."""
    req = JavaDebugRequest(code="   ")
    res = debugger.analyze(req)

    assert isinstance(res, JavaDebugResult)
    assert res.is_ambiguous is True
    assert "No Java code was submitted" in res.root_cause
    assert res.execution_sandboxed is True


def test_debugger_fragment_ambiguity(debugger: JavaDebugger) -> None:
    """Ensure isolated fragment returns an ambiguity warning asking for context."""
    req = JavaDebugRequest(code="}")
    res = debugger.analyze(req)

    assert isinstance(res, JavaDebugResult)
    assert res.is_ambiguous is True
    assert "incomplete" in res.root_cause.lower()
    assert res.missing_context is not None


def test_debugger_successful_5_section_parsing(
    debugger: JavaDebugger,
    mock_client: MagicMock,
) -> None:
    """Verify standard response correctly parses all 5 required sections."""
    mock_response_text = """### 👻 Ghost's Whisper
The null pointer demon has stolen your object reference in the dark.

### Root Cause
NullPointerException at line 14 because `userList` was declared but never initialized before invoking `.add()`.

### Corrected Code
```java
List<String> userList = new ArrayList<>();
userList.add("Gemma");
```

### Explanation
Instantiating the ArrayList allocates the backing memory, allowing elements to be added without dereferencing null.

### Verification
Instantiate the class and invoke the method with test strings. Verify no NullPointerException is thrown.
"""
    mock_client.chat_completion.return_value = CompletionResponse(
        content=mock_response_text,
        model="gemma-3-1b-it",
        prompt_tokens=40,
        completion_tokens=85,
        total_tokens=125,
        latency_ms=110.0,
    )

    req = JavaDebugRequest(
        code="userList.add(\"Gemma\");",
        error_message="Exception in thread \"main\" java.lang.NullPointerException",
    )
    result = debugger.analyze(req)

    assert result.whisper == "The null pointer demon has stolen your object reference in the dark."
    assert "NullPointerException" in result.root_cause
    assert "new ArrayList<>()" in result.corrected_code
    assert "allocates the backing memory" in result.explanation
    assert "Instantiate the class" in result.verification
    assert result.tokens == 125
    assert result.latency_ms == 110.0
    assert result.execution_sandboxed is True


def test_debugger_incorrect_loop_increment_detection(
    debugger: JavaDebugger,
    mock_client: MagicMock,
) -> None:
    """Acceptance Test B & Requirement 6: Diagnose incorrect loop increment (row++ instead of col++)."""
    loop_code = """
for (int row = 1; row <= 5; row++) {
    for (int col = 1; col <= row; row++) {
        System.out.print("* ");
    }
    System.out.println();
}
"""
    mock_gemma_loop_response = """### 👻 Ghost's Whisper
Your loop is caught in an eternal spectral loop, incrementing the master instead of the apprentice.

### Root Cause
Wrong variable incremented in inner loop: `row++` was used instead of `col++`. The loop variable `col` remains 1 forever while `row` grows indefinitely.

### Corrected Code
```java
for (int row = 1; row <= 5; row++) {
    for (int col = 1; col <= row; col++) {
        System.out.print("* ");
    }
    System.out.println();
}
```

### Explanation
In the inner loop header `for (int col = 1; col <= row; row++)`, `row` was incremented rather than `col`. Because `col` never increases, `col <= row` stays perpetually true, resulting in an infinite loop. Changing it to `col++` ensures the column index terminates once it reaches `row`.

### Verification
Run the pattern printing loop and verify that a triangle with 5 rows (1 to 5 asterisks) prints and exits cleanly.
"""
    mock_client.chat_completion.return_value = CompletionResponse(
        content=mock_gemma_loop_response,
        model="gemma-3-1b-it",
        prompt_tokens=65,
        completion_tokens=140,
        total_tokens=205,
        latency_ms=135.0,
    )

    req = JavaDebugRequest(code=loop_code)
    result = debugger.analyze(req)

    assert "eternal spectral loop" in result.whisper
    assert "row++" in result.root_cause
    assert "col++" in result.root_cause or "col++" in result.explanation
    assert "col++" in result.corrected_code
    assert "infinite loop" in result.explanation.lower()
    assert result.execution_sandboxed is True


def test_debugger_server_offline_fallback(
    debugger: JavaDebugger,
    mock_client: MagicMock,
) -> None:
    """Requirement 12: Handle unavailable servers with clear offline guidance."""
    mock_client.chat_completion.side_effect = ModelServerError(
        message="Connection refused",
        is_offline=True,
        endpoint="http://127.0.0.1:9931/v1/chat/completions",
    )

    req = JavaDebugRequest(code="for (int col = 1; col <= row; row++) {}")
    result = debugger.analyze(req)

    assert result.status == "CONDUIT_SEVERED"
    assert "unreachable" in result.root_cause.lower()
    assert "llama-server" in result.explanation
    assert "9931" in result.explanation
    # Verify offline heuristic caught the loop increment bug even with server down!
    assert "col++" in result.corrected_code


def test_debugger_malformed_response_fallback(
    debugger: JavaDebugger,
    mock_client: MagicMock,
) -> None:
    """Verify fallback parser when Gemma omits standard headers."""
    raw_unformatted = """Here is the fix for your array error:
```java
int[] arr = new int[5];
arr[0] = 10;
```
You attempted to access an out-of-bounds index."""

    mock_client.chat_completion.return_value = CompletionResponse(
        content=raw_unformatted,
        model="gemma-3-1b-it",
        prompt_tokens=20,
        completion_tokens=30,
        total_tokens=50,
        latency_ms=80.0,
    )

    req = JavaDebugRequest(code="arr[10] = 10;")
    result = debugger.analyze(req)

    assert result.whisper is not None
    assert "new int[5]" in result.corrected_code
    assert result.root_cause is not None
    assert result.verification is not None
