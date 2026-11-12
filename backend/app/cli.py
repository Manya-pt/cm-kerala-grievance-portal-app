"""Command line helpers. Run from the backend folder:

  python -m app.cli load-reference-data   # departments (same SQL as supabase/reference_data.sql)
  python -m app.cli create-cmo            # first CMO administrator (asks for a password)

They use DATABASE_URL from backend/.env, so they work for local SQLite and for Supabase.
"""
import argparse
import getpass
import sys
from pathlib import Path

from sqlalchemy import text

from . import create_app
from .models import User, db
from .validators import validate_account

SQL_DIR = Path(__file__).resolve().parents[2] / "supabase"


def run_sql_file(path):
    """Run a .sql file made of plain statements ending in ';' (comment lines ignored)."""
    lines = [ln for ln in Path(path).read_text(encoding="utf-8").splitlines()
             if not ln.strip().startswith("--")]
    for statement in "\n".join(lines).split(";"):
        if statement.strip():
            db.session.execute(text(statement))
    db.session.commit()


def create_cmo(name, email, mobile, password):
    errors = validate_account(name, email, mobile, password)
    if errors:
        return errors
    user = User(name=name, email=email, mobile=mobile, role="cmo")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return {}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("load-reference-data", help="insert the departments")
    cmo = sub.add_parser("create-cmo", help="create a CMO administrator")
    cmo.add_argument("--name", default="CMO Administrator")
    cmo.add_argument("--email", required=True)
    cmo.add_argument("--mobile", required=True)
    args = parser.parse_args(argv)

    app = create_app()
    with app.app_context():
        if args.command == "load-reference-data":
            run_sql_file(SQL_DIR / "reference_data.sql")
            print("Departments loaded.")
            return 0
        password = getpass.getpass("Password for the CMO account: ")
        errors = create_cmo(args.name, args.email.strip().lower(), args.mobile, password)
        if errors:
            print("Could not create the account:", *errors.values(), sep="\n  ")
            return 1
        print(f"CMO account created for {args.email}.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
