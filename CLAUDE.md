# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is lazyblorg

A static blog generator that converts Org-mode files into HTML5. Blog entries are scattered throughout regular Org-mode files (no dedicated blog file needed). Uses pickle-based metadata to track changes and only regenerate what's needed.

## Build & Run Commands

```bash
# Run tests (unit + integration)
uv --project . run pytest

# Run end-to-end tests
./start_end-to-end-test.sh

# Run all tests
./start_all_tests.sh

# Run a single test file
uv --project . run pytest lib/tests/htmlizer_test.py

# Run a single test
uv --project . run pytest lib/tests/htmlizer_test.py::HtmlizerTest::test_method_name

# Run the blog generator
uv --project . run ./lazyblorg.py \
   --targetdir "/tmp/lazyblorg/blog" \
   --previous-metadata "/tmp/lazyblorg/blog/metadata.pk" \
   --new-metadata "/tmp/lazyblorg/blog/metadata.pk" \
   --logfile "/tmp/lazyblorg/blog/logfile.org" \
   --orgfiles "./testdata/end_to_end_test/orgfiles/test.org" \
              "./templates/blog-format.org"
```

## Architecture

**Data flow:** Org files → OrgParser → blog_data (list of dicts) → metadata comparison → Htmlizer → HTML5 + RSS/ATOM feeds

**Core components:**
- `lazyblorg.py` — Main orchestrator. Parses CLI args, loads config, coordinates parsing and generation. Implements 8-case decision algorithm (`_compare_blogdata_to_metadata`) to determine what changed.
- `lib/orgparser.py` — **Finite state machine** parser that reads Org files line-by-line. States include SEARCHING_BLOG_HEADER, BLOG_HEADER, ENTRY_CONTENT, DRAWER_PROP, BLOCK, LIST, TABLE, etc. Returns structured blog_data dicts.
- `lib/htmlizer.py` — Converts parsed content to HTML5. Generates temporal pages, persistent pages, tag pages, entry page (homepage), archive pages, and 3 RSS/ATOM feed variants. Handles image resizing via OpenCV and falls back to pandoc for unsupported Org syntax.
- `config.py` — All configuration constants (author, domain, tags, image paths, feed settings). Validated with assertions on import. Can be overridden via `--config` flag.
- `lib/utils.py` — Static utilities: logging setup, error handling, metadata generation, language detection via stopwords.
- `templates/blog-format.org` — HTML template definitions with placeholder variables, parsed as a special Org entry tagged `lb_templates`.

**Blog entry requirements** (all must be present to publish):
1. `:blog:` tag (direct, not inherited)
2. Unique `:ID:` property
3. `DONE` state
4. `:LOGBOOK:` drawer with DONE state transition timestamp
5. `:CREATED:` property

**Entry categories:** TEMPORAL (dated articles), PERSISTENT (undated pages), TAGS (tag descriptions), ENTRYPAGE (homepage), TAGOVERVIEWPAGE (tag cloud), TEMPLATES (not published).

**Change detection:** No change detection. All blog files are re-generated from scratch on each publishing process.

## Testing

- Test framework: pytest with unittest-style test classes
- Test files: `*_test.py` in `lib/tests/` and `tests/`
- pytest config in `pyproject.toml`: testpaths = `["lib/tests", "tests"]`, import-mode = `importlib`
- End-to-end tests compare generated HTML against expected output in `testdata/end_to_end_test/comparison/`

## Dependencies

- Python ≥3.13, managed with `uv`
- Runtime: opencv-python, orgformat, pypandoc, werkzeug
- System: pandoc (for fallback Org conversion)

## Code Style

- PEP8
- Custom exceptions: `OrgParserException`, `HtmlizerException`
- Logging via Python logging module (--verbose/--quiet flags)
