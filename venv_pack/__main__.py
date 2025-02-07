from __future__ import print_function, absolute_import

import argparse
import sys
import traceback

from . import __version__
from .core import pack, VenvPackException


class MultiAppendAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:  # pragma: nocover
            raise ValueError("nargs not allowed")
        super(MultiAppendAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest) is None:
            setattr(namespace, self.dest, [])
        getattr(namespace, self.dest).append((option_string.strip('-'), values))


def build_parser():
    description = "Package an existing virtual environment into an archive file."
    kwargs = dict(prog="venv-pack",
                  description=description,
                  add_help=False)
    if sys.version_info >= (3, 5):
        kwargs['allow_abbrev'] = False
    parser = argparse.ArgumentParser(**kwargs)
    parser.add_argument("--prefix", "-p",
                        metavar="PATH",
                        help=("Full path to environment prefix. Default is "
                              "current environment."))
    parser.add_argument("--output", "-o",
                        metavar="PATH",
                        help=("The path of the output file. Defaults to the "
                              "environment name with a ``.tar.gz`` suffix "
                              "(e.g.  ``my_env.tar.gz``)."))
    parser.add_argument("--format",
                        choices=['infer', 'zip', 'tar.gz', 'tgz', 'tar.bz2',
                                 'tbz2', 'tar'],
                        default='infer',
                        help=("The archival format to use. By default this is "
                              "inferred by the output file extension."))
    parser.add_argument("--python-prefix",
                        metavar="PATH",
                        help=("If provided, will be used as the new prefix path "
                              "for linking ``python`` in the packaged "
                              "environment. Note that this is the path to the "
                              "*prefix*, not the path to the *executable* (e.g. "
                              "``/usr/`` not ``/usr/lib/python3.6``)."))
    parser.add_argument("--compress-level",
                        type=int,
                        default=4,
                        help=("The compression level to use, from 0 to 9. "
                              "Higher numbers decrease output file size at "
                              "the expense of compression time. Ignored for "
                              "``format='zip'``. Default is 4."))
    parser.add_argument("--zip-symlinks",
                        action="store_true",
                        help=("Symbolic links aren't supported by the Zip "
                              "standard, but are supported by *many* common "
                              "Zip implementations. If set, store symbolic "
                              "links in the archive, instead of the file "
                              "referred to by the link. This can avoid storing "
                              "multiple copies of the same files. *Note that "
                              "the resulting archive may silently fail on "
                              "decompression if the ``unzip`` implementation "
                              "doesn't support symlinks*. Ignored if format "
                              "isn't ``zip``."))
    parser.add_argument("--no-zip-64",
                        action="store_true",
                        help="Disable ZIP64 extensions.")
    parser.add_argument("--no-shebang-rewrite",
                        action="store_true",
                        help="Disable shebang rewriting")
    parser.add_argument("--exclude",
                        action=MultiAppendAction,
                        metavar="PATTERN",
                        dest="filters",
                        help="Exclude files matching this pattern")
    parser.add_argument("--include",
                        action=MultiAppendAction,
                        metavar="PATTERN",
                        dest="filters",
                        help="Re-add excluded files matching this pattern")
    parser.add_argument("--force", "-f",
                        action="store_true",
                        help="Overwrite any existing archive at the output path.")
    parser.add_argument("--quiet", "-q",
                        action="store_true",
                        help="Do not report progress")
    parser.add_argument("--help", "-h", action='help',
                        help="Show this help message then exit")
    parser.add_argument("--version",
                        action='store_true',
                        help="Show version then exit")
    return parser


# Parser at top level to allow sphinxcontrib.autoprogram to work
PARSER = build_parser()


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def main(args=None, pack=pack):
    args = PARSER.parse_args(args=args)

    # Manually handle version printing to output to stdout in python < 3.4
    if args.version:
        print('venv-pack %s' % __version__)
        sys.exit(0)

    try:
        pack(prefix=args.prefix,
             output=args.output,
             format=args.format,
             python_prefix=args.python_prefix,
             force=args.force,
             compress_level=args.compress_level,
             zip_symlinks=args.zip_symlinks,
             zip_64=not args.no_zip_64,
             verbose=not args.quiet,
             rewrite_shebang=not args.no_shebang_rewrite,
             filters=args.filters)
    except VenvPackException as e:
        fail("VenvPackError: %s" % e)
    except KeyboardInterrupt as e:  # pragma: nocover
        fail("Interrupted")
    except Exception as e:  # pragma: nocover
        fail(traceback.format_exc())
    sys.exit(0)


if __name__ == '__main__':  # pragma: nocover
    main()
