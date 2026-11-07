#!/usr/bin/env bash
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || exit 2
exec /usr/local/bin/python - "$ROOT" "$@" <<'ADAPTER_PY'
import argparse
import base64
import fnmatch
import io
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
from xml.etree import ElementTree as ET

PROFILE = json.loads(base64.b64decode('{{profile_b64}}'))
DEADLINE = None
COMMAND_STATUSES = []


def command(argv, cwd, env, timeout, phase="command"):
    if DEADLINE is not None:
        timeout = min(timeout, max(0.1, DEADLINE - time.monotonic()))
    try:
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, errors='replace', start_new_session=True)
        try:
            output, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            output, _ = proc.communicate()
            COMMAND_STATUSES.append({'phase': phase, 'exit': 124})
            return 124, output + '\ntimeout: ' + str(timeout) + ' seconds\n'
        COMMAND_STATUSES.append({'phase': phase, 'exit': proc.returncode})
        return proc.returncode, output
    except OSError as exc:
        COMMAND_STATUSES.append({'phase': phase, 'exit': 127})
        return 127, str(exc)


def canonical(case):
    return (case.get('classname') + '::' if case.get('classname') else '') + case.get('name', '')


def write_report(output, expected, cases, diagnostic, code, mode):
    issues = []
    actual = {}
    for case in cases:
        key = canonical(case)
        if key in actual:
            issues.append('duplicate ID: ' + key)
        if key not in expected:
            issues.append('unexpected ID: ' + key)
        else:
            actual[key] = case
    if not expected:
        raise RuntimeError('nonempty expected IDs required; configure profile before execution')
    missing = set(expected) - actual.keys()
    if missing:
        issues.append('missing IDs: ' + ', '.join(sorted(missing)))
    suite = ET.Element('testsuite', name=mode)
    failed = bool(code or issues)
    for key in expected:
        case = actual.get(key)
        if case is None:
            classname, sep, name = key.rpartition('::')
            case = ET.Element('testcase', classname=classname, name=name if sep else key)
            error = ET.SubElement(case, 'error', message='build/setup/collection/report failure')
            error.text = diagnostic + '\n' + '\n'.join(issues)
        if case.find('skipped') is not None and (mode == 'new' or not PROFILE['skip_allowlist'].get(key)):
            skipped = case.find('skipped')
            reason = skipped.get('message', '') + '\n' + (skipped.text or '')
            case.remove(skipped)
            ET.SubElement(case, 'error', message='unapproved skip').text = reason + '\n' + diagnostic
        if any(case.find(tag) is not None for tag in ('failure', 'error')):
            failed = True
        suite.append(case)
    if (code or issues) and all(c.find('error') is None and c.find('failure') is None for c in suite):
        ET.SubElement(suite[0], 'error', message='runner/report status failed').text = diagnostic + '\n' + '\n'.join(issues)
    suite.set('tests', str(len(suite)))
    for tag, attr in (('failure', 'failures'), ('error', 'errors'), ('skipped', 'skipped')):
        suite.set(attr, str(sum(c.find(tag) is not None for c in suite)))
    root = ET.Element('testsuites')
    root.append(suite)
    ET.SubElement(suite, 'system-out').text = diagnostic + '\nCOMMAND_STATUSES=' + json.dumps(COMMAND_STATUSES)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    for element in root.iter():
        if element.text:
            element.text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', lambda m: '\\x%02x' % ord(m[0]), element.text)
    ET.ElementTree(root).write(output, encoding='utf-8', xml_declaration=True)
    if issues:
        print('\n'.join(issues), file=sys.stderr)
    return 1 if failed else 0


