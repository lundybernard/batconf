Developers' Blog
================

Welcome to the BatConf Developers' Blog!
Here you'll find development updates,
tips, and other insights related to BatConf.

.. _freethreading_blog:

Support for free-threaded/nogil applications
--------------------------------------------------------------------------------
Now that
`free-threading <https://docs.python.org/3/howto/free-threading-python.html>`__
(`PEP 703 <https://peps.python.org/pep-0703/>`__)
is officially supported in Python 3.14, BatConf will also officially support it.

**Test Coverage**
We added 3.14t (nogil) to our CI test matrix, to make sure the standard test
suite passes without the GIL in place.

We added new multi-threaded stress tests, which hammer a single Configuration
object with many reads.

**Supported use cases**
The intended and supported use-case for Configuration objects,
is that they will be created, and values will be read from them.
We expect them to be used for configuration values, not general-purpose data
access, and we do not expect values to be written to them...

However, these uses are not prohibited, and we do not intend to prevent users
from accessing large data sets, or mutable data.  The thread-safety from race
conditions and read/write contention will be your responsibility if you choose
to push these limits.


.. _supplychain_security_blog:

Security: Supply-Chain
---------------------------------------------------------------------
Modern Python applications often carry significant supply chain
risk through their dependencies.
Each additional dependency represents a potential security risk
and attack vector.

**The BatConf Approach**

By providing core functionality through the standard library
and additional features through optional extras,
BatConf demonstrates how thoughtful dependency management can significantly
reduce supply chain risks.
This "pay for what you need" approach ensures that applications carry only the
dependencies they actually use.

Using batconf in your project does not bring any implicit dependencies

**Optional Extras**

Optional extras, such as Yaml support, should be explicitly documented
in your project's requirements.

Projects which only require Yaml for BatConf should document this explicitly:

.. code-block:: TOML
    :caption: pyproject.toml

    dependencies = [
        "batconf[yaml]>=0.2",
    ]

Projects which require Yaml for their core functionality and for BatConf
should make make this explicit.

.. code-block:: TOML
    :caption: pyproject.toml

    dependencies = [
        "batconf[yaml]>=0.2",
        "pyyaml=*",
    ]


.. _upcoming_changes_in_02x:

Big changes coming in 0.2.x
---------------------------

**Possible breaking changes and new features**

- **Optional Yaml dependency**

  - Yaml has been a hard-coded dependency, after 0.2.0 is released it will
    become an optional extra.
  - We are adding more support for more config file types (.ini and .toml)
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

- **More Flexible Configuration Structure**

  - Originally, batconf required the config structure to match the project's module structure.
    This worked in the context of the original Basic Automation Tool project,
    but its limits have become apparent.
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
