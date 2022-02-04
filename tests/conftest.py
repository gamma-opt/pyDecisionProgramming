import pytest


def pytest_addoption(parser):
    print("pytest_addoption")
    parser.addoption(
        "--gurobi", action="store_true", default=False,
        help="run tests that require Gurobi"
    )


def pytest_configure(config):
    print("pytest_configure")
    config.addinivalue_line("markers", "with_gurobi: mark test that require Gurobi")


def pytest_collection_modifyitems(config, items):
    print("pytest_collection_modifyitems")
    if not config.getoption("--gurobi"):
        skip_gurobi = pytest.mark.skip(reason="needs --gurobi")
        for item in items:
            if "with_gurobi" in item.keywords:
                item.add_marker(skip_gurobi)
