```markdown
# hot-trend-root Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches you the core development patterns, coding conventions, and key workflows used in the `hot-trend-root` Python repository. The project manages data extraction, schema migrations, and single-file HTML site generation for tracking vendor trends, with a focus on maintainable code and clear documentation. You’ll learn how to implement new data parsers, migrate schemas, update documentation, and build distributable site files—all following the repository’s established conventions.

---

## Coding Conventions

### File Naming

- **CamelCase** is used for file names.
  - Example: `codingPlanSaver.py`, `dataMap.md`

### Import Style

- **Relative imports** are preferred within packages.
  ```python
  from .sources import deepseek
  from . import runner
  ```

### Export Style

- **Default export**: Modules expose their main functionality via the default module export (Python convention: module-level functions/classes).

### Commit Messages

- **Conventional commit prefixes**: `feat`, `docs`, `fix`, `refactor`, `chore`, `cleanup`
- **Example:**
  ```
  feat: add parser for new vendor extraction (DeepSeek)
  docs: update schema documentation for new fields
  ```

---

## Workflows

### Data Schema Migration and Update

**Trigger:** When the data model or schema changes, or when migrating data to a new structure  
**Command:** `/migrate-schema`

1. Edit or create `project/codingplan-saver/data/SCHEMA.md` to define schema changes.
2. Update or migrate JSON data files:
   - `site.json`
   - `vendors.json`
   - `plans.json`
   - `changes.json`
3. If needed, write migration scripts or perform manual data transformation.
   ```python
   # Example migration script snippet
   import json

   with open('vendors.json') as f:
       vendors = json.load(f)

   for vendor in vendors:
       if 'oldField' in vendor:
           vendor['newField'] = vendor.pop('oldField')

   with open('vendors.json', 'w') as f:
       json.dump(vendors, f, indent=2)
   ```
4. Clean up or remove deprecated data fields and files.
5. Update documentation (e.g., `reference/data-map.md`) to reflect new schema.
6. Regenerate or update `dist/codingplan-saver.html` to reflect data changes.

---

### Parser Implementation and Integration

**Trigger:** When adding support for a new vendor or extraction method  
**Command:** `/add-parser`

1. Create or update parser file in `tools/collector/collector/sources/` (e.g., `deepseek.py`, `tencent.py`).
   ```python
   # tools/collector/collector/sources/deepseek.py
   def extract_data(html):
       # Extraction logic here
       pass
   ```
2. Register the parser in `sources/__init__.py` or `runner.py`.
   ```python
   # sources/__init__.py
   from .deepseek import extract_data as deepseek_extract
   ```
3. Update `project/codingplan-saver/data/vendors.json` to set `extractStrategy` for the vendor.
4. Test extraction and generate `data/signals/extract-{date}.json`.
5. Update `docs/pricing-urls.md` or similar documentation with extraction status.
6. Regenerate or update `dist/codingplan-saver.html` if needed.

---

### Skill and Workflow Documentation Update

**Trigger:** When a new workflow is defined, or an existing one is updated, or after major architectural changes  
**Command:** `/update-skill-docs`

1. Edit or create `.claude/skills/*.md` to document the workflow, skill usage, or implementation details.
2. Update or create `docs/superpowers/specs/*.md` and `docs/superpowers/plans/*.md` for design specs and implementation plans.
3. Update project-level documentation files (e.g., `CLAUDE.md`, `reference/data-map.md`) as needed.
4. Reference or link to updated schema, workflows, or data files.

---

### Single-file HTML Build and Release

**Trigger:** When data or templates change, or after a major feature or data update  
**Command:** `/build-site`

1. Run or update build script (`tools/builder/build.py`).
   ```bash
   python tools/builder/build.py
   ```
2. Read data from `project/codingplan-saver/data/*.json` and template from `template/index.html`.
3. Generate `dist/codingplan-saver.html`.
4. Commit `dist/codingplan-saver.html` (ensure `.gitignore` allows it).
5. Optionally, clean up or fix `.gitignore` for `dist/`.

---

## Testing Patterns

- **Test files** follow the pattern: `*.test.*`
- **Testing framework:** Not specified (add or update as needed)
- **Example test file:** `extractor.test.py`
  ```python
  def test_extract_data():
      html = "<html>...</html>"
      result = extract_data(html)
      assert result['price'] == 42
  ```

---

## Commands

| Command         | Purpose                                                           |
|-----------------|-------------------------------------------------------------------|
| /migrate-schema | Migrate or update the data schema and related data files          |
| /add-parser     | Implement and integrate a new data extraction parser              |
| /update-skill-docs | Update or create documentation for skills and workflows        |
| /build-site     | Build and release the single-file HTML output for the site        |
```
