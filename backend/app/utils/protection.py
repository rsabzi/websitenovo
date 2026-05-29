from __future__ import annotations
from pathlib import Path

# Directories and files that indicate a programming project or system folder
PROTECTED_PATTERNS = {
    "node_modules",
    ".git",
    ".svn",
    ".hg",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".next",
    ".nuxt",
    "dist",
    "build",
    "target",  # Rust
    "bin",     # .NET/Java
    "obj",     # .NET
    ".idea",
    ".vscode",
    ".bolt",
}

PROTECTED_FILES = {
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "requirements.txt",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "Makefile",
    "CMakeLists.txt",
    ".gitignore",
    ".env",
}

def is_protected(path: Path) -> bool:
    """
    Checks if a path or any of its parent directories are part of a 
    programming project or contain sensitive system/library files.
    """
    try:
        # Check if the file itself is a protected project file
        if path.name in PROTECTED_FILES:
            return True
            
        # Check all parent directories for protected patterns
        # We stop checking once we reach the root or a watched folder limit (handled by caller)
        for part in path.parts:
            if part in PROTECTED_PATTERNS:
                return True
                
        return False
    except Exception:
        return True # Default to protected if we can't determine
