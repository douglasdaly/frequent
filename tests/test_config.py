# -*- coding: utf-8 -*-
"""
Unit tests for the `config` module.
"""
import os
from tempfile import mkstemp

from frequent import config


class TestConfiguration(object):
    """
    Tests for the :obj:`Configuration` class.
    """

    def test_usage(self):
        cfg = config.Configuration()
        assert len(cfg) == 0

        try:
            _ = cfg.a
            assert False
        except AttributeError:
            assert True

        cfg['a'] = 5
        assert cfg['a'] == 5
        assert cfg.a == 5
        assert cfg.a == cfg['a']

        assert cfg == cfg

        cfg.a = 6
        assert cfg['a'] == 6
        cfg.a += 1
        assert cfg['a'] == 7

        cfg['b.c'] = 10
        cfg['b.d'] = 11

        for k, v in cfg['b'].items():
            if k == 'c':
                assert v == 10
            elif k == 'd':
                assert v == 11

        for k in ('a', 'b', 'b.c', 'b.d'):
            assert k in cfg.keys()

        return

    def test_clear(self):
        cfg = config.Configuration()
        cfg['a.b.c'] = 10
        cfg['b'] = 'value'
        assert len(cfg) == 2

        cfg.clear()
        assert len(cfg) == 0

        return

    def test_copy(self):
        cfg = config.Configuration()
        cfg.a = 10
        cfg.b = 12
        cfg.c = 'value'
        assert cfg == cfg.copy()

        return

    def test_file_functions(self):
        cfg = config.Configuration()
        cfg.a = 10
        cfg.b = 5.0
        cfg.c = 'value'
        cfg['d.first'] = 42
        cfg['d.second'] = 42.0
        cfg['d.third'] = 'forty-two'

        _, tmp_path = mkstemp(suffix='.json')
        try:
            cfg.save(tmp_path)
            loaded = config.Configuration.load(tmp_path)
        finally:
            os.remove(tmp_path)
        assert cfg == loaded

        return


def test_get_set_config():
    """Tests the get_config and set_config functions"""
    config.clear_config()

    cfg = config.get_config()
    assert type(cfg) == config.Configuration
    assert len(cfg) == 0

    try:
        config.get_config('test')
        assert False
    except KeyError:
        assert True

    assert config.get_config('test', 42) == 42

    config.set_config('test', 'value')
    assert config.get_config('test') == 'value'
    assert config.get_config('test', 'not value') == 'value'


def test_temp_config():
    """Tests the temp_config context manager"""
    config.clear_config()

    config.set_config('a', 42)

    with config.temp_config(a=0) as tmp_cfg:
        assert type(tmp_cfg) == config.Configuration
        assert tmp_cfg.a == 0
        assert config.get_config('a') == 0
        config.set_config('a', 5)
        assert config.get_config('a') == 5
    assert config.get_config('a') == 42

    return



