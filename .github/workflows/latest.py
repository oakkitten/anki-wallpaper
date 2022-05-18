import subprocess
import shlex
import re
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


def log(*args):
    print(*args, file=sys.stderr)


def run(command: str) -> str:
    return (
        subprocess.run(shlex.split(command), capture_output=True, check=True)
                  .stdout
                  .decode()
    )


def last_bit(version: str) -> str:
    return version.split(".")[-1]


def remove_two_edge_newlines(text: str) -> str:
    if text.startswith("\n"):
        text = text[1:]
    if text.endswith("\n"):
        text = text[:-1]
    return text


@dataclass
class File:
    contents: str

    # Inserts into `text` before line that matches `line_re`, additional lines.
    # These lines are dedented and then inserted on the same level as the matched line.
    # One leading and one trailing newlines of addition, if any, are removed.
    def insert_before_line(self, line_re: str, addition: str):
        lines = []
        for line in self.contents.split("\n"):
            if re.search(line_re, line):
                leading_spaces = len(line) - len(line.lstrip())
                for new_line in remove_two_edge_newlines(dedent(addition)).split("\n"):
                    if new_line.strip():
                        lines.append(" " * leading_spaces + new_line)
                    else:
                        lines.append("")
            lines.append(line)
        self.contents = "\n".join(lines)


@contextmanager
def editing(file_name) -> File:
    file_path = Path(file_name)
    file = File(file_path.read_text())
    yield file
    file_path.write_text(file.contents)


########################################################################################


def update_prerelease(tox_ini: File, main_yml: File, version):
    if re.search(fr"ankilatest: anki=={version}\b", tox_ini.contents):
        exit(1)
    else:
        log(f":: updating pre-release test environment with Anki {version}")

        tox_ini.contents = re.sub(
            r"ankilatest: (anki|aqt\[qt6])==\d+\.\d+\.[a-z0-9]+",
            fr"ankilatest: \1=={version}",
            tox_ini.contents
        )

        main_yml.contents = re.sub(
            r"Latest Anki \(\d+\.\d+\.[a-z0-9]+\)",
            fr"Latest Anki ({version})",
            main_yml.contents
        )


########################################################################################


def add_stable(tox_ini: File, main_yml: File, version):
    if re.search(fr"}}: anki=={version}\b", tox_ini.contents):
        exit(1)
    else:
        log(f":: adding new stable test environment with Anki {version}")

        tag = last_bit(version)

        tox_ini.insert_before_line(
            "py39-ankilatest",
            f"py39-anki{tag}qt{{5,6}}"
        )

        tox_ini.insert_before_line(
            "ankilatest: anki==",
            f"""
            anki{tag}qt{{5,6}}: anki=={version}
            anki{tag}qt5: aqt[qt5]=={version}
            anki{tag}qt6: aqt[qt6]=={version}\n
            """
        )

        main_yml.insert_before_line(
            "name: Latest Anki",
            f"""
            - name: Anki {version} (Qt5)
              python: 3.9
              environment: py39-anki{tag}qt5
            - name: Anki {version} (Qt6)
              python: 3.9
              environment: py39-anki{tag}qt6
            """
        )


########################################################################################


def upgrade():
    with editing("tox.ini") as tox_ini, editing(".github/workflows/main.yml") as main_yml:
        if sys.argv[1] == "update-prerelease":
            update_prerelease(tox_ini, main_yml, sys.argv[2])
        elif sys.argv[1] == "add-stable":
            add_stable(tox_ini, main_yml, sys.argv[2])
        else:
            exit(2)


if __name__ == "__main__":
    upgrade()
