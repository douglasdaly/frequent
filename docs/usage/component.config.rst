################################
Global Application Configuration
################################

The :doc:`frequent.config <../api/frequent.config>` module provides a global
applicaton configuration state for managing configuration settings
application-wide.  It also provides built-in JSON-based serialization and
file-storage (though it can easily be extended to use *any* type of
serialization/format desired).


Usage
=====

The :obj:`config <frequent.config>` module provides the following functions for
working with the global application configuration:

get_config(name=None, default=_MISSING)
    Gets the configuration setting specified by the ``name`` parameter, it will
    return that setting's value (or, if provided, the given ``default``).  If
    that setting isn't found (and no default value was given) a :obj:`KeyError`
    is raised.

    If the ``name`` is not provided then a **copy** of the global configuration
    object is returned.

set_config(name, value)
    Sets the configuration setting with the given ``name`` to the given
    ``value``.

clear_config()
    Clears out all of the global configuration settings.

save_config(path)
    Saves the current global configuration state to the ``path`` specified.

load_config(path=None, config_cls=Configuration)
    Loads a new configuration object as the global configuration state.  If the
    ``path`` parameter is provided it will load it from that file.  If the
    ``config_cls`` is specified it will use that class to store the global
    configuration.

temp_config(**settings)
    Provides a context-managed temporary configuration object, with the current
    global configuration settings as it's starting state (with any given
    ``settings`` keyword arguments set).  When the context is exited the
    original global configuration state is restored.


Getting, Setting & Clearing Settings
------------------------------------

To get a copy of the entire
:obj:`Configuration <frequent.config.Configuration>` object:

>>> get_config()
<Configuration settings={}>

To set a value:

>>> set_config('setting', 'value')
>>> get_config()
<Configuration settings={'setting': 'value'}>

To get a specific setting:

>>> get_config('setting')
'value'

To clear the entire global configuration:

>>> get_config('setting')
'value'
>>> clear_config()
>>> get_config('setting')
Traceback (most recent call last):
  ...
KeyError: 'setting'


Saving & Loading Configurations
-------------------------------

To save the current global configuration settings to disk:

>>> save_config('/path/to/config.json')

To load a configuration object from disk:

>>> load_config('/path/to/config.json')
>>> get_config()
<Configuration settings={'setting': 'value'}>

To load a custom configuration class from disk (in this case a class called
``YamlConfiguration``):

>>> load_config(path='/path/to/custom_cfg.yaml', config_cls=YamlConfiguration)
>>> get_config()
<YamlConfiguration settings={'setting': 'yaml_stored_value'}>


Temporary Configuration Contexts
--------------------------------

To temporarily modify the configuration for a particular block of code you can
use the provided :obj:`temp_config <frequent.config.temp_config>` context
manager:

>>> get_config()
<Configuration settings={'setting': 'value'}>
>>> with temp_config() as t_cfg:
...     print(t_cfg)
...     set_config('setting', 'temp_value')
...     print(get_config('setting'))
<Configuration settings={'setting': 'value'}>
'temp_value'
>>> get_config('setting')
'value'

You can also set temporary settings in the call to
:obj:`temp_config <frequent.config.temp_config>`:

>>> with temp_config(setting='another_value'):
...     get_config('setting')
'another_value'
>>> get_config('setting')
'value'


Links
=====

API
---

Module
    :doc:`frequent.config <../api/frequent.config>`

Classes
    :obj:`Configuration <frequent.config.Configuration>`

Functions
    :obj:`clear_config <frequent.config.clear_config>`,
    :obj:`get_config <frequent.config.get_config>`,
    :obj:`load_config <frequent.config.load_config>`,
    :obj:`set_config <frequent.config.set_config>`

Context Managers:
    :obj:`temp_config <frequent.config.temp_config>`

