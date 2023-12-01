import sys


def setup() -> None:
    try:
        path = sys.executable
        bin_dir = path.rsplit("/", 1)[0]
        main_executable_path = bin_dir + "/image_scan"
        with open(main_executable_path) as f:
            lines = f.readlines()

        new_lines = ["from app.cli.ela_nn.model import IMDModel\n"]
        new_lines.extend(lines)

        with open(main_executable_path, "w") as f:
            f.writelines(new_lines)
    except Exception:
        print("Error when setting up the `image_scan` script, `ela` subcommand will not work")
    else:
        print("Success")


if __name__ == "__main__":
    setup()
