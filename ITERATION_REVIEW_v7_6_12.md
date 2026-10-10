# v7.6.12 iteration review

This release adds a conservative direct-address parsing path for Madam/Sir and a meaningful multi-module translator SHA256. It does **not** claim to reach 73/80 complete. A generated language without a corresponding vocative lexeme remains partial. Existing language packages are untouched.

Test: `python -m unittest discover -s tests -q`

Translate: `python src/translate.py --language output/Example --input translations/contrast_suite_v1.txt --diagnostics`

A locally updated MagicTest directory is not included in the release; preserve it during installation.
