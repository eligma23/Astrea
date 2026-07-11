"""Validate system.yaml and print the build plan:  python -m astrea.assembly"""
from astrea.assembly.assembler import load_config_cli

load_config_cli()
