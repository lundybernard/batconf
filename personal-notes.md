# Configuration management for Python projects


## Abstract
Configuration management is a common pain point for Python developers,
especially as applications grow and environments become more complex.

In this presentation, we will explore these challenges in detail 
 and present best practices for managing configurations effectively. 
Finally, we’ll introduce **BatConf**, 
 a Python module built to help you address these issues. 
Through practical examples, we will demonstrate how BatConf simplifies 
 configuration tasks, and integrates seamlessly into Python projects.


# Presentation Outline: BatConf

## Title Slide
- **Title**: Configuration management for Python projects
- **Presenter**: Lundy Bernard
- **Affiliation**: Project Maintainer

---

## 1. Introduction (2 minutes)
- **Introduce Yourself**:
  - Lundy Bernard, Project Maintainer.
  - Background: Sr. Software Engineer, Traditional non-academic path.
- **Set the Stage**:
  - Clear, catchy statement about the problem your project addresses.
    - Config management is frequently a problem that we overlook, 
      until it suddenly becomes a critical feature.
  - Why this problem matters.
    - Hastily implemented solutions quickly become the source of more problems.
    - Configs are naturally rigid, and difficult to update once defined.
    - Serving many users: 
      - ask your friends in Operations about deploying containers.
      - ask your scientist friends about managing environment variables.
    - Localization
- **Purpose of the Talk**:
  - By the end of the talk, the audience will:
    - Understand the challenges and dangers Config Management presents.
    - Learn techniques to address these issues.
    - Have a new tool in their Python development kit.

---

## 2. Problem Statement (3 minutes)
- **The Problem**:
  Configuration Management (CM) is something every developer has to deal with, 
  even with very simple scripts or apps.

  Without a robust framework, 
  developers often find themselves writing redundant code
  or patching together inconsistent solutions.

  - Blank Slate problem:
    - lack of template/framework for guidance, how-to guides and walkthroughs.
  - Users with different needs: how do we make everyone happy?
  - Painting yourself into a corner:
    - CM is a hard problem
    - Incremental solutions often lead to dead-ends, and rigid code.
  - localization:
    - support for multiple languages, is a configuration problem.

- **Challenges Before This Project**:
  - Knowing where to start, lacking clear guidelines, and re-inventing the wheel.
  - How will your project serve users with different configuration needs?
    - config files, Environment variables, CLI arguments, Config management systems, ...
  - How will you handle conflicts between different config sources?
  - How will you over-write a setting for a single execution?
- **Lead into Your Solution**:
  How Batconf addresses these issues
    - It provides a structure to help you bootstrap your config management.
    - Multi-Source Configuration Merging
    - Extensability: Add new config sources to suit your needs

---

## 3. Project Overview (8 minutes)

- **Introduce the Project**:
  - Elevator pitch: "BatConf is a lightweight, respectful, extendable
     solution for your project's configuration management needs"

- **Key Features**:
  - Multi-Source Configuration Merging
     - Seamlessly integrate configurations from environment variables, 
       files (YAML, JSON, etc.), and command-line arguments 
       into a single unified structure.
  - Merge and Precedence Rules
    - Automatically resolve conflicts between multiple configuration sources 
      using a deterministic precedence hierarchy.
  - Environment-Aware Configurations
     - Easily adapt configurations for multiple environments 
       (e.g., development, testing, production)
  - Clean and Pythonic API
    - A simple, intuitive interface that enables developers to load, access, 
      and manage configurations with minimal boilerplate
  - Testability
    - Encourages testable configuration workflows by providing clear APIs 
      and structured configuration management.

- **Design Philosophy**:
  - Minimize dependencies: 
    - stdlib only
    - yaml is an optional extra
  - Respect your user's codebase:
    - Limit required imports to a single file
    - Provide simple, elegant API
  - Be flexable: Allow users to build the config that works for them
  - Be extendable: Allow users to utilize any config source they dream up.

