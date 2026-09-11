from datetime import datetime
from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKUP_DIR = PROJECT_ROOT / "data" / "db" / "backups"

BACKUP_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_file = BACKUP_DIR / f"war_analysis_{timestamp}.dump"

command = [
    "docker",
    "compose",
    "exec",
    "-T",
    "postgres",
    "sh",
    "-c",
    'pg_dump -Fc -U "$POSTGRES_USER" "$POSTGRES_DB"',
]

print(f"Creating database backup:")
print(f"  {backup_file}")

try:
    with backup_file.open("wb") as output:
        subprocess.run(
            command,
            stdout=output,
            check=True,
        )
except subprocess.CalledProcessError:
    if backup_file.exists():
        backup_file.unlink()

    print("Backup failed.")
    raise

size_mb = backup_file.stat().st_size / 1024 / 1024

print("Backup completed successfully.")
print(f"  File: {backup_file}")
print(f"  Size: {size_mb:.2f} MB")