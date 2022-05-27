import src.LoggingUtilities

def test_cull_logs():
    initial_string = "test1 \n test2 \n test3 \n test4"

    Expected = " test2 \n test3 \n test4"

    Result = src.LoggingUtilities.cap_log_string_length_in_lines(initial_string, 3)

    assert Result == Expected