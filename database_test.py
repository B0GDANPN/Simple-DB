import io
import os

import database


def check(test_number: int):
    os.chdir(f"./tests/{test_number}")
    try:
        with open(f"./{test_number}.in", "r", encoding="utf-8") as inp, \
                open(f"./{test_number}.out", "r", encoding="utf-8") as out:

            result = io.StringIO("")
            database.solution(inp, f"{test_number}.db", result)

            result.seek(0)
            for expected_line in out:
                real_line = result.readline()
                assert real_line.strip() == expected_line.strip()

            assert not result.readline()
    finally:
        os.chdir("../..")


# check(16)


def test1():
    check(1)


def test2():
    check(2)


def test3():
    check(3)


def test4():
    check(4)


def test5():
    check(5)


def test6():
    check(6)


def test7():
    check(7)


def test8():
    check(8)


def test9():
    check(9)


def test10():
    check(10)


def test11():
    check(11)


def test12():
    check(12)


def test13():
    check(13)


def test14():
    check(14)


def test15():
    check(15)


def test16():
    check(16)


def test17():
    check(17)


def test18():
    check(18)


def test19():
    check(19)


def test20():
    check(20)


def test21():
    check(21)


def test22():
    check(22)


def test23():
    check(23)


def test24():
    check(24)


def test25():
    check(25)
