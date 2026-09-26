"""Do the tarballs published on Zenodo match the tags they claim to come from?

The public history of this repository was rewritten on 2026-09-26 to remove
third-party e-prints, so every commit hash moved (COMMIT-MAP.txt).  The archive
published with record v1.0.0 was built from a commit that no longer exists, and a
reader comparing it with the repository has to be able to check what the
difference is.  This script does that check, for every published version:

  * download the tarball from the record (or use a local copy),
  * unpack it and `git archive` the tag beside it,
  * report every path that differs, and classify it as intentional or not.

Intentional, and the only intentional, differences:
  v1.0.0 -- the six sources/<id>/SHA256 files, which the pruning of that archive
            removed along with the e-print directories; the mistake is stated in
            the v1.1.0 record and fixed by its archive.
  (both) -- nothing else.  Any other line in the report is a problem.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSIONS = [
    {"tag": "v1.0.0", "record": 22972847, "file": "shannon-1.0.0.tar.gz",
     "expected_only_in_tag": ["sources/%s/SHA256" % a for a in
                              ("1504.01472", "1808.07438", "2607.21517",
                               "2607.27869", "2607.29681", "2608.30273")]},
    {"tag": "v1.1.0", "record": 22979509, "file": "shannon-1.1.0.tar.gz",
     "expected_only_in_tag": []},
]


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def fetch(url, dest):
    r = subprocess.run(["curl", "-sL", "--max-time", "600", "-o", dest,
                        "-w", "%{http_code}", url], capture_output=True, text=True)
    return r.stdout.strip()


def tree_of_tar(path, workdir):
    with tarfile.open(path) as t:
        t.extractall(workdir)
    top = os.path.join(workdir, os.listdir(workdir)[0])
    return top


def files_under(root):
    out = {}
    for dirpath, _, names in os.walk(root):
        for n in names:
            p = os.path.join(dirpath, n)
            out[os.path.relpath(p, root)] = md5(p)
    return out


def main():
    cache = os.environ.get("SHANNON_TMP", tempfile.gettempdir())
    report = {"repository": "aoktyabrev/shannon", "commit_map": "COMMIT-MAP.txt", "versions": []}
    bad = 0
    for v in VERSIONS:
        url = f"https://zenodo.org/records/{v['record']}/files/{v['file']}?download=1"
        tarball = os.path.join(cache, v["file"])
        code = "cached" if os.path.exists(tarball) else fetch(url, tarball)
        with tempfile.TemporaryDirectory() as tmp:
            a, b = os.path.join(tmp, "record"), os.path.join(tmp, "tag")
            os.makedirs(a), os.makedirs(b)
            rec = tree_of_tar(tarball, a)
            subprocess.run(f"git archive {v['tag']} | tar -x -C {b}", shell=True, cwd=ROOT, check=True)
            fr, ft = files_under(rec), files_under(b)
            only_tag = sorted(set(ft) - set(fr))
            only_rec = sorted(set(fr) - set(ft))
            differing = sorted(p for p in set(fr) & set(ft) if fr[p] != ft[p])
        unexpected = (sorted(set(only_tag) - set(v["expected_only_in_tag"]))
                      + only_rec + differing)
        row = {
            "tag": v["tag"], "tag_commit": subprocess.run(
                ["git", "rev-parse", v["tag"] + "^{commit}"], cwd=ROOT,
                capture_output=True, text=True).stdout.strip(),
            "record": f"10.5281/zenodo.{v['record']}",
            "file": v["file"], "download_http": code, "tarball_md5": md5(tarball),
            "files_in_record": len(fr), "files_in_tag": len(ft),
            "only_in_tag": only_tag, "only_in_record": only_rec,
            "content_differs": differing,
            "intentional": v["expected_only_in_tag"],
            "unexpected_differences": unexpected,
            "pass": not unexpected,
        }
        bad += 0 if row["pass"] else 1
        report["versions"].append(row)
        print(f"{v['tag']} vs {row['record']}: {len(fr)} files in the record, {len(ft)} in the tag, "
              f"{len(only_tag)} only in the tag, {len(only_rec)} only in the record, "
              f"{len(differing)} differing -> {'PASS' if row['pass'] else 'FAIL'}")
        for p in unexpected:
            print("   UNEXPECTED", p)
    report["all_pass"] = bad == 0
    with open(os.path.join(ROOT, "results", "json", "w_archive.json"), "w") as f:
        json.dump(report, f, indent=2)
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