def prepare(root, scratch, env, mode="base"):
    commit = PROFILE['identity']['commit']
    status, text = command(['git', '-c', 'safe.directory=' + str(root), '-C', str(root),
                            'cat-file', '-e', commit + '^{commit}'], '/', env, 30, phase='restore.verify')
    if status:
        raise RuntimeError('pristine base commit unavailable: ' + text)
    work = scratch / 'repo'
    overlay_paths = PROFILE['hidden_paths'] if mode == 'new' else PROFILE.get('base_hidden_paths', [])
    hidden = {name: ((root / name).read_bytes(), (root / name).stat().st_mode & 0o777) for name in overlay_paths}
    all_overlays = set(PROFILE['hidden_paths'] + PROFILE.get('base_hidden_paths', []))
    pristine = PROFILE['restore_paths']
    if not pristine:
        raise RuntimeError('pristine grading-path inventory is empty; refusing to restore production')
    test_roots = {n.split('/')[0] for n in PROFILE['tests'] if n.startswith(('tests/', 'test/', '__tests__/'))}
    grade_roots = set(test_roots)
    for name in PROFILE.get('helpers', []):
        directory = Path(name).parent.as_posix()
        if directory != '.':
            grade_roots.add(directory)
    for name in PROFILE.get('fixtures', []):
        parts = name.split('/')
        for index, part in enumerate(parts[:-1]):
            if part in ('testutil', 'testutils', 'testhelpers', '__mocks__', 'testdata', 'fixture', 'fixtures', '__snapshots__'):
                grade_roots.add('/'.join(parts[:index + 1]))
                break
    patterns = ('.git', '__pycache__', '*.pyc', '*.so', '*.pyd', '*.o', '*.a', '.pytest_cache', 'build', 'dist')
    if PROFILE['language'] == 'typescript':
        patterns += ('node_modules',)
    generated = shutil.ignore_patterns(*patterns)
    def ignore(directory, names):
        ignored = set(generated(directory, names))
        for entry in names:
            name = (Path(directory) / entry).relative_to(root).as_posix()
            grading = (name in pristine or name in all_overlays or name in grade_roots or any(name.startswith(d + '/') for d in grade_roots) or
                       bool(re.search(r'(^|/)(?:conftest\.py|pytest\.ini|(?:vitest|jest)\.config\.[cm]?[jt]s)$|(^|/)test_[^/]+\.py$|_test\.go$|\.(test|spec)\.[jt]sx?$', name)))
            if grading:
                ignored.add(entry)
        return ignored
    shutil.copytree(root, work, ignore=ignore)
    # Archive output stays binary; do not let text newline conversion corrupt fixtures.
    archive = subprocess.run(['git', '-c', 'safe.directory=' + str(root), '-C', str(root),
                              'archive', commit, '--', *pristine], capture_output=True)
    COMMAND_STATUSES.append({'phase': 'restore.archive', 'exit': archive.returncode})
    if archive.returncode:
        raise RuntimeError('pristine archive failed: ' + archive.stderr.decode(errors='replace'))
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
        for member in tar.getmembers():
            target = (work / member.name).resolve()
            if not target.is_relative_to(work.resolve()) or member.issym() or member.islnk():
                raise RuntimeError('unsafe pristine archive member: ' + member.name)
        tar.extractall(work, filter='data')
    for pyx in work.rglob('*.pyx'):
        pyx.with_suffix('.c').unlink(missing_ok=True)
    for name, (data, permissions) in hidden.items():
        path = work / name
        if not path.resolve().is_relative_to(work.resolve()):
            raise RuntimeError('hidden path escapes source')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(permissions)
    if PROFILE['language'] == 'typescript':
        shutil.copytree('/opt/adapter-node_modules', work / 'node_modules', dirs_exist_ok=True, symlinks=True)
    return work


def node_run(work, scratch, env, selected=None, ids=None):
    if 'vitest' not in PROFILE['frameworks']:
        raise RuntimeError('UNPROVEN: only the Vitest JUnit recipe is implemented; qualify a Jest adapter separately')
    report = scratch / 'vitest.xml'
    args = [str(work / 'node_modules/.bin/vitest'), 'run', '--reporter=junit', '--outputFile=' + str(report)]
    if selected is None:
        args += PROFILE['selectors'][env['ADAPTER_MODE']]
    else:
        args += sorted({ids[k][0] for k in selected})
        if set(selected) != set(ids):
            names = [ids[k][1] for k in selected]
            args += ['-t', '^(?:' + '|'.join(re.escape(n) for n in names) + ')$']
    status, log = command(args, work, env, PROFILE['timeout'], phase='test')
    print(log, end='')
    try:
        cases = list(ET.parse(report).iter('testcase'))
    except (OSError, ET.ParseError) as exc:
        return status or 1, [], log + '\nabsent/empty/malformed Vitest report: ' + str(exc)
    if selected is not None:
        cases = [c for c in cases if canonical(c) in selected or canonical(c) not in ids or c.find('skipped') is None]
    return status, cases, log


