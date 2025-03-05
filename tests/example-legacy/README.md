# Example Project (Legacy)
This example project demonstrates how to use BatConf 
to provide config management for a python project.
The implementation in legacy/conf.py, and uses in example lib and cli modules
should be considered standard-practice.

TODO: tests/example-legacy can be removed after we complete the 0.2.0 release
It exists to catch and help us document breaking changes and their fixes.

## Legacy
This example was copied and left unaltered to help us keep track of possible
breaking changes in the upcoming 0.2.0 release.
Hopefully this example will continue to work unaltered, and the update will be
minimally disruptive.

## Testing
example_test.py, and other *_test.py files are included to provide documentation
and ensure that the example code continues to function as expected.

## Experimentation
The example project is working python package, 
and can be a useful playground for experimentation.

### Ipython
1. change directory into tests/example-legacy: `> cd tests/example-legacy/`
2. Run the ipython repl: `> ipython`
3. Interact with the module:
```python
In [1]: from legacy.conf import get_config

In [2]: cfg = get_config()

In [3]: cfg.submodule.sub
Out[3]: Configuration(source_list=SourceList(sources=[<batconf.sources.env.
    EnvConfig object at 0x7b45d1b6fed0>, <batconf.sources.file.FileConfig 
    object at 0x7b45d057b290>, <batconf.sources.dataclass.DataclassConfig object
    at 0x7b45d08f4790>]), config_class=<class
    'legacy.submodule.sub.MyClient.Config'>)
    
In [4]: print(cfg.submodule.sub)
Root <class 'legacy.submodule.sub.MyClient.Config'>:
    |- key1: "Config.yaml: test.legacy.submodule.sub.key1"
    |- key2: "DEFAULT VALUE"
SourceList=[
    <batconf.sources.env.EnvConfig object at 0x7b45d1b6fed0>,
    <batconf.sources.file.FileConfig object at 0x7b45d057b290>,
    <batconf.sources.dataclass.DataclassConfig object at 0x7b45d08f4790>,
]

In [5]: cfg.submodule.sub.key1
Out[5]: 'Config.yaml: test.legacy.submodule.sub.key1'
```

### Example CLI
The CLI is fully functional, try it out, modify and experiment.
1. change directory into tests/example: `> cd tests/example/`
2. use runcli.py as the entry-point: `python runcli.py`
3. try out the "print-config" command! `python runcli.py print-config`
