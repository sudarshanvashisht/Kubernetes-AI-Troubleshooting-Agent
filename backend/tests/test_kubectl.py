import pytest
from app.kubernetes.kubectl import validate_namespace, validate_context, ValidationError


@pytest.mark.parametrize("ns", ["default", "kube-system", "a"])
def test_namespace_valid(ns):
    assert validate_namespace(ns) == ns


def test_namespace_empty_allowed():
    assert validate_namespace(None) is None
    assert validate_namespace("") is None


@pytest.mark.parametrize("ns", ["Default", "x;", "x; id", "$(id)", "../../etc", "--server=x", "a b", "a" * 64, "1" + "a" * 63])
def test_namespace_invalid(ns):
    with pytest.raises(ValidationError):
        validate_namespace(ns)


def test_context_valid():
    assert validate_context("kind-cluster") == "kind-cluster"
    assert validate_context(None) is None


@pytest.mark.parametrize("ctx", ["x; id", "$(id)", "../../etc", "a b", "x" * 254, "--server=x"])
def test_context_invalid(ctx):
    with pytest.raises(ValidationError):
        validate_context(ctx)