def collect(work, scratch, env, mode):
    language = PROFILE['language']
    selection = PROFILE['selectors'][mode]
    if not selection:
        raise RuntimeError('zero selection: selectors.' + mode + ' is empty')
    if language == 'go':
        args = ['go', 'list', '-json', *selection]
        code, log = command(args, work, env, PROFILE['timeout'], phase='discovery')
        if code:
            raise RuntimeError('package discovery failed: ' + log)
        packages = []
        decoder = json.JSONDecoder()
        while log.strip():
            item, end = decoder.raw_decode(log.lstrip())
            packages.append(item)
            log = log.lstrip()[end:]
        ids = {}
        for pkg in packages:
            code, log = command(['go', 'test', '-list', '.', pkg['ImportPath']], work, env, PROFILE['timeout'], phase='discovery.tests')
            if code:
                raise RuntimeError('test discovery failed: ' + log)
            for line in log.splitlines():
                if re.fullmatch(r'(?:Test|Fuzz)\w+|Example\w*', line) and line != 'TestMain':
                    ids[pkg['ImportPath'] + '::' + line] = [pkg['ImportPath'], line]
        return ids
    if language == 'python':
        plugin = scratch / 'adapter_collect.py'
        plugin.write_text('''import json, os
from pathlib import Path
def pytest_collection_finish(session):
    values = {}
    for item in session.items:
        parts = item.nodeid.split('::')
        classname = parts[0].removesuffix('.py').replace('/', '.')
        if len(parts) > 2:
            classname += '.' + '.'.join(parts[1:-1])
        key = classname + '::' + item.name
        if key in values:
            raise RuntimeError('duplicate canonical ID: ' + key)
        values[key] = item.nodeid
    Path(os.environ['ADAPTER_COLLECT']).write_text(json.dumps(values))
''')
        env['PYTHONPATH'] = str(scratch) + ':' + str(work)
        env['ADAPTER_COLLECT'] = str(scratch / 'collected.json')
        args = [sys.executable, '-m', 'pytest', '-p', 'no:cacheprovider', '-p', 'adapter_collect',
                '-o', 'addopts=', '--collect-only', '-q', *selection]
        code, log = command(args, work, env, PROFILE['timeout'], phase='discovery')
        print(log, end='')
        if code or not Path(env['ADAPTER_COLLECT']).is_file():
            raise RuntimeError('collection failed: ' + log)
        return json.loads(Path(env['ADAPTER_COLLECT']).read_text())
    if language == 'typescript':
        code, cases, log = node_run(work, scratch, env)
        if code or not cases:
            raise RuntimeError('Vitest baseline discovery failed: ' + log)
        result = {}
        for case in cases:
            key = canonical(case)
            if key in result:
                raise RuntimeError('duplicate canonical Vitest ID: ' + key)
            result[key] = [case.get('classname', ''), case.get('name', '').replace(' > ', ' ')]
        return result
    raise RuntimeError('UNPROVEN adapter: qualify native test enumeration and reporter before execution')


def execute(work, scratch, env, selected, ids):
    cases = []
    diagnostics = []
    status = 0
    if PROFILE['language'] == 'go':
        packages = sorted({ids[key][0] for key in selected})
        for package in packages:
            names = [ids[key][1] for key in selected if ids[key][0] == package]
            regex = '^(?:' + '|'.join(re.escape(n) for n in names) + ')$'
            code, log = command(['go', 'test', '-json', '-count=1', '-timeout=360s', '-run', regex, package],
                                work, env, PROFILE['timeout'], phase='test')
            print(log, end='')
            diagnostics.append(log)
            status = status or code
            outputs = {}
            for line in log.splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                name = event.get('Test', '')
                top = name.split('/')[0]
                if top and 'Output' in event:
                    outputs[top] = outputs.get(top, '') + event['Output']
                if name and '/' not in name and event.get('Action') in ('pass', 'fail', 'skip'):
                    case = ET.Element('testcase', classname=package, name=name, time=str(event.get('Elapsed', 0)))
                    tag = {'fail': 'failure', 'skip': 'skipped'}.get(event['Action'])
                    if tag:
                        ET.SubElement(case, tag).text = outputs.get(name, log)
                    ET.SubElement(case, 'system-out').text = outputs.get(name, '')
                    cases.append(case)
    elif PROFILE['language'] == 'typescript':
        status, cases, log = node_run(work, scratch, env, selected, ids)
        diagnostics.append(log)
    else:
        report = scratch / 'native.xml'
        args = [sys.executable, '-m', 'pytest', '-v', '-p', 'no:cacheprovider', '-o', 'addopts=',
                '-o', 'junit_family=xunit1', '--continue-on-collection-errors', '--junitxml=' + str(report),
                *[ids[key] for key in selected]]
        status, log = command(args, work, env, PROFILE['timeout'], phase='test')
        print(log, end='')
        diagnostics.append(log)
        try:
            cases = list(ET.parse(report).iter('testcase'))
        except (OSError, ET.ParseError) as exc:
            status = status or 1
            diagnostics.append('absent/empty/malformed native report: ' + str(exc))
    return status, cases, '\n'.join(diagnostics)


