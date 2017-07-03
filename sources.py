"""Parse Sequell's sources.yml file and download logfiles."""

import multiprocessing
import os
import sys
import subprocess
import urllib.parse
import re
import shlex
from typing import Optional, Iterable, Sequence
import logging

import yaml
from braceexpand import braceexpand

SIMULTANEOUS_DOWNLOADS = 10
WGET_NAME = 'wget.exe' if sys.platform == 'win32' else 'wget'
WGET_SOURCE_CMDLINE = ("%s --timeout 10 --no-verbose -c --tries 5 "
                       "-O '{outfile}' '{url}'" % WGET_NAME)
# Ignored stuff: sprint & zotdef games, dead servers
IGNORED_FILES_REGEX = re.compile(
    r'(sprint|zotdef|rl.heh.fi|crawlus.somatika.net|nostalgia|mulch|squarelos|combo_god)'
)


def sources(src: dict) -> Iterable[str]:
    """Return a full, raw listing of logfile/milestone URLs for a given src dict.

    Expands bash style '{a,b}{1,2}' strings into all their permutations.
    Excludes URLs that match IGNORED_FILES_REGEX.
    """
    expanded_sources = []  # type: list
    if not src['base'].endswith('/'):
        src['base'] += '/'
    for line in src['logs']:
        # Some entries are dicts of the form { 'pattern': 'explbr'}
        # So when we want to support non-vanilla branches this will have to
        # be supported
        if not isinstance(line, str):
            continue
        # We don't support using autoindex folders to download wildcard file
        # names, luckily only a few weird files are affected so we just ignore
        # them until someone complains.
        line = line.replace('*', '')
        expanded_sources.extend(braceexpand(line))
    for line in expanded_sources:
        entry = "{}{}".format(src['base'], line)
        if re.search(IGNORED_FILES_REGEX, entry):
            continue
        yield entry

def source_yaml(sources_yaml_path: str) -> dict:
    rawpath = os.path.join(os.path.dirname(__file__), sources_yaml_path)
    return yaml.safe_load(open(rawpath, encoding='utf8'))

def source_urls(sources_yaml_path: str) -> dict:
    raw_yaml = source_yaml(sources_yaml_path)
    out = {}
    for src in raw_yaml['sources']:
        out[src['name']] = src['base']
    return out


def source_data(sources_yaml_path: str) -> dict:
    """Return a dict of {src: data, src: data} from sources.yml."""
    out = {}
    raw_yaml = source_yaml(sources_yaml_path)
    for src in raw_yaml['sources']:
        out[src['name']] = tuple(sources(src))
    return out


def url_to_filename(url: str) -> str:
    """Convert milestone/logfile url to filename.

    Example:
        From: http://rl.heh.fi/meta/crawl-0.12/logfile
        To: meta-crawl-0.12-milestones.
    """
    return urllib.parse.urlparse(url).path.lstrip('/').replace('/', '-')


def download_source_files(urls: Sequence, dest: str) -> None:
    """Download logfile/milestone files for a single source."""
    logging.debug("Downloading {} files to {}".format(len(urls), dest))
    for url in urls:
        destfile = os.path.join(dest, url_to_filename(url))
        # Skip 0-byte files -- the source is assumed bad
        if os.path.exists(destfile) and os.stat(destfile).st_size == 0:
            continue
        # logging.debug("Downloading {} to {}".format(url, destfile))
        cmdline = shlex.split(
            WGET_SOURCE_CMDLINE.format(
                outfile=destfile, url=url))
        logging.debug("Executing subprocess: {}".format(cmdline))
        p = subprocess.run(cmdline,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        if p.returncode:
            logging.warning("Couldn't download {}. Error: {}".format(url, p.stderr))
            if b'ERROR 404' in p.stderr or b'ERROR 403' in p.stderr:
                # Write a zero-byte file so we don't try it again in future
                open(destfile, 'w').close()
        else:
            logging.debug("Finished downloading {}.".format(url))


def download_sources(sources_yaml_path: str, dest: str, servers: Optional[str]=None) -> None:
    """Download all logfile/milestone files.

    Parameters:
        dest: path to download destination directory
        servers: if specified, the servers to download from

    Returns:
        Nothing
    """
    #logging.debug("Downloading source files to {}".format(dest))
    if not os.path.exists(dest):
        os.mkdir(dest)
    all_sources = source_data(sources_yaml_path)
    if servers:
        temp = {}
        for server in servers:
            if server in all_sources:
                temp[server] = all_sources[server]
                logging.debug("Downloading from whitelisted server '%s'." % server)
            else:
                logging.info("Invalid server '%s' specified, skipping." % server)
        all_sources = temp
    # Not yet in typeshet
    p = multiprocessing.Pool(SIMULTANEOUS_DOWNLOADS)  # type: ignore
    jobs = []
    for src, urls in all_sources.items():
        destdir = os.path.join(dest, src)
        if not os.path.exists(destdir):
            os.mkdir(destdir)
        jobs.append(p.apply_async(download_source_files, (urls, destdir)))
    for job in jobs:
        job.get()
    p.close()
    p.join()
