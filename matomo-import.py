import subprocess
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class MatomoProject:
    name: str
    idSite: int
    urls: list[str]


@dataclass
class MatomoAPIConf:
    projects: list[MatomoProject]


def load():
    with open("matomo.toml", "rb") as f:
        data = tomllib.load(f)
        projects = []
        for p in data.get("project", []):
            projects.append(
                MatomoProject(
                    name=p["name"],
                    idSite=p["idSite"],
                    urls=p["urls"]
                )
            )
        return MatomoAPIConf(projects=projects)


def gen_idsite_host_path(conf: MatomoAPIConf):
    d: dict[str, dict[str, list[str]]] = {}
    for project in conf.projects:
        dsite: dict[str, list[str]] = d.setdefault(project.idSite, {})
        for url in project.urls:
            pu = urlparse(url)
            path = pu.path if pu.path.endswith("*") else pu.path + "*"
            dsite.setdefault(pu.netloc, []).append(path)

    for idSite, value in d.items():
        for host, paths in value.items():
            for path in paths:
                yield idSite, host, path


def main():
    conf = load()

    # Run import_logs.py for each host
    for idSite, host, path in gen_idsite_host_path(conf):
        command = [
            "python",
            "import_logs.py",
            "--idsite", str(idSite),
            "--hostname", host,
            "--include-path",
            f"\"{path}\"",
            *sys.argv[1:],
        ]
        print("\n\n---------------------------------------------------------------------------------------------------")
        print("# ", " ".join(command))
        subprocess.run(
            command,
            capture_output=False,
            text=True,
            encoding="utf-8",
            check=True,
            shell=False,
        )


if __name__ == "__main__":
    main()
