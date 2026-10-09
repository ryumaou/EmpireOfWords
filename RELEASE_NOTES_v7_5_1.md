# v7.5.1 — Deployment verification hotfix

## Finding
The latest three contrast-suite diagnostics are identical to the prior run. All explicitly report translator version **7.4** and the same translator SHA256. The v7.5 translation changes have therefore **not been tested** in the supplied diagnostics. The language packages may legitimately remain at build version 7.4; translator version is what matters for this check.

## Changes
- Translator now supports `--version` without requiring a language or input, displaying both version and absolute script location.
- `verify_install.cmd` verifies the translator in the folder containing the script.
- Fixed the hard-coded generated-language build metadata in `build_language.py`, which still said 7.4 in the previous v7.5 release. This does not require rebuilding existing languages.
- Tool version 7.5.1 identifies this hotfix.

## Windows CMD instructions
1. Extract this ZIP into a **new folder** (do not merge it with the old v7.4 folder).
2. Open Command Prompt in the extracted `Empire_Of_Words_v7_5_1` directory.
3. Run `verify_install.cmd`; it must report **7.5.1** and the correct absolute script path.
4. Run `python src\translate.py --language output\Example --input translations\contrast_suite_v1.txt --diagnostics` (adjust paths to your actual language package location).
5. Confirm the **new** diagnostic report header says `Translator version: 7.5.1` before comparing results. Repeat for Test1 and Test2.

**Caution:** This release adds deployment verification, not a new translation feature. No improvement in translation coverage has been measured. Keep the existing language packages if they are compatible. Do not infer a successful v7.5 test from a 7.4 diagnostic.
