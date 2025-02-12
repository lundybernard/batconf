Developers Blog
===============

Welcome to the BatConf Developer Blog!
Here, you'll find development updates,
tips, and other insights related to BatConf.


.. _upcoming_changes_in_02x:

Big changes coming in 0.2.x
---------------------------

**Possible breaking changes, and new features**

- **Optional Yaml dependency**:

  - Yaml has been a hard-coded dependency, after 0.2.0 is released it will
    become an optional extra.
  - We are adding more supported for more config file types (.ini, and .toml)
  - Projects which currently utilize .yaml/.yml config files will need to update
    their dependencies
    ex: in your pyproject.toml file:

    .. code-block:: toml

        dependencies = [
            "batconf"
        ]
        # changes to
        dependencies = [
            "batconf[yaml]"
        ]

- **More Flexible Configuration Structure**:

  - Originally, batconf required the config structure to match the project's module structure.
    This worked in the context of the original Basic Automation Tool project,
    but its limits have apparent.
  - We are still working out the details, more to come as we approach the relase day.
  - Objectives:

    - Developers should be able to structure their config as they see fit.
    - A structured config may become entirely optional.
    - Developers should be able to define the config structure independently
      of the module structure, in a single file,
      instead of scattered through __init.py__ files.

- **New Config File Sources**

  - **.ini** file support
  - **.toml** file support
  - Neither will require any additional dependencies.
  - Using either of these options without Yaml support, means BatConf will
    require no additional dependencis beyond stdlib ;)
