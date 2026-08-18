"""Routing tests for remote-first and local-fallback Ollama behavior."""

import pytest

from brain.llm.client import LLMDecision, LLMError
from brain.llm.router import LLMRouter, LLMRouterError


class FakeClient:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = 0

    def decide(self, command, context=""):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.result


def decision(text):
    return LLMDecision(
        tool="unknown_request",
        arguments={},
        response=text,
    )


def test_auto_prefers_remote():
    remote = FakeClient(result=decision("remote"))
    local = FakeClient(result=decision("local"))

    router = LLMRouter(remote_client=remote, local_client=local, mode="AUTO")
    result = router.decide("hello")

    assert result.response == "remote"
    assert remote.calls == 1
    assert local.calls == 0


def test_auto_falls_back_to_local_when_remote_fails():
    remote = FakeClient(error=LLMError("remote unavailable"))
    local = FakeClient(result=decision("local"))

    router = LLMRouter(remote_client=remote, local_client=local, mode="AUTO")
    result = router.decide("hello")

    assert result.response == "local"
    assert remote.calls == 1
    assert local.calls == 1


def test_remote_mode_does_not_fall_back():
    remote = FakeClient(error=LLMError("remote unavailable"))
    local = FakeClient(result=decision("local"))

    router = LLMRouter(remote_client=remote, local_client=local, mode="REMOTE")

    with pytest.raises(LLMError):
        router.decide("hello")

    assert remote.calls == 1
    assert local.calls == 0


def test_local_mode_uses_only_local():
    remote = FakeClient(result=decision("remote"))
    local = FakeClient(result=decision("local"))

    router = LLMRouter(remote_client=remote, local_client=local, mode="LOCAL")
    result = router.decide("hello")

    assert result.response == "local"
    assert remote.calls == 0
    assert local.calls == 1


def test_auto_reports_both_failures():
    remote = FakeClient(error=LLMError("remote unavailable"))
    local = FakeClient(error=LLMError("local unavailable"))

    router = LLMRouter(remote_client=remote, local_client=local, mode="AUTO")

    with pytest.raises(LLMRouterError, match="Both remote and local"):
        router.decide("hello")