---

## 4. Code Walkthrough (10 minutes)
In this walkthrough, I’ll focus on the core logic 
behind how `BatConf` merges configurations from multiple sources, 
demonstrating the clean API and extensibility of the library.
Ref: [Introduction
 
- **High-Level Workflow**:
  - Walk through the main workflow with code snippets:
    1. Create a Config dataclass for the project
    2. Define your get_config method
    3. Create config files
    4. Use the Configuration object to access values
- **Deep Dive into Core Functions**:
  - dataclass based configuration definition and structure
  - Integration with your CLI (argparse)
- **Example Use Cases**:
  - [Tested Example Code](https://github.com/lundybernard/batconf/tree/main/tests/example)
  - [Document Introduction](https://batconf.readthedocs.io/en/latest/intro.html)
  - [Quick Start Guide](https://batconf.readthedocs.io/en/latest/quickstart.html)

---

## 5. Results and Benefits (5 minutes)
- **Results**:
  - Demonstrate how your solution works effectively:
    - Simplifies code complexity.
    - Reduces redundant data-processing steps.
- **Comparison with Alternatives**:
  - [Dynaconf](https://www.dynaconf.com/)
    - Pros: Validation and Interpolation, nice config API
    - Cons: dependencies(vendored), and Interpolation
  - [python-decouple](https://pypi.org/project/python-decouple/)
    - Pros: No dependencies, simple and straight-forward
    - Cons: Only supports ENV based configuration.
  - [ConfigParser](https://docs.python.org/3/library/configparser.html)
    - Pros: It's in stdlib, Interpolation support
    - Cons: No ENV or hierarchical merge, limited supported sources. 

- **Community Impact**:
  BatConf encourages best practices in configuration management 
  by providing a clear, structured path for handling configurations, 
  making it easier for developers and scientists
  to build scalable and maintainable codebases.

---

## 6. Future Directions (2 minutes)
- **Planned Features**:
  - Adding more builtin sources.
  - Additional documentation and example code
  - More extensive walkthrough for setting up a new project
- **Open Challenges**:
  - Document and demonstrate multi-stage configs
    - pre-config to modify behavior of the configuration manager
    - configurable config file locations
    - allow devs to warn or fail when a config file is not found.
  - Decide if we should cache, or re-load values.  
    - Should values be changeable durring runtime?
    - maybe make the behavior configurable with a reasonable default ;)
  - Should we build a CLI to help explore configs, and bootstrap projects?
- **Collaboration Opportunities**:
  - Check out open issues on our [github repo](https://github.com/lundybernard/batconf) 

---

## 7. Conclusion and Call to Action (2 minutes)
- **Recap Key Takeaways**:
  - What problem does this project solve?
  - What makes it unique?
  - How does it benefit the community?
- **Call to Action**:
  - Where to find the project:
    - [github](https://github.com/lundybernard/batconf)
    - [readthedocs](https://batconf.readthedocs.io/en/latest/index.html)
    - [pypi]()
  - Encourage the audience to:
    - Try it out in their workflows.
    - Provide feedback and suggestions.
    - Contribute via pull requests or issue tracking.
- **Thank the Audience**:
  - Always thank them for their time and questions.

---

## 8. Q&A (5 minutes)
- Leave a slide with "Questions?" or the project logo to visually prompt the audience.
- Engage politely and concisely with questions.
  - If a question falls outside your scope, offer to follow up after the session!

---

## Tips for Markdown to Slides Conversion
If you're using tools like [Reveal.js](https://revealjs.com/), [RMarkdown](https://rmarkdown.rstudio.com/), or [Marp](https://marp.app/):
- Add slide breaks using `---` between sections.
- Use bullet points consistently for clarity.
- Highlight code snippets by wrapping them in triple backticks (e.g., ` ```python `).

---

Lauren's Awesome Edits!!!

                                |.
                               ::.
                               :::
              ___              |::
             `-._''--.._       |::
                 `-._   `-._  .|::
                    `-._    `-::::
                       `.     |:::.
                         )    |::`:"-._ 
                       <'   _.7  ::::::`-,.._
                        `-.:        `` '::::::".
                        .:'       .    .   `::::\
                      .:'        .           .:::}
                   _.:'    __          .     :::/
     ,-.___,,..--'' --.""``  ``"".-- --,.._____.-.
    ((   ___ """   -- ...     ....   __  ______  (D
     "-'`   ```''-.  __,,.......,,__      ::.  `-"
                   `<-....,,,,....-<   .:::'
                     "._       ___,,._:::(
                        ::--=''       `\:::.
                       / :::'           `\::.
            pils      / ::'               `\::
                     / :'                   `\:
                    ( /                       `"
                     "
# Configuration management for Python projects

Abstract

Configuration management is a common pain point that affects all aspects of Python development, from running a single script in a notebook, integrating libraries into research projects, to managing fully scaled and deployed applications. Without a robust framework to guide the design of configuration management, developers often find themselves writing redundant code or patching together inconsistent solutions. Hastily implemented solutions can be rigid, difficult to update, and quickly become the source of more problems.

We will explore these challenges in detail and present best practices for managing configurations effectively. Finally, we'll introduce Batconf, a python module built to provide a framework that addresses these challenges. Through practical examples, we will demonstrate how BatConf simplifies configuration tasks for new or existing Python projects, while following the design principles that will allow projects to scale and grow.


Description

Configuration management is a difficult and complex task that all developers and data scientists must eventually grapple with. Even basic scripts include elements that present configuration challenges, such as file paths, runtime behavior flags, server addresses and port settings. Configurations can be defined in a variety of sources (config files, environment variables, CLI arguments, external config management systems, application frameworks) that can conflict with each other. Configuration settings are frequently tied to the context in which the code is run, which can change as projects grow and scale.  Different users of your code such as collaborators, downstream projects, or deployment managers may have specific requirements for handling configurations. 

We will explore how the current Python ecosystem fails to provide robust guidance or templates for best practices in dealing with these challenges of configuration management, and the problems that can arise from dealing with configurations improperly or too late in project development.

The BatConf Project was developed as a response to these challenges. BatConf encourages best practices in configuration management by providing clear, structured guidelines for handling configurations, making it easier for developers and scientists to build scalable and maintainable codebases. The BatConf package is a lightweight, respectful, extendable solution that can be easily integrated into existing projects or used to bootstrap config management for new projects. 

We will discuss how the BatConf Project focuses on important design principles including:
- Minimize dependencies: stdlib only with yaml as an optional extra, builtin dataclasses as config objects
- Respect your user's codebase: limit required imports to a single file and provide a simple, elegant API
- Be flexible: allow users to build the config that works for them
- Be extendable: allow users to utilize any config source they dream up
- Be testable: support maintainability by extending test coverage to configuration management

We will also discuss how important features of the Batconf package follow those design principles, including walkthroughs of example cases. Some of these features are:

Multi-Source Configuration Merging
- Seamlessly integrates configurations from environment variables, files (YAML, JSON, etc.), and command-line arguments into a single unified structure.

Merge and Precedence Rules
- Automatically resolves conflicts between multiple configuration sources using a deterministic precedence hierarchy.

Environment-Aware Configurations
- Easily adapt configurations for multiple environments

Clean and Pythonic API
- A simple, intuitive interface that enables developers to load, access, and manage configurations with minimal boilerplate

Testability
- Encourages testable configuration workflows with 100% test coverage by providing clear APIs and structured configuration management
	

Project Links
github: https://github.com/lundybernard/batconf
readthedocs: https://batconf.readthedocs.io/en/latest/index.html


(in the NOTES section)
- extra info about that sexy presenter
- plans for batconf dev before scipy convention

