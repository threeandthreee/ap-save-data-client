import os
import shutil
import subprocess

# Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_ROOT = os.path.join(BASE_DIR, "src")
LIBS_DEST_DIR = os.path.join(SRC_ROOT, "libs")
LIBS_CLONE_DIR = os.path.join(BASE_DIR, "libs")

# Repos and source subdirs
REPOS = {
    "wsproto": {
        "repo_url": "https://github.com/python-hyper/wsproto.git",
        "source_subdir": os.path.join("src", "wsproto")
    },
    "h11": {
        "repo_url": "https://github.com/python-hyper/h11.git",
        "source_subdir": "h11"
    },
    "certifi": {
        "repo_url": "https://github.com/certifi/python-certifi.git",
        "source_subdir": "certifi"
    }
}

# Unwanted files/directories to prune
JUNK_DIRS = {'tests', 'test', 'testing', '__pycache__', 'docs', 'examples', 'build', 'dist'}
JUNK_FILES = {'.c', '.h', '.so', '.pyd', '.dll', '.lib', 'setup.py', 'setup.cfg', 'Makefile', 'CMakeLists.txt'}

def clone_repo(name, url):
    dest = os.path.join(LIBS_CLONE_DIR, name)
    if not os.path.exists(dest):
        print(f"Cloning {name}...")
        subprocess.run(["git", "clone", "--depth=1", url, dest], check=True)
    else:
        print(f"{name} already cloned. Skipping.")

    # Remove .git folder
    git_dir = os.path.join(dest, ".git")
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir)
    return dest

def remove_junk(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for d in dirs:
            if d in JUNK_DIRS:
                full_path = os.path.join(root, d)
                print(f"Removing directory: {full_path}")
                shutil.rmtree(full_path, ignore_errors=True)
        for f in files:
            if f.endswith(tuple(JUNK_FILES)) or f in JUNK_FILES:
                full_path = os.path.join(root, f)
                print(f"Removing file: {full_path}")
                os.remove(full_path)

def copy_source(name, source_dir):
    source_path = os.path.join(LIBS_CLONE_DIR, name, source_dir)
    dest_path = os.path.join(LIBS_DEST_DIR, name)

    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source not found: {source_path}")

    print(f"Copying {name} to {dest_path}")
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)

    shutil.copytree(source_path, dest_path)
    remove_junk(dest_path)

def prepare():
    os.makedirs(LIBS_DEST_DIR, exist_ok=True)
    os.makedirs(LIBS_CLONE_DIR, exist_ok=True)

    for name, config in REPOS.items():
        clone_repo(name, config["repo_url"])
        copy_source(name, config["source_subdir"])

    print("\nCleaning up cloned repos...")
    shutil.rmtree(LIBS_CLONE_DIR)

    print("\n✅ All libraries bundled in src/libs/")

if __name__ == "__main__":
    prepare()
