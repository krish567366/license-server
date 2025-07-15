"""Main CLI application using Typer."""

import sys
from pathlib import Path
from typing import List, Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
import json
import webbrowser
import subprocess
import tempfile
import shutil

from ..core.license_manager import LicenseManager
from ..core.validation import check_license_status, is_development_mode
from ..core.usage_tracker import UsageTracker
from ..core.hardware import get_machine_id
from ..core.encryption import LicenseSignature

app = typer.Typer(
    name="quantum-license",
    help="QuantumMeta License Manager - Universal licensing system for QuantumMeta ecosystem",
    add_completion=False
)
console = Console()

# Admin commands subgroup
admin_app = typer.Typer(help="Admin commands for license management")
app.add_typer(admin_app, name="admin")


@app.command()
def generate(
    package: str = typer.Option(..., "--package", "-p", help="Package name to license"),
    user: str = typer.Option(..., "--user", "-u", help="User email or ID"),
    output: str = typer.Option(..., "--output", "-o", help="Output license file path"),
    features: str = typer.Option("core", "--features", "-f", help="Comma-separated list of features"),
    validity_days: int = typer.Option(365, "--days", "-d", help="License validity in days"),
    machine_id: Optional[str] = typer.Option(None, "--machine-id", "-m", help="Target machine ID (default: current machine)"),
    sign: bool = typer.Option(False, "--sign", "-s", help="Sign the license with Ed25519"),
):
    """Generate a new license file (admin use)."""
    try:
        license_manager = LicenseManager()
        
        # Parse features
        feature_list = [f.strip() for f in features.split(",") if f.strip()]
        
        # Generate signing key if requested
        private_key_bytes = None
        if sign:
            private_key_bytes, public_key_bytes = LicenseSignature.generate_keypair()
            rprint("[yellow]Generated Ed25519 keypair for signing[/yellow]")
            
            # Save public key for reference
            pub_key_file = Path(output).with_suffix('.pub')
            with open(pub_key_file, 'wb') as f:
                f.write(public_key_bytes)
            rprint(f"[green]Public key saved to: {pub_key_file}[/green]")
        
        # Create license
        license_data = license_manager.create_license(
            package=package,
            user=user,
            machine_id=machine_id,
            features=feature_list,
            validity_days=validity_days,
            private_key_bytes=private_key_bytes
        )
        
        # Save license file
        license_manager.save_license_file(license_data, output)
        
        rprint(f"[green]✅ License generated successfully: {output}[/green]")
        
        # Display license info
        table = Table(title="License Details")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Package", license_data["package"])
        table.add_row("User", license_data["user"])
        table.add_row("Machine ID", license_data["machine_id"])
        table.add_row("Issued", license_data["issued"])
        table.add_row("Expires", license_data["expires"])
        table.add_row("Features", ", ".join(license_data["features"]))
        table.add_row("Signed", "Yes" if sign else "No")
        
        console.print(table)
        
    except Exception as e:
        rprint(f"[red]❌ Error generating license: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def activate(
    license_file: str = typer.Argument(..., help="Path to the license file to activate")
):
    """Activate a license by installing it to the system."""
    try:
        license_path = Path(license_file)
        
        if not license_path.exists():
            rprint(f"[red]❌ License file not found: {license_file}[/red]")
            raise typer.Exit(1)
        
        license_manager = LicenseManager()
        
        if license_manager.activate_license(str(license_path)):
            rprint(f"[green]✅ License activated successfully![/green]")
            
            # Show activated license info
            from ..core.encryption import LicenseEncryption
            license_data = LicenseEncryption.read_license_file(str(license_path))
            
            rprint(f"[cyan]Package:[/cyan] {license_data['package']}")
            rprint(f"[cyan]User:[/cyan] {license_data['user']}")
            rprint(f"[cyan]Expires:[/cyan] {license_data['expires']}")
            rprint(f"[cyan]Features:[/cyan] {', '.join(license_data['features'])}")
        else:
            rprint(f"[red]❌ Failed to activate license[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        rprint(f"[red]❌ Error activating license: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def validate(
    package: str = typer.Argument(..., help="Package name to validate"),
    features: Optional[str] = typer.Option(None, "--features", "-f", help="Required features (comma-separated)")
):
    """Validate license for a specific package."""
    try:
        # Parse required features
        required_features = None
        if features:
            required_features = [f.strip() for f in features.split(",") if f.strip()]
        
        # Get license status
        status_info = check_license_status(package)
        
        # Create status panel
        if status_info["status"] == "development_mode":
            panel = Panel(
                "[yellow]🚧 Development Mode Active[/yellow]\n"
                "All license checks are bypassed.",
                title="License Status",
                border_style="yellow"
            )
        elif status_info["status"] == "licensed":
            license_info = status_info["license_info"]
            panel_content = (
                f"[green]✅ Valid License Found[/green]\n"
                f"User: {license_info['user']}\n"
                f"Issued: {license_info['issued']}\n"
                f"Expires: {license_info['expires']}\n"
                f"Features: {', '.join(license_info['features'])}"
            )
            
            # Check required features
            if required_features:
                missing = []
                for feature in required_features:
                    if feature not in license_info['features']:
                        missing.append(feature)
                
                if missing:
                    panel_content += f"\n[red]❌ Missing features: {', '.join(missing)}[/red]"
                else:
                    panel_content += f"\n[green]✅ All required features available[/green]"
            
            panel = Panel(panel_content, title=f"License Status - {package}", border_style="green")
            
        elif status_info["status"] == "grace_period":
            grace_info = status_info["grace_info"]
            panel_content = (
                f"[yellow]⏳ Grace Period Active[/yellow]\n"
                f"First use: {grace_info['first_use']}\n"
                f"Expires: {grace_info['expiry_date']}\n"
                f"Days remaining: {grace_info['days_remaining']}\n"
                f"Hours remaining: {grace_info['hours_remaining']}"
            )
            panel = Panel(panel_content, title=f"License Status - {package}", border_style="yellow")
            
        elif status_info["status"] == "expired":
            grace_info = status_info["grace_info"]
            panel_content = (
                f"[red]❌ Grace Period Expired[/red]\n"
                f"Expired on: {grace_info['expiry_date']}\n"
                f"Please activate a valid license."
            )
            panel = Panel(panel_content, title=f"License Status - {package}", border_style="red")
            
        else:  # invalid_license
            license_info = status_info["license_info"]
            panel_content = (
                f"[red]❌ Invalid License[/red]\n"
                f"Reason: {status_info['message']}\n"
                f"User: {license_info['user']}\n"
                f"Expires: {license_info['expires']}"
            )
            panel = Panel(panel_content, title=f"License Status - {package}", border_style="red")
        
        console.print(panel)
        
        # Exit with appropriate code
        if status_info["status"] in ["licensed", "development_mode", "grace_period"]:
            if required_features and status_info["status"] == "licensed":
                license_info = status_info["license_info"]
                missing = [f for f in required_features if f not in license_info['features']]
                if missing:
                    raise typer.Exit(1)
            raise typer.Exit(0)
        else:
            raise typer.Exit(1)
            
    except typer.Exit:
        raise
    except Exception as e:
        rprint(f"[red]❌ Error validating license: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def info():
    """Display system information and installed licenses."""
    try:
        # System info
        machine_id = get_machine_id()
        dev_mode = is_development_mode()
        
        rprint("[bold cyan]System Information[/bold cyan]")
        rprint(f"Machine ID: {machine_id}")
        rprint(f"Development Mode: {'Enabled' if dev_mode else 'Disabled'}")
        rprint()
        
        # List installed licenses
        license_manager = LicenseManager()
        licenses = license_manager.list_licenses()
        
        if licenses:
            table = Table(title="Installed Licenses")
            table.add_column("Package", style="cyan")
            table.add_column("User", style="white")
            table.add_column("Expires", style="white")
            table.add_column("Features", style="white")
            table.add_column("Status", style="white")
            
            for license_info in licenses:
                status = "✅ Valid" if license_info["is_valid"] else "❌ Invalid"
                if license_info["is_expired"]:
                    status = "⏰ Expired"
                
                table.add_row(
                    license_info["package"],
                    license_info["user"],
                    license_info["expires"],
                    ", ".join(license_info["features"]),
                    status
                )
            
            console.print(table)
        else:
            rprint("[yellow]No licenses installed[/yellow]")
        
        # Usage tracking info
        usage_tracker = UsageTracker()
        usage_data = usage_tracker.get_all_usage_data()
        
        if usage_data:
            rprint("\n[bold cyan]Grace Period Usage[/bold cyan]")
            for package, data in usage_data.items():
                grace_info = usage_tracker.get_grace_period_info(package)
                status = "Active" if not grace_info["is_expired"] else "Expired"
                rprint(f"  {package}: {status} (first use: {data['first_use']})")
        
    except Exception as e:
        rprint(f"[red]❌ Error getting info: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list():
    """List all installed licenses."""
    try:
        license_manager = LicenseManager()
        licenses = license_manager.list_licenses()
        
        if not licenses:
            rprint("[yellow]No licenses installed[/yellow]")
            return
        
        table = Table(title="Installed Licenses")
        table.add_column("Package", style="cyan")
        table.add_column("User", style="white")
        table.add_column("Issued", style="white")
        table.add_column("Expires", style="white")
        table.add_column("Features", style="white")
        table.add_column("Status", style="white")
        
        for license_info in licenses:
            status = "✅ Valid" if license_info["is_valid"] else "❌ Invalid"
            if license_info["is_expired"]:
                status = "⏰ Expired"
            
            table.add_row(
                license_info["package"],
                license_info["user"],
                license_info["issued"][:10],  # Show only date part
                license_info["expires"][:10],
                ", ".join(license_info["features"]),
                status
            )
        
        console.print(table)
        
    except Exception as e:
        rprint(f"[red]❌ Error listing licenses: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def remove(
    package: str = typer.Argument(..., help="Package name to remove license for"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Remove a license for a specific package."""
    try:
        license_manager = LicenseManager()
        
        # Check if license exists
        if not license_manager.get_license(package):
            rprint(f"[yellow]No license found for package: {package}[/yellow]")
            return
        
        # Confirm removal
        if not confirm:
            if not typer.confirm(f"Remove license for '{package}'?"):
                rprint("Cancelled.")
                return
        
        if license_manager.remove_license(package):
            rprint(f"[green]✅ License removed for: {package}[/green]")
        else:
            rprint(f"[red]❌ Failed to remove license for: {package}[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        rprint(f"[red]❌ Error removing license: {e}[/red]")
        raise typer.Exit(1)


# Admin commands

@admin_app.command()
def setup(
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path")
):
    """Set up admin configuration."""
    try:
        config_path = Path(config_file) if config_file else Path.home() / ".quantummeta" / "admin_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate admin token
        import secrets
        admin_token = f"qm_admin_{secrets.token_urlsafe(32)}"
        
        config = {
            "admin_email": "admin@quantummeta.com",
            "admin_token": admin_token,
            "server_port": 8080,
            "server_host": "localhost",
            "encryption_enabled": True,
            "license_storage_path": str(Path.home() / ".quantummeta" / "licenses"),
            "created_at": typer.get_app_dir("quantummeta")
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        rprint(f"[green]✅ Admin configuration created at: {config_path}[/green]")
        rprint(f"[yellow]Admin Token: {admin_token}[/yellow]")
        rprint("[cyan]Keep this token secure - it provides full admin access![/cyan]")
        
    except Exception as e:
        rprint(f"[red]❌ Error setting up admin config: {e}[/red]")
        raise typer.Exit(1)


@admin_app.command()
def server(
    port: int = typer.Option(8080, "--port", "-p", help="Server port"),
    host: str = typer.Option("localhost", "--host", "-h", help="Server host"),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open browser automatically")
):
    """Start the admin dashboard server."""
    try:
        # Try to import required dependencies
        try:
            import http.server
            import socketserver
            import threading
            import time
        except ImportError as e:
            rprint(f"[red]❌ Missing dependencies: {e}[/red]")
            rprint("[yellow]Install with: pip install quantummeta-license[admin][/yellow]")
            raise typer.Exit(1)
        
        # Find the admin dashboard HTML file
        from importlib import resources
        import quantummeta_license
        
        # For development, use the docs directory
        admin_html_path = Path(__file__).parent.parent.parent / "docs" / "admin-app.html"
        
        if not admin_html_path.exists():
            rprint(f"[red]❌ Admin dashboard not found at: {admin_html_path}[/red]")
            raise typer.Exit(1)
        
        # Create a temporary directory and copy the HTML file
        temp_dir = Path(tempfile.mkdtemp())
        temp_html = temp_dir / "index.html"
        shutil.copy2(admin_html_path, temp_html)
        
        # Custom HTTP handler to serve the dashboard
        class AdminHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(temp_dir), **kwargs)
            
            def do_GET(self):
                if self.path == "/" or self.path == "/index.html":
                    self.path = "/index.html"
                return super().do_GET()
        
        # Start the server
        with socketserver.TCPServer((host, port), AdminHandler) as httpd:
            server_url = f"http://{host}:{port}"
            
            rprint(f"[green]🚀 Admin dashboard server started![/green]")
            rprint(f"[cyan]URL: {server_url}[/cyan]")
            rprint(f"[yellow]Press Ctrl+C to stop the server[/yellow]")
            
            if open_browser:
                threading.Thread(target=lambda: [time.sleep(1), webbrowser.open(server_url)]).start()
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                rprint("\n[yellow]Shutting down server...[/yellow]")
            finally:
                # Cleanup temp directory
                shutil.rmtree(temp_dir, ignore_errors=True)
                
    except Exception as e:
        rprint(f"[red]❌ Error starting admin server: {e}[/red]")
        raise typer.Exit(1)


@admin_app.command()
def dashboard():
    """Open the admin dashboard in browser."""
    try:
        admin_html_path = Path(__file__).parent.parent.parent / "docs" / "admin-app.html"
        
        if not admin_html_path.exists():
            rprint(f"[red]❌ Admin dashboard not found at: {admin_html_path}[/red]")
            rprint("[yellow]Run 'quantum-license admin server' to start the web server[/yellow]")
            raise typer.Exit(1)
        
        # Open the HTML file directly in browser
        webbrowser.open(f"file://{admin_html_path.absolute()}")
        rprint(f"[green]✅ Opening admin dashboard in browser[/green]")
        
    except Exception as e:
        rprint(f"[red]❌ Error opening dashboard: {e}[/red]")
        raise typer.Exit(1)


@admin_app.command()
def list_licenses(
    package: Optional[str] = typer.Option(None, "--package", "-p", help="Filter by package"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format (table, json)")
):
    """List all licenses in the system."""
    try:
        license_manager = LicenseManager()
        
        # Get all licenses (this would need to be implemented in LicenseManager)
        # For now, show a sample implementation
        rprint("[yellow]Note: This is a demo implementation[/yellow]")
        
        if output_format == "json":
            licenses_data = {
                "licenses": [
                    {
                        "id": "lic_2025_001",
                        "package": "quantum-metalearn",
                        "user": "user1@example.com",
                        "status": "active",
                        "expires": "2025-12-31"
                    }
                ]
            }
            rprint(json.dumps(licenses_data, indent=2))
        else:
            table = Table(title="License Database")
            table.add_column("License ID", style="cyan")
            table.add_column("Package", style="green")
            table.add_column("User", style="yellow")
            table.add_column("Status", style="magenta")
            table.add_column("Expires", style="blue")
            
            # Sample data
            table.add_row("lic_2025_001", "quantum-metalearn", "user1@example.com", "active", "2025-12-31")
            table.add_row("lic_2025_002", "quantum-neural", "user2@example.com", "expired", "2025-06-30")
            
            console.print(table)
            
    except Exception as e:
        rprint(f"[red]❌ Error listing licenses: {e}[/red]")
        raise typer.Exit(1)


@admin_app.command()
def expire_license(
    license_id: str = typer.Argument(..., help="License ID to expire"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Expire a specific license."""
    try:
        if not confirm:
            if not typer.confirm(f"Expire license '{license_id}'?"):
                rprint("Cancelled.")
                return
        
        # This would need to be implemented in LicenseManager
        rprint(f"[green]✅ License {license_id} has been expired[/green]")
        rprint("[yellow]Note: This is a demo implementation[/yellow]")
        
    except Exception as e:
        rprint(f"[red]❌ Error expiring license: {e}[/red]")
        raise typer.Exit(1)


@admin_app.command()
def delete_license(
    license_id: str = typer.Argument(..., help="License ID to delete"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Delete a specific license."""
    try:
        if not confirm:
            if not typer.confirm(f"Delete license '{license_id}'? This cannot be undone."):
                rprint("Cancelled.")
                return
        
        # This would need to be implemented in LicenseManager
        rprint(f"[green]✅ License {license_id} has been deleted[/green]")
        rprint("[yellow]Note: This is a demo implementation[/yellow]")
        
    except Exception as e:
        rprint(f"[red]❌ Error deleting license: {e}[/red]")
        raise typer.Exit(1)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
