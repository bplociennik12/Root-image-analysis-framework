from shared.logging_utils import utc_timestamp


def make_audit_event(
    *,
    record_id,
    image_id="",
    image_name="",
    sample_id="",
    step,
    rule_id,
    rule_description,
    input_value="",
    output_value="",
    action,
    status,
    reason,
    message,
) -> dict:
    return {
        "timestamp": utc_timestamp(),
        "record_id": record_id,
        "image_id": image_id,
        "image_name": image_name,
        "sample_id": sample_id,
        "step": step,
        "rule_id": rule_id,
        "rule_description": rule_description,
        "input_value": input_value,
        "output_value": output_value,
        "action": action,
        "status": status,
        "reason": reason,
        "message": message,
    }
