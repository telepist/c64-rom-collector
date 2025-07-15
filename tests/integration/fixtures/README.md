# Integration Test Fixtures

This directory contains comprehensive fixtures for integration testing of the C64 ROM collector.

## Structure

- `fixture_definitions.py` - Contains all fixture data definitions
- `fixture_creator.py` - Utilities for creating dynamic fixtures and expected results
- `roms/` - Physical fixture files used by filesystem integration tests
- `__init__.py` - Package initialization

## Physical Fixtures (roms/)

The `roms/` directory contains realistic ROM files organized by collection:

- `NoIntro/` - No-Intro collection fixtures (20 files)
- `TOSEC/` - TOSEC collection fixtures (34 files)  
- `OneLoad64/` - OneLoad64 collection fixtures (2 files)

### File Types

- **ROM files**: `.d64`, `.crt`, `.tap`, `.t64`, `.g64`, `.nib`, `.prg`
- **Skipped files**: `.txt`, `.pdf`, `.zip`, `.rar`, `.DS_Store`, `desktop.ini`, `Thumbs.db`

## Usage

### Filesystem Integration Tests

Use the physical fixtures in the `roms/` directory:

```python
from pathlib import Path
fixtures_dir = Path(__file__).parent / "fixtures" / "roms"
```

### Comprehensive Integration Tests

Use dynamic fixtures created in memory:

```python
from .fixtures.fixture_creator import create_comprehensive_fixtures, get_expected_results
```

## Test Coverage

The fixtures provide comprehensive coverage for:

- **Regional prioritization**: Europe/PAL > World > USA > Japan/NTSC
- **Format prioritization**: CRT > Disk > Tape
- **Collection prioritization**: NoIntro > TOSEC > OneLoad64
- **Multi-disk games**: Games with multiple parts and M3U playlists
- **Edge cases**: Complex game names, version numbers, special characters
- **File skipping**: Non-ROM files that should be ignored

## Maintenance

The physical fixtures are committed to the repository and should not need regeneration unless:
1. New test scenarios are added
2. The fixture data definitions are updated
3. The prioritization logic changes significantly

To regenerate fixtures (if needed):
```python
from tests.integration.fixtures.fixture_creator import create_comprehensive_fixtures
# This would require re-implementing the filesystem creation logic
```
