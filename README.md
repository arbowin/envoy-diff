# envoy-diff

> Utility to compare `.env` files across environments and flag missing or mismatched keys.

---

## Installation

```bash
pip install envoy-diff
```

Or install from source:

```bash
git clone https://github.com/yourname/envoy-diff.git
cd envoy-diff
pip install .
```

---

## Usage

Compare two `.env` files and see what's missing or mismatched:

```bash
envoy-diff .env.development .env.production
```

**Example output:**

```
Missing in .env.production:
  - DEBUG
  - STRIPE_TEST_KEY

Mismatched keys:
  - DATABASE_URL  (values differ)

✔ 12 keys match across both files.
```

You can also compare multiple files at once:

```bash
envoy-diff .env.development .env.staging .env.production
```

Use `--keys-only` to suppress value comparison and check for key presence only:

```bash
envoy-diff .env.development .env.production --keys-only
```

---

## Options

| Flag | Description |
|------|-------------|
| `--keys-only` | Only check for missing keys, skip value comparison |
| `--strict` | Exit with a non-zero code if any differences are found |
| `--quiet` | Suppress output, useful for CI pipelines |

---

## License

This project is licensed under the [MIT License](LICENSE).