def main():
    global DEADLINE
    DEADLINE = time.monotonic() + PROFILE['timeout']
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('mode', choices=('base', 'new'))
    parser.add_argument('--output_path', required=False)
    parser.add_argument('--one')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--discover', action='store_true')
    args = parser.parse_args(sys.argv[2:])
    if sum(a == '--output_path' or a.startswith('--output_path=') for a in sys.argv[2:]) > 1:
        parser.error('--output_path given twice')
    if not args.output_path and not (args.list or args.discover):
        parser.error('--output_path is required')
    output = str(Path(args.output_path).resolve()) if args.output_path else None
    expected = PROFILE['expected'][args.mode]
    if args.one:
        if args.one not in expected:
            parser.error('--one must name an expected canonical ID')
        expected = [args.one]
    if args.list:
        if not expected:
            parser.error('nonempty expected IDs required')
        print(json.dumps(expected))
        return 0
    scratch = Path(tempfile.mkdtemp(prefix='repo-adapter-', dir='/var/tmp'))
    env = {'PATH': '/usr/local/go/bin:/opt/go/bin:/usr/local/bin:/usr/bin:/bin',
           'HOME': str(scratch / 'home'), 'TMPDIR': str(scratch),
           'GOCACHE': str(scratch / 'gocache'), 'GOPATH': '/opt/go', 'GOMODCACHE': '/opt/go/pkg/mod',
           'GOTOOLCHAIN': 'local', 'GOWORK': 'off', 'GOPROXY': 'off', 'GOSUMDB': 'off',
           'GOFLAGS': '-buildvcs=false -trimpath', 'PYTHONDONTWRITEBYTECODE': '1',
           'PIP_NO_INDEX': '1', 'LANG': 'C.UTF-8', **PROFILE['env']}
    env['ADAPTER_MODE'] = args.mode
    cases, diagnostic, status = [], '', 1
    try:
        Path(env['HOME']).mkdir()
        if PROFILE['language'] == 'go':
            env['GOCACHE'] = '/opt/adapter-gocache'
            if not os.access(env['GOCACHE'], os.W_OK | os.X_OK):
                raise RuntimeError('prepared Go cache is not writable; rebuild the generated Dockerfile')
        if not expected and not args.discover:
            raise RuntimeError('nonempty expected IDs required; qualification or new-test configuration is OPEN')
        work = prepare(Path(sys.argv[1]), scratch, env, args.mode)
        for argv in PROFILE['setup_commands']:
            code, text = command(argv, work, env, PROFILE['timeout'], phase='setup.build')
            print(text, end='')
            diagnostic += text
            if code:
                raise RuntimeError('setup/build failed: ' + text)
        for module in PROFILE['setup_imports']:
            code, text = command([sys.executable, '-c', 'import ' + module + '; from pathlib import Path; assert Path(' + module + '.__file__).resolve().is_relative_to(Path.cwd()), "import escaped candidate source"'], work, env, PROFILE['timeout'], phase='setup.import')
            diagnostic += text
            if code:
                raise RuntimeError('compiled/import check failed: ' + text)
        if not PROFILE['selectors'][args.mode]:
            raise RuntimeError('zero selection: selectors.' + args.mode + ' is empty')
        native_map = PROFILE.get('native_ids', {}) if args.mode == 'base' else PROFILE.get('new_native_ids', {})
        if not args.discover and PROFILE['language'] == 'typescript' and not native_map:
            raise RuntimeError('Vitest native ID mapping is not qualified; discover on a successful source tree first')
        ids = collect(work, scratch, env, args.mode) if args.discover or not native_map else native_map
        if not ids:
            raise RuntimeError('zero tests discovered')
        if args.discover:
            print('=====ADAPTER-IDS=====')
            print(json.dumps(ids, sort_keys=True))
            return 0
        selected = set(expected)
        available = set(ids) - set(PROFILE.get('deselected', []))
        if (not args.one and selected != available) or not selected <= available:
            raise RuntimeError('collection inventory drift: missing=' + str(sorted(selected - available)) +
                               ', unexpected=' + str(sorted(available - selected)))
        status, cases, log = execute(work, scratch, env, expected, ids)
        diagnostic += log
    except Exception as exc:
        diagnostic += '\n' + type(exc).__name__ + ': ' + str(exc)
        print(diagnostic, file=sys.stderr)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    if args.discover and not output:
        return 1
    if not expected:
        print('cannot emit named cases without a configured expected inventory', file=sys.stderr)
        return 2
    try:
        return write_report(output, expected, cases, diagnostic, status, args.mode)
    except Exception as exc:
        from html import escape
        COMMAND_STATUSES.append({'phase': 'reporter.converter', 'exit': 1})
        cause = diagnostic + '\nconverter failure: ' + str(exc) + '\nCOMMAND_STATUSES=' + json.dumps(COMMAND_STATUSES)
        print(cause, file=sys.stderr)
        items = []
        for key in expected:
            classname, sep, name = key.rpartition('::')
            items.append('<testcase classname="' + escape(classname, quote=True) + '" name="' +
                         escape(name if sep else key, quote=True) + '"><error message="converter failure">' +
                         escape(cause) + '</error></testcase>')
        fallback = '<testsuites><testsuite tests="' + str(len(expected)) + '" errors="' + str(len(expected)) + '\">' + ''.join(items) + '</testsuite></testsuites>'
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(fallback, encoding='utf-8')
        return 1


sys.exit(main())

ADAPTER_PY
