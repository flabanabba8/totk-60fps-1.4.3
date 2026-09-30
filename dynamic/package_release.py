"""Build the shareable kit from an explicit allowlist; never include game files."""
import argparse
import hashlib
from pathlib import Path
import zipfile

NAME = 'totk-dynamic-60fps-1.4.3-experimental-0.2.0'
LIBRARY_SHA256 = '31d683cdaa4576142e6b8d912ff53eea280851eecd4293cd3a70eb23c7c7d357'


def package(library, destination):
    root = Path(__file__).resolve().parent
    if library.stat().st_size > 2 * 1024 * 1024:
        raise ValueError('Expected the tested ARMeilleure.dll, under 2 MiB')
    dll = library.read_bytes()
    if hashlib.sha256(dll).hexdigest() != LIBRARY_SHA256:
        raise ValueError('ARMeilleure.dll does not match the tested repair')
    files = {'LICENSE': root.parent / 'LICENSE'}
    for name in ('README.md', 'build_dynamic.py', 'timing.s', 'test_dynamic.py'):
        files[name] = root / name
    for name in ('README.md', 'LICENSE-Ryujinx.txt', 'patch_bundle.py',
                 'region-ownership.patch', 'CacheRegression.csproj',
                 'PatchedLibrary.csproj', 'Program.cs'):
        files['ryujinx-fix/' + name] = root / 'ryujinx-fix' / name
    contents = {name: path.read_bytes() for name, path in files.items()}
    contents['ryujinx-fix/ARMeilleure.dll'] = dll
    contents['SHA256SUMS'] = ''.join(
        hashlib.sha256(data).hexdigest() + '  ' + name + '\n'
        for name, data in sorted(contents.items())
    ).encode()
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / (NAME + '.zip')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as output:
        for name, data in sorted(contents.items()):
            entry = zipfile.ZipInfo(NAME + '/' + name, date_time=(2026, 9, 30, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            output.writestr(entry, data)
    with zipfile.ZipFile(archive) as output:
        assert output.testzip() is None
        assert len(output.namelist()) == len(contents)
        for name, data in contents.items():
            assert output.read(NAME + '/' + name) == data
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(digest + '  ' + archive.name + '\n')
    print(f'{archive}: {archive.stat().st_size:,} bytes; SHA256 {digest}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('library', type=Path, help='The tested repaired ARMeilleure.dll')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'dist')
    args = parser.parse_args()
    package(args.library, args.output)
