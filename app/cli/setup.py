import sys


def setup() -> None:
    try:
        path = sys.executable
        bin_dir = path.rsplit("/", 1)[0]
        main_executable_path = bin_dir + "/image_scan"
        with open(main_executable_path) as f:
            lines = f.readlines()
        lines[3] = "from app.cli.ela_nn.model import IMDModel\n"

        with open(main_executable_path, "w") as f:
            f.writelines(lines)
    except Exception:
        print("Error when setting up the `image_scan` script, `ela` subcommand will not work")
    else:
        print("Success")


if __name__ == "__main__":
    setup()
