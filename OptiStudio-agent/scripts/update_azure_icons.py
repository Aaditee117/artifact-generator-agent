"""
Azure Icon Update Script

Downloads and updates Azure architecture icons from Microsoft's official source.
Keeps track of service status (current, preview, deprecated, discontinued).

Source: https://learn.microsoft.com/en-us/azure/architecture/icons/
Official repo: https://github.com/microsoft/azure-icons

Usage:
    python scripts/update_azure_icons.py [--force]
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CLIENT_ASSETS_DIR = PROJECT_ROOT / "OptiStudio-client" / "src" / "assets"
METADATA_FILE = SCRIPT_DIR / "azure_services_metadata.json"

# Microsoft Azure Icons GitHub repo
AZURE_ICONS_API = "https://api.github.com/repos/microsoft/azure-icons/contents/icons"
AZURE_ICONS_RAW = "https://raw.githubusercontent.com/microsoft/azure-icons/main/icons"


class AzureIconUpdater:
    def __init__(self, force_update: bool = False):
        self.force_update = force_update
        self.metadata = self.load_metadata()
        self.updated_count = 0
        self.new_count = 0
        self.skipped_count = 0

    def load_metadata(self) -> Dict:
        """Load service metadata (status, last updated, etc.)"""
        if METADATA_FILE.exists():
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "last_updated": None,
            "services": {},
            "categories": {},
            "deprecated_services": [],
            "discontinued_services": []
        }

    def save_metadata(self):
        """Save updated metadata"""
        self.metadata["last_updated"] = datetime.utcnow().isoformat()
        METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)
        print(f"✅ Metadata saved to {METADATA_FILE}")

    def get_file_hash(self, file_path: Path) -> Optional[str]:
        """Calculate SHA256 hash of a file"""
        if not file_path.exists():
            return None
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def fetch_icon_list(self) -> List[Dict]:
        """Fetch list of available icons from GitHub"""
        print("📡 Fetching icon list from Microsoft Azure Icons repository...")
        try:
            response = requests.get(AZURE_ICONS_API)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to fetch icon list: {e}")
            return []

    def categorize_icon(self, filename: str) -> str:
        """Determine category based on filename patterns"""
        filename_lower = filename.lower()
        
        # Category mapping based on common patterns
        categories = {
            "AI-and-Machine-Learning": ["openai", "cognitive", "machine-learning", "ai-", "bot-", "speech", "vision", "language"],
            "Analytics": ["analytics", "synapse", "databricks", "data-factory", "data-lake", "stream-analytics", "event-hub", "power-bi"],
            "Compute": ["app-service", "function", "container-app", "virtual-machine", "vm-", "kubernetes", "aks", "batch"],
            "Containers": ["container-", "kubernetes", "registry"],
            "Databases": ["cosmos", "sql", "database", "mysql", "postgresql", "redis", "cache"],
            "Storage": ["storage", "blob", "file-share", "data-lake-storage", "netapp"],
            "Networking": ["network", "vnet", "firewall", "gateway", "load-balancer", "front-door", "cdn", "dns", "vpn", "bastion"],
            "Security": ["key-vault", "entra", "active-directory", "sentinel", "defender", "security"],
            "Integration": ["service-bus", "event-grid", "logic-app", "api-management"],
            "DevOps": ["devops", "monitor", "application-insights", "log-analytics"],
            "Web": ["web-", "signalr", "static-app", "api-center"],
            "Identity": ["identity", "b2c", "users", "groups", "app-registration"],
            "Management": ["policy", "automation", "arc", "blueprint", "resource-group"],
        }

        for category, patterns in categories.items():
            if any(pattern in filename_lower for pattern in patterns):
                return category

        return "Other"

    def download_icon(self, icon_info: Dict) -> bool:
        """Download a single icon file"""
        filename = icon_info['name']

        # Skip non-SVG files
        if not filename.lower().endswith('.svg'):
            return False

        # Determine category and target directory
        category = self.categorize_icon(filename)
        target_dir = CLIENT_ASSETS_DIR / category
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / filename

        # Track if file existed before download and get its hash if so
        file_existed_before_download = target_file.exists()
        existing_hash = self.get_file_hash(target_file) if file_existed_before_download else None

        # Download the icon
        try:
            download_url = icon_info['download_url']
            response = requests.get(download_url)
            response.raise_for_status()

            # Calculate hash of new content
            new_hash = hashlib.sha256(response.content).hexdigest()

            # Check if file exists and has same content
            if file_existed_before_download:
                if existing_hash == new_hash and not self.force_update:
                    self.skipped_count += 1
                    return False

            # Write file
            with open(target_file, 'wb') as f:
                f.write(response.content)

            # Update metadata
            service_key = filename.replace('.svg', '').lower()
            if file_existed_before_download and existing_hash != new_hash:
                self.updated_count += 1
                status = "updated"
            elif not file_existed_before_download:
                self.new_count += 1
                status = "new"
            else:
                # This case should not occur due to earlier skip, but fallback to 'new'
                self.new_count += 1
                status = "new"

            self.metadata["services"][service_key] = {
                "filename": filename,
                "category": category,
                "path": str(target_file.relative_to(CLIENT_ASSETS_DIR)),
                "hash": new_hash,
                "status": "current",
                "last_checked": datetime.utcnow().isoformat()
            }

            if category not in self.metadata["categories"]:
                self.metadata["categories"][category] = []
            if service_key not in self.metadata["categories"][category]:
                self.metadata["categories"][category].append(service_key)

            print(f"  {'✨' if status == 'new' else '🔄'} {filename} → {category}/")
            return True

        except Exception as e:
            print(f"  ❌ Failed to download {filename}: {e}")
            return False

    def mark_deprecated_services(self):
        """Mark services that are no longer in the official repo as deprecated"""
        # This is a manual list that should be maintained based on Azure service lifecycle
        known_deprecated = [
            "azure-information-protection",
            "microsoft-genomics",
            "machine-learning-studio-classic",
            "azure-blockchain-service",
            "kinect-dk",
            "azure-active-directory-domain-services",  # Renamed to Entra Domain Services
        ]
        
        self.metadata["deprecated_services"] = known_deprecated
        
        known_discontinued = [
            "azure-blockchain-workbench",
            "azure-internet-analyzer",
            "azure-time-series-insights",
        ]
        
        self.metadata["discontinued_services"] = known_discontinued

    def update_all_icons(self):
        """Main update process"""
        print("🎨 Azure Icon Updater")
        print("=" * 60)
        
        icon_list = self.fetch_icon_list()
        if not icon_list:
            print("❌ No icons to process")
            return

        total = len(icon_list)
        print(f"📦 Found {total} items in repository")
        print()

        for icon_info in icon_list:
            self.download_icon(icon_info)

        self.mark_deprecated_services()
        self.save_metadata()

        print()
        print("=" * 60)
        print(f"✅ Icon update complete!")
        print(f"   New icons: {self.new_count}")
        print(f"   Updated icons: {self.updated_count}")
        print(f"   Skipped (unchanged): {self.skipped_count}")
        print(f"   Total services tracked: {len(self.metadata['services'])}")
        print(f"   Deprecated services: {len(self.metadata.get('deprecated_services', []))}")
        print(f"   Discontinued services: {len(self.metadata.get('discontinued_services', []))}")


def main():
    force_update = "--force" in sys.argv or "-f" in sys.argv
    
    updater = AzureIconUpdater(force_update=force_update)
    updater.update_all_icons()


if __name__ == "__main__":
    main()
