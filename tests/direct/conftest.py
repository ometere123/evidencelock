import pytest

@pytest.fixture(autouse=True)
def harden_direct_vm(request):
    """Turn on GenLayer's two recommended Direct Mode safety checks everywhere."""
    if 'direct_vm' not in request.fixturenames:
        yield
        return
    vm=request.getfixturevalue('direct_vm')
    vm.strict_mocks=True
    vm.check_pickling=True
    yield
