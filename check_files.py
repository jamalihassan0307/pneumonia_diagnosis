"""
Create a detailed report of mismatches between database and disk.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pneumonia_diagnosis.settings')
django.setup()

from django.conf import settings
from xray_detector.models import XRayImage
from django.contrib.auth.models import User

print("=" * 80)
print("DETAILED FILE STATUS REPORT")
print("=" * 80)
print()

media_root = Path(settings.MEDIA_ROOT)
print(f"Media Root: {media_root}")
print(f"Media Root Writable: {os.access(media_root, os.W_OK)}")
print()

# Get all images
all_images = XRayImage.objects.all().select_related('user')
print(f"Total images in database: {all_images.count()}")
print()

# Categorize
missing = []
ok = []

for img in all_images:
    file_path = media_root / str(img.file_path)
    if file_path.exists():
        ok.append(img)
    else:
        missing.append(img)

print(f"✓ Images with files: {len(ok)}")
print(f"✗ Images with missing files: {len(missing)}")
print()

if missing:
    print("MISSING FILES:")
    print("-" * 80)
    for img in missing:
        file_path = media_root / str(img.file_path)
        print(f"ID: {img.id:3d} | User: {img.user.username:15s} | File: {img.original_filename}")
        print(f"        Expected path: {file_path}")
        print()
    
    # Suggest cleanup
    print()
    print("To clean up these orphaned records, run:")
    print("  python manage.py fix_uploads")
else:
    print("✓ All database records have valid files!")
    print()

# Check if there are actual files on disk that aren't in the database
print()
print("Scanning actual files on disk...")
xray_dir = media_root / 'xray_images'
if xray_dir.exists():
    total_files = len(list(xray_dir.rglob('*.jpg'))) + len(list(xray_dir.rglob('*.jpeg'))) + len(list(xray_dir.rglob('*.png')))
    print(f"Total image files on disk: {total_files}")
    print(f"Total images in database: {len(ok)}")
    if total_files != len(ok):
        print(f"⚠ Discrepancy: {total_files - len(ok)} files have no database record")

print()
print("=" * 80)
