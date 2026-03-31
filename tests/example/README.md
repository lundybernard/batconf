# Example Project
This example project demonstrates how to use BatConf 
to provide config management for a python project.
The implementation in project/conf.py, and uses in example lib and cli modules
should be considered standard-practice.

## Testing
example_test.py, and other *_test.py files are included to provide documentation
and ensure that the example code continues to function as expected.

## Experimentation
The example project is working python package, 
and can be a useful playground for experimentation.

### Ipython
1. change directory into tests/example: `> cd tests/example/`
2. Run the ipython repl: `> ipython`
3. Interact with the module:
```python
In [1]: from project.conf import get_config

In [2]: cfg = get_config()

In [3]: cfg.submodule.client
Out[3]: Configuration(source_list=SourceList(sources=[<batconf.sources.env.
    EnvConfig object at 0x7b45d1b6fed0>, <batconf.sources.ini.IniConfig
    object at 0x7b45d057b290>]), config_class=<class
    'project.submodule.client.MyClient.Config'>)

In [4]: print(cfg.submodule.client)
project.submodule.client <class 'project.submodule.client.MyClient.Config'>:
    |- key1: "Config.ini: test.project.submodule.client.key1"
    |- key2: "DEFAULT VALUE"
SourceList=[
    <batconf.sources.env.EnvConfig object at 0x7b45d1b6fed0>,
    <batconf.sources.ini.IniConfig object at 0x7b45d057b290>,
]

In [5]: cfg.submodule.client.key1
Out[5]: 'Config.ini: test.project.submodule.client.key1'
```

### Example CLI
The CLI is fully functional, try it out, modify and experiment.
1. change directory into tests/example: `> cd tests/example/`
2. use runcli.py as the entry-point: `python runcli.py`
3. try out the "print-config" command! `python runcli.py print-config`
