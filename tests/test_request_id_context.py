import re
from utils import request_id_context as rc

def test_request_id_lifecycle():
    # Set and get
    rid = rc.set_request_id()
    assert re.match(r"^[a-f0-9\-]{36}$", rid)
    assert rc.get_request_id() == rid

    # Clear resets
    rc.clear_request_id()
    assert rc.get_request_id() == "-"
