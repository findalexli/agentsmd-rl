#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fledge

# Idempotency guard
if grep -qF "- All log entries should be written to be human readable and standalone from the" ".cursor/rules/C/core.mdc" && grep -qF "|kvlist|A key value pair list. The key is a string value always but the value of" ".cursor/rules/C/plugins/filter.mdc" && grep -qF "|kvlist|A key value pair list. The key is a string value always but the value of" ".cursor/rules/C/plugins/north.mdc" && grep -qF "|kvlist|A key value pair list. The key is a string value always but the value of" ".cursor/rules/C/plugins/south.mdc" && grep -qF "\u2502\u00a0\u00a0 \u251c\u2500\u2500 core.mdc          # Core C++ Standards + + platform requirements" ".cursor/rules/README.md" && grep -qF "# Fledge Notification Service - Feature Development Rules (MDC Format)" ".cursor/services/notification.mdc" && grep -qF "This MDC file serves as a comprehensive guide for AI-assisted development and co" ".cursor/services/notification_code_review.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/C/core.mdc b/.cursor/rules/C/core.mdc
@@ -0,0 +1,156 @@
+---
+description: Enforce C++11 coding standards for Fledge plugins.
+globs: ["*.cpp", "*.h"]
+alwaysApply: true
+author: "Devki Nandan Ghildiyal"
+---
+
+##  Fledge Project Context
+
+- **Language Focus**: C++11
+- **Primary Target**: South/North/Filter plugins
+- **Tech Stack**
+  - **Languages** : C++11
+  - **Libraries** : GTest version 1.10.0, boost version 1.71
+  - **Database** : SQLite version 3, Postgres version 12
+
+
+# Roles
+
+## Senior Architect
+- Focus: System design, scalability, security, module boundaries, third-party integrations
+- Responsibilities:
+  - Review requirements and suggest if any gap is there in the requirement.
+  - Suggest design patterns, scalability strategies, and deployment models.
+  - Validate alignment with NFRs (non-functional requirements).
+
+## Senior Developer
+- Focus: Implementation, performance, maintainability, code quality
+- Responsibilities:
+  - Review core logic, refactoring, and REST API contracts.
+  - Ensure idiomatic usage of C++11 standards.
+  - Enforce clean coding practices and SOLID principles.
+  - Fledge plugin API and extension points  
+  - Filter pipeline structure and reading processing logic  
+  - South/North plugin lifecycle
+
+## Senior QA Engineer
+- Focus: Test coverage, edge cases, negative scenarios, automation
+- Responsibilities:
+  - Review requirements and prepare test plan
+  - Validate test plans and coverage.
+  - Suggest boundary tests, failure modes, stress scenarios.
+  - Generate unit tests using GTest version 1.10.0 
+  - Review unit test structure.
+  
+
+You are playing **three roles** while reviewing, commenting, or helping with with deep knowledge of Fledge:
+
+1. **Senior Architect** – Guide the system and module design.
+2. **Senior Developer** – Evaluate the code quality and implementation.
+3. **Senior QA Engineer** – Think from a test and validation standpoint.
+
+Respond with comments or suggestions **clearly labeled** by the role, e.g.:
+
+- `[Architect] Analyze requirements.md file to find out gaps in requirements if any.`
+- `[Developer] Use range-based loops.`
+- `[QA] Add unit tests for empty asset name.`
+
+
+## Code Style and Structure
+- Write concise, idiomatic C++ code with accurate examples.
+- Follow modern C++11 conventions and best practices.
+- Use object-oriented, procedural, or functional programming patterns as appropriate.
+- Leverage STL and standard algorithms for collection operations.
+- Use descriptive variable and method names (e.g., 'isUserSignedIn', 'calculateTotal').
+- Structure files into headers (*.h) and implementation files (*.cpp) with logical separation of concerns.
+
+## Naming Conventions
+- Use PascalCase for class names.
+- Use camelCase for variable names and methods.
+- Use SCREAMING_SNAKE_CASE for constants and macros.
+- Prefix member variables with an m_ (e.g., `m_userId`).
+
+## C++ Features Usage
+
+- Prefer modern C++11 features (e.g., auto, range-based loops).
+- Use `constexpr` and `const` to optimize compile-time computations.
+
+## Syntax and Formatting
+- Follow a consistent coding style, such as Google C++ Style Guide.
+- Place braces on the same line for control structures and methods.
+- Use clear and consistent commenting practices.
+
+## JSON Parsing
+- Fledge uses RapidJSON for JSON parsing by using C++ '*.h' files from '../../../C/thirdparty/rapidjson/include/rapidjson/'
+
+## REST API Support
+- Fledge supports REST API by using C++ files from '../../../C/thirdparty/Simple-Web-Server'
+
+## Error Handling and Validation
+- Use exceptions for error handling (e.g., `std::runtime_error`, `std::invalid_argument`).
+- Use RAII for resource management to avoid memory leaks.
+- Validate inputs at function boundaries.
+- Log errors using a logging class logger.h from '../../../C/common/include/logger.h'
+
+## Performance Optimization
+- Avoid unnecessary heap allocations; prefer stack-based objects where possible.
+- Use `std::move` to enable move semantics and avoid copies.
+- Optimize loops with algorithms from `<algorithm>` (e.g., `std::sort`, `std::for_each`).
+- Profile and optimize critical sections with tools like Valgrind.
+
+## Key Conventions
+- Do not use smart pointers.
+- Avoid global variables; use singletons sparingly.
+- Use `enum class` for strongly typed enumerations.
+- Separate interface from implementation in classes.
+- Use templates and metaprogramming judiciously for generic solutions.
+
+## Testing
+- Write unit tests using frameworks like Google Test (GTest version 1.10.0).
+- Mock dependencies with libraries like Google Mock.
+- Implement integration tests for system components.
+
+## Security
+- Use secure coding practices to avoid vulnerabilities (e.g., buffer overflows, dangling pointers).
+- Prefer `std::array` or `std::vector` over raw arrays.
+- Avoid C-style casts; use `static_cast`, `dynamic_cast`, or `reinterpret_cast` when necessary.
+- Enforce const-correctness in functions and member variables.
+
+## Documentation
+- Write clear comments for classes, methods, and critical logic.
+- Use Doxygen for generating API documentation.
+- Document assumptions, constraints, and expected behavior of code. All public classes and methods must include Doxygen comments specifying assumptions, constraints, and expected input/output.
+
+Follow the official ISO C++ standards and guidelines for best practices in modern C++11 development.
+
+## C++ south plugin development
+
+- Use 'plugins/south.mdc'
+
+## C++ north plugin development
+
+- use 'plugins/north.mdc'
+
+## C++ Filter plugin development
+
+- use 'plugins/filter.mdc'
+
+## Log Levels
+
+Fledge support 5 levels of logging, which can be considered in descending order of severity; fatal, error, warning, info and debug. Each of these has a defined use and a targeted audience. By default only the 3 most severe levels of log will be written and presented to the user.
+
+| Log Level | Intended Audience | Usage |
+| :---- | :---- | :---- |
+| fatal | End-user | This is the most severe error level and is reserved for situations whereby the service that raises them can not continue. It is not for transient failures. |
+| error | End-user | Errors should be used when a transient issue prevents the service continuing in the short term, but may be recovered without the service restarting. |
+| warning | End-user | A warning message should be used if the user needs to be aware of some reduction in service or non-fatal issue that does not stop the flow of data. |
+| info | Code/Pipeline Developer | Informational messages should be used to give the user or developer more information as to the progress of a process or task, but does not impact the result of that task. It can be considered more as a progress tracking aid. |
+| debug | Code Developer | Debug messages are reserved for the code developers working on a plugin or core features of the Fledge services. |
+
+# Message Content Fog Logs
+
+- All log entries should be written to be human readable and standalone from the code that raises them. The reader of the log message should not need to have access to the source code in order to understand a log message. They should not include internal code references or variable names, but rather be descriptive regarding any variables printed in the log.
+- Log messages should not contain source file names, line numbers or function names as these have little to no meaning to the intended audience for the majority of log messages These also take up valuable space that can be better used to give a more in-depth description of the issue.
+- Not only are the lengths of messages limited in syslog, but special characters such as new lines and carriage returns are mapped to hash codes and hence do not format correctly. Messages should not include such characters and should be simple strings.
+
diff --git a/.cursor/rules/C/plugins/filter.mdc b/.cursor/rules/C/plugins/filter.mdc
@@ -0,0 +1,296 @@
+---
+description: C++ Filter Plugin Architecture.
+globs: ["*.cpp", "*.h"]
+alwaysApply: true
+author: "Devki Nandan Ghildiyal"
+---
+
+## Filter Plugin
+
+- Filter plugin provides a mechanism to alter data as it flows from sensor to Fledge, or from Fledge to outside. 
+
+
+## General plugin guidelines
+
+- General guidelines to write a Fledge plugin is at '../../../docs/plugin_developers_guide/02_writing_plugins.rst' file
+
+## South plugin Guidelines
+
+- Specific guidelines to write a north plugin is at '../../../docs/plugin_developers_guide/06_filter_plugins.rst'
+
+
+## Common support classes
+
+- Information about common support classes used by plugin is at '../../../docs/plugin_developers_guide/035_CPP.rst'
+
+## Mutex and Locking
+
+- Thread Safety: The fledge filter plugin can receive data (ingest()) and configuration changes (reconfigure()) simultaneously from different threads
+- Data Consistency: Prevents reading configuration while it's being modified
+- RAII Pattern: std::lock_guard automatically unlocks when going out of scope, preventing deadlocks
+
+- Following sample code demonstrates use of mutex and locks when doing ingestion
+
+```
+void ingest(std::vector<Reading *> *readings, std::vector<Reading *>& outReadings)
+{
+    std::lock_guard<std::mutex> guard(m_configMutex);
+    IngestData(readings, outReadings);
+    readings->clear();
+}
+
+```
+
+- Following sample code demonstrates use of mutex and locks when doing configuration changes
+
+```
+void reconfigure(const std::string& conf)
+{
+    std::lock_guard<std::mutex> guard(m_configMutex);
+    setConfig(conf);
+    handleConfig(m_config);
+}
+
+```
+
+## Implementation details of plugin
+
+- South plugin fetches data from sensors or external sources and store in Fledge
+- Common C++ classes used in Fledge framework are at following location '../../../C/common/include' and '../../../C/common/'
+- C++ class to handle reading in Fledge is at '../../../C/common/include/reading.h'
+- C++ class to handle datapoint in Fledge is at '../../../C/common/include/datapoint.h'
+- C++ class to handle logging in Fledge is at '../../../C/common/include/logger.h'
+- C++ plugin must have a 'plugin.cpp' file
+- 'plugin.cpp' file must have plugin configuration and 
+- Implementation of requirement of plugin is kept into a separate header and class implementation file which is used by 'plugin.cpp' file
+- Every plugin has 'docs' and 'tests' directory
+- 'plugin.cpp' must define plugin of the configuration
+
+## Fledge plugin configuration
+
+Every Fledge plugin has a default configuration represented by a JSON.
+
+Following example demonstrates minimial configurtion for every plugin. configuration JSON for each plugin must have an elments called "plugin"
+
+
+```
+const char *default_config = QUOTE({
+              "plugin" : {
+                      "description" : "My example plugin in C++",
+                      "type" : "string",
+                      "default" : "MyPlugin",
+                      "readonly" : "true"
+                      }
+});
+```
+
+- constant default_config is a string that contains the JSON configuration document.
+- QUOTE macro is used to manage JSON document easily
+- Configuation JSON documment will have multiple elements for each configuration item.
+- Fledge plugin supports following types
+
+| Type | Description | 
+|:-----|:------------|
+|integer|An integer numeric value. The minimum and maximum properties may be used to control the limits of the values assigned to an integer.|
+|float|A floating point numeric item. The minimum and maximum properties may be used to control the limits of the values assigned to a float.|
+|string|An alpha-numeric array of characters that may contain any printable characters. The length property can be used to constrain the maximum length of the string.|
+|password|It is same as string type. User interfaces do not show this in plain text.|
+|boolean|A boolean value that can be assigned the values true or false.|
+|enumeration|The item can be assigned one of a fixed set of values. These values are defined in the options property of the item.|
+|list|A list of items, the items can be of type string, integer, float, enumeration or object. The type of the items within the list must all be the same, and this is defined via the items property of the list. A limit on the maximum number of entries allowed in the list can be enforced by use of the listSize property.|
+|kvlist|A key value pair list. The key is a string value always but the value of the item in the list may be of type string, enumeration, float, integer or object. The type of the values in the kvlist is defined by the items property of the configuration item. A limit on the maximum number of entries allowed in the list can be enforced by use of the listSize property.|
+|object|A complex configuration type with multiple elements that may be used within list and kvlist items only, it is not possible to have object type items outside of a list. Object type configuration items have a set of properties defined, each of which is itself a configuration item.|
+
+## Example for integer type
+
+Sample configuration item "register"
+
+```
+ "register" : {
+			  "description" : "The register number to read",
+			  "displayName" : "Register",
+			  "type" : "integer",
+			  "default" : "0",
+			  "order" : "1"
+			  }
+```
+
+## Example for integer type
+
+Sample configuration item "temperature"
+
+```
+ "temperature" : {
+			  "description" : "Temperate of PLC",
+			  "displayName" : "PLC Temperature",
+			  "type" : "float",
+			  "default" : "0",
+			   "order" : "2"
+			  }
+
+```
+
+## Example for string type
+
+Sample configuration item "asset"
+
+```
+"asset" : {
+		  "description" : "The name of the asset the plugin will produce",
+		  "displayName" : "Asset Name",
+		  "type" : "string",
+		  "default" : "MyAsset",
+		   "order" : "3"
+		  }
+```
+
+## Example of password type
+
+Sample configuration item "db_password"
+
+```
+"db_password" : {
+		  "description" : "Password of the database",
+		  "displayName" : "Database Password",
+		  "type" : "boolean",
+		  "default" : "MyAsset",
+		   "order" : "4"
+		  }
+```
+
+## Example of boolean type
+
+Sample configuration item "apply_scaling"
+
+```
+"apply_scaling": {
+				"description": "Option to apply scaling",
+				"displayName": "Use Scaling"
+				"type": "boolean",
+				"default": "true",
+				 "order" : "5"
+			}
+```
+
+## Example of enumeration type
+
+Sample configuration item "authentication"
+
+```
+"authentication": {
+  "description": "Server Authentication",
+  "displayName": "Authentication",
+  "type": "enumeration",
+  "options": [
+    "mandatory",
+    "optional"
+  ],
+  "default": "optional",
+   "order" : "6"
+  
+}
+```
+
+## Example of list type
+
+Sample configuration item "tags"
+
+```
+"tags" : {
+               "description" : "A set of tag names on which to operate",
+			   "displayName" : "Labels",
+               "type" : "list",
+               "items" : "string",
+               "default" : "[ \"speed\", \"temperature\", \"voltage\" ]",
+               "order" : "7"
+               
+          }
+
+```
+
+## Example of kvlist type
+
+Sample configuration item "expressions"
+
+```
+"expressions" : {
+              "description" : "A set of expressions used to evaluate and label data",
+			  "displayName" : "Labels",
+              "type" : "kvlist",
+              "items" : "string",
+              "default" : "{\"idle\" : \"speed == 0\"}",
+              "order" : "8"
+              
+              }
+```
+
+## Example of object type
+
+Sample configuration item "map" 
+
+```
+"map": {
+      "description": "A list of datapoints to read and PLC register definitions",
+      "type": "list",
+      "items" : "object",
+      "default": "[ { \"datapoint\" : \"speed\", \"register\" : \"10\", \"width\" : \"1\", \"type\" : \"integer\"} ]",
+      "order" : "3",
+      "displayName" : "PLC Map",
+      "properties" : {
+              "datapoint" : {
+                      "description" : "The name of the datapoint to create for the map entry",
+                      "displayName" : "Datapoint",
+                      "type" : "string",
+                      "default" : "datapoint"
+                      },
+              "register" : {
+                      "description" : "The register number to read",
+                      "displayName" : "Register",
+                      "type" : "integer",
+                      "default" : "0"
+                      },
+              "width" : {
+                      "description" : "Number of registers to read",
+                      "displayName" : "Width",
+                      "type" : "integer",
+                      "maximum" : "4",
+                      "default" : "1"
+                      },
+              "type" : {
+                      "description" : "The data type to read",
+                      "displayName" : "Data Type",
+                      "type" : "enumeration",
+                      "options" : [ "integer","float", "boolean" ],
+                      "default" : "integer"
+                      }
+              }
+      }
+```
+
+## Supported Poperties by configuration items in configuration JSON document
+
+|Property|Description|
+|:-----|:------------|
+|default|The default value for the configuration item. This is always expressed as a string regardless of the type of the configuration item.|
+|deprecated|A boolean flag to indicate that this item is no longer used and will be removed in a future release.|
+|description|A description of the configuration item used in the user interface to give more details of the item. Commonly used as a mouse over help prompt.|
+|displayName|The string to use in the user interface when presenting the configuration item. Generally a more user friendly form of the item name. Item names are referenced within the code.|
+|items|The type of the items in a list or kvlist configuration item.|
+|length|The maximum length of the string value of the item.|
+|listSize|The maximum number of entries allowed in a list or kvlist item.|
+|mandatory|A boolean flag to indicate that this item can not be left blank.|
+|maximum|The maximum value for a numeric configuration item.|
+|minimum|The minimum value for a numeric configuration item.|
+|options|Only used for enumeration type elements. This is a JSON array of string that contains the options in the enumeration.|
+|order|Used in the user interface to give an indication of how high up in the dialogue to place this item.|
+|group|Used to group related items together. The main use of this is within the GUI which will turn each group into a tab in the creation and edit screens.|
+|readonly|A boolean property that can be used to include items that can not be altered by the API.|
+|rule|A validation rule that will be run against the value. This must evaluate to true for the new value to be accepted by the API|
+|type|The type of the configuration item. The list of types supported are; integer, float, string, password, enumeration, boolean, list, kvlist, JSON, URL, IPV4, IPV6, script, code, X509 certificate and northTask.|
+|validity|An expression used to determine if the configuration item is valid. Used in the UI to gray out one value based on the value of others.|
+|value|The current value of the configuration item. This is not included when defining a set of default configuration in, for example, a plugin.|
+|properties|A set of items that are used in list and kvlist type items to create a list of groups of configuration items.|
+|keyName|A display name to be used for entry and display of key in the key-value list type, with item being an object.|
+|keyDescription|A description of key value in the key-value list type, with item being an object.|
+|permissions|An array of user roles that are allowed to update this configuration item. If not given then the configuration item can be updated by any user. If the permissions property is included in a configuration item the array must have at least one entry.|
+
diff --git a/.cursor/rules/C/plugins/north.mdc b/.cursor/rules/C/plugins/north.mdc
@@ -0,0 +1,302 @@
+---
+description: C++ North Plugin Architecture.
+globs: ["*.cpp", "*.h"]
+alwaysApply: true
+author: "Devki Nandan Ghildiyal"
+---
+
+## North Plugin
+
+- North plugin extracts data stored into the Fledge and sends it out side to Fledge.
+- North plugin can send data to a server, a service in the cloud, or other Fledge instance.
+
+
+## General plugin guidelines
+
+- General guidelines to write a Fledge plugin is at '../../../docs/plugin_developers_guide/02_writing_plugins.rst' file
+
+## South plugin Guidelines
+
+- Specific guidelines to write a north plugin is at '../../../docs/plugin_developers_guide/04_north_plugins.rst'
+
+## Persisting Data 
+
+- Persistence feature can be implemented in the plugin to persist state between the execution of plugin.
+
+- Guidelines to implement persistance feature is at '../../../docs/plugin_developers_guide/02_persisting_data.rst'
+
+## Common support classes
+
+- Information about common support classes used by plugin is at '../../../docs/plugin_developers_guide/035_CPP.rst'
+
+## Mutex and Locking
+
+- Thread Safety: The fledge north plugin can send data (send()) and configuration changes (reconfigure()) simultaneously from different threads
+- Data Consistency: Prevents reading configuration while it's being modified
+- RAII Pattern: std::lock_guard automatically unlocks when going out of scope, preventing deadlocks
+
+- Following sample code demonstrates use of mutex and locks when sending data
+
+```
+void send(std::vector<Reading *> *readings, std::vector<Reading *>& outReadings)
+{
+    std::lock_guard<std::mutex> guard(m_configMutex);
+    sendData(readings, outReadings);
+    readings->clear();
+}
+
+```
+
+- Following sample code demonstrates use of mutex and locks when doing configuration changes
+
+```
+void reconfigure(const std::string& conf)
+{
+    std::lock_guard<std::mutex> guard(m_configMutex);
+    setConfig(conf);
+    handleConfig(m_config);
+}
+
+```
+
+## Implementation details of plugin
+
+- South plugin fetches data from sensors or external sources and store in Fledge
+- Common C++ classes used in Fledge framework are at following location '../../../C/common/include' and '../../../C/common/'
+- C++ class to handle reading in Fledge is at '../../../C/common/include/reading.h'
+- C++ class to handle datapoint in Fledge is at '../../../C/common/include/datapoint.h'
+- C++ class to handle logging in Fledge is at '../../../C/common/include/logger.h'
+- C++ plugin must have a 'plugin.cpp' file
+- 'plugin.cpp' file must have plugin configuration and 
+- Implementation of requirement of plugin is kept into a separate header and class implementation file which is used by 'plugin.cpp' file
+- Every plugin has 'docs' and 'tests' directory
+- 'plugin.cpp' must define plugin of the configuration
+
+## Fledge plugin configuration
+
+Every Fledge plugin has a default configuration represented by a JSON.
+
+Following example demonstrates minimial configurtion for every plugin. configuration JSON for each plugin must have an elments called "plugin"
+
+
+```
+const char *default_config = QUOTE({
+              "plugin" : {
+                      "description" : "My example plugin in C++",
+                      "type" : "string",
+                      "default" : "MyPlugin",
+                      "readonly" : "true"
+                      }
+});
+```
+
+- constant default_config is a string that contains the JSON configuration document.
+- QUOTE macro is used to manage JSON document easily
+- Configuation JSON documment will have multiple elements for each configuration item.
+- Fledge plugin supports following types
+
+| Type | Description | 
+|:-----|:------------|
+|integer|An integer numeric value. The minimum and maximum properties may be used to control the limits of the values assigned to an integer.|
+|float|A floating point numeric item. The minimum and maximum properties may be used to control the limits of the values assigned to a float.|
+|string|An alpha-numeric array of characters that may contain any printable characters. The length property can be used to constrain the maximum length of the string.|
+|password|It is same as string type. User interfaces do not show this in plain text.|
+|boolean|A boolean value that can be assigned the values true or false.|
+|enumeration|The item can be assigned one of a fixed set of values. These values are defined in the options property of the item.|
+|list|A list of items, the items can be of type string, integer, float, enumeration or object. The type of the items within the list must all be the same, and this is defined via the items property of the list. A limit on the maximum number of entries allowed in the list can be enforced by use of the listSize property.|
+|kvlist|A key value pair list. The key is a string value always but the value of the item in the list may be of type string, enumeration, float, integer or object. The type of the values in the kvlist is defined by the items property of the configuration item. A limit on the maximum number of entries allowed in the list can be enforced by use of the listSize property.|
+|object|A complex configuration type with multiple elements that may be used within list and kvlist items only, it is not possible to have object type items outside of a list. Object type configuration items have a set of properties defined, each of which is itself a configuration item.|
+
+## Example for integer type
+
+Sample configuration item "register"
+
+```
+ "register" : {
+			  "description" : "The register number to read",
+			  "displayName" : "Register",
+			  "type" : "integer",
+			  "default" : "0",
+			  "order" : "1"
+			  }
+```
+
+## Example for integer type
+
+Sample configuration item "temperature"
+
+```
+ "temperature" : {
+			  "description" : "Temperate of PLC",
+			  "displayName" : "PLC Temperature",
+			  "type" : "float",
+			  "default" : "0",
+			   "order" : "2"
+			  }
+
+```
+
+## Example for string type
+
+Sample configuration item "asset"
+
+```
+"asset" : {
+		  "description" : "The name of the asset the plugin will produce",
+		  "displayName" : "Asset Name",
+		  "type" : "string",
+		  "default" : "MyAsset",
+		   "order" : "3"
+		  }
+```
+
+## Example of password type
+
+Sample configuration item "db_password"
+
+```
+"db_password" : {
+		  "description" : "Password of the database",
+		  "displayName" : "Database Password",
+		  "type" : "boolean",
+		  "default" : "MyAsset",
+		   "order" : "4"
+		  }
+```
+
+## Example of boolean type
+
+Sample configuration item "apply_scaling"
+
+```
+"apply_scaling": {
+				"description": "Option to apply scaling",
+				"displayName": "Use Scaling"
+				"type": "boolean",
+				"default": "true",
+				 "order" : "5"
+			}
+```
+
+## Example of enumeration type
+
+Sample configuration item "authentication"
+
+```
+"authentication": {
+  "description": "Server Authentication",
+  "displayName": "Authentication",
+  "type": "enumeration",
+  "options": [
+    "mandatory",
+    "optional"
+  ],
+  "default": "optional",
+   "order" : "6"
+  
+}
+```
+
+## Example of list type
+
+Sample configuration item "tags"
+
+```
+"tags" : {
+               "description" : "A set of tag names on which to operate",
+			   "displayName" : "Labels",
+               "type" : "list",
+               "items" : "string",
+               "default" : "[ \"speed\", \"temperature\", \"voltage\" ]",
+               "order" : "7"
+               
+          }
+
+```
+
+## Example of kvlist type
+
+Sample configuration item "expressions"
+
+```
+"expressions" : {
+              "description" : "A set of expressions used to evaluate and label data",
+			  "displayName" : "Labels",
+              "type" : "kvlist",
+              "items" : "string",
+              "default" : "{\"idle\" : \"speed == 0\"}",
+              "order" : "8"
+              
+              }
+```
+
+## Example of object type
+
+Sample configuration item "map" 
+
+```
+"map": {
+      "description": "A list of datapoints to read and PLC register definitions",
+      "type": "list",
+      "items" : "object",
+      "default": "[ { \"datapoint\" : \"speed\", \"register\" : \"10\", \"width\" : \"1\", \"type\" : \"integer\"} ]",
+      "order" : "3",
+      "displayName" : "PLC Map",
+      "properties" : {
+              "datapoint" : {
+                      "description" : "The name of the datapoint to create for the map entry",
+                      "displayName" : "Datapoint",
+                      "type" : "string",
+                      "default" : "datapoint"
+                      },
+              "register" : {
+                      "description" : "The register number to read",
+                      "displayName" : "Register",
+                      "type" : "integer",
+                      "default" : "0"
+                      },
+              "width" : {
+                      "description" : "Number of registers to read",
+                      "displayName" : "Width",
+                      "type" : "integer",
+                      "maximum" : "4",
+                      "default" : "1"
+                      },
+              "type" : {
+                      "description" : "The data type to read",
+                      "displayName" : "Data Type",
+                      "type" : "enumeration",
+                      "options" : [ "integer","float", "boolean" ],
+                      "default" : "integer"
+                      }
+              }
+      }
+```
+
+## Supported Poperties by configuration items in configuration JSON document
+
+|Property|Description|
+|:-----|:------------|
+|default|The default value for the configuration item. This is always expressed as a string regardless of the type of the configuration item.|
+|deprecated|A boolean flag to indicate that this item is no longer used and will be removed in a future release.|
+|description|A description of the configuration item used in the user interface to give more details of the item. Commonly used as a mouse over help prompt.|
+|displayName|The string to use in the user interface when presenting the configuration item. Generally a more user friendly form of the item name. Item names are referenced within the code.|
+|items|The type of the items in a list or kvlist configuration item.|
+|length|The maximum length of the string value of the item.|
+|listSize|The maximum number of entries allowed in a list or kvlist item.|
+|mandatory|A boolean flag to indicate that this item can not be left blank.|
+|maximum|The maximum value for a numeric configuration item.|
+|minimum|The minimum value for a numeric configuration item.|
+|options|Only used for enumeration type elements. This is a JSON array of string that contains the options in the enumeration.|
+|order|Used in the user interface to give an indication of how high up in the dialogue to place this item.|
+|group|Used to group related items together. The main use of this is within the GUI which will turn each group into a tab in the creation and edit screens.|
+|readonly|A boolean property that can be used to include items that can not be altered by the API.|
+|rule|A validation rule that will be run against the value. This must evaluate to true for the new value to be accepted by the API|
+|type|The type of the configuration item. The list of types supported are; integer, float, string, password, enumeration, boolean, list, kvlist, JSON, URL, IPV4, IPV6, script, code, X509 certificate and northTask.|
+|validity|An expression used to determine if the configuration item is valid. Used in the UI to gray out one value based on the value of others.|
+|value|The current value of the configuration item. This is not included when defining a set of default configuration in, for example, a plugin.|
+|properties|A set of items that are used in list and kvlist type items to create a list of groups of configuration items.|
+|keyName|A display name to be used for entry and display of key in the key-value list type, with item being an object.|
+|keyDescription|A description of key value in the key-value list type, with item being an object.|
+|permissions|An array of user roles that are allowed to update this configuration item. If not given then the configuration item can be updated by any user. If the permissions property is included in a configuration item the array must have at least one entry.|
+
diff --git a/.cursor/rules/C/plugins/south.mdc b/.cursor/rules/C/plugins/south.mdc
@@ -0,0 +1,317 @@
+---
+description: C++ South Plugin Architecture.
+globs: ["*.cpp", "*.h"]
+alwaysApply: true
+author: "Devki Nandan Ghildiyal"
+---
+
+## South Plugin
+
+- South plugin are of two types poll plugin and asyc plugin
+
+- Poll type plugin calls plugin_poll method at the defined interval to collect data from sensor.
+
+- Asych type plugin use some incoming event from device or callback mechanism
+
+- SP_ASYNC flag is used to support async feature
+
+- Plugin interface version 1.0.0 is used to fetch single reading
+
+- Plugin interface version 2.0.0 is used to fetch multiple readings
+
+- South plugin can be used to extract controls (Set Point Control) on the underlying device to which it is connected
+
+- SP_CONTROL Flag is used to support Set Point Control feature
+
+
+## General plugin guidelines
+
+- General guidelines to write a Fledge plugin is at '../../../docs/plugin_developers_guide/02_writing_plugins.rst' file
+
+## South plugin Guidelines
+
+- Specific guidelines to write a south plugin is at '../../../docs/plugin_developers_guide/03_south_C_plugins.rst'
+
+## Persisting Data 
+
+- Persistence feature can be implemented in the plugin to persist state between the execution of plugin.
+
+- SP_PERSIST_DATA flag is used to support persist data feature
+
+- Guidelines to implement persistance feature is at '../../../docs/plugin_developers_guide/02_persisting_data.rst'
+
+## Common support classes
+
+- Information about common support classes used by plugin is at '../../../docs/plugin_developers_guide/035_CPP.rst'
+
+## Mutex and Locking
+
+- Thread Safety: The fledge south plugin can receive data (ingest()) and configuration changes (reconfigure()) simultaneously from different threads
+- Data Consistency: Prevents reading configuration while it's being modified
+- RAII Pattern: std::lock_guard automatically unlocks when going out of scope, preventing deadlocks
+
+- Following sample code demonstrates use of mutex and locks when doing ingestion
+
+```
+void ingest(std::vector<Reading *> *readings, std::vector<Reading *>& outReadings)
+{
+    std::lock_guard<std::mutex> guard(m_configMutex);
+    IngestData(readings, outReadings);
+    readings->clear();
+}
+
+```
+
+- Following sample code demonstrates use of mutex and locks when doing configuration changes
+
+```
+void reconfigure(const std::string& conf)
+{
+    std::lock_guard<std::mutex> guard(m_configMutex);
+    setConfig(conf);
+    handleConfig(m_config);
+}
+
+```
+
+## Implementation details of plugin
+
+- South plugin fetches data from sensors or external sources and store in Fledge
+- Common C++ classes used in Fledge framework are at following location '../../../C/common/include' and '../../../C/common/'
+- C++ class to handle reading in Fledge is at '../../../C/common/include/reading.h'
+- C++ class to handle datapoint in Fledge is at '../../../C/common/include/datapoint.h'
+- C++ class to handle logging in Fledge is at '../../../C/common/include/logger.h'
+- C++ plugin must have a 'plugin.cpp' file
+- 'plugin.cpp' file must have plugin configuration and 
+- Implementation of requirement of plugin is kept into a separate header and class implementation file which is used by 'plugin.cpp' file
+- Every plugin has 'docs' and 'tests' directory
+- 'plugin.cpp' must define plugin of the configuration
+
+## Fledge plugin configuration
+
+Every Fledge plugin has a default configuration represented by a JSON.
+
+Following example demonstrates minimial configurtion for every plugin. configuration JSON for each plugin must have an elments called "plugin"
+
+
+```
+const char *default_config = QUOTE({
+              "plugin" : {
+                      "description" : "My example plugin in C++",
+                      "type" : "string",
+                      "default" : "MyPlugin",
+                      "readonly" : "true"
+                      }
+});
+```
+
+- constant default_config is a string that contains the JSON configuration document.
+- QUOTE macro is used to manage JSON document easily
+- Configuation JSON documment will have multiple elements for each configuration item.
+- Fledge plugin supports following types
+
+| Type | Description | 
+|:-----|:------------|
+|integer|An integer numeric value. The minimum and maximum properties may be used to control the limits of the values assigned to an integer.|
+|float|A floating point numeric item. The minimum and maximum properties may be used to control the limits of the values assigned to a float.|
+|string|An alpha-numeric array of characters that may contain any printable characters. The length property can be used to constrain the maximum length of the string.|
+|password|It is same as string type. User interfaces do not show this in plain text.|
+|boolean|A boolean value that can be assigned the values true or false.|
+|enumeration|The item can be assigned one of a fixed set of values. These values are defined in the options property of the item.|
+|list|A list of items, the items can be of type string, integer, float, enumeration or object. The type of the items within the list must all be the same, and this is defined via the items property of the list. A limit on the maximum number of entries allowed in the list can be enforced by use of the listSize property.|
+|kvlist|A key value pair list. The key is a string value always but the value of the item in the list may be of type string, enumeration, float, integer or object. The type of the values in the kvlist is defined by the items property of the configuration item. A limit on the maximum number of entries allowed in the list can be enforced by use of the listSize property.|
+|object|A complex configuration type with multiple elements that may be used within list and kvlist items only, it is not possible to have object type items outside of a list. Object type configuration items have a set of properties defined, each of which is itself a configuration item.|
+
+## Example for integer type
+
+Sample configuration item "register"
+
+```
+ "register" : {
+			  "description" : "The register number to read",
+			  "displayName" : "Register",
+			  "type" : "integer",
+			  "default" : "0",
+			  "order" : "1"
+			  }
+```
+
+## Example for integer type
+
+Sample configuration item "temperature"
+
+```
+ "temperature" : {
+			  "description" : "Temperate of PLC",
+			  "displayName" : "PLC Temperature",
+			  "type" : "float",
+			  "default" : "0",
+			   "order" : "2"
+			  }
+
+```
+
+## Example for string type
+
+Sample configuration item "asset"
+
+```
+"asset" : {
+		  "description" : "The name of the asset the plugin will produce",
+		  "displayName" : "Asset Name",
+		  "type" : "string",
+		  "default" : "MyAsset",
+		   "order" : "3"
+		  }
+```
+
+## Example of password type
+
+Sample configuration item "db_password"
+
+```
+"db_password" : {
+		  "description" : "Password of the database",
+		  "displayName" : "Database Password",
+		  "type" : "boolean",
+		  "default" : "MyAsset",
+		   "order" : "4"
+		  }
+```
+
+## Example of boolean type
+
+Sample configuration item "apply_scaling"
+
+```
+"apply_scaling": {
+				"description": "Option to apply scaling",
+				"displayName": "Use Scaling"
+				"type": "boolean",
+				"default": "true",
+				 "order" : "5"
+			}
+```
+
+## Example of enumeration type
+
+Sample configuration item "authentication"
+
+```
+"authentication": {
+  "description": "Server Authentication",
+  "displayName": "Authentication",
+  "type": "enumeration",
+  "options": [
+    "mandatory",
+    "optional"
+  ],
+  "default": "optional",
+   "order" : "6"
+  
+}
+```
+
+## Example of list type
+
+Sample configuration item "tags"
+
+```
+"tags" : {
+               "description" : "A set of tag names on which to operate",
+			   "displayName" : "Labels",
+               "type" : "list",
+               "items" : "string",
+               "default" : "[ \"speed\", \"temperature\", \"voltage\" ]",
+               "order" : "7"
+               
+          }
+
+```
+
+## Example of kvlist type
+
+Sample configuration item "expressions"
+
+```
+"expressions" : {
+              "description" : "A set of expressions used to evaluate and label data",
+			  "displayName" : "Labels",
+              "type" : "kvlist",
+              "items" : "string",
+              "default" : "{\"idle\" : \"speed == 0\"}",
+              "order" : "8"
+              
+              }
+```
+
+## Example of object type
+
+Sample configuration item "map" 
+
+```
+"map": {
+      "description": "A list of datapoints to read and PLC register definitions",
+      "type": "list",
+      "items" : "object",
+      "default": "[ { \"datapoint\" : \"speed\", \"register\" : \"10\", \"width\" : \"1\", \"type\" : \"integer\"} ]",
+      "order" : "3",
+      "displayName" : "PLC Map",
+      "properties" : {
+              "datapoint" : {
+                      "description" : "The name of the datapoint to create for the map entry",
+                      "displayName" : "Datapoint",
+                      "type" : "string",
+                      "default" : "datapoint"
+                      },
+              "register" : {
+                      "description" : "The register number to read",
+                      "displayName" : "Register",
+                      "type" : "integer",
+                      "default" : "0"
+                      },
+              "width" : {
+                      "description" : "Number of registers to read",
+                      "displayName" : "Width",
+                      "type" : "integer",
+                      "maximum" : "4",
+                      "default" : "1"
+                      },
+              "type" : {
+                      "description" : "The data type to read",
+                      "displayName" : "Data Type",
+                      "type" : "enumeration",
+                      "options" : [ "integer","float", "boolean" ],
+                      "default" : "integer"
+                      }
+              }
+      }
+```
+
+## Supported Poperties by configuration items in configuration JSON document
+
+|Property|Description|
+|:-----|:------------|
+|default|The default value for the configuration item. This is always expressed as a string regardless of the type of the configuration item.|
+|deprecated|A boolean flag to indicate that this item is no longer used and will be removed in a future release.|
+|description|A description of the configuration item used in the user interface to give more details of the item. Commonly used as a mouse over help prompt.|
+|displayName|The string to use in the user interface when presenting the configuration item. Generally a more user friendly form of the item name. Item names are referenced within the code.|
+|items|The type of the items in a list or kvlist configuration item.|
+|length|The maximum length of the string value of the item.|
+|listSize|The maximum number of entries allowed in a list or kvlist item.|
+|mandatory|A boolean flag to indicate that this item can not be left blank.|
+|maximum|The maximum value for a numeric configuration item.|
+|minimum|The minimum value for a numeric configuration item.|
+|options|Only used for enumeration type elements. This is a JSON array of string that contains the options in the enumeration.|
+|order|Used in the user interface to give an indication of how high up in the dialogue to place this item.|
+|group|Used to group related items together. The main use of this is within the GUI which will turn each group into a tab in the creation and edit screens.|
+|readonly|A boolean property that can be used to include items that can not be altered by the API.|
+|rule|A validation rule that will be run against the value. This must evaluate to true for the new value to be accepted by the API|
+|type|The type of the configuration item. The list of types supported are; integer, float, string, password, enumeration, boolean, list, kvlist, JSON, URL, IPV4, IPV6, script, code, X509 certificate and northTask.|
+|validity|An expression used to determine if the configuration item is valid. Used in the UI to gray out one value based on the value of others.|
+|value|The current value of the configuration item. This is not included when defining a set of default configuration in, for example, a plugin.|
+|properties|A set of items that are used in list and kvlist type items to create a list of groups of configuration items.|
+|keyName|A display name to be used for entry and display of key in the key-value list type, with item being an object.|
+|keyDescription|A description of key value in the key-value list type, with item being an object.|
+|permissions|An array of user roles that are allowed to update this configuration item. If not given then the configuration item can be updated by any user. If the permissions property is included in a configuration item the array must have at least one entry.|
+
diff --git a/.cursor/rules/README.md b/.cursor/rules/README.md
@@ -8,6 +8,12 @@ Rules are organized for Python development and documentation:
 
 ```
 .cursor/rules/
+├── C
+│   ├── core.mdc          # Core C++ Standards + + platform requirements
+│   └── plugins
+│       ├── filter.mdc    # C++ filter plugin rules
+│       ├── north.mdc     # C++ north plugin rules
+│       └── south.mdc     # C++ south plugin rules
 ├── README.md             # This usage guide
 ├── python/               # Python-specific rules (Python 3.8.10-3.12, Ubuntu LTS 20.04+, Raspberry Pi)
 │   ├── core.mdc          # Core Python standards + platform requirements
@@ -25,6 +31,10 @@ Rules are organized for Python development and documentation:
 
 | Rule File | Purpose | Applies To |
 |-----------|---------|------------|
+| `@C/core` | Core C++ standards,| `*.h`, `*.cpp` |
+| `@C/plugins/south` | C++ South Plugin| `*.h`, `*.cpp` |
+| `@C/plugins/north` | C++ North Plugin| `*.h`, `*.cpp` |
+| `@C/plugins/filter` | C++ Filter Plugin| `*.h`, `*.cpp` |
 | `@python/core` | Core Python standards, naming, imports | `*.py`, `python/**/*` |
 | `@python/api` | REST APIs, routes, middleware | API files, routes.py, web middleware |
 | `@python/config` | Configuration system, data formats | Config files, configuration modules |
@@ -38,6 +48,7 @@ Rules are organized for Python development and documentation:
 All Python rules include consistent platform and dependency information:
 
 ### **Platform Requirements** (Built into all Python rules)
+- **C++ Standard**: C++11
 - **Python Versions**: 3.8.10 - 3.12 (inclusive)
 - **Ubuntu**: LTS versions, 20.04 onwards (x86_64 & aarch64)
 - **Raspberry Pi OS**: Bullseye and Bookworm (aarch64 & armv7l)
diff --git a/.cursor/services/notification.mdc b/.cursor/services/notification.mdc
@@ -0,0 +1,651 @@
+# Fledge Notification Service - Feature Development Rules (MDC Format)
+
+---
+metadata:
+  version: "1.0.0"
+  last_updated: "2024-01-01"
+  author: "Fledge Development Team"
+  service: "notification-service"
+  language: "cpp"
+  framework: "custom"
+  license: "MIT"
+---
+
+## Configuration
+
+### Development Environment
+```yaml
+development:
+  language: "cpp"
+  standard: "c++11"
+  compiler: "gcc-11"
+  build_system: "cmake"
+  testing_framework: "gtest"
+  linting: "clang-tidy"
+  formatting: "clang-format"
+  documentation: "doxygen"
+```
+
+### Project Structure
+```yaml
+project_structure:
+  root: "fledge-service-notification"
+  directories:
+    src:
+      - core/           # Core business logic
+      - api/            # API endpoints and handlers
+      - storage/        # Data persistence layer
+      - utils/          # Utility functions
+      - tests/          # Unit and integration tests
+    include:            # Header files
+    docs:              # Documentation
+    scripts:           # Build and deployment scripts
+    config:            # Configuration files
+```
+
+### Naming Conventions
+```yaml
+naming_conventions:
+  classes: "PascalCase"
+  methods: "camelCase"
+  member_variables: "m_camelCase"
+  constants: "UPPER_SNAKE_CASE"
+  namespaces: "lowercase"
+  files: "snake_case"
+  examples:
+    classes: ["NotificationManager", "EmailService"]
+    methods: ["sendNotification", "validateRecipient"]
+    member_variables: ["m_notificationQueue", "m_config"]
+    constants: ["MAX_RETRY_ATTEMPTS", "DEFAULT_TIMEOUT"]
+```
+
+## Development Rules
+
+### Pre-Development Checklist
+```yaml
+pre_development_checklist:
+  architecture:
+    - "Review existing architecture and module boundaries"
+    - "Identify affected components and dependencies"
+    - "Plan integration points with existing services"
+  requirements:
+    - "Define clear acceptance criteria"
+    - "Consider backward compatibility requirements"
+    - "Plan error handling and edge cases"
+  observability:
+    - "Design logging and observability strategy"
+    - "Plan metrics collection"
+    - "Define monitoring alerts"
+```
+
+### Code Quality Standards
+```yaml
+code_quality:
+  complexity:
+    max_function_lines: 50
+    max_nesting_levels: 3
+    max_cyclomatic_complexity: 10
+  memory_management:
+    required: "raw_pointers"
+  thread_safety:
+    required: "mutex_protection"
+    patterns: ["lock_guard", "unique_lock", "atomic_operations"]
+  error_handling:
+    required: "exception_based"
+    forbidden: ["silent_failures", "error_ignoring"]
+    patterns: ["try_catch", "custom_exceptions", "error_logging"]
+```
+
+### C++ Development Standards
+```yaml
+cpp_standards:
+  memory_management:
+    preferred:
+      - "Notification* notification = new Notification()"
+      - "delete notification"
+  
+  error_handling:
+    preferred:
+      - "class NotificationException : public std::runtime_error"
+      - "throw NotificationException(\"Invalid recipient: \" + recipient)"
+    patterns:
+      - "exception_based"
+      - "meaningful_error_messages"
+      - "proper_logging"
+  
+  thread_safety:
+    required:
+      - "mutex_protection_for_shared_resources"
+      - "atomic_operations_where_appropriate"
+    patterns:
+      - "std::lock_guard<std::mutex> lock(m_mutex)"
+      - "std::atomic<int> counter"
+```
+
+### API Design Standards
+```yaml
+api_design:
+  restful_endpoints:
+    base_path: "/api/v1"
+    patterns:
+      - "GET /notifications"
+      - "POST /notifications"
+      - "GET /notifications/{id}"
+      - "PUT /notifications/{id}"
+      - "DELETE /notifications/{id}"
+  
+  request_models:
+    required_fields:
+      - "recipient"
+      - "subject"
+      - "message"
+      - "type"
+    optional_fields:
+      - "templateId"
+      - "metadata"
+    validation:
+      - "recipient_format"
+      - "message_length"
+      - "type_enumeration"
+  
+  response_models:
+    standard_fields:
+      - "id"
+      - "status"
+      - "createdAt"
+      - "updatedAt"
+    error_response:
+      - "error_code"
+      - "error_message"
+      - "timestamp"
+```
+
+### Testing Standards
+```yaml
+testing_standards:
+  unit_tests:
+    required:
+      - "success_paths"
+      - "failure_paths"
+      - "edge_cases"
+      - "boundary_conditions"
+    patterns:
+      - "Arrange-Act-Assert"
+      - "Given-When-Then"
+    naming: "MethodName_Scenario_ExpectedResult"
+  
+  integration_tests:
+    required:
+      - "end_to_end_flows"
+      - "api_endpoints"
+      - "database_operations"
+    patterns:
+      - "TestHttpClient"
+      - "TestDatabase"
+      - "MockServices"
+  
+  test_coverage:
+    minimum: 80
+    critical_paths: 100
+    new_features: 90
+```
+
+### Logging and Observability
+```yaml
+logging_standards:
+  levels:
+    - "TRACE"
+    - "DEBUG"
+    - "INFO"
+    - "WARN"
+    - "ERROR"
+    - "FATAL"
+  
+  structured_logging:
+    required_fields:
+      - "timestamp"
+      - "level"
+      - "service"
+      - "operation"
+    optional_fields:
+      - "request_id"
+      - "user_id"
+      - "duration"
+      - "metadata"
+  
+  sensitive_data:
+    forbidden_in_logs:
+      - "passwords"
+      - "api_keys"
+      - "personal_identifiers"
+      - "credit_card_numbers"
+    redaction_patterns:
+      - "password=***"
+      - "key=***"
+```
+
+### Security Standards
+```yaml
+security_standards:
+  input_validation:
+    required:
+      - "recipient_format"
+      - "message_length"
+      - "type_enumeration"
+      - "sql_injection_prevention"
+    patterns:
+      - "whitelist_validation"
+      - "regex_validation"
+      - "length_limits"
+  
+  authentication:
+    required:
+      - "token_validation"
+      - "permission_checks"
+      - "session_management"
+    patterns:
+      - "JWT_tokens"
+      - "OAuth2"
+      - "API_keys"
+  
+  authorization:
+    required:
+      - "role_based_access"
+      - "resource_permissions"
+      - "audit_logging"
+    patterns:
+      - "RBAC"
+      - "ABAC"
+      - "Permission_matrix"
+```
+
+### Performance Guidelines
+```yaml
+performance_guidelines:
+  memory_management:
+    preferred:
+      - "RAII_principles"
+      - "smart_pointers"
+      - "move_semantics"
+    avoid:
+      - "unnecessary_copies"
+      - "memory_leaks"
+      - "fragmentation"
+  
+  async_processing:
+    patterns:
+      - "thread_pools"
+      - "async_await"
+      - "future_promise"
+    use_cases:
+      - "notification_sending"
+      - "batch_processing"
+      - "external_api_calls"
+  
+  caching:
+    strategies:
+      - "in_memory_cache"
+      - "distributed_cache"
+      - "cache_invalidation"
+    patterns:
+      - "LRU_cache"
+      - "TTL_expiration"
+      - "cache_warming"
+```
+
+### Configuration Management
+```yaml
+configuration_management:
+  structure:
+    required_sections:
+      - "database"
+      - "email"
+      - "logging"
+      - "security"
+    optional_sections:
+      - "caching"
+      - "monitoring"
+      - "external_services"
+  
+  validation:
+    required:
+      - "type_safety"
+      - "value_ranges"
+      - "required_fields"
+    patterns:
+      - "schema_validation"
+      - "environment_validation"
+      - "dependency_validation"
+  
+  environment_specific:
+    development:
+      - "debug_logging"
+      - "mock_services"
+      - "local_database"
+    production:
+      - "error_logging_only"
+      - "real_services"
+      - "clustered_database"
+```
+
+### Documentation Standards
+```yaml
+documentation_standards:
+  code_documentation:
+    required:
+      - "public_apis"
+      - "complex_algorithms"
+      - "business_logic"
+    format: "doxygen"
+    tags:
+      - "@brief"
+      - "@param"
+      - "@return"
+      - "@throws"
+      - "@example"
+  
+  api_documentation:
+    required:
+      - "endpoint_descriptions"
+      - "request_response_examples"
+      - "error_codes"
+    format: "OpenAPI_3.0"
+  
+  deployment_documentation:
+    required:
+      - "build_instructions"
+      - "deployment_steps"
+      - "configuration_guide"
+      - "troubleshooting"
+```
+
+### Deployment and DevOps
+```yaml
+deployment_standards:
+  build_system:
+    tool: "cmake"
+    minimum_version: "3.16"
+    cpp_standard: "17"
+    dependencies:
+      - "gtest"
+      - "spdlog"
+      - "nlohmann_json"
+  
+  containerization:
+    base_image: "gcc:11"
+    runtime_image: "debian:bullseye-slim"
+    multi_stage: true
+    security_scanning: true
+  
+  ci_cd:
+    required_stages:
+      - "build"
+      - "test"
+      - "lint"
+      - "security_scan"
+      - "deploy"
+    quality_gates:
+      - "test_coverage >= 80%"
+      - "no_critical_vulnerabilities"
+      - "build_success"
+```
+
+## Code Review Checklist
+
+### Architecture & Design
+```yaml
+architecture_checklist:
+  - "Code follows established architectural patterns"
+  - "No unnecessary coupling between modules"
+  - "Clear separation of concerns"
+  - "Proper use of inheritance vs composition"
+  - "Module boundaries respected"
+```
+
+### Code Quality
+```yaml
+code_quality_checklist:
+  - "All functions are under 50 lines"
+  - "No more than 4 levels of nesting"
+  - "No code duplication (DRY principle)"
+  - "Meaningful variable and function names"
+  - "Consistent coding style"
+  - "No magic numbers without constants"
+```
+
+### Testing
+```yaml
+testing_checklist:
+  - "Unit tests cover all new functionality"
+  - "Integration tests for API endpoints"
+  - "Edge cases and error conditions tested"
+  - "Test names clearly describe behavior"
+  - "Mock objects used appropriately"
+  - "Test coverage meets minimum requirements"
+```
+
+### Security
+```yaml
+security_checklist:
+  - "Input validation implemented"
+  - "Authentication/authorization checks"
+  - "No sensitive data in logs"
+  - "Secure error handling"
+  - "No SQL injection vulnerabilities"
+  - "Proper secrets management"
+```
+
+### Performance
+```yaml
+performance_checklist:
+  - "No N+1 query patterns"
+  - "Efficient algorithms used"
+  - "Memory management follows RAII"
+  - "Async operations where appropriate"
+  - "No blocking operations in hot paths"
+  - "Resource cleanup implemented"
+```
+
+### Documentation
+```yaml
+documentation_checklist:
+  - "Public APIs documented with Doxygen"
+  - "README updated if needed"
+  - "Code comments explain 'why' not 'what'"
+  - "Configuration documented"
+  - "Deployment instructions updated"
+  - "API documentation current"
+```
+
+## Anti-Patterns
+
+### Memory Management Anti-Patterns
+```yaml
+memory_anti_patterns:
+  - "Missing cleanup in destructors"
+  - "Resource leaks in error paths"
+  - "Improper ownership semantics"
+```
+
+### Thread Safety Anti-Patterns
+```yaml
+thread_safety_anti_patterns:
+  - "Shared mutable state without protection"
+  - "Missing mutex locks"
+  - "Race conditions in concurrent access"
+  - "Improper atomic operation usage"
+  - "Deadlock scenarios"
+```
+
+### Error Handling Anti-Patterns
+```yaml
+error_handling_anti_patterns:
+  - "Silent failures"
+  - "Catching all exceptions without handling"
+  - "Incomplete error recovery"
+  - "Insufficient error logging"
+  - "Error swallowing"
+```
+
+### Performance Anti-Patterns
+```yaml
+performance_anti_patterns:
+  - "Unnecessary object copying"
+  - "Inefficient algorithms"
+  - "Blocking operations in hot paths"
+  - "Memory allocation in performance-critical code"
+  - "N+1 query patterns"
+```
+
+## Feature Development Template
+
+### Template Structure
+```yaml
+feature_template:
+  interface_definition:
+    - "Define the feature interface"
+    - "Specify public API methods"
+    - "Document method signatures"
+  
+  implementation:
+    - "Implement the feature class"
+    - "Add proper error handling"
+    - "Include logging and metrics"
+    - "Follow thread safety patterns"
+  
+  testing:
+    - "Create unit tests"
+    - "Add integration tests"
+    - "Test edge cases"
+    - "Verify error conditions"
+  
+  documentation:
+    - "Document public APIs"
+    - "Add usage examples"
+    - "Update README if needed"
+    - "Include configuration docs"
+```
+
+### Template Code Structure
+```yaml
+template_code:
+  header_file: "include/[FeatureName]Service.h"
+  implementation_file: "src/core/[FeatureName]Service.cpp"
+  test_file: "src/tests/[FeatureName]ServiceTest.cpp"
+  documentation_file: "docs/[FeatureName]Service.md"
+  
+  class_structure:
+    - "Public interface methods"
+    - "Private helper methods"
+    - "Member variables"
+    - "Constructor and destructor"
+  
+  test_structure:
+    - "Setup and teardown"
+    - "Success path tests"
+    - "Failure path tests"
+    - "Edge case tests"
+```
+
+## Validation Rules
+
+### Code Validation
+```yaml
+code_validation:
+  static_analysis:
+    - "clang-tidy"
+    - "cppcheck"
+    - "sonarqube"
+  
+  dynamic_analysis:
+    - "valgrind"
+    - "asan"
+    - "tsan"
+  
+  style_checking:
+    - "clang-format"
+    - "cpplint"
+    - "custom_style_rules"
+```
+
+### Test Validation
+```yaml
+test_validation:
+  coverage_requirements:
+    line_coverage: 80
+    branch_coverage: 70
+    function_coverage: 90
+  
+  test_quality:
+    - "No flaky tests"
+    - "Fast execution"
+    - "Clear assertions"
+    - "Proper mocking"
+```
+
+### Security Validation
+```yaml
+security_validation:
+  static_analysis:
+    - "semgrep"
+    - "bandit"
+    - "custom_security_rules"
+  
+  dependency_checking:
+    - "safety"
+    - "snyk"
+    - "vulnerability_scanning"
+```
+
+## Compliance
+
+### Standards Compliance
+```yaml
+compliance:
+  coding_standards:
+    - "C++11 standard"
+    - "MISRA C++ guidelines"
+    - "Google C++ Style Guide"
+    - "Project-specific conventions"
+  
+  security_standards:
+    - "OWASP guidelines"
+    - "CWE/SANS Top 25"
+    - "Industry best practices"
+  
+  performance_standards:
+    - "Response time requirements"
+    - "Throughput requirements"
+    - "Resource utilization limits"
+```
+
+### Quality Gates
+```yaml
+quality_gates:
+  build:
+    - "Successful compilation"
+    - "No warnings"
+    - "Static analysis passed"
+  
+  test:
+    - "All tests passing"
+    - "Coverage requirements met"
+    - "No flaky tests"
+  
+  security:
+    - "No critical vulnerabilities"
+    - "Security scan passed"
+    - "Dependency audit clean"
+  
+  performance:
+    - "Performance benchmarks passed"
+    - "Memory usage within limits"
+    - "Response time requirements met"
+```
+
+---
+# End of MDC Configuration
+description:
+globs:
+alwaysApply: false
+---
diff --git a/.cursor/services/notification_code_review.mdc b/.cursor/services/notification_code_review.mdc
@@ -0,0 +1,449 @@
+---
+description: 
+globs: 
+alwaysApply: true
+---
+# Fledge Notification Service - Multi-Document Context (MDC)
+
+### Project Overview
+This MDC file contains comprehensive rules, guidelines, and documentation for AI-assisted development and code review in the Fledge Notification Service project. It combines code review evaluation criteria, git diff analysis techniques, and project-specific standards.
+
+---
+
+## 1. Code Review Evaluation Criteria
+
+### 1.1 Design & Architecture
+- Verify the change fits your system's architectural patterns
+- Avoid unnecessary coupling or speculative features
+- Enforce clear separation of concerns
+- Align with defined module boundaries
+- Check for proper inheritance vs composition decisions
+
+### 1.2 Complexity & Maintainability
+- Ensure control flow remains flat
+- Keep cyclomatic complexity low
+- Abstract duplicate logic (DRY principle)
+- Remove dead or unreachable code
+- Refactor dense logic into testable helper methods
+- Break down complex methods into smaller, focused functions
+
+### 1.3 Functionality & Correctness
+- Confirm new code paths behave correctly under valid and invalid inputs
+- Cover all edge cases
+- Maintain idempotency for retry-safe operations
+- Satisfy all functional requirements or user stories
+- Include robust error-handling semantics
+- Validate input parameters and configuration
+
+### 1.4 Readability & Naming
+- Check that identifiers clearly convey intent
+- Comments should explain *why* (not *what*)
+- Code blocks should be logically ordered
+- No surprising side-effects hide behind deceptively simple names
+- Use consistent naming conventions
+
+### 1.5 Best Practices & Patterns
+- Validate use of language- or framework-specific idioms
+- Adhere to SOLID principles
+- Ensure proper resource cleanup
+- Maintain consistent logging/tracing
+- Clear separation of responsibilities across layers
+- Use RAII and smart pointers for memory management
+
+### 1.6 Test Coverage & Quality
+- Verify unit tests for both success and failure paths
+- Include integration tests exercising end-to-end flows
+- Use appropriate mocks/stubs
+- Include meaningful assertions (including edge-case inputs)
+- Test names should accurately describe behavior
+
+### 1.7 Standardization & Style
+- Ensure conformance to style guides (indentation, import/order, naming conventions)
+- Maintain consistent project structure (folder/file placement)
+- Zero new linter or formatter warnings
+- Follow C++11 standards and project conventions
+
+### 1.8 Documentation & Comments
+- Confirm public APIs or complex algorithms have clear in-code documentation
+- Update README, Swagger/OpenAPI, CHANGELOG, or other user-facing docs
+- Use Doxygen-style comments for all public APIs
+- Include `@brief`, `@param`, `@return`, `@throws` tags
+
+### 1.9 Security & Compliance
+- Check input validation and sanitization against injection attacks
+- Ensure proper output encoding
+- Implement secure error handling
+- Check dependency license and vulnerability checks
+- Follow secrets management best practices
+- Enforce authZ/authN where applicable
+
+### 1.10 Performance & Scalability
+- Identify N+1 query patterns or inefficient I/O
+- Check memory management concerns
+- Avoid heavy hot-path computations
+- Consider caching, batching, memoization, async patterns
+- Optimize algorithms where necessary
+
+### 1.11 Observability & Logging
+- Verify that key events emit metrics or tracing spans
+- Use appropriate log levels
+- Redact sensitive data
+- Include contextual information for monitoring and debugging
+- Support post-mortem analysis
+
+### 1.12 CI/CD & DevOps
+- Validate build pipeline integrity
+- Ensure automated test gating
+- Check artifact creation
+- Verify dependency declarations
+- Follow organizational DevOps best practices
+
+---
+
+## 2. C++ Specific Standards
+
+### 2.1 Naming Conventions
+- **Classes**: PascalCase (e.g., `NotificationManager`)
+- **Methods**: camelCase (e.g., `setupFilterPipeline()`)
+- **Member variables**: m_camelCase (e.g., `m_filterPipeline`)
+- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_RETRIGGER_TIME`)
+- **Namespaces**: lowercase (e.g., `std`)
+
+### 2.2 Memory Management
+- Follow RAII principles
+- Avoid manual memory management where possible
+- Ensure proper cleanup in destructors
+
+### 2.3 Error Handling
+- Use exceptions for exceptional conditions
+- Log errors with appropriate log levels
+- Provide meaningful error messages
+- Handle resource failures gracefully
+
+### 2.4 Thread Safety
+- Use mutex for shared resource protection
+- Consider atomic operations where appropriate
+- Document thread safety guarantees
+- Avoid race conditions in concurrent code
+
+---
+
+## 3. Git Diff Analysis Techniques
+
+### 3.1 Understanding Git Diff Commands
+```bash
+# Show file names only
+git diff --name-only origin/develop...origin/feature-branch
+
+# Show statistics
+git diff --stat origin/develop...origin/feature-branch
+
+# Show detailed statistics
+git diff --numstat origin/develop...origin/feature-branch
+
+# Show short statistics
+git diff --shortstat origin/develop...origin/feature-branch
+
+# Show word-level changes
+git diff --word-diff origin/develop...origin/feature-branch
+
+# Show context with more lines
+git diff -U10 origin/develop...origin/feature-branch
+```
+
+### 3.2 Diff Output Interpretation
+
+#### File Statistics Analysis
+```bash
+git diff --numstat origin/develop...origin/feature-branch
+```
+Output format: `[insertions] [deletions] [filename]`
+
+#### Change Pattern Recognition
+- **High insertion count**: New functionality or major refactoring
+- **High deletion count**: Code cleanup or breaking changes
+- **Balanced changes**: Refactoring or feature updates
+- **Low net change**: Bug fixes or minor improvements
+
+### 3.3 Three-Way Merge Analysis
+```bash
+# Compare two branches
+git diff branch1...branch2
+
+# Compare with common ancestor
+git diff branch1..branch2
+```
+
+### 3.4 Change Impact Assessment
+
+#### File-Level Analysis
+1. **Header Files**: Interface changes, new dependencies
+2. **Source Files**: Implementation changes, new functionality
+3. **Test Files**: Test coverage, validation logic
+4. **Configuration Files**: Settings, defaults, options
+
+#### Line-Level Analysis
+1. **Additions (+)**: New code, features, methods
+2. **Deletions (-)**: Removed code, cleanup, breaking changes
+3. **Context**: Surrounding code for understanding changes
+
+### 3.5 Pattern Recognition in Diffs
+
+#### Common Patterns
+1. **New Includes**: `#include <new_header.h>`
+2. **Method Signatures**: Parameter changes, return type changes
+3. **Class Inheritance**: `class X : public Y`
+4. **Member Variables**: `Type* m_variable;`
+5. **Configuration**: JSON structures, default values
+
+#### Red Flags in Diffs
+1. **Manual Memory Management**: `new`/`delete` without smart pointers
+2. **Missing Error Handling**: No try-catch blocks
+3. **Inconsistent Naming**: Mixed naming conventions
+4. **Large Methods**: Methods with many lines added
+5. **Missing Documentation**: New methods without comments
+
+---
+
+## 4. Issue Severity Levels
+
+### 4.1 Critical
+- Memory leaks or resource leaks
+- Race conditions or thread safety issues
+- Security vulnerabilities
+- Data corruption risks
+- Build failures or compilation errors
+
+### 4.2 Major
+- Performance issues affecting scalability
+- Architectural violations
+- Missing error handling
+- Incomplete functionality
+- Breaking changes without proper migration
+
+### 4.3 Minor
+- Code style violations
+- Missing documentation
+- Inefficient algorithms
+- Code duplication
+- Minor bugs with workarounds
+
+### 4.4 Enhancement
+- Missing test coverage
+- Performance optimizations
+- Code refactoring opportunities
+- Additional features or improvements
+- Better error messages or logging
+
+---
+
+## 5. Code Review Process
+
+### 5.1 High-Level Summary
+Describe product impact and engineering approach in 2-3 sentences:
+- **Product impact**: What does this change deliver for users or customers?
+- **Engineering approach**: Key patterns, frameworks, or best practices in use
+
+### 5.2 Fetch and Scope the Diff
+1. Run `git fetch origin` to ensure latest code
+2. Compute `git diff --name-only --diff-filter=M origin/develop...origin/feature-branch`
+3. For each file, run `git diff --quiet origin/develop...origin/feature-branch -- <file>`
+4. Skip files that produce no actual diff hunks
+
+### 5.3 Evaluate Against Criteria
+For each truly changed file and each diffed hunk, evaluate against the 12 evaluation criteria listed above.
+
+### 5.4 Report Issues
+For each validated issue, output a nested bullet like this:
+- File: `<path>:<line-range>`
+  - Issue: [One-line summary of the root problem]
+  - Fix: [Concise suggested change or code snippet]
+
+### 5.5 Prioritize Issues
+Group issues by severity in this order:
+- Critical
+- Major
+- Minor
+- Enhancement
+
+### 5.6 Highlight Positives
+Include a brief bulleted list of positive findings or well-implemented patterns observed in the diff.
+
+---
+
+## 6. Common Issues to Watch For
+
+### 6.1 Memory Management
+- Manual `new`/`delete` without smart pointers
+- Missing cleanup in destructors
+- Resource leaks in error paths
+- Improper ownership semantics
+
+### 6.2 Thread Safety
+- Shared mutable state without protection
+- Missing mutex locks
+- Race conditions in concurrent access
+- Improper atomic operation usage
+
+### 6.3 Error Handling
+- Missing exception handling
+- Incomplete error recovery
+- Silent failures
+- Insufficient error logging
+
+### 6.4 Performance
+- Unnecessary object copying
+- Inefficient algorithms
+- Blocking operations in hot paths
+- Memory allocation in performance-critical code
+
+### 6.5 Code Quality
+- Code duplication
+- Complex methods (>50 lines)
+- Deep nesting (>4 levels)
+- Magic numbers without constants
+- Inconsistent naming
+
+---
+
+## 7. Positive Patterns to Recognize
+
+- Proper use of RAII and smart pointers
+- Clear separation of concerns
+- Comprehensive error handling
+- Good logging and observability
+- Consistent coding style
+- Thorough documentation
+- Appropriate test coverage
+- Performance-conscious design
+- Thread-safe implementations
+- Backward compatibility maintenance
+
+---
+
+## 8. Advanced Git Commands for Analysis
+
+```bash
+# Show only function changes
+git diff -p origin/develop...origin/feature-branch | grep -A 5 -B 5 "^[+-].*("
+
+# Show only structural changes
+git diff --stat --summary origin/develop...origin/feature-branch
+
+# Show changes with context
+git diff -U5 origin/develop...origin/feature-branch
+
+# Show only additions
+git diff --diff-filter=A origin/develop...origin/feature-branch
+
+# Show only deletions
+git diff --diff-filter=D origin/develop...origin/feature-branch
+
+# Show only modifications
+git diff --diff-filter=M origin/develop...origin/feature-branch
+
+# Count lines by type
+git diff origin/develop...origin/feature-branch | grep -c "^+"
+git diff origin/develop...origin/feature-branch | grep -c "^-"
+
+# Find new includes
+git diff origin/develop...origin/feature-branch | grep "^+#include"
+
+# Find new class definitions
+git diff origin/develop...origin/feature-branch | grep "^+class"
+
+# Find new method definitions
+git diff origin/develop...origin/feature-branch | grep "^+.*("
+```
+
+---
+
+## 9. Fledge-Specific Guidelines
+
+### 9.1 Notification Service Architecture
+- Follow existing notification patterns and conventions
+- Maintain backward compatibility with existing configurations
+- Use proper plugin architecture for extensibility
+- Implement proper resource cleanup for notification instances
+
+### 9.2 Filter Pipeline Integration
+- Ensure thread-safe filter pipeline operations
+- Implement proper error handling for filter setup
+- Use smart pointers for filter pipeline management
+- Add comprehensive logging for filter operations
+
+### 9.3 Configuration Management
+- Follow Fledge configuration patterns
+- Implement proper category registration/unregistration
+- Handle configuration changes gracefully
+- Validate configuration parameters
+
+### 9.4 Testing Requirements
+- Unit tests for all new functionality
+- Integration tests for filter pipeline workflows
+- Performance tests for large datasets
+- Error condition testing
+
+---
+
+## 10. AI-Assisted Development Guidelines
+
+### 10.1 Code Generation
+- Follow established naming conventions
+- Include proper error handling
+- Add comprehensive documentation
+- Ensure thread safety where applicable
+
+### 10.2 Code Review Assistance
+- Analyze git diffs systematically
+- Identify potential issues early
+- Suggest improvements and optimizations
+- Maintain consistency with existing codebase
+
+### 10.3 Documentation Generation
+- Create clear, concise documentation
+- Include examples and usage patterns
+- Document API changes and breaking changes
+- Maintain up-to-date README files
+
+### 10.4 Testing Assistance
+- Generate comprehensive test cases
+- Include edge case testing
+- Ensure proper test coverage
+- Create integration test scenarios
+
+---
+
+## 11. Project-Specific Rules
+
+### 11.1 File Organization
+- Keep header files in `include/` directories
+- Organize source files logically
+- Maintain consistent file naming
+- Group related functionality together
+
+### 11.2 Build System
+- Follow CMake conventions
+- Maintain proper dependency management
+- Ensure cross-platform compatibility
+- Include proper version information
+
+### 11.3 Version Control
+- Use meaningful commit messages
+- Create feature branches for new development
+- Maintain clean git history
+- Follow branching strategies
+
+### 11.4 Code Quality
+- Pass all linting checks
+- Maintain consistent formatting
+- Follow coding standards
+- Include proper comments
+
+---
+
+This MDC file serves as a comprehensive guide for AI-assisted development and code review in the Fledge Notification Service project. It provides structured evaluation criteria, git diff analysis techniques, and project-specific guidelines to ensure high-quality code development and review processes.
+description:
+globs:
+alwaysApply: false
+---
PATCH

echo "Gold patch applied."
