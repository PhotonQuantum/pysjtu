import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-cuda", action="store_true", default=False, help="run tests requiring a CUDA device"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "cuda: mark test as requiring a CUDA device to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-cuda"):
        return
    cuda = pytest.mark.skip(reason="need --run-cuda option to run")
    for item in items:
        if "cuda" in item.keywords:
            item.add_marker(cuda)
