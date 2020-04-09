import io
import os
from pathlib import Path
from contextlib import redirect_stdout

import pytest

import sunpy
from sunpy import config
from sunpy.util import SunpyUserWarning
from sunpy.util.config import (get_and_create_sample_dir, get_and_create_download_dir,
                               CONFIG_DIR, print_config, _find_config_files, dirs,
                               _get_user_configdir, _is_writable_dir, write_config)

USER = os.path.expanduser('~')


def test_is_writable_dir(tmpdir, tmp_path):
    assert _is_writable_dir(tmpdir)
    tmp_file = tmpdir.join("hello.txt")
    # Have to write to the file otherwise its seen as a directory(?!)
    tmp_file.write("content")
    # Checks directory with a file
    assert _is_writable_dir(tmpdir)
    # Checks a filepath instead of directory
    assert not _is_writable_dir(tmp_file)


def test_get_user_configdir(tmpdir, tmp_path, undo_config_dir_patch):
    # Default
    assert USER in CONFIG_DIR
    assert CONFIG_DIR.split(os.path.sep)[-1] == "sunpy"
    assert CONFIG_DIR == _get_user_configdir()
    # Try to set a manual one (already created)
    tmp_config_dir = tmpdir.mkdir("config_here")
    os.environ["SUNPY_CONFIGDIR"] = tmp_config_dir.strpath
    assert tmp_config_dir == _get_user_configdir()
    # Bypass this under windows.
    if not (os.name == "nt"):
        os.unsetenv("SUNPY_CONFIGDIR")
    del os.environ["SUNPY_CONFIGDIR"]
    # Try to set a manual one (not created)
    os.environ["SUNPY_CONFIGDIR"] = str(tmp_path)
    assert str(tmp_path) == _get_user_configdir()
    # Bypass this under windows.
    if not (os.name == "nt"):
        os.unsetenv("SUNPY_CONFIGDIR")
    del os.environ["SUNPY_CONFIGDIR"]


def test_print_config_files(tmpdir, tmp_path, undo_download_dir_patch):
    with io.StringIO() as buf, redirect_stdout(buf):
        print_config()
        printed = buf.getvalue()
    assert "time_format = %Y-%m-%d %H:%M:%S" in printed
    assert _find_config_files()[0] in printed
    assert get_and_create_download_dir() in printed
    assert get_and_create_sample_dir() in printed


def test_get_and_create_download_dir(undo_download_dir_patch):
    # test default config
    path = get_and_create_download_dir()
    assert Path(path) == Path(USER) / 'sunpy' / 'data'
    # test updated config
    new_path = os.path.join(USER, 'sunpy_data_here_please')
    config.set('downloads', 'download_dir', new_path)
    path = get_and_create_download_dir()
    assert path == os.path.join(USER, new_path)
    # Set the config back
    os.rmdir(new_path)
    config.set('downloads', 'download_dir', os.path.join(USER, 'sunpy', 'data'))


def test_get_and_create_sample_dir():
    # test default config
    path = get_and_create_sample_dir()
    assert Path(path) == Path(dirs.user_data_dir)
    # test updated config
    new_path = os.path.join(USER, 'sample_data_here_please')
    config.set('downloads', 'sample_dir', new_path)
    path = get_and_create_sample_dir()
    assert path == new_path
    # Set the config back
    os.rmdir(new_path)
    config.set('downloads', 'sample_dir', os.path.join(USER, 'sunpy', 'data', 'sample_data'))


def test_write_config_create_new_config(tmpdir, undo_config_dir_patch):
    config_filename = 'sunpyrc'

    # Try to set a manual one (already created)
    tmp_config_dir = tmpdir.mkdir("sunpy_test_configdir")
    os.environ["SUNPY_CONFIGDIR"] = tmp_config_dir.strpath

    assert tmp_config_dir == _get_user_configdir()

    config_file = Path(sunpy.__file__).parent / 'data' / config_filename
    user_config_file = tmp_config_dir / config_filename

    # Create a new config file
    write_config()
    assert open(user_config_file, 'r').read() == open(config_file, 'r').read()

    if os.name != "nt":
        os.unsetenv("SUNPY_CONFIGDIR")
    del os.environ["SUNPY_CONFIGDIR"]


def test_write_config_without_overwrite(tmpdir, undo_config_dir_patch):

    # Try to set a manual one (already created)
    tmp_config_dir = tmpdir.mkdir("sunpy_test_configdir")
    os.environ["SUNPY_CONFIGDIR"] = tmp_config_dir.strpath

    assert tmp_config_dir == _get_user_configdir()

    # Create a new config file
    write_config()

    # Without the `overwrite` parameter
    # the function should raise an error.
    with pytest.warns(SunpyUserWarning):
        write_config()

    # Bypass this under windows.
    if os.name != "nt":
        os.unsetenv("SUNPY_CONFIGDIR")
    del os.environ["SUNPY_CONFIGDIR"]


def test_write_config_with_overwrite(tmpdir, undo_config_dir_patch):

    # Try to set a manual one (already created)
    tmp_config_dir = tmpdir.mkdir("sunpy_test_configdir")
    os.environ["SUNPY_CONFIGDIR"] = tmp_config_dir.strpath

    assert tmp_config_dir == _get_user_configdir()

    # Create a new config file
    write_config()

    # With the `overwrite` parameter
    # the function does not raise any error.
    with pytest.warns(SunpyUserWarning):
        write_config(overwrite=True)

    # Bypass this under windows.
    if os.name != "nt":
        os.unsetenv("SUNPY_CONFIGDIR")
    del os.environ["SUNPY_CONFIGDIR"]
