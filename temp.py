import os
import sys
import subprocess
import importlib.util

def is_tensorflow_shadowed():
    try:
        import tensorflow
        tf_path = tensorflow.__file__
        print(f"[INFO] TensorFlow is being imported from: {tf_path}")
        cwd = os.getcwd()
        if cwd in tf_path or "OneDrive" in tf_path:
            print("[WARNING] TensorFlow is shadowed by a local file.")
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Couldn't import TensorFlow: {e}")
        return True

def uninstall_tensorflow():
    print("\n[INFO] Uninstalling TensorFlow and related packages...")
    packages = [
        "tensorflow", "tensorflow-cpu", "tensorflow-gpu",
        "keras", "keras-nightly", "keras-preprocessing"
    ]
    for pkg in packages:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", pkg])

def delete_site_packages_residue():
    print("\n[INFO] Scanning site-packages for TensorFlow/keras remnants...")
    import site
    folders = [
        "tensorflow", "tensorflow_core", "keras", "keras_preprocessing"
    ]
    for path in site.getsitepackages():
        for folder in folders:
            full_path = os.path.join(path, folder)
            if os.path.exists(full_path):
                print(f"[DELETE] {full_path}")
                try:
                    if os.path.isdir(full_path):
                        subprocess.run(["rmdir", "/S", "/Q", full_path], shell=True)
                    else:
                        os.remove(full_path)
                except Exception as e:
                    print(f"[ERROR] Failed to delete {full_path}: {e}")

def delete_local_tf_files():
    print("\n[INFO] Checking current directory for tensorflow.py or __pycache__...")
    suspicious_files = ["tensorflow.py", "tensorflow.pyc", "__pycache__"]
    deleted = False
    for f in suspicious_files:
        if os.path.exists(f):
            try:
                if os.path.isdir(f):
                    subprocess.run(["rmdir", "/S", "/Q", f], shell=True)
                else:
                    os.remove(f)
                print(f"[DELETE] Removed: {f}")
                deleted = True
            except Exception as e:
                print(f"[ERROR] Could not remove {f}: {e}")
    return deleted

if __name__ == "__main__":
    print("=== TensorFlow Cleanup Utility ===\n")

    shadowed = is_tensorflow_shadowed()
    local_deleted = delete_local_tf_files()

    if shadowed or local_deleted:
        uninstall_tensorflow()
        delete_site_packages_residue()
        print("\n[DONE] Cleanup completed. Now reinstall with:")
        print("    pip install tensorflow==2.16.1\n")
    else:
        print("\n[INFO] No shadowing or local tensorflow.py detected.")
        print("If the error persists, consider using a virtual environment:\n")
        print("    python -m venv venv")
        print("    venv\\Scripts\\activate")
        print("    pip install tensorflow==2.16.1\n")
