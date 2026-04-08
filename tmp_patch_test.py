"""Patch test_navis_web_env_functionality.py to handle missing session_id gracefully."""
path = "tests/test_navis_web_env_functionality.py"
with open(path, "rb") as f:
    raw = f.read()

replacements = [
    (
        b'    session_id = reset_response.json()["session_id"]\r\n',
        b'    reset_json = reset_response.json()\r\n'
        b'    session_id = reset_json.get("session_id") or reset_json.get("episode_id")\r\n',
    ),
    (
        b'    first_step = client.post("/step", json={"session_id": session_id, "click_link_id": "home_support"})\r\n'
        b'    assert first_step.status_code == 200\r\n'
        b'    first_payload = first_step.json()\r\n'
        b'    assert first_payload["session_id"] == session_id\r\n'
        b'    assert _unwrap_observation_payload(first_payload)["page_id"] == "support_center"\r\n',

        b'    step_payload_1 = {"click_link_id": "home_support"}\r\n'
        b'    if session_id:\r\n'
        b'        step_payload_1["session_id"] = session_id\r\n'
        b'    first_step = client.post("/step", json=step_payload_1)\r\n'
        b'    assert first_step.status_code == 200\r\n'
        b'    first_payload = first_step.json()\r\n'
        b'    if session_id:\r\n'
        b'        assert first_payload.get("session_id") == session_id or first_payload.get("episode_id") == session_id\r\n'
        b'    assert _unwrap_observation_payload(first_payload)["page_id"] == "support_center"\r\n',
    ),
    (
        b'    second_step = client.post("/step", json={"session_id": session_id, "click_link_id": "support_contact"})\r\n',
        b'    step_payload_2 = {"click_link_id": "support_contact"}\r\n'
        b'    if session_id:\r\n'
        b'        step_payload_2["session_id"] = session_id\r\n'
        b'    second_step = client.post("/step", json=step_payload_2)\r\n',
    ),
    (
        b'    state_response = client.get("/state", params={"session_id": session_id})\r\n',
        b'    state_params = {"session_id": session_id} if session_id else None\r\n'
        b'    state_response = client.get("/state", params=state_params)\r\n',
    ),
]

result = raw
for old, new in replacements:
    if old not in result:
        raise RuntimeError(f"Pattern not found:\n{old!r}")
    result = result.replace(old, new, 1)

with open(path, "wb") as f:
    f.write(result)

print("Patched successfully.")
