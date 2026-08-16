from gateway.response_filters import (
    is_autonomous_silence_response,
    is_intentional_silence_agent_result,
    is_intentional_silence_response,
    strip_file_mutation_verifier_footer,
)


VERIFIER_FOOTER = (
    "⚠️ File-mutation verifier: 2 file(s) were NOT modified this turn despite "
    "any wording above that may suggest otherwise. Run `git status` or "
    "`read_file` to confirm.\n"
    "  • `/tmp/a` — [patch] failed\n"
    "  • `/tmp/b` — [patch] failed"
)


def test_exact_silence_tokens_are_intentional_silence():
    for token in ("[SILENT]", " SILENT ", "NO_REPLY", "no reply"):
        assert is_intentional_silence_response(token)


def test_silence_token_stays_silent_when_finalizer_appends_verifier_footer():
    assert is_intentional_silence_response("NO_REPLY\n\n" + VERIFIER_FOOTER)


def test_verifier_footer_is_removed_without_suppressing_substantive_reply():
    response = "The requested fix is live.\n\n" + VERIFIER_FOOTER
    assert strip_file_mutation_verifier_footer(response) == "The requested fix is live."
    assert not is_intentional_silence_response(response)


def test_verifier_heading_in_legitimate_prose_is_preserved():
    responses = (
        "⚠️ File-mutation verifier: this phrase names a Hermes subsystem.",
        (
            "Legitimate answer.\n"
            "⚠️ File-mutation verifier: this heading is quoted for discussion.\n"
            "The conclusion remains visible."
        ),
        (
            "⚠️ File-mutation verifier: 2 file(s) were NOT modified this turn despite "
            "any wording above that may suggest otherwise. Run `git status` or "
            "`read_file` to confirm."
        ),
    )
    for response in responses:
        assert strip_file_mutation_verifier_footer(response) == response


def test_autonomous_silence_accepts_marker_with_own_line_note():
    """The loose rule for cron/webhook lanes: marker + explanation suppresses."""
    assert is_autonomous_silence_response("[SILENT]")
    assert is_autonomous_silence_response("[SILENT]\n\nNothing new this tick.")
    assert is_autonomous_silence_response("2 deals filtered\n\n[SILENT]")
    assert is_autonomous_silence_response("no_reply\nduplicate inbound, already handled")
    assert is_autonomous_silence_response("[SILENT] No changes detected")


