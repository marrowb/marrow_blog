import click
import pyotp  # Uncomment if using pyotp for MFA
from flask.cli import AppGroup

from marrow_blog.blueprints.admin.models import AdminUser
from marrow_blog.extensions import db

admin_cli = AppGroup("admin", help="Manage admin users.")


@admin_cli.command("create")
@click.option("--username", prompt=True, help="The username for the admin.")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="The password for the admin.",
)
@click.option(
    "--enable-mfa", is_flag=True, help="Enable MFA for the admin user."
)
def create_admin(username, password, enable_mfa):
    """Creates or updates the admin user."""
    user = AdminUser.query.filter_by(username=username).first()
    if user:
        click.echo(
            f"Admin user '{username}' already exists. Updating password and MFA status."
        )
    else:
        user = AdminUser(username=username)
        db.session.add(user)
        click.echo(f"Creating admin user '{username}'.")

    user.set_password(password)

    if enable_mfa:
        user.mfa_secret = pyotp.random_base32()  # Uncomment for pyotp
        provisioning_uri = pyotp.TOTP(user.mfa_secret).provisioning_uri(
            name=user.username, issuer_name="MarrowBlog"
        )
        click.echo(f"MFA enabled for {username}.")
        click.echo(
            "Scan this QR code with your authenticator app (or enter secret manually):"
        )
        click.echo(f"Secret: {user.mfa_secret}")
        click.echo(
            f"URI: {provisioning_uri}"
        )  # You might want to use a QR code library to display this
        # user.mfa_secret = "PLACEHOLDER_MFA_SECRET" # Placeholder
        # click.echo(f"MFA enabled for {username}. (Placeholder secret: {user.mfa_secret})")
    else:
        user.mfa_secret = None
        click.echo(f"MFA disabled for {username}.")

    db.session.commit()
    click.echo(f"Admin user '{username}' processed successfully.")


def init_app(app):
    app.cli.add_command(admin_cli)
