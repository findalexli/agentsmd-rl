#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skillnet

# Idempotency guard
if grep -qF "description: Navigates the agent to a target appliance (microwave, stove, fridge" "experiments/src/skills/alfworld/alfworld-appliance-navigator/SKILL.md" && grep -qF "description: Prepares a household appliance (microwave, oven, toaster, fridge) f" "experiments/src/skills/alfworld/alfworld-appliance-preparer/SKILL.md" && grep -qF "description: Cleans a specified object using an appropriate cleaning receptacle " "experiments/src/skills/alfworld/alfworld-clean-object/SKILL.md" && grep -qF "description: Operates a device or appliance (like a desklamp, microwave, or frid" "experiments/src/skills/alfworld/alfworld-device-operator/SKILL.md" && grep -qF "description: Performs an initial scan of the ALFWorld environment to identify al" "experiments/src/skills/alfworld/alfworld-environment-scanner/SKILL.md" && grep -qF "description: Uses a heating appliance (microwave, stoveburner, oven) to apply he" "experiments/src/skills/alfworld/alfworld-heat-object-with-appliance/SKILL.md" && grep -qF "description: Use when the agent must collect and track multiple instances of the" "experiments/src/skills/alfworld/alfworld-inventory-management/SKILL.md" && grep -qF "description: Navigates to a suspected location and identifies a target object. U" "experiments/src/skills/alfworld/alfworld-locate-target-object/SKILL.md" && grep -qF "description: Cools a held object using an appropriate cooling appliance such as " "experiments/src/skills/alfworld/alfworld-object-cooler/SKILL.md" && grep -qF "description: Heats a specified object using an available heating appliance (e.g." "experiments/src/skills/alfworld/alfworld-object-heater/SKILL.md" && grep -qF "description: Use when the agent needs to find a specific object in ALFWorld that" "experiments/src/skills/alfworld/alfworld-object-locator/SKILL.md" && grep -qF "description: Inspects a receptacle's contents by navigating to it and reading th" "experiments/src/skills/alfworld/alfworld-object-state-inspector/SKILL.md" && grep -qF "description: Uses an appliance to change the state of an object (cooling, heatin" "experiments/src/skills/alfworld/alfworld-object-state-modifier/SKILL.md" && grep -qF "description: Use when the agent is holding an object and needs to place it into " "experiments/src/skills/alfworld/alfworld-object-storer/SKILL.md" && grep -qF "description: Picks up a target object from its current receptacle and moves it t" "experiments/src/skills/alfworld/alfworld-object-transporter/SKILL.md" && grep -qF "description: Closes an open receptacle to maintain environment tidiness after in" "experiments/src/skills/alfworld/alfworld-receptacle-closer/SKILL.md" && grep -qF "description: Searches for a suitable empty or appropriately occupied receptacle " "experiments/src/skills/alfworld/alfworld-receptacle-finder/SKILL.md" && grep -qF "description: Plans and executes movement to a target receptacle within the ALFWo" "experiments/src/skills/alfworld/alfworld-receptacle-navigator/SKILL.md" && grep -qF "description: Systematically searches a sequence of likely locations for a target" "experiments/src/skills/alfworld/alfworld-search-pattern-executor/SKILL.md" && grep -qF "description: Re-examines previously visited locations to confirm the absence of " "experiments/src/skills/alfworld/alfworld-search-verifier/SKILL.md" && grep -qF "description: Systematically explores storage receptacles (drawers, cabinets, she" "experiments/src/skills/alfworld/alfworld-storage-explorer/SKILL.md" && grep -qF "description: Use when the agent needs to check whether an ALFWorld task objectiv" "experiments/src/skills/alfworld/alfworld-task-verifier/SKILL.md" && grep -qF "description: Manages the temperature state of an object by placing it into an ap" "experiments/src/skills/alfworld/alfworld-temperature-regulator/SKILL.md" && grep -qF "description: Searches for a specified tool or device (e.g., a desklamp, knife, o" "experiments/src/skills/alfworld/alfworld-tool-locator/SKILL.md" && grep -qF "description: Use when the agent needs to apply a tool to a target object in ALFW" "experiments/src/skills/alfworld/alfworld-tool-user/SKILL.md" && grep -qF "description: Use when the ScienceWorld environment returns an \"Ambiguous request" "experiments/src/skills/scienceworld/scienceworld-ambiguous-action-resolution/SKILL.md" && grep -qF "description: Use when the agent needs to locate, identify, and focus on a specif" "experiments/src/skills/scienceworld/scienceworld-animal-identifier/SKILL.md" && grep -qF "description: This skill constructs a simple electrical circuit by connecting com" "experiments/src/skills/scienceworld/scienceworld-circuit-builder/SKILL.md" && grep -qF "description: This skill connects two electrical components (e.g., wires, batteri" "experiments/src/skills/scienceworld/scienceworld-circuit-connector/SKILL.md" && grep -qF "description: Executes a 'focus on OBJ' action on a specific object based on the " "experiments/src/skills/scienceworld/scienceworld-conditional-focus-executor/SKILL.md" && grep -qF "description: Places an object into one of several designated containers based on" "experiments/src/skills/scienceworld/scienceworld-conditional-placer/SKILL.md" && grep -qF "description: Inspects the contents of a container or device using the 'look at' " "experiments/src/skills/scienceworld/scienceworld-container-inspector/SKILL.md" && grep -qF "3. Expected observation: \"You move the avocado seed to the inventory.\"" "experiments/src/skills/scienceworld/scienceworld-container-item-retriever/SKILL.md" && grep -qF "description: Moves an object from inventory to a specified container in a target" "experiments/src/skills/scienceworld/scienceworld-container-relocator/SKILL.md" && grep -qF "description: Moves a substance or object from one container to another (e.g., mo" "experiments/src/skills/scienceworld/scienceworld-container-transfer/SKILL.md" && grep -qF "description: Executes timed waiting using 'wait' or 'wait1' actions to advance t" "experiments/src/skills/scienceworld/scienceworld-controlled-waiting/SKILL.md" && grep -qF "description: Activates a device (e.g., blast furnace, stove) to initiate a proce" "experiments/src/skills/scienceworld/scienceworld-device-activator/SKILL.md" && grep -qF "description: Use when you need to isolate a space (like a greenhouse) by closing" "experiments/src/skills/scienceworld/scienceworld-environment-isolation/SKILL.md" && grep -qF "description: Use when you have planted a seed or need to track a plant's growth " "experiments/src/skills/scienceworld/scienceworld-growth-focuser/SKILL.md" && grep -qF "description: Reads a recipe or note from the inventory using the 'read' action a" "experiments/src/skills/scienceworld/scienceworld-instruction-reader/SKILL.md" && grep -qF "description: Use when the agent needs to confirm and prepare a specific inventor" "experiments/src/skills/scienceworld/scienceworld-inventory-focus/SKILL.md" && grep -qF "description: Handles picking up objects from the environment into the agent's in" "experiments/src/skills/scienceworld/scienceworld-inventory-manager/SKILL.md" && grep -qF "description: Picks up a specified object from the environment and moves it into " "experiments/src/skills/scienceworld/scienceworld-item-fetcher/SKILL.md" && grep -qF "description: Transfers the contents of a source liquid container into a target c" "experiments/src/skills/scienceworld/scienceworld-liquid-pourer/SKILL.md" && grep -qF "description: Analyzes room observations to identify potential living things (e.g" "experiments/src/skills/scienceworld/scienceworld-living-entity-identifier/SKILL.md" && grep -qF "Activate when direct experimental testing of a material property (conductivity, " "experiments/src/skills/scienceworld/scienceworld-material-classifier/SKILL.md" && grep -qF "description: Use when the agent needs to measure a quantitative property (temper" "experiments/src/skills/scienceworld/scienceworld-measurement-taker/SKILL.md" && grep -qF "description: This skill chemically mixes the contents of a container using the '" "experiments/src/skills/scienceworld/scienceworld-mixture-creator/SKILL.md" && grep -qF "description: Moves a tested or examined object into a designated container (e.g." "experiments/src/skills/scienceworld/scienceworld-object-classifier/SKILL.md" && grep -qF "description: This skill selects and focuses on a specific object to signal task " "experiments/src/skills/scienceworld/scienceworld-object-focuser/SKILL.md" && grep -qF "description: Searches for a specific target object across multiple rooms by syst" "experiments/src/skills/scienceworld/scienceworld-object-locator/SKILL.md" && grep -qF "description: Moves a specified object from the environment or inventory into a t" "experiments/src/skills/scienceworld/scienceworld-object-placer/SKILL.md" && grep -qF "description: Acquires a specified object by moving it from the environment into " "experiments/src/skills/scienceworld/scienceworld-object-retriever/SKILL.md" && grep -qF "description: Use when the agent needs to choose a specific object from multiple " "experiments/src/skills/scienceworld/scienceworld-object-selector/SKILL.md" && grep -qF "description: This skill observes the state of an active apparatus and its conten" "experiments/src/skills/scienceworld/scienceworld-process-monitor/SKILL.md" && grep -qF "description: This skill introduces deliberate pauses in task execution. Use when" "experiments/src/skills/scienceworld/scienceworld-process-pauser/SKILL.md" && grep -qF "description: This skill locates and acquires a recipe or instruction document by" "experiments/src/skills/scienceworld/scienceworld-recipe-retriever/SKILL.md" && grep -qF "description: Performs an initial survey of a room to identify all visible object" "experiments/src/skills/scienceworld/scienceworld-room-explorer/SKILL.md" && grep -qF "description: Teleports the agent to a specified room within the ScienceWorld env" "experiments/src/skills/scienceworld/scienceworld-room-navigator/SKILL.md" && grep -qF "description: This skill performs a 'look around' action to scan and describe the" "experiments/src/skills/scienceworld/scienceworld-room-scanner/SKILL.md" && grep -qF "description: This skill initiates the cooling of a substance by moving it into a" "experiments/src/skills/scienceworld/scienceworld-substance-cooler/SKILL.md" && grep -qF "description: Locates and retrieves a target substance or material from a contain" "experiments/src/skills/scienceworld/scienceworld-substance-fetcher/SKILL.md" && grep -qF "description: Use when you need to transfer a target substance into an appropriat" "experiments/src/skills/scienceworld/scienceworld-substance-preparator/SKILL.md" && grep -qF "description: This skill determines the most likely location for a target object " "experiments/src/skills/scienceworld/scienceworld-target-locator/SKILL.md" && grep -qF "description: Use when the agent needs to direct attention to a specific object i" "experiments/src/skills/scienceworld/scienceworld-task-focuser/SKILL.md" && grep -qF "description: Analyzes user instructions in ScienceWorld environments to extract " "experiments/src/skills/scienceworld/scienceworld-task-parser/SKILL.md" && grep -qF "description: Use when the agent has just obtained a numerical measurement (tempe" "experiments/src/skills/scienceworld/scienceworld-threshold-evaluator/SKILL.md" && grep -qF "description: Uses a tool from inventory on a target object or location to perfor" "experiments/src/skills/scienceworld/scienceworld-tool-user/SKILL.md" && grep -qF "description: Use when the agent has acquired a tool or instrument and needs to v" "experiments/src/skills/scienceworld/scienceworld-tool-validator/SKILL.md" && grep -qF "description: Focuses on a specific target object to signal task completion. Use " "experiments/src/skills/scienceworld/task-completion-focus/SKILL.md" && grep -qF "Thought: The user wants a black leather wallet under $40. The price is $35.99, w" "experiments/src/skills/webshop/webshop-attribute-verifier/SKILL.md" && grep -qF "description: Performs the first search on an e-commerce platform using keywords " "experiments/src/skills/webshop/webshop-initial-search/SKILL.md" && grep -qF "**Thought:** The user needs a long, natural-looking, clip-in hair extension unde" "experiments/src/skills/webshop/webshop-product-detail-check/SKILL.md" && grep -qF "**Thought:** The user needs a teeth whitening toothpaste that freshens breath, u" "experiments/src/skills/webshop/webshop-product-evaluator/SKILL.md" && grep -qF "4.  **Validate Results:** Success is marked by a \"Page 1\" observation containing" "experiments/src/skills/webshop/webshop-product-search/SKILL.md" && grep -qF "**Thought:** The user needs a portable, double horn bluetooth speaker that is ea" "experiments/src/skills/webshop/webshop-product-selector/SKILL.md" && grep -qF "description: Executes the purchase action for a confirmed suitable product on an" "experiments/src/skills/webshop/webshop-purchase-executor/SKILL.md" && grep -qF "**Thought:** The user needs a teeth whitening toothpaste that freshens breath, u" "experiments/src/skills/webshop/webshop-purchase-initiator/SKILL.md" && grep -qF "3.  **Hand Off:** Pass the structured parameters to the search execution skill (" "experiments/src/skills/webshop/webshop-query-interpreter/SKILL.md" && grep -qF "2.  **Validate Constraints:** Confirm you have at least one constraint extracted" "experiments/src/skills/webshop/webshop-result-filter/SKILL.md" && grep -qF "**Thought:** The user needs a clip-in hair extension that is long and natural lo" "experiments/src/skills/webshop/webshop-search-executor/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/experiments/src/skills/alfworld/alfworld-appliance-navigator/SKILL.md b/experiments/src/skills/alfworld/alfworld-appliance-navigator/SKILL.md
@@ -1,17 +1,32 @@
 ---
 name: alfworld-appliance-navigator
-description: This skill navigates the agent to a target appliance (like a microwave, stove, or fridge) needed for a task. It should be triggered when the agent has an object that requires processing (heating, cooling, cleaning) and needs to move to the appropriate station. The skill identifies the appliance from the environment and executes the movement action.
+description: Navigates the agent to a target appliance (microwave, stove, fridge, or sinkbasin) needed for object processing. Use when you are holding an object that needs heating, cooling, or cleaning and must move to the correct appliance station. Identifies the required appliance from the task context and executes the movement action.
 ---
 # Instructions
 Use this skill when you are holding an object that needs to be processed (heated, cooled, or cleaned) and you must locate and move to the correct appliance to perform the action.
 
-## Process
-1.  **Identify the Target Appliance:** Determine which appliance is required for the task (e.g., microwave for heating, fridge for cooling, sink for cleaning). The required appliance is implied by the action needed (`heat`, `cool`, `clean`).
-2.  **Locate the Appliance:** Scan the provided environment observation for the target appliance (e.g., `microwave 1`, `fridge 1`, `sinkbasin 1`).
-3.  **Navigate:** Execute the `go to {appliance}` action to move to the identified appliance location.
-4.  **Prepare Appliance (if needed):** Upon arrival, check if the appliance requires preparation (e.g., opening a closed microwave or fridge door). If so, perform the necessary action (`open {appliance}`) before proceeding with the object processing.
+## Workflow
+1. **Identify the Target Appliance:** Determine which appliance is required for the task. Map the action to the appliance: `heat` -> microwave/stoveburner, `cool` -> fridge, `clean` -> sinkbasin.
+2. **Locate the Appliance:** Scan the environment observation for the target appliance (e.g., `microwave 1`, `fridge 1`, `sinkbasin 1`).
+3. **Navigate:** Execute `go to {appliance}` to move to the identified appliance location.
+4. **Prepare Appliance (if needed):** Upon arrival, check if the appliance requires preparation (e.g., opening a closed microwave or fridge door). If so, perform `open {appliance}` before proceeding.
+
+## Example
+
+**Scenario:** You are holding `potato 1` and need to heat it.
+
+```
+Thought: I need to heat this potato. The microwave is the appropriate appliance.
+Action: go to microwave 1
+Observation: The microwave 1 is closed.
+Thought: I need to open the microwave before I can use it.
+Action: open microwave 1
+Observation: You open the microwave 1. The microwave 1 is open. In it, you see nothing.
+```
+
+**Result:** You are now at the open microwave, ready to heat the potato.
 
 ## Key Principles
-*   **Trigger:** The agent is holding an object and the next step in the task is to `heat`, `cool`, or `clean` it.
-*   **Core Action:** The primary output of this skill is the navigation command `go to {target_appliance}`.
-*   **Prerequisite Check:** Always ensure the appliance is accessible (e.g., open) before attempting to use it for processing.
+- **Trigger:** The agent is holding an object and the next step in the task is to `heat`, `cool`, or `clean` it.
+- **Core Action:** The primary output of this skill is the navigation command `go to {target_appliance}`.
+- **Prerequisite Check:** Always ensure the appliance is accessible (e.g., open) before attempting to use it for processing.
diff --git a/experiments/src/skills/alfworld/alfworld-appliance-preparer/SKILL.md b/experiments/src/skills/alfworld/alfworld-appliance-preparer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-appliance-preparer
-description: This skill prepares an appliance (like a microwave, oven, or toaster) for use by ensuring it is in the correct open/closed state. Trigger this when the agent needs to use an appliance for heating, cooling, or cooking and must first open or close it. It takes an appliance identifier as input and outputs a confirmation that the appliance is ready.
+description: Prepares a household appliance (microwave, oven, toaster, fridge) for use by ensuring it is in the correct open/closed state. Use when the agent needs to heat, cool, or cook an item and must first open or close the appliance before placing an object inside. Takes an appliance identifier as input and outputs a confirmation that the appliance is ready for the next action.
 ---
 # Instructions
 
@@ -22,5 +22,15 @@ Prepare a specified household appliance for immediate use by ensuring it is in t
 - **Error Handling**: If the action fails (environment outputs "Nothing happened"), the appliance may already be in the desired state. Re-check the observation and proceed.
 - **Trajectory Insight**: Refer to the example in `references/trajectory_example.md` to see a practical application of this skill in the context of a larger task.
 
+## Example
+
+**Input:** `appliance_identifier: microwave 1`
+
+**Sequence:**
+1. `go to microwave 1` → Observation: "You are at microwave 1. The microwave 1 is closed."
+2. `open microwave 1` → Observation: "You open the microwave 1. The microwave 1 is open."
+
+**Output:** "The microwave 1 is open and ready for use."
+
 ## Output
 A confirmation that the appliance is ready, typically in the form of the agent's `Thought` summarizing the prepared state and the environment's observation.
diff --git a/experiments/src/skills/alfworld/alfworld-clean-object/SKILL.md b/experiments/src/skills/alfworld/alfworld-clean-object/SKILL.md
@@ -1,28 +1,36 @@
 ---
 name: alfworld-clean-object
-description: This skill cleans a specified object using an appropriate cleaning receptacle (e.g., sink). It should be triggered when a task requires an object to be in a clean state (e.g., 'clean potato') before proceeding. The skill involves navigating to the cleaning location and performing the clean action, outputting confirmation that the object is now clean.
+description: Cleans a specified object using an appropriate cleaning receptacle (e.g., sinkbasin). Use when a task requires an object to be in a clean state (e.g., "clean potato", "wash apple") before proceeding. Navigates to the cleaning location, performs the clean action, and confirms the object is now clean.
 ---
 # Instructions
 
-## When to Use
-Use this skill when your task requires an object to be in a "clean" state before proceeding (e.g., "clean potato", "wash apple"). The skill is specifically designed for the ALFWorld environment.
+Clean an object you are holding using a sinkbasin. The object must be in your inventory before cleaning.
 
-## Prerequisites
-1. You must already possess the target object in your inventory.
-2. You must have identified an appropriate cleaning receptacle (typically a sinkbasin).
-
-## Core Procedure
-1. **Navigate to Cleaning Location**: Go to the identified cleaning receptacle (e.g., `sinkbasin 1`).
-2. **Execute Clean Action**: Perform the `clean` action using the format: `clean {object_name} with {receptacle_name}`.
-3. **Confirm Success**: Verify the environment's observation confirms the object has been cleaned.
+## Workflow
+1. **Navigate:** `go to sinkbasin 1` (or the appropriate sinkbasin in the environment)
+2. **Clean:** `clean {object} with sinkbasin 1` -- verify observation confirms "You clean the {object}"
+3. **Proceed:** The object is now clean. Continue with the next task step
 
 ## Action Format
-- Use the exact ALFWorld action: `clean {obj} with {recep}`
-- Example: `clean potato 1 with sinkbasin 1`
+- `clean {obj} with {recep}` (e.g., `clean potato 1 with sinkbasin 1`)
+
+## Error Recovery
+- "Nothing happened": Check (1) you are holding the object, (2) you are at the sinkbasin, (3) object and receptacle names are correct
+- Not at sinkbasin: execute `go to sinkbasin 1` first
+
+## Example
+
+**Scenario:** You are holding `potato 1` and need to clean it.
+
+```
+Thought: I need to clean this potato. I should go to the sinkbasin.
+Action: go to sinkbasin 1
+Observation: On the sinkbasin 1, you see nothing.
+Action: clean potato 1 with sinkbasin 1
+Observation: You clean the potato 1 using the sinkbasin 1.
+```
 
-## Error Handling
-- If the action fails (e.g., "Nothing happened"), consult the troubleshooting guide in the references.
-- Ensure you are at the correct receptacle and the object is in your inventory before attempting to clean.
+**Result:** The potato is now in a clean state and ready for the next task step.
 
 ## Post-Condition
-After successful execution, the object will be in a clean state. You may proceed with the next step of your task (e.g., placing the clean object in a microwave).
+After successful execution, the object will be in a clean state. You may proceed with the next step of your task (e.g., placing the clean object on a shelf or in a microwave).
diff --git a/experiments/src/skills/alfworld/alfworld-device-operator/SKILL.md b/experiments/src/skills/alfworld/alfworld-device-operator/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-device-operator
-description: This skill operates a device or appliance (like a desklamp) to interact with another object. It should be triggered when the task requires using a tool on a target item (e.g., 'look at laptop under the desklamp'). The skill assumes the target object and the operating device are co-located, and it executes the appropriate use action (e.g., toggle, heat, clean).
+description: Operates a device or appliance (like a desklamp, microwave, or fridge) to interact with another object. Use when the task requires using a tool on a target item (e.g., "look at laptop under the desklamp", "heat potato with microwave"). Locates both the device and target object, co-locates them, and executes the appropriate use action (toggle, heat, cool, or clean).
 ---
 # Instructions
 
@@ -42,3 +42,24 @@ Follow this sequence when the skill is triggered:
 *   **Co-location Required:** The skill assumes the final action requires the target object and the operating device to be in the same location (on the same receptacle).
 *   **Device First:** Prioritize finding the device before extensively searching for the target object, as the device's location is often a fixed landmark.
 *   **Invalid Actions:** If the environment responds with "Nothing happened," re-evaluate your object/device names and your location. Ensure you are using the correct action verb for the device type.
+
+## Example
+
+**Scenario:** Task is "look at laptop under the desklamp."
+
+```
+Thought: I need to find the desklamp first. It's likely on a sidetable or desk.
+Action: go to sidetable 1
+Observation: On the sidetable 1, you see a desklamp 1.
+Thought: Found the desklamp. Now I need to find the laptop.
+Action: go to desk 1
+Observation: On the desk 1, you see a laptop 1, a pen 2.
+Action: take laptop 1 from desk 1
+Observation: You pick up the laptop 1 from the desk 1.
+Action: go to sidetable 1
+Observation: On the sidetable 1, you see a desklamp 1.
+Action: use desklamp 1
+Observation: You turn on the desklamp 1.
+```
+
+**Result:** The laptop is now being examined under the desklamp, completing the task.
diff --git a/experiments/src/skills/alfworld/alfworld-environment-scanner/SKILL.md b/experiments/src/skills/alfworld/alfworld-environment-scanner/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-environment-scanner
-description: Performs an initial scan of the Alfworld environment to identify all visible objects and receptacles. Processes raw observation text into a structured list of entities to build a mental map for planning.
+description: Performs an initial scan of the ALFWorld environment to identify all visible objects and receptacles. Use when you first enter an environment and need to build a mental map for task planning. Processes raw observation text into a structured list of entities, categorizing them as objects or receptacles.
 ---
 # Instructions
 
diff --git a/experiments/src/skills/alfworld/alfworld-heat-object-with-appliance/SKILL.md b/experiments/src/skills/alfworld/alfworld-heat-object-with-appliance/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-heat-object-with-appliance
-description: This skill uses a heating appliance (e.g., microwave, stove) to apply heat to a specified object. It should be triggered when the task requires warming or cooking an item, and the appliance is available and properly prepared (e.g., empty, closed). The input is the object name and appliance name, and the output is the object being heated, changing its state to fulfill task goals like 'heat some egg'.
+description: Uses a heating appliance (microwave, stoveburner, oven) to apply heat to a specified object. Use when the task requires warming or cooking an item (e.g., "heat some egg", "warm the mug") and a heating appliance is available. Takes the object name and appliance name as input and outputs the object in a heated state, ready for placement at the task's target location.
 ---
 # Skill: Heat Object with Appliance
 
@@ -24,6 +24,23 @@ Follow this sequence of actions. Use the bundled `validate_and_plan.py` script t
 *   **Object Location:** The object may not be at the initial location. Be prepared to search other receptacles (e.g., fridge, countertop, cabinet) if not found.
 *   **Alternative Appliances:** If the primary appliance (e.g., microwave) is unavailable or broken, consider alternatives like a stoveburner.
 
+## Example
+
+**Task:** "Heat some egg and put it on the diningtable."
+
+**Input:** `object: egg 1`, `appliance: microwave 1`, `target: diningtable 1`
+
+**Sequence:**
+1. `go to fridge 1` → Observation: "You are at fridge 1."
+2. `open fridge 1` → Observation: "You open the fridge 1. You see egg 1, ..."
+3. `take egg 1 from fridge 1` → Observation: "You pick up the egg 1 from the fridge 1."
+4. `go to microwave 1` → Observation: "You are at microwave 1."
+5. `heat egg 1 with microwave 1` → Observation: "You heat the egg 1 using the microwave 1."
+6. `go to diningtable 1` → Observation: "You are at diningtable 1."
+7. `put egg 1 in/on diningtable 1` → Observation: "You put the egg 1 in/on the diningtable 1."
+
+**Output:** The egg 1 is heated and placed on the diningtable 1. Task complete.
+
 ## Bundled Resources
 *   `scripts/validate_and_plan.py`: A utility to check the initial environment state against the skill's prerequisites.
 *   `references/common_heating_appliances.md`: A list of typical appliances and their properties in the ALFWorld environment.
diff --git a/experiments/src/skills/alfworld/alfworld-inventory-management/SKILL.md b/experiments/src/skills/alfworld/alfworld-inventory-management/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-inventory-management
-description: This skill tracks which objects have been collected and which remain to be found for multi-object tasks. It should be triggered when working with tasks requiring multiple instances of the same object type. The skill maintains a count of collected vs. needed objects and guides the search for remaining items.
+description: Use when the agent must collect and track multiple instances of the same object type in ALFWorld (e.g., "put two cellphone in bed"). This skill maintains a count of collected versus needed objects, guides systematic searching through receptacles, and ensures each found object is placed at the target before searching for the next.
 ---
 # Inventory Management Skill
 
@@ -14,19 +14,69 @@ Activate this skill when:
 
 ### 1. Initialize Inventory
 - Parse the task description to identify:
-  - Target object type (e.g., "cellphone")
-  - Required quantity (e.g., "two")
+  - **Target object type** (e.g., "cellphone")
+  - **Required quantity** (e.g., "two" = 2)
+  - **Target receptacle** (e.g., "bed 1")
 - Initialize counters: `collected = 0`, `needed = <quantity>`
 - Create empty list for searched locations
 
 ### 2. Systematic Search Pattern
 Follow this search priority:
-1. **Visible surfaces** (desks, dressers, beds) - check first
-2. **Closed containers** (drawers, cabinets) - open and inspect
-3. **Return to known locations** if inventory incomplete
+1. **Visible surfaces** (desks, dressers, beds, countertops) - check first
+2. **Closed containers** (drawers, cabinets, safes) - open and inspect
+3. **Less common locations** (shelves, side tables, garbage cans)
+4. **Return to known locations** if inventory incomplete
 
-**Critical Rule:** After finding an object, immediately place it at the target location before searching for the next one.
+**Critical Rule:** After finding an object, immediately place it at the target location before searching for the next one. Do not attempt to carry multiple objects simultaneously.
 
 ### 3. Action Decision Logic
-Use this decision tree:
+Use this decision tree at each step:
 
+```
+Is target object visible in current observation?
+├── YES → Take it, go to target receptacle, put it down
+│         └── Increment collected counter
+│             ├── collected == needed → TASK COMPLETE
+│             └── collected < needed → Continue searching
+└── NO → Have all receptacles been searched?
+          ├── YES → Revisit receptacles (objects may have been missed)
+          └── NO → Go to next unsearched receptacle
+```
+
+### 4. Per-Object Cycle
+For each object instance found, follow this exact sequence:
+1. `take {object} from {current_receptacle}`
+2. `go to {target_receptacle}`
+3. `put {object} in/on {target_receptacle}`
+4. Update counter: `collected += 1`
+5. If `collected < needed`, navigate to next unsearched receptacle
+
+## Example
+
+**Task:** "Put two cellphone in bed 1."
+
+```
+> go to desk 1
+On the desk 1, you see a cellphone 2, a pen 1.
+> take cellphone 2 from desk 1
+You pick up the cellphone 2 from the desk 1.
+> go to bed 1
+On the bed 1, you see a pillow 1.
+> put cellphone 2 in/on bed 1
+You put the cellphone 2 in/on the bed 1.
+[collected: 1/2]
+> go to dresser 1
+On the dresser 1, you see a cellphone 3, a keychain 1.
+> take cellphone 3 from dresser 1
+You pick up the cellphone 3 from the dresser 1.
+> go to bed 1
+On the bed 1, you see a cellphone 2, a pillow 1.
+> put cellphone 3 in/on bed 1
+You put the cellphone 3 in/on the bed 1.
+[collected: 2/2 — TASK COMPLETE]
+```
+
+## Error Handling
+- **Object not at expected location**: Mark location as searched, proceed to next receptacle
+- **"Nothing happened"**: The action syntax may be wrong; verify object name and receptacle
+- **Counter mismatch**: Re-examine the target receptacle to confirm how many objects are already placed
diff --git a/experiments/src/skills/alfworld/alfworld-locate-target-object/SKILL.md b/experiments/src/skills/alfworld/alfworld-locate-target-object/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-locate-target-object
-description: This skill navigates to a suspected location and identifies a target object. It should be triggered when the agent's goal requires finding a specific object (e.g., 'potato', 'plate') and its location is not immediately known. The skill involves moving to a relevant receptacle (like a fridge or cabinet) and checking its contents, outputting the object's location or confirming its absence.
+description: Navigates to a suspected location and identifies a target object. Use when your goal requires finding a specific object (e.g., "potato", "plate") and its location is not immediately known. Moves to a relevant receptacle (like a fridge or cabinet), checks its contents, and outputs the object's location or confirms its absence.
 ---
 # Skill: Locate Target Object
 
@@ -36,5 +36,19 @@ Follow this sequence of actions and reasoning.
 *   **Sequential Access:** You must `go to` a location before you can `open` it.
 *   **Visual Confirmation:** Only trust the `Observation` after opening a receptacle to confirm an object's presence or absence.
 
+## Example
+
+**Scenario:** You need to find a potato for a heating task.
+
+```
+Thought: I need to find a potato. Potatoes are commonly stored in the fridge.
+Action: go to fridge 1
+Observation: The fridge 1 is closed.
+Action: open fridge 1
+Observation: You open the fridge 1. The fridge 1 is open. In it, you see a potato 1, a lettuce 2.
+```
+
+**Result:** The potato has been located in `fridge 1`. You can now `take potato 1 from fridge 1` and proceed.
+
 ## Next Steps
 After successfully locating the object, you will typically need to `take` it or interact with it, which is outside the scope of this skill. If the object is not found, trigger this skill again with a new suspected location.
diff --git a/experiments/src/skills/alfworld/alfworld-object-cooler/SKILL.md b/experiments/src/skills/alfworld/alfworld-object-cooler/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-object-cooler
-description: This skill cools a held object using an appropriate cooling appliance, such as a fridge. It should be triggered when the task requires reducing the temperature of an object (e.g., a hot pot). The skill assumes the agent is holding the object and is near the cooling receptacle; it performs the 'cool' action to achieve the desired state change, preparing the object for subsequent steps like placement or serving.
+description: Cools a held object using an appropriate cooling appliance such as a fridge or freezer. Use when the task requires reducing the temperature of an object (e.g., "cool some pot", "chill the mug") and the agent is already holding the object. Performs the ALFWorld `cool` action and outputs the cooled object ready for subsequent placement or serving steps.
 ---
 # Skill: Cool Held Object
 
diff --git a/experiments/src/skills/alfworld/alfworld-object-heater/SKILL.md b/experiments/src/skills/alfworld/alfworld-object-heater/SKILL.md
@@ -1,31 +1,42 @@
 ---
 name: alfworld-object-heater
-description: This skill heats a specified object using an available heating appliance (e.g., microwave, stove). Activate this skill when the agent has an object that requires heating and the appliance is prepared. It requires the object and appliance as inputs and results in the object being heated.
+description: Heats a specified object using an available heating appliance (e.g., microwave, stoveburner). Use when you are holding an object that requires heating and need to navigate to and operate the heating appliance. Takes the object and appliance as inputs and results in the object being in a heated state.
 ---
-# Skill: Heat Object
+# Instructions
 
-## Purpose
-Use this skill to heat a specified object (e.g., potato, soup) using a compatible heating appliance (e.g., microwave, stove) in the ALFWorld environment. The skill handles the sequence of navigation, preparation, and operation of the appliance.
+Heat an object you are holding using a compatible heating appliance (microwave or stoveburner).
 
 ## Prerequisites
-1. **Object in Inventory:** The target object must be in the agent's possession (e.g., recently taken from a receptacle).
-2. **Appliance Available:** A compatible heating appliance (microwave, stoveburner) must be present and accessible in the environment.
-3. **Appliance State:** The appliance must be in a state ready for heating (e.g., microwave door open, stove burner available).
-
-## Core Workflow
-Follow this high-level sequence. For detailed, error-prone steps (like checking appliance state), use the bundled script.
-
-1.  **Navigate** to the target heating appliance.
-2.  **Prepare** the appliance (e.g., open the microwave door).
-3.  **Execute** the heating action on the object using the appliance.
-4.  **(Optional) Navigate** to a target location (e.g., dining table) to place the heated object.
-
-## Key Decision Points
-*   **Appliance Selection:** Choose the most appropriate appliance based on the object and context (e.g., use a microwave for quick heating, a stove for cooking).
-*   **Error Recovery:** If an action fails ("Nothing happened"), re-evaluate the appliance's state (is it open? is it free?) or your inventory (do you have the object?).
-*   **Post-Heating Action:** Decide if the heated object should be placed elsewhere (e.g., on a dining table) as part of the task.
-
-## Important Notes
-*   The `heat` action requires the object to be in your inventory and the appliance to be ready.
-*   Always verify the observation after each action to confirm success before proceeding.
-*   Refer to the bundled reference for a detailed breakdown of the example trajectory and common pitfalls.
+- The target object must be in your inventory
+- A heating appliance (microwave, stoveburner) must exist in the environment
+
+## Workflow
+1. **Navigate:** `go to {appliance}` (e.g., `go to microwave 1`)
+2. **Check state:** If observation says appliance is closed, execute `open {appliance}` -- verify observation confirms it is now open
+3. **Heat:** `heat {object} with {appliance}` -- verify observation confirms "You heat the {object}"
+4. **(Optional) Place:** If the task requires it, navigate to the destination and place the heated object
+
+## Action Format
+- `go to microwave 1` / `go to stoveburner 1`
+- `open microwave 1`
+- `heat {object} with {appliance}` (e.g., `heat potato 1 with microwave 1`)
+
+## Error Recovery
+- "Nothing happened" on heat: Check (1) you are holding the object, (2) appliance is open, (3) appliance name is correct
+- Appliance occupied: Take the existing item out first, then retry
+
+## Example
+
+**Scenario:** You are holding `potato 1` and need to heat it.
+
+```
+Thought: I need to heat the potato. I'll go to the microwave.
+Action: go to microwave 1
+Observation: The microwave 1 is closed.
+Action: open microwave 1
+Observation: You open the microwave 1. The microwave 1 is open. In it, you see nothing.
+Action: heat potato 1 with microwave 1
+Observation: You heat the potato 1 using the microwave 1.
+```
+
+**Result:** The potato is now heated. Proceed to place it at the destination if required by the task.
diff --git a/experiments/src/skills/alfworld/alfworld-object-locator/SKILL.md b/experiments/src/skills/alfworld/alfworld-object-locator/SKILL.md
@@ -1,22 +1,74 @@
 ---
 name: alfworld-object-locator
-description: This skill scans the current environment observation to identify the presence and location of a target object needed for a task. It should be triggered when the agent's goal requires an object that is not currently in the agent's inventory, and the observation does not explicitly state where the object is. The skill analyzes the textual observation to find receptacles that likely contain the target, based on common sense or domain knowledge (e.g., a 'dishsponge' might be on a 'cart'), and outputs the identified target receptacle location for navigation.
+description: Use when the agent needs to find a specific object in ALFWorld that is not currently in inventory and whose location is unknown. This skill parses the environment observation, ranks receptacles by likelihood of containing the target object using common-sense reasoning, and outputs a navigation action to the most promising location.
 ---
 # Skill: Object Locator for ALFWorld
 
 ## When to Use
 Trigger this skill when:
-1. Your goal requires a specific object
+1. Your goal requires a specific object (e.g., `knife`, `cellphone`, `apple`)
 2. The object is not in your inventory
 3. The current observation does not explicitly state the object's location
 
-## Core Logic
-1. **Parse Observation**: Extract all mentioned receptacles from the environment description
-2. **Analyze Likelihood**: Use common-sense reasoning to rank receptacles where the target object is most likely to be found
-3. **Output Action**: Generate a navigation action to the most promising receptacle
+## Core Workflow
 
-## Quick Reference
-- For detailed object-receptacle mappings, see `references/object_mappings.md`
-- For the core location algorithm, see `scripts/locate_object.py`
+### 1. Parse the Environment
+Extract all visible receptacles from the observation text. Typical ALFWorld receptacles include:
+- **Surfaces**: countertop, desk, dresser, bed, shelf, sidetable, coffeetable, diningtable
+- **Containers**: drawer, cabinet, safe, fridge, microwave, garbagecan
+- **Appliances**: sinkbasin, bathtub, stoveburner, toaster
 
-## Basic Usage Pattern
+### 2. Rank by Likelihood
+Use common-sense reasoning to prioritize where the target object is most likely found:
+
+| Object Type | High-Probability Receptacles |
+|-------------|------------------------------|
+| Kitchen items (knife, spatula, pan) | countertop, drawer, diningtable, stoveburner |
+| Food (apple, potato, tomato, bread) | fridge, countertop, diningtable, microwave |
+| Bathroom items (sponge, cloth, soap) | sinkbasin, bathtub, cart, shelf |
+| Electronics (cellphone, laptop, remote) | desk, sidetable, dresser, bed, coffeetable |
+| Stationery (pen, pencil, book) | desk, shelf, drawer, sidetable |
+| Lighting (candle, desklamp) | sidetable, shelf, desk, dresser |
+
+### 3. Navigate and Search
+For each candidate receptacle (in priority order):
+1. `go to {receptacle}`
+2. Read the observation — does it mention the target object?
+   - **YES**: `take {object} from {receptacle}` — object found
+   - **NO**: If the receptacle is closed, `open {receptacle}` and re-check
+   - **Still NO**: Move to the next candidate receptacle
+
+### 4. Track Searched Locations
+Maintain a list of already-searched receptacles to avoid revisiting them. If all high-probability locations are exhausted, expand the search to remaining receptacles.
+
+## Example
+
+**Task:** "Clean the knife and put it in drawer."
+**Observation:** "You are in the middle of a room. Looking quickly around you, you see a countertop 1, a drawer 1, a drawer 2, a fridge 1, a sinkbasin 1, a stoveburner 1."
+
+```
+> go to countertop 1
+On the countertop 1, you see a knife 1, a saltshaker 2, a bread 1.
+> take knife 1 from countertop 1
+You pick up the knife 1 from the countertop 1.
+```
+
+**Result:** Target object `knife 1` located and acquired from `countertop 1`.
+
+**Example — Object not at first location:**
+
+```
+> go to countertop 1
+On the countertop 1, you see a saltshaker 2, a bread 1.
+> go to drawer 1
+The drawer 1 is closed.
+> open drawer 1
+You open the drawer 1. The drawer 1 is open. In it, you see a knife 1.
+> take knife 1 from drawer 1
+You pick up the knife 1 from the drawer 1.
+```
+
+## Error Handling
+- **Object not found in any receptacle**: Re-check closed containers that may not have been opened. Some objects are only visible after opening.
+- **Multiple instances**: If the task requires a specific instance (e.g., `knife 1` vs `knife 2`), verify the object identifier matches before taking it.
+- **"Nothing happened"**: The `take` command may fail if the agent is not at the receptacle. Ensure navigation was successful before attempting to take.
diff --git a/experiments/src/skills/alfworld/alfworld-object-state-inspector/SKILL.md b/experiments/src/skills/alfworld/alfworld-object-state-inspector/SKILL.md
@@ -1,30 +1,42 @@
 ---
 name: alfworld-object-state-inspector
-description: Checks the current state or contents of a specified object or receptacle. Trigger this skill when the agent needs to determine if an object is present, missing, or in a certain condition before proceeding with a task, such as verifying if a holder is empty or if an item is available. It typically follows navigation and involves observing the environment's feedback, providing crucial information for decision-making in the task flow.
+description: Inspects a receptacle's contents by navigating to it and reading the observation. Use when you need to check what is on or inside a receptacle (e.g., "what's on the shelf", "is the holder empty", "check the table for items"). Executes `go to {receptacle}`, parses the observation listing items present, and decides whether to take an item, search elsewhere, or proceed.
 ---
 # Instructions
 
-Use this skill to inspect the state of a target object or receptacle in an AlfWorld household environment. The primary goal is to obtain the observation feedback from the environment about what is currently on or in the target.
+Inspect the state or contents of a target receptacle by navigating to it and parsing the environment's observation feedback.
 
-## When to Trigger
-Trigger this skill immediately after navigating to a target receptacle (e.g., `go to toiletpaperhanger 1`) when you need to know:
-*   If the target is empty.
-*   What specific objects are present on/in the target.
-*   The condition or state of the target (implied by the environment's observation).
+## Workflow
+1. **Navigate:** Execute `go to {target_receptacle}`
+2. **Read observation:** The environment automatically reports what is on/in the receptacle -- no additional inspection action is needed
+3. **Parse contents:** Look for patterns:
+   - `"On the {receptacle}, you see nothing."` -- receptacle is empty
+   - `"On the {receptacle}, you see a {item1}, and a {item2}."` -- items are present
+4. **Decide next action** based on the observation:
+   - Empty: search elsewhere for the needed item
+   - Item found: `take {item} from {receptacle}`
+   - Wrong items: move on to the next receptacle
 
-## Core Procedure
-1.  **Navigate to Target:** First, ensure the agent has executed a `go to {target_receptacle}` action. This skill assumes the agent is already at the target's location.
-2.  **Observe Environment Feedback:** The skill is complete once the environment provides an observation in response to the navigation. **Do not perform an additional inspection action.** The observation from the `go to` action contains the state information.
-3.  **Parse Observation:** Interpret the observation message (e.g., "On the toiletpaperhanger 1, you see nothing." or "On the toilet 1, you see a soapbottle 1, and a toiletpaper 1.").
-4.  **Output Decision Data:** Based on the observation, determine the next step in the broader task (e.g., "Target is empty, proceed to find item" or "Target contains required item, proceed to pick it up").
+## Error Recovery
+- "Nothing happened": the `go to` target name is invalid -- verify the receptacle name from your environment scan
+- This skill uses only `go to` for navigation; it does not use `open`, `close`, or `toggle`
 
-## Input/Output Format
-*   **Input Context:** The agent must be at the target location. The last action should be `go to {target_receptacle}`.
-*   **Output:** The observation string from the environment and a brief interpretation.
-    *   **Example Output:** `Observation: On the toiletpaperhanger 1, you see nothing. | Interpretation: The holder is empty. A toiletpaper roll must be found elsewhere.`
+## Example
 
-## Error Handling
-*   If the observation is "Nothing happened," the previous `go to` action was likely invalid. Re-evaluate the target's name or location.
-*   This skill does not involve actions like `open`, `close`, or `toggle`. It relies solely on the observational feedback from navigation.
+**Scenario 1:** Check if a toiletpaperhanger has toilet paper.
 
-**Key Principle:** This skill encapsulates the **waiting and parsing** of the environment's state disclosure after navigation. It provides the critical information needed to decide the subsequent `take`, `put`, or further `go to` action.
+```
+Action: go to toiletpaperhanger 1
+Observation: On the toiletpaperhanger 1, you see nothing.
+```
+
+**Decision:** Holder is empty. Find a toiletpaper roll elsewhere and bring it here.
+
+**Scenario 2:** Check a toilet for available items.
+
+```
+Action: go to toilet 1
+Observation: On the toilet 1, you see a soapbottle 1, and a toiletpaper 1.
+```
+
+**Decision:** toiletpaper 1 is available. Execute `take toiletpaper 1 from toilet 1`.
diff --git a/experiments/src/skills/alfworld/alfworld-object-state-modifier/SKILL.md b/experiments/src/skills/alfworld/alfworld-object-state-modifier/SKILL.md
@@ -1,31 +1,40 @@
 ---
 name: alfworld-object-state-modifier
-description: This skill uses an appliance to change the state of an object (e.g., cooling, heating, cleaning). It should be triggered when the task requires altering an object's temperature or cleanliness using a specific device (like cooling with a fridge or heating with a microwave). The skill requires the object, the target state, and the appliance as inputs, and executes the corresponding modifier action (e.g., 'cool X with Y').
+description: Uses an appliance to change the state of an object (cooling, heating, or cleaning). Use when the task requires altering an object's temperature or cleanliness using a specific device (e.g., cooling with a fridge, heating with a microwave, cleaning with a sinkbasin). Takes the object, target state, and appliance as inputs and executes the corresponding modifier action.
 ---
 # Instructions
 
-## When to Use
-Use this skill when the task requires you to **change the state of an object** using a specific household appliance. The primary actions are:
-- **Cool** an object (e.g., with a fridge).
-- **Heat** an object (e.g., with a microwave or stove).
-- **Clean** an object (e.g., with a sink).
-
-## Core Procedure
-1.  **Locate & Acquire Object:** First, navigate to and pick up the target object.
-2.  **Navigate to Appliance:** Go to the appliance required for the state change (e.g., `fridge 1`, `microwave 1`).
-3.  **Prepare Appliance (if needed):** Some appliances require preparation (e.g., opening a fridge or microwave door). Perform the necessary `open` or `toggle` action.
-4.  **Execute State Change:** Perform the core modifier action: `cool {obj} with {appliance}`, `heat {obj} with {appliance}`, or `clean {obj} with {appliance}`.
-5.  **Complete Task:** After the state is changed, proceed with the next task step (e.g., placing the object elsewhere).
-
-## Key Considerations
-- **Invalid Actions:** If the environment responds with "Nothing happened," your action was invalid. Consult the `references/appliance_interaction_guide.md` for troubleshooting.
-- **Appliance State:** Always check if an appliance is open/closed/on/off before attempting the modifier action.
-- **Object Holding:** You must be holding the target object (`{obj}`) before executing the state change action.
-
-## Inputs Required
-- `{obj}`: The specific object identifier (e.g., `tomato 1`).
-- `{target_state}`: The desired state change (`cool`, `heat`, or `clean`).
-- `{appliance}`: The specific appliance identifier (e.g., `fridge 1`).
-
-## Output Action
-The skill's final output is a single, formatted action string: `{target_state} {obj} with {appliance}`.
+Change an object's state (cool, heat, or clean) using a household appliance. You must be holding the target object before executing the state change.
+
+## Workflow
+1. **Navigate to appliance:** `go to {appliance}` (e.g., `go to fridge 1`)
+2. **Prepare if closed:** If observation says appliance is closed, execute `open {appliance}` -- verify it opens
+3. **Execute state change:** `{action} {obj} with {appliance}` -- verify observation confirms the change
+4. **Proceed:** Continue with the next task step (e.g., placing the modified object)
+
+## Action Mapping
+| State Change | Action | Typical Appliance |
+|---|---|---|
+| Cool | `cool {obj} with {appliance}` | `fridge 1` |
+| Heat | `heat {obj} with {appliance}` | `microwave 1`, `stoveburner 1` |
+| Clean | `clean {obj} with {appliance}` | `sinkbasin 1` |
+
+## Error Recovery
+- "Nothing happened": Check (1) you are holding the object, (2) appliance is open/ready, (3) object and appliance names are correct
+- Appliance occupied: remove existing items first with `take {item} from {appliance}`
+
+## Example
+
+**Scenario:** You need to cool a tomato using the fridge.
+
+```
+Thought: I'm holding tomato 1 and need to cool it. I'll go to the fridge.
+Action: go to fridge 1
+Observation: The fridge 1 is closed.
+Action: open fridge 1
+Observation: You open the fridge 1. The fridge 1 is open. In it, you see a lettuce 1.
+Action: cool tomato 1 with fridge 1
+Observation: You cool the tomato 1 using the fridge 1.
+```
+
+**Result:** The tomato is now in a cooled state. Proceed with the next task step (e.g., placing it on a countertop).
diff --git a/experiments/src/skills/alfworld/alfworld-object-storer/SKILL.md b/experiments/src/skills/alfworld/alfworld-object-storer/SKILL.md
@@ -1,34 +1,64 @@
 ---
 name: alfworld-object-storer
-description: This skill places an object into a selected storage receptacle after confirming its suitability. It should be triggered when the agent has identified an appropriate storage location and is ready to complete the storage task. The skill takes the object and target receptacle as inputs and results in the object being stored.
+description: Use when the agent is holding an object and needs to place it into a target receptacle in ALFWorld. This skill checks receptacle suitability, opens closed containers if needed, and executes the `put` command to store the object. It handles both open surfaces (countertops, beds) and closed containers (drawers, cabinets).
 ---
 # Skill: Object Storer
 
-## Purpose
-This skill orchestrates the final step of storing a clean object into a designated receptacle within a household environment. It is triggered after the agent has:
-1. Located the target object.
-2. Cleaned the object if required.
-3. Identified and validated a suitable storage location.
-
-## Core Logic
-The skill performs a final suitability check and executes the storage action. The core decision is:
-- **If the receptacle is open and empty (or appropriately designated)**, proceed with storage.
-- **If the receptacle is closed**, open it first, then store the object.
-- **If the receptacle is unsuitable** (e.g., already contains unrelated items), the agent should abort this skill and search for an alternative location.
-
-## Inputs & Execution
-- **Primary Inputs:** `{object_name}`, `{target_receptacle}`
-- **Prerequisite State:** The agent must be holding the clean `{object_name}` and be at the location of the `{target_receptacle}`.
-- **Action:** Execute the `put {object_name} in/on {target_receptacle}` command.
-
-## Example from Trajectory
-**Scenario:** Storing a clean knife.
-1. **Trigger Condition:** Agent is holding `knife 1` (cleaned) and has determined `drawer 1` is a suitable, empty storage location.
-2. **Skill Execution:**
-   - Agent is at `drawer 1`.
-   - Observation: `On the drawer 1, you see nothing.`
-   - **Action:** `put knife 1 in/on drawer 1`
+## When to Use
+Trigger this skill when:
+1. The agent is holding the target object (optionally cleaned/heated/cooled as required)
+2. A suitable storage receptacle has been identified
+3. The agent needs to execute the final placement step
+
+## Core Workflow
+
+### 1. Validate Prerequisites
+- Confirm the agent is holding `{object_name}` (check inventory)
+- Confirm the agent is at the location of `{target_receptacle}`
+- If not at the receptacle, navigate there first: `go to {target_receptacle}`
+
+### 2. Check Receptacle State
+Evaluate the receptacle before placing:
+
+| Receptacle State | Action |
+|-----------------|--------|
+| Open and empty/suitable | Proceed with `put` |
+| Closed (drawer, cabinet, safe) | `open {target_receptacle}` first, then `put` |
+| Unsuitable (wrong type, full) | Abort and search for alternative receptacle |
+
+### 3. Execute Storage
+- Run: `put {object_name} in/on {target_receptacle}`
+- Check the observation for confirmation
+
+### 4. Verify Placement
+- A successful placement updates the receptacle contents in the observation
+- If the observation confirms the object is now in/on the receptacle, storage is complete
+
+## Example
+
+**Task:** "Clean the knife and put it in a drawer."
+
+```
+> go to drawer 1
+The drawer 1 is closed.
+> open drawer 1
+You open the drawer 1. The drawer 1 is open. In it, you see nothing.
+> put knife 1 in/on drawer 1
+You put the knife 1 in/on the drawer 1.
+```
+
+**Result:** `knife 1` is now stored in `drawer 1`. Task complete.
+
+**Example 2 — Open surface:**
+
+```
+> go to bed 1
+On the bed 1, you see a pillow 1.
+> put cellphone 2 in/on bed 1
+You put the cellphone 2 in/on the bed 1.
+```
 
 ## Error Handling
-- If the environment responds with "Nothing happened," the action was invalid. Consult the `receptacle_suitability_guide.md` reference and restart the search process.
-- Do not use this skill if the receptacle contains items that conflict with the object's storage norms (e.g., putting a knife in a drawer full of spoons).
+- **"Nothing happened"**: The agent may not be holding the object, or the receptacle name is incorrect. Verify with `inventory` and re-check the receptacle identifier.
+- **Receptacle unsuitable**: If the receptacle is not appropriate for the object, search for an alternative using the object-locator skill.
+- **Agent not at receptacle**: Navigate to the receptacle with `go to {target_receptacle}` before attempting `put`.
diff --git a/experiments/src/skills/alfworld/alfworld-object-transporter/SKILL.md b/experiments/src/skills/alfworld/alfworld-object-transporter/SKILL.md
@@ -1,36 +1,43 @@
 ---
 name: alfworld-object-transporter
-description: This skill picks up a target object from its current receptacle and moves it to a specified destination receptacle. It should be triggered when the agent has located an object and needs to relocate it to complete a task (e.g., moving a laptop to a desk). The skill requires the object identifier and source location as input, and it outputs the action sequence to take and transport the object.
+description: Picks up a target object from its current receptacle and moves it to a specified destination receptacle. Use when you have located an object and need to relocate it to complete a task (e.g., moving a laptop to a desk). Takes the object identifier, source receptacle, and destination receptacle as inputs and outputs the action sequence to take, transport, and place the object.
 ---
 # Instructions
 
-## When to Use
-Use this skill when you have:
-1. **Identified the target object** (e.g., `laptop 1`) and its **current source receptacle** (e.g., `bed 2`).
-2. **Identified the destination receptacle** (e.g., `desk 1`).
-3. The goal requires moving the object to the destination to complete a task.
+Pick up an object from its current location and transport it to a destination receptacle.
 
-## Input Requirements
-You must provide the following information to execute this skill:
-- **`target_object`**: The identifier of the object to move (e.g., `laptop 1`).
-- **`source_receptacle`**: The identifier of the receptacle where the object is currently located (e.g., `bed 2`).
-- **`destination_receptacle`**: The identifier of the receptacle where the object must be placed (e.g., `desk 1`).
-
-## Execution Flow
-1. **Navigate to Source**: Go to the `source_receptacle`.
-2. **Pick Up Object**: Take the `target_object` from the `source_receptacle`.
-3. **Navigate to Destination**: Go to the `destination_receptacle`.
-4. **Place Object**: Put the `target_object` in/on the `destination_receptacle`.
+## Workflow
+1. **Navigate to source:** `go to {source_receptacle}` -- verify observation shows the target object
+2. **Pick up:** `take {object} from {source_receptacle}` -- verify "You pick up" confirmation
+3. **Navigate to destination:** `go to {destination_receptacle}`
+4. **Place:** `put {object} in/on {destination_receptacle}` -- verify "You put" confirmation
 
 ## Action Format
-All actions must follow the Alfworld environment's strict format:
 - `go to {receptacle}`
 - `take {object} from {receptacle}`
 - `put {object} in/on {receptacle}`
 
-## Error Handling
-- If an action fails (environment returns "Nothing happened"), consult the troubleshooting guide in `references/troubleshooting.md`.
-- If the object or receptacle is not found, re-scan the environment before retrying.
+## Error Recovery
+- "Nothing happened" on take: verify you are at the correct receptacle and the object name matches the observation
+- "Nothing happened" on put: verify you are holding the object and at the correct destination
+- Object not visible: re-scan the environment to locate it before retrying
+
+## Example
+
+**Scenario:** Move `laptop 1` from `bed 2` to `desk 1`.
+
+```
+Action: go to bed 2
+Observation: On the bed 2, you see a laptop 1, a pillow 1.
+Action: take laptop 1 from bed 2
+Observation: You pick up the laptop 1 from the bed 2.
+Action: go to desk 1
+Observation: On the desk 1, you see a pen 2.
+Action: put laptop 1 in/on desk 1
+Observation: You put the laptop 1 in/on the desk 1.
+```
+
+**Result:** The laptop has been transported from the bed to the desk.
 
 ## Bundled Resources
 - **Script**: `scripts/transport_sequence.py` provides a deterministic sequence generator.
diff --git a/experiments/src/skills/alfworld/alfworld-receptacle-closer/SKILL.md b/experiments/src/skills/alfworld/alfworld-receptacle-closer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-receptacle-closer
-description: Closes an open receptacle to maintain environment tidiness after inspection. Trigger this after you have finished searching a container and no longer need it open. It helps prevent clutter and is often used as a cleanup step following object searching inside drawers or similar containers.
+description: Closes an open receptacle to maintain environment tidiness after inspection. Use when you have finished searching a container (drawer, cabinet, fridge) and no longer need it open. Takes a receptacle identifier as input and outputs confirmation that the receptacle is closed, preventing clutter during multi-step search tasks.
 ---
 # Skill: Receptacle Closer
 
diff --git a/experiments/src/skills/alfworld/alfworld-receptacle-finder/SKILL.md b/experiments/src/skills/alfworld/alfworld-receptacle-finder/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-receptacle-finder
-description: This skill searches for a suitable empty or appropriately occupied receptacle (like a shelf) to place an object. It should be triggered when the agent needs to store or place an object and must evaluate available receptacles. The skill examines candidate receptacles and identifies one meeting the placement criteria.
+description: Searches for a suitable empty or appropriately occupied receptacle (like a shelf or table) to place an object. Use when you are holding an object that needs to be stored or placed and must find a receptacle that meets the placement criteria. Examines candidate receptacles by navigating to and inspecting each one until a suitable location is found.
 ---
 # Instructions
 
@@ -20,5 +20,22 @@ description: This skill searches for a suitable empty or appropriately occupied
 *   **Observation Parsing:** Carefully read the observation after each `go to` action. The line "On the {recep}, you see..." lists its contents. "you see nothing." indicates it is empty.
 *   **Invalid Actions:** If an action fails ("Nothing happened"), re-evaluate your target and try a different receptacle or confirm the object is in your inventory.
 
-## Example Trajectory (from `references/example_trajectory.md`)
-For a detailed example of this skill in action, including handling object pre-cleaning and sequential shelf evaluation, refer to the bundled reference.
+## Example
+
+**Scenario:** You are holding `soapbar 1` (clean) and need to find an empty shelf to place it.
+
+```
+Thought: I need to find an empty shelf for the soapbar. I'll check shelf 1 first.
+Action: go to shelf 1
+Observation: On the shelf 1, you see a tissuebox 1.
+Thought: Shelf 1 has items. Let me try shelf 2.
+Action: go to shelf 2
+Observation: On the shelf 2, you see nothing.
+Action: put soapbar 1 in/on shelf 2
+Observation: You put the soapbar 1 in/on the shelf 2.
+```
+
+**Result:** Found an empty shelf and placed the soapbar on it.
+
+## Bundled Reference
+For a detailed example including handling object pre-cleaning and sequential shelf evaluation, refer to `references/example_trajectory.md`.
diff --git a/experiments/src/skills/alfworld/alfworld-receptacle-navigator/SKILL.md b/experiments/src/skills/alfworld/alfworld-receptacle-navigator/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-receptacle-navigator
-description: This skill plans and executes movement to a target receptacle within the environment. It should be triggered when the agent needs to interact with an object at a specific location (e.g., go to fridge to cool an item) or needs to access a receptacle itself (e.g., go to garbagecan to dispose of an item). The skill uses the receptacle name from the observation or task goal, outputs the 'go to' action, and confirms arrival at the destination.
+description: Plans and executes movement to a target receptacle within the ALFWorld environment. Use when the agent needs to reach a specific location before interacting with objects there (e.g., go to fridge to cool an item, go to garbagecan to dispose of an item). Takes a receptacle identifier as input, executes the `go to` action, and outputs confirmation of arrival at the destination.
 ---
 # Skill: Receptacle Navigator
 
@@ -23,6 +23,15 @@ Trigger this skill when the agent's plan requires:
 3.  If the environment responds with "Nothing happened", the action was invalid. Consult the `references/common_receptacles.md` list and the latest observation to formulate a new `go to` target.
 4.  Upon successful navigation, proceed with the next skill in the plan (e.g., `alfworld-object-interactor`).
 
+## Example
+
+**Input:** `target_receptacle: fridge 1`
+
+**Sequence:**
+1. `go to fridge 1` → Observation: "You are at fridge 1. On the fridge 1, you see nothing."
+
+**Output:** Agent has arrived at fridge 1 and can now interact with it (open, take items, cool objects, etc.).
+
 ## Error Handling
 - **Invalid Target:** If "Nothing happened" is observed, the receptacle may be unreachable or incorrectly named. Re-analyze the scene description to find a valid path or alternative receptacle.
 - **Already at Location:** If the observation indicates you are already at the target, skip the `go to` action and proceed.
diff --git a/experiments/src/skills/alfworld/alfworld-search-pattern-executor/SKILL.md b/experiments/src/skills/alfworld/alfworld-search-pattern-executor/SKILL.md
@@ -1,35 +1,47 @@
 ---
 name: alfworld-search-pattern-executor
-description: Systematically searches a sequence of likely locations for a target object based on common sense. Takes a list of candidate receptacles, orchestrates navigation and inspection, and outputs when the target is found or all locations are exhausted.
+description: Systematically searches a sequence of likely locations for a target object based on common sense. Use when you need to find a specific object and know which receptacles to check but not which one contains it. Takes a list of candidate receptacles, orchestrates navigation and inspection, and outputs when the target is found or all locations are exhausted.
 ---
-# Skill: Systematic Object Search
-
-## Purpose
-Use this skill when you need to find a specific object in a household environment without prior knowledge of its exact location. The skill implements a robust search pattern based on common sense about where objects are typically stored.
-
-## Core Workflow
-1.  **Input:** A target object name (e.g., `remotecontrol`) and an ordered list of candidate receptacles to search.
-2.  **Process:** Navigate to each candidate location in sequence. For each receptacle:
-    *   If it's closed, open it.
-    *   Inspect its contents.
-    *   If the target object is found, take it and proceed to the placement phase.
-    *   If the receptacle was opened and is empty, close it before moving on.
-3.  **Output:** Success when the object is found, or a failure state after all candidates are exhausted.
-
-## Key Principles
-*   **Methodical Search:** Do not skip locations in the provided sequence unless the object is found.
-*   **State Management:** Always close drawers/cabinets after checking them if they were opened.
-*   **Focus:** Once the object is found, immediately transition to the next phase of the task (e.g., `put`). Avoid redundant searches.
-*   **Error Handling:** If an action fails (e.g., "Nothing happened"), the skill logic in `scripts/search_orchestrator.py` provides fallback reasoning.
-
-## Usage Example
+# Instructions
+
+For each candidate receptacle in order, execute this action sequence:
+
+## Workflow
+1. **Navigate:** `go to {receptacle}`
+2. **Open if closed:** If observation says "{receptacle} is closed", execute `open {receptacle}`
+3. **Inspect:** Read the observation for the target object name
+4. **If found:** Execute `take {target_object} from {receptacle}` and stop searching
+5. **If not found:** If you opened the receptacle, execute `close {receptacle}`, then continue to the next candidate
+6. **If all exhausted:** Report that the target was not found in any candidate location
+
+## Action Format
+- `go to {receptacle}` -- navigate to a location
+- `open {receptacle}` -- open a closed drawer/cabinet/fridge
+- `close {receptacle}` -- close after checking (state management)
+- `take {object} from {receptacle}` -- pick up the target when found
+
+## Key Rules
+- Search candidates in order; do not skip locations
+- Always close drawers/cabinets after checking if you opened them
+- Once the object is found, immediately stop searching and proceed to the next task phase
+- If "Nothing happened" is returned, verify the receptacle name and retry with the correct identifier
+
+## Example
+
 **Goal:** "find two remotecontrol and put them in armchair."
-**Skill Execution:**
-1.  Activate this skill with target=`remotecontrol`, candidates=`['sofa 1', 'sidetable 1', 'dresser 1', 'drawer 1', 'drawer 2', 'drawer 3', 'drawer 4', 'coffeetable 1']`.
-2.  The skill searches locations in order. It finds the first `remotecontrol` on `coffeetable 1`.
-3.  The agent takes the object and proceeds to place it in `armchair 1`.
-4.  The skill is re-activated for the second `remotecontrol`, searching the remaining candidates (or the same list). It finds the second `remotecontrol` on `coffeetable 1`.
-5.  The agent takes and places the second object, completing the task.
-
-## Integration
-This skill is designed to be called as a subroutine within a larger task plan. The bundled `search_orchestrator.py` script handles the low-level action sequencing to prevent logical errors and repetitive mistakes observed in the learning trajectory.
+
+```
+Thought: I need to find remotecontrol. Candidates: sofa 1, sidetable 1, coffeetable 1. Starting search.
+Action: go to sofa 1
+Observation: On the sofa 1, you see a pillow 1.
+Thought: No remotecontrol on sofa 1. Checking next candidate.
+Action: go to sidetable 1
+Observation: On the sidetable 1, you see a keychain 1.
+Thought: Not here either. Checking coffeetable.
+Action: go to coffeetable 1
+Observation: On the coffeetable 1, you see a remotecontrol 1, a remotecontrol 2.
+Action: take remotecontrol 1 from coffeetable 1
+Observation: You pick up the remotecontrol 1 from the coffeetable 1.
+```
+
+**Result:** First remotecontrol found and picked up. Proceed to place it in `armchair 1`, then re-activate search for the second one.
diff --git a/experiments/src/skills/alfworld/alfworld-search-verifier/SKILL.md b/experiments/src/skills/alfworld/alfworld-search-verifier/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-search-verifier
-description: This skill re-examines previously visited locations to confirm the absence of a target object or to check for overlooked items. It should be triggered when an initial search fails to find enough objects or when double-checking is required for task completion. The skill systematically revisits receptacles, ensuring no viable location is missed before concluding the search.
+description: Re-examines previously visited locations to confirm the absence of a target object or to check for overlooked items. Use when an initial search fails to find enough objects or when double-checking is required before concluding task failure. Systematically revisits receptacles, re-opens closed containers, and re-inspects contents to ensure no viable location was missed.
 ---
 # Instructions
 
@@ -26,5 +26,20 @@ description: This skill re-examines previously visited locations to confirm the
     *   **If the target object was found:** Integrate it into your main task plan.
     *   **If the target object was not found:** You can conclusively report that the object is not available in the searched area and adjust your task strategy accordingly (e.g., consider task failure or exploring a new, unsearched area).
 
+## Example
+
+**Scenario:** You need two cellphones but only found one. Revisiting previously searched locations.
+
+```
+Thought: I only found 1 cellphone but need 2. Let me revisit sidetable 1 which I checked earlier.
+Action: go to sidetable 1
+Observation: On the sidetable 1, you see a cellphone 2, a keychain 1.
+Thought: Found cellphone 2! I must have overlooked it during the initial search.
+Action: take cellphone 2 from sidetable 1
+Observation: You pick up the cellphone 2 from the sidetable 1.
+```
+
+**Result:** The second cellphone was found by re-examining a previously visited location.
+
 ## Thought Process Template
 When executing this skill, structure your reasoning as follows:
diff --git a/experiments/src/skills/alfworld/alfworld-storage-explorer/SKILL.md b/experiments/src/skills/alfworld/alfworld-storage-explorer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-storage-explorer
-description: This skill systematically explores storage receptacles (like drawers or cabinets) to find an appropriate placement location for an object. It should be triggered when the agent needs to store an item but the exact storage location is unknown or must be validated. The skill involves opening, inspecting, and closing receptacles to assess their suitability.
+description: Systematically explores storage receptacles (drawers, cabinets, shelves) to find an appropriate placement location for an object. Use when the agent needs to store an item but the exact target receptacle is unknown or ambiguous. Opens, inspects, and closes candidate receptacles to assess suitability, then places the object in the best match.
 ---
 # Skill: Storage Explorer
 
@@ -51,5 +51,18 @@ For each candidate receptacle:
 - If unable to place object in a receptacle, try alternative locations
 - If all exploration fails, reconsider your understanding of "appropriate" storage
 
+## Example
+
+**Task:** "Put a clean sponge in drawer."
+
+**Input:** Holding `sponge 1` (already cleaned). Target type: drawer.
+
+**Sequence:**
+1. `go to drawer 1` → Observation: "You are at drawer 1."
+2. `open drawer 1` → Observation: "You open the drawer 1. The drawer 1 is open. You see nothing."
+3. `put sponge 1 in/on drawer 1` → Observation: "You put the sponge 1 in/on the drawer 1."
+
+**Output:** The sponge 1 has been stored in drawer 1. Task complete.
+
 ## Output Format
 Maintain the standard action format:
diff --git a/experiments/src/skills/alfworld/alfworld-task-verifier/SKILL.md b/experiments/src/skills/alfworld/alfworld-task-verifier/SKILL.md
@@ -1,30 +1,66 @@
 ---
 name: alfworld-task-verifier
-description: This skill checks the current state against the task goal to determine if the objective has been met or if further actions are needed. It is triggered after completing a key sub-action, such as placing an object, to assess progress. The skill evaluates the observation feedback and the remaining requirements, outputting a decision to either continue searching for missing items or conclude the task.
+description: Use when the agent needs to check whether an ALFWorld task objective has been met after completing a sub-action (e.g., placing an object). This skill parses the task goal, evaluates the latest environment observation, and outputs a verification decision — task complete, task incomplete, or action ineffective — to guide the next step.
 ---
-# Instructions
-
-Use this skill to verify task progress in an ALFWorld household environment. The skill is triggered after a key sub-action (e.g., `put {obj} in/on {recep}`) is performed.
-
-## 1. Input Analysis
-- **Input:** The most recent `Observation:` from the environment following an action.
-- **Task Goal:** The original, full task description (e.g., "find two pen and put them in garbagecan").
-
-## 2. Verification Logic
-Analyze the observation to determine if the task's goal conditions are satisfied.
-1.  **Parse the Goal:** Identify the target object(s) and the target receptacle from the task description.
-2.  **Check the Observation:** Scrutinize the observation text for evidence that the required objects are present in the target receptacle.
-    -   Positive evidence: Phrases like `"you see a pen 3"` located `"in/on the garbagecan 1"`.
-    -   The presence of other items in the receptacle does not invalidate success.
-3.  **Make a Decision:**
-    -   **Task Complete:** If the observation confirms all required objects are in the target receptacle. Output: `"Verification: Task complete. No further action needed."`
-    -   **Continue Task:** If the observation shows some, but not all, required objects are in the target receptacle, or if the target object was just placed elsewhere. Output: `"Verification: Task incomplete. Continue searching for [missing object(s)]."`
-    -   **Action Invalid/No Change:** If the observation is `"Nothing happened"` or does not reflect the intended outcome of the last action. Output: `"Verification: Last action was ineffective. Re-assess and try a different approach."`
-
-## 3. Output
-Output only the verification decision in the specified format. Do not output the next action. This skill informs the planning for the *next* action.
-
-**Example Outputs:**
-- `Verification: Task complete. No further action needed.`
-- `Verification: Task incomplete. Continue searching for pen 2.`
-- `Verification: Last action was ineffective. Re-assess and try a different approach.`
+# Skill: Task Verifier for ALFWorld
+
+## When to Use
+Trigger this skill when:
+1. The agent has just completed a key sub-action (e.g., `put {obj} in/on {recep}`)
+2. The agent needs to determine whether the overall task goal is satisfied
+3. The agent must decide whether to continue searching or conclude the task
+
+## Core Workflow
+
+### 1. Parse the Task Goal
+Extract from the original task description:
+- **Target object(s)**: What needs to be found/placed (including quantity)
+- **Target receptacle**: Where objects must end up
+- **Required transformations**: Any cleaning, heating, or cooling steps
+
+### 2. Analyze the Observation
+Evaluate the most recent `Observation:` text from the environment:
+- Look for evidence that required objects are present in the target receptacle
+- Count how many target objects have been successfully placed
+- Note: Other items in the receptacle do not invalidate success
+
+### 3. Make a Verification Decision
+
+| Condition | Decision | Output |
+|-----------|----------|--------|
+| All required objects confirmed in target receptacle | Complete | `Verification: Task complete. No further action needed.` |
+| Some but not all objects placed | Incomplete | `Verification: Task incomplete. Continue searching for {missing object(s)}.` |
+| Observation says "Nothing happened" | Ineffective | `Verification: Last action was ineffective. Re-assess and try a different approach.` |
+| Object placed in wrong receptacle | Incorrect | `Verification: Object placed in wrong location. Retrieve and redirect to {correct receptacle}.` |
+
+### 4. Output Format
+Output **only** the verification decision. Do not output the next action. This skill informs the planning for the next step, not the execution.
+
+## Example
+
+**Task:** "Find two pen and put them in garbagecan."
+
+```
+Action: put pen 3 in/on garbagecan 1
+Observation: You put the pen 3 in/on the garbagecan 1.
+
+> Verification: Task incomplete. Continue searching for pen (1 of 2 placed).
+
+Action: put pen 1 in/on garbagecan 1
+Observation: You put the pen 1 in/on the garbagecan 1.
+
+> Verification: Task complete. No further action needed.
+```
+
+**Example — Failed action:**
+
+```
+Action: put pen 3 in/on garbagecan 1
+Observation: Nothing happened.
+
+> Verification: Last action was ineffective. Re-assess and try a different approach.
+```
+
+## Error Handling
+- **Ambiguous observation**: If the observation does not clearly confirm or deny placement, navigate to the target receptacle and re-examine it to get an updated state.
+- **Quantity tracking**: For multi-object tasks, maintain a running count. Re-examine the target receptacle if the count is uncertain.
diff --git a/experiments/src/skills/alfworld/alfworld-temperature-regulator/SKILL.md b/experiments/src/skills/alfworld/alfworld-temperature-regulator/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: alfworld-temperature-regulator
-description: This skill manages the temperature state of an object by placing it into an appropriate environment (e.g., fridge for cooling, microwave for heating). It should be triggered when the task requires modifying an object's temperature property, such as cooling bread or heating food. The skill requires the object identifier and the target temperature-modifying receptacle as inputs and confirms the object's placement for the intended thermal effect.
+description: Manages the temperature state of an object by placing it into an appropriate appliance (fridge for cooling, microwave for heating). Use when the task requires modifying an object's temperature property, such as "cool some bread" or "heat some food". Takes the object identifier, temperature-modifying receptacle, and final target receptacle as inputs, and outputs the object at the target location with its temperature state changed.
 ---
 # Instructions
 This skill executes a sequence to change an object's temperature by placing it in a specific receptacle (e.g., fridge for cooling, microwave for heating) and then relocating it to a final target location.
@@ -25,5 +25,21 @@ Follow this core logic. Use deterministic scripts for error-prone steps (see `sc
 *   Always verify the state change after each action (e.g., "You pick up...", "You open...", "You put...").
 *   If the object is not at the expected location, pause execution and re-scan the environment.
 
-## 4. Completion
+## 4. Example
+
+**Task:** "Cool some bread and put it on the diningtable."
+
+**Input:** `object: bread 1`, `temperature_receptacle: fridge 1`, `target_receptacle: diningtable 1`
+
+**Sequence:**
+1. `go to countertop 1` → Observation: "You are at countertop 1. You see bread 1, ..."
+2. `take bread 1 from countertop 1` → Observation: "You pick up the bread 1 from the countertop 1."
+3. `go to fridge 1` → Observation: "You are at fridge 1."
+4. `cool bread 1 with fridge 1` → Observation: "You cool the bread 1 using the fridge 1."
+5. `go to diningtable 1` → Observation: "You are at diningtable 1."
+6. `put bread 1 in/on diningtable 1` → Observation: "You put the bread 1 in/on the diningtable 1."
+
+**Output:** The bread 1 is cooled and placed on the diningtable 1. Task complete.
+
+## 5. Completion
 The skill is complete when the object has been placed into the `temperature_receptacle` and subsequently placed onto the `target_receptacle`. Confirm the final observation states the object is on the target.
diff --git a/experiments/src/skills/alfworld/alfworld-tool-locator/SKILL.md b/experiments/src/skills/alfworld/alfworld-tool-locator/SKILL.md
@@ -1,37 +1,43 @@
 ---
 name: alfworld-tool-locator
-description: This skill searches for a specified tool or device (e.g., a desklamp) within the environment by checking relevant surfaces. It should be triggered when the agent needs a tool to interact with another object as part of the task. The skill takes a tool name as implicit input and outputs navigation actions to likely storage spots (e.g., sidetables, shelves) until the tool is found.
+description: Searches for a specified tool or device (e.g., a desklamp, knife, or sponge) within the ALFWorld environment by checking relevant surfaces. Use when you need a tool to interact with another object as part of a task but the tool is not in your inventory or immediate vicinity. Takes a tool name as implicit input and navigates to likely storage spots (sidetables, shelves, countertops) until the tool is found.
 ---
-# Skill: Tool Locator
-
-## Purpose
-Search for a specified tool or device in an ALFWorld household environment by systematically checking relevant receptacles.
-
-## When to Use
-Trigger this skill when:
-1. You have identified a need for a specific tool (e.g., "desklamp", "knife", "sponge") to complete a task.
-2. The tool is not currently in your inventory or immediate vicinity.
-3. You need to locate the tool before proceeding with the main task.
-
-## Input (Implicit)
-- **Tool Name**: The name of the tool/device to locate (e.g., "desklamp", "book", "remotecontrol").
-
-## Core Logic
-1. **Identify Search Targets**: Based on the tool type, prioritize likely storage locations:
-   - For small tools/electronics: `sidetable`, `drawer`, `shelf`
-   - For kitchen tools: `countertop`, `cabinet`, `fridge`
-   - For cleaning tools: `shelf`, `cabinet`, `garbagecan`
-   - Default: Check all visible receptacles in order
-
-2. **Systematic Search Pattern**:
-   - Navigate to each prioritized receptacle
-   - Observe what's on/in the receptacle
-   - If tool is found, stop searching and proceed to use it
-   - If not found, continue to next receptacle
-
-3. **Error Handling**:
-   - If "Nothing happened" is observed, try alternative actions
-   - If tool not found after checking all likely spots, expand search to all receptacles
-
-## Output Format
-Follow the ALFWorld action format:
+# Instructions
+
+Locate a specified tool or device by systematically checking receptacles where it is likely stored.
+
+## Workflow
+1. **Prioritize search locations** based on tool type:
+   - Small tools/electronics (desklamp, remotecontrol): `sidetable`, `desk`, `drawer`, `shelf`
+   - Kitchen tools (knife, spatula): `countertop`, `cabinet`, `drawer`
+   - Cleaning tools (sponge, spraybottle): `shelf`, `cabinet`, `countertop`
+   - Default: check all visible receptacles in order
+2. **Navigate** to each prioritized receptacle: `go to {receptacle}`
+3. **Inspect** the observation for the target tool name
+4. **If found:** Stop searching. Proceed to use the tool for the main task
+5. **If not found:** Continue to the next receptacle in the priority list
+6. **If exhausted:** Expand search to remaining receptacles not yet checked
+
+## Action Format
+- `go to {receptacle}` -- navigate to check a location
+- `take {tool} from {receptacle}` -- pick up the tool once found (if needed)
+- `use {tool}` / `toggle {tool}` -- operate the tool in place (e.g., desklamp)
+
+## Error Recovery
+- If "Nothing happened": verify the receptacle name matches the environment scan
+- If tool not found after all likely spots: expand search to every receptacle from the initial environment scan
+
+## Example
+
+**Scenario:** You need to find a desklamp to examine an object.
+
+```
+Thought: I need to find a desklamp. Desklamps are usually on sidetables or desks.
+Action: go to sidetable 1
+Observation: On the sidetable 1, you see a keychain 1.
+Thought: No desklamp here. Let me check the next sidetable.
+Action: go to sidetable 2
+Observation: On the sidetable 2, you see a desklamp 1.
+```
+
+**Result:** Found `desklamp 1` on `sidetable 2`. Proceed to use it for the task.
diff --git a/experiments/src/skills/alfworld/alfworld-tool-user/SKILL.md b/experiments/src/skills/alfworld/alfworld-tool-user/SKILL.md
@@ -1,12 +1,61 @@
 ---
 name: alfworld-tool-user
-description: This skill uses a tool on a target object to accomplish a specific interaction, such as examining, cleaning, or manipulating. It should be triggered when both the object and the required tool are in the agent's possession or within reach. The skill takes the tool and object as implicit inputs and executes the appropriate interaction action (e.g., 'use', 'clean', 'heat') to progress the task.
+description: Use when the agent needs to apply a tool to a target object in ALFWorld to accomplish an interaction such as cleaning, heating, cooling, or examining. This skill handles locating both the tool and target object, then executing the correct environment action (e.g., `clean`, `heat`, `cool`, `use`) to progress the task.
 ---
-# Instructions
-1.  **Objective:** Use a specified tool on a target object to complete a task (e.g., examine, clean, heat).
-2.  **Prerequisites:** The agent must have the target object in its inventory or be at its location. The required tool must be accessible (in inventory or on a nearby receptacle).
-3.  **Procedure:**
-    a.  **Locate Target:** Navigate to and acquire the target object if not already held.
-    b.  **Locate Tool:** Navigate to and identify the required tool.
-    c.  **Execute Interaction:** Perform the environment-specific action to apply the tool to the object (e.g., `use {tool}`, `clean {obj} with {tool}`). The exact action verb is determined by the task context.
-4.  **Error Handling:** If an action fails (e.g., "Nothing happened"), reassess the object/tool state and location before retrying or attempting an alternative approach.
+# Skill: Tool User for ALFWorld
+
+## When to Use
+Trigger this skill when:
+1. A task requires applying a tool to an object (e.g., cleaning a knife with a sinkbasin, heating food with a microwave)
+2. Both the tool and target object are in the agent's possession or within reach
+3. The agent knows which interaction verb to use for the task context
+
+## Core Workflow
+
+### 1. Identify Requirements
+- Parse the task to determine:
+  - **Target object**: The item to be acted upon (e.g., `knife 1`, `potato 2`)
+  - **Required tool**: The appliance or instrument needed (e.g., `sinkbasin 1`, `microwave 1`)
+  - **Interaction type**: The action verb (`clean`, `heat`, `cool`, `use`, `examine`)
+
+### 2. Locate and Acquire
+- **Target object**: If not in inventory, navigate to its location and `take {object} from {receptacle}`
+- **Tool**: Navigate to the tool's location (tools are typically stationary appliances)
+
+### 3. Execute Interaction
+Apply the tool to the object using the correct action syntax:
+
+| Interaction | Action Command | Example |
+|-------------|---------------|---------|
+| Clean | `clean {obj} with {tool}` | `clean knife 1 with sinkbasin 1` |
+| Heat | `heat {obj} with {tool}` | `heat potato 2 with microwave 1` |
+| Cool | `cool {obj} with {tool}` | `cool apple 1 with fridge 1` |
+| Examine | `examine {obj}` | `examine book 3` |
+| Use | `use {tool}` | `use desklamp 1` |
+
+### 4. Verify Outcome
+- Check the environment observation after the action
+- A successful interaction changes the object state (e.g., `knife 1` becomes clean)
+- If the observation says "Nothing happened," the action was invalid
+
+## Error Handling
+- **"Nothing happened"**: Reassess whether the agent is at the correct location and holding the correct object. Verify the action verb matches the task context.
+- **Wrong tool**: If the tool does not match the interaction type, search for the correct appliance (e.g., use `sinkbasin` for cleaning, not `bathtub`).
+- **Object not held**: The agent must be holding the target object before most interactions. Use `take` first.
+
+## Example
+
+**Task:** "Clean the knife and put it in the drawer."
+
+```
+> go to countertop 1
+On the countertop 1, you see a knife 1, a saltshaker 2.
+> take knife 1 from countertop 1
+You pick up the knife 1 from the countertop 1.
+> go to sinkbasin 1
+On the sinkbasin 1, you see nothing.
+> clean knife 1 with sinkbasin 1
+You clean the knife 1 using the sinkbasin 1.
+```
+
+**Result:** `knife 1` is now clean and ready for the next step (storing).
diff --git a/experiments/src/skills/scienceworld/scienceworld-ambiguous-action-resolution/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-ambiguous-action-resolution/SKILL.md
@@ -1,28 +1,67 @@
 ---
 name: scienceworld-ambiguous-action-resolution
-description: Resolves system ambiguity prompts by selecting the appropriate action from numbered options. Trigger this skill when the environment presents multiple identical action possibilities and requires explicit selection. This ensures task progression when the system cannot automatically disambiguate identical object instances.
+description: Use when the ScienceWorld environment returns an "Ambiguous request" prompt with a numbered list of identical action options. This skill resolves the disambiguation by selecting the lowest available number (typically 0) to proceed, ensuring task progression when multiple identical object instances exist and the system cannot automatically determine which instance to act upon.
 ---
-# Skill: Ambiguous Action Resolution
+# Skill: scienceworld-ambiguous-action-resolution
+
+## Purpose
+
+Resolve system disambiguation prompts that block task progression when the ScienceWorld environment cannot determine which identical object instance the agent intends to act upon. This is a mechanical bypass, not a decision-making step.
 
 ## When to Use
-Activate this skill **only** when the environment returns an "Ambiguous request" observation with a numbered list of identical action options. This typically occurs when multiple identical object instances exist (e.g., five identical banana seeds in a jar) and the system cannot determine which specific instance you intend to act upon.
 
-## Core Procedure
-1.  **Identify the Ambiguity:** Recognize the prompt format: `"Ambiguous request: Please enter the number for the action you intended (or blank to cancel):"` followed by a numbered list (0, 1, 2...).
-2.  **Parse the Options:** Quickly scan the listed options. They will be functionally identical but refer to different instances of the same object.
-3.  **Select a Number:** Choose the **lowest available number** (typically `0`) to proceed. The specific instance is irrelevant for task completion; any valid selection will satisfy the system's requirement and allow the action to execute.
-4.  **Execute:** Output the selected number as the next action (e.g., `Action: 0`).
+- When the environment returns an observation containing `"Ambiguous request: Please enter the number for the action you intended (or blank to cancel):"` followed by a numbered list
+- When multiple identical object instances exist (e.g., five identical banana seeds in a jar) and the system requires explicit selection
+- Only when options are functionally identical -- do NOT use this skill for menu selections where options have different meanings
+
+## Workflow
+
+1. **Recognize the prompt** -- Identify the exact phrase: `"Ambiguous request: Please enter the number for the action you intended (or blank to cancel):"`.
+2. **Scan the options** -- Confirm that the listed options (0, 1, 2...) are functionally identical, referring to different instances of the same object.
+3. **Select the lowest number** -- Choose `0` (the first option) to proceed. Any valid selection will produce the same result.
+4. **Execute** -- Output the selected number as the next action.
+
+## Examples
+
+### Example 1: Moving one of several identical banana seeds
+
+**Observation:**
+```
+Ambiguous request: Please enter the number for the action you intended (or blank to cancel):
+0: move banana seed (in seed jar, in inventory, in agent, in greenhouse) to flower pot 1 (in greenhouse)
+1: move banana seed (in seed jar, in inventory, in agent, in greenhouse) to flower pot 1 (in greenhouse)
+2: move banana seed (in seed jar, in inventory, in agent, in greenhouse) to flower pot 1 (in greenhouse)
+```
+
+**Action:**
+```
+> 0
+```
+
+The system proceeds with moving one banana seed to flower pot 1.
+
+### Example 2: Picking up one of several identical items
+
+**Observation:**
+```
+Ambiguous request: Please enter the number for the action you intended (or blank to cancel):
+0: pick up red wire (on table, in workshop)
+1: pick up red wire (on table, in workshop)
+```
+
+**Action:**
+```
+> 0
+```
 
 ## Key Principles
-*   **Efficiency:** Do not overthink. The objects are identical; any choice is valid.
-*   **Consistency:** Always default to the first option (`0`) unless a previous step in the task logic specifically requires targeting a different instance (which is rare).
-*   **Focus:** This skill is a **disambiguation mechanic**, not a decision-making process. Its sole purpose is to bypass a system prompt blocking progress.
-
-## Example from Trajectory
-**Observation:** "Ambiguous request: Please enter the number for the action you intended (or blank to cancel): 0: move banana seed (in seed jar, in inventory, in agent, in greenhouse) to flower pot 1 (in greenhouse) 1: move banana seed (in seed jar, in inventory, in agent, in greenhouse) to flower pot 1 (in greenhouse) ..."
-**Correct Skill Application:** `Action: 0`
-
-## Anti-Patterns to Avoid
-*   Do NOT use this skill for non-ambiguous choices or menu selections where options have different meanings.
-*   Do NOT trigger this skill if the observation does not contain the exact "Ambiguous request" phrase.
-*   Do NOT waste steps analyzing the differences between identical instances.
+
+- **Efficiency** -- Do not overthink; the objects are identical and any choice is valid.
+- **Consistency** -- Always default to `0` unless task logic specifically requires a different instance.
+- **Scope** -- This skill is strictly a disambiguation mechanic, not a decision-making process.
+
+## Anti-Patterns
+
+- Do NOT use for non-ambiguous choices where options have different meanings.
+- Do NOT trigger if the observation does not contain the exact "Ambiguous request" phrase.
+- Do NOT waste steps analyzing differences between identical instances.
diff --git a/experiments/src/skills/scienceworld/scienceworld-animal-identifier/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-animal-identifier/SKILL.md
@@ -1,23 +1,66 @@
 ---
 name: scienceworld-animal-identifier
-description: This skill identifies and focuses on specific animals or biological entities present in the environment. It should be triggered when the task requires examining, comparing, or interacting with animals, such as determining lifespan attributes. The skill takes an animal identifier as input and outputs a confirmation of focus, aiding in targeted analysis for scientific experiments or comparisons.
+description: Use when the agent needs to locate, identify, and focus on a specific animal or biological entity in the ScienceWorld environment. This skill handles tasks involving animal comparison, examination, or interaction (such as determining lifespan extremes) by navigating to the correct location with "teleport to", surveying with "look around", and executing "focus on ANIMAL" with the exact entity name.
 ---
-# Instructions
+# Skill: scienceworld-animal-identifier
 
 ## Purpose
-This skill enables the agent to locate and focus on a specified animal or biological entity within the ScienceWorld environment. It is designed for tasks involving animal comparison, examination, or interaction, such as determining lifespan extremes.
 
-## Core Workflow
-1.  **Locate Target Environment:** If the target animal is known to be in a specific location (e.g., 'outside'), teleport there first.
-2.  **Survey the Area:** Use `look around` to list all visible objects and entities in the current location.
-3.  **Identify Target:** Parse the observation to find the specified animal identifier (e.g., 'parrot egg', 'baby dragonfly').
-4.  **Execute Focus:** Use the `focus on <ANIMAL>` action to signal intent on the identified target object.
+Locate and focus on a specified animal or biological entity within the ScienceWorld environment for tasks involving animal comparison, examination, or interaction (e.g., determining lifespan extremes, identifying species).
+
+## When to Use
+
+- When a task requires finding and focusing on a specific animal or biological entity
+- When comparing attributes (lifespan, size, type) across multiple animals
+- When the task instructs examining or interacting with an animal in a specific location
+
+## Workflow
+
+1. **Navigate to the target location** -- If the animal is in a specific room (e.g., "outside", "greenhouse"), execute `teleport to <LOCATION>`.
+2. **Survey the area** -- Use `look around` to list all visible objects and entities.
+3. **Identify the target** -- Parse the observation to find the exact animal name as displayed (e.g., `baby dragonfly`, `parrot egg`, `adult blue jay`).
+4. **Execute focus** -- Run `focus on <ANIMAL>` using the exact name from the observation.
+5. **Confirm success** -- Wait for the system response: `"You focus on the <ANIMAL>."`.
+
+## Examples
+
+### Example 1: Find the animal with the longest lifespan
+
+**Task:** "Find the animal with the longest life span and focus on it."
+
+```
+> teleport to outside
+You teleport to outside.
+
+> look around
+You see: baby dragonfly, adult blue jay, parrot egg, oak tree, grass.
+
+> focus on adult blue jay
+You focus on the adult blue jay.
+```
+
+(Blue jays have a longer lifespan than dragonflies among the visible animals.)
+
+### Example 2: Sequential identification of two animals
+
+**Task:** "First focus on the longest-lived animal, then the shortest-lived."
+
+```
+> teleport to outside
+You teleport to outside.
+
+> look around
+You see: baby dragonfly, adult blue jay, parrot egg.
+
+> focus on adult blue jay
+You focus on the adult blue jay.
+
+> focus on baby dragonfly
+You focus on the baby dragonfly.
+```
 
 ## Key Principles
-*   **Context-Aware Navigation:** Always verify your current location. If you are not in the correct room for the target animal, use `teleport to <LOCATION>` as the first step.
-*   **Precise Targeting:** The `focus on` action requires the exact object name as it appears in the `look around` observation (e.g., "baby dragonfly", not just "dragonfly").
-*   **Sequential Execution:** This skill is often used in a sequence (e.g., find longest-lived, then shortest-lived animal). Complete the focus action for one target before proceeding to the next.
 
-## Input/Output
-*   **Input:** An animal identifier or a task description implying the need to identify/focus on an animal (e.g., "find the animal with the longest life span").
-*   **Output:** A confirmation that the `focus on <ANIMAL>` action has been successfully executed on the correct target.
+- **Exact names** -- The `focus on` action requires the precise object name as it appears in `look around` (e.g., `"baby dragonfly"`, not just `"dragonfly"`).
+- **Navigate first** -- Always verify your location and `teleport to` the correct room before surveying.
+- **Sequential execution** -- When focusing on multiple animals in sequence, complete each `focus on` action before proceeding to the next.
diff --git a/experiments/src/skills/scienceworld/scienceworld-circuit-builder/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-circuit-builder/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-circuit-builder
-description: This skill constructs a simple electrical circuit by connecting components like batteries, wires, and light bulbs. It should be triggered when the agent needs to test electrical conductivity or create a functional circuit for an experiment. The input is a set of available components, and the output is a fully connected circuit ready for activation.
+description: This skill constructs a simple electrical circuit by connecting components like batteries, wires, and light bulbs. Use when the agent needs to test electrical conductivity or create a functional circuit for an experiment. The input is a set of available components, and the output is a fully connected circuit ready for activation.
 ---
 # Instructions
 
@@ -42,3 +42,16 @@ Follow these steps to construct the series circuit. Use the exact `connect` acti
 *   **Circuit Logic:** This builds a simple series circuit: Battery -> Wire1 -> Light Bulb -> Wire3 -> Target Object -> Wire2 -> Battery.
 *   **Action Precision:** Use the exact object names and connection points (anode, cathode, terminal 1/2) as observed in the environment.
 *   **Error Handling:** If a component is missing, examine the room (`look around`) to identify available substitutes before proceeding.
+
+## 6. Example
+**Task:** Test whether a metal pot is electrically conductive.
+1. `teleport to workshop`
+2. `pick up metal pot`
+3. `connect battery anode to orange wire terminal 1`
+4. `connect battery cathode to yellow wire terminal 1`
+5. `connect orange wire terminal 2 to blue light bulb cathode`
+6. `connect green wire terminal 2 to anode in blue light bulb`
+7. `connect metal pot terminal 1 to yellow wire terminal 2`
+8. `connect metal pot terminal 2 to green wire terminal 1`
+9. `wait1` — observe if the light bulb turns on
+10. Light bulb is on → `move metal pot to blue box` (conductive)
diff --git a/experiments/src/skills/scienceworld/scienceworld-circuit-connector/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-circuit-connector/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-circuit-connector
-description: This skill connects two electrical components (e.g., wires, batteries, devices) by their terminals to build or modify a circuit. It should be triggered when constructing electrical setups for testing, such as conductivity checks or device activation. The input includes two component identifiers and their connection points, and the output is an established electrical connection.
+description: This skill connects two electrical components (e.g., wires, batteries, devices) by their terminals to build or modify a circuit. Use when constructing electrical setups for testing, such as conductivity checks or device activation. The input includes two component identifiers and their connection points, and the output is an established electrical connection.
 ---
 # Instructions
 
diff --git a/experiments/src/skills/scienceworld/scienceworld-conditional-focus-executor/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-conditional-focus-executor/SKILL.md
@@ -1,19 +1,23 @@
 ---
 name: scienceworld-conditional-focus-executor
-description: Executes a 'focus' action on a specific object based on the outcome of a prior conditional evaluation. It should be triggered when task instructions specify focusing on different objects (e.g., different colored boxes) depending on a measurement result. The skill takes the conditional outcome as input and performs the corresponding focus action.
+description: Executes a 'focus on OBJ' action on a specific object based on the outcome of a prior conditional evaluation. Use when you have a measurement result and task instructions specify focusing on different objects (e.g., colored boxes) depending on whether the result meets a threshold.
 ---
 # Conditional Focus Executor
 
-## Purpose
-This skill automates the final step in a conditional measurement task within the ScienceWorld environment. After obtaining a measurement result (e.g., a temperature reading), you must focus on a specific object (e.g., a colored box) based on whether the result meets a defined threshold.
-
 ## When to Use
-Use this skill **only** when:
-1. You have completed a measurement (e.g., temperature, pH, mass).
-2. The task instructions explicitly state a conditional rule (e.g., "If result > X, focus on A; if result < X, focus on B").
-3. You have already determined the conditional outcome (True/False or the specific branch).
+Use after completing a measurement (temperature, pH, mass) when the task specifies a conditional rule like "If result > X, focus on A; otherwise, focus on B."
+
+## Procedure
+1. **Evaluate the condition** against your measurement result.
+2. **Determine the target object** based on which branch is true.
+3. **Execute:** `focus on <TARGET_OBJECT>`
+4. **Verify:** Confirm the focus action succeeded before proceeding.
 
-## Input Required
-Before executing, you **must** have determined the correct conditional branch. The skill requires this as a clear decision.
+If the focus action fails (e.g., object not found), use `look around` to verify the target object name matches exactly.
 
-**Required Input Format:**
+## Example
+**Task:** "If the temperature of the substance is above 50C, focus on the red box. Otherwise, focus on the blue box."
+1. Measurement result: 63C
+2. Evaluation: 63 > 50 is true → target is red box
+3. Execute: `focus on red box`
+4. Observation: "You focus on the red box." → task complete.
diff --git a/experiments/src/skills/scienceworld/scienceworld-conditional-placer/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-conditional-placer/SKILL.md
@@ -1,28 +1,39 @@
 ---
 name: scienceworld-conditional-placer
-description: Places an object into one of several designated containers based on a measured condition, such as a temperature threshold. It is triggered after a measurement or assessment when the task requires sorting or storing the object according to a rule.
+description: Places an object into one of several designated containers based on a measured condition, such as a temperature threshold. Use this skill when you have completed a measurement or assessment and the task requires sorting or storing the object into one of multiple containers according to a rule (e.g., "if temperature > X, place in container A; otherwise container B").
 ---
 # Skill: Conditional Object Placer
 
 ## Purpose
-This skill enables an agent to place a target object into a specific container based on a measured condition (e.g., temperature). It is used after a measurement step to complete a conditional sorting or storage objective.
+Place a target object into the correct container based on a measured condition (e.g., temperature threshold, conductivity result). This skill executes the full measure-then-sort workflow.
 
 ## Core Workflow
-1.  **Locate & Acquire Measurement Tool:** Find and pick up the required measurement device (e.g., thermometer).
-2.  **Locate & Acquire Target Object:** Find and pick up the object to be measured and placed (e.g., metal fork).
-3.  **Identify Target Containers:** Find the designated containers (e.g., blue box, orange box).
-4.  **Perform Measurement:** Use the measurement tool on the target object to obtain the relevant value.
-5.  **Evaluate Condition & Execute Placement:** Apply the given rule to the measured value to select the correct container, then move the object into it.
+1. **Locate & Acquire Measurement Tool:** `teleport to LOC` then `pick up` the measurement device (e.g., thermometer).
+2. **Locate & Acquire Target Object:** `teleport to LOC` then `pick up` the object to be measured (e.g., metal fork).
+3. **Identify Target Containers:** Use `look around` to find the designated containers (e.g., blue box, orange box).
+4. **Perform Measurement:** `use OBJ on OBJ` (e.g., `use thermometer on metal fork`) to obtain the value.
+5. **Evaluate Condition & Place:** Compare the measured value against the threshold, then `move OBJ to OBJ` to place the object in the correct container.
 
-## Key Actions & Logic
-*   Use `teleport to LOC` to navigate efficiently between rooms.
-*   Use `look around` to survey a room and locate objects.
-*   Use `pick up OBJ` to acquire tools and the target object.
-*   Use `use OBJ [on OBJ]` to perform the measurement (e.g., `use thermometer on metal fork`).
-*   Use `move OBJ to OBJ` to place the target object into the selected container.
-*   The decision logic is simple: compare the measured value against the provided threshold and select the corresponding container.
+## Key Actions
+| Action | Purpose |
+|--------|---------|
+| `teleport to LOC` | Navigate between rooms |
+| `look around` | Survey a room for objects |
+| `pick up OBJ` | Acquire tools or target object |
+| `use OBJ on OBJ` | Perform measurement |
+| `move OBJ to OBJ` | Place object into selected container |
+
+## Example
+**Task:** "Measure the temperature of the metal fork. If above 50C, place in the orange box. Otherwise, place in the blue box."
+
+1. `teleport to kitchen`
+2. `look around` — find thermometer and metal fork
+3. `pick up thermometer`
+4. `pick up metal fork`
+5. `use thermometer on metal fork` — reads 72 degrees
+6. 72 > 50, so: `move metal fork to orange box`
 
 ## Important Notes
-*   All containers are pre-opened. Do not use `open` or `close` actions.
-*   The skill assumes the measurement tool and target object can be picked up and are used from the inventory.
-*   The specific rooms, object names, threshold value, and container names will vary per task. Adapt the skill steps accordingly.
+* All containers are pre-opened. Do not use `open` or `close` actions.
+* The measurement tool and target object must be picked up and used from inventory.
+* Room names, object names, thresholds, and container names vary per task — adapt accordingly.
diff --git a/experiments/src/skills/scienceworld/scienceworld-container-inspector/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-container-inspector/SKILL.md
@@ -1,12 +1,9 @@
 ---
 name: scienceworld-container-inspector
-description: This skill performs a 'look at' action to inspect the contents of a specific container or device. It should be triggered when the agent needs to verify what is inside a container (e.g., checking if lead is in the blast furnace) or monitor the state of contents (e.g., solid vs. liquid). The skill outputs a detailed list of contents and their states, providing essential feedback for process monitoring.
+description: Inspects the contents of a container or device using the 'look at' action. Use this skill when you need to verify what is inside a container (e.g., checking if lead is in the blast furnace), monitor the state of contents (e.g., solid vs. liquid phase changes), or confirm that a placement or process step succeeded. Returns a detailed list of contents and their states for process monitoring.
 ---
 # Skill: Container/Device Inspector
 
-## Purpose
-Execute a `look at` action on a specified container or device to retrieve a detailed observation of its contents and their states. This is a critical monitoring skill for verifying process steps, such as confirming an item is present inside a furnace or checking the phase (solid/liquid) of a substance.
-
 ## When to Use
 Trigger this skill when you need to:
 1.  **Verify Placement:** Confirm an object has been successfully moved into a target container (e.g., "Is the metal pot in the blast furnace?").
@@ -48,5 +45,3 @@ This skill is often used in a sequence:
 -   If the container door is closed, you must `open` it before using this skill.
 -   The skill only inspects; it does not manipulate contents. Use `pick up`, `move`, or `use` for manipulation.
 
----
-*For detailed examples of container interactions and state transitions, see the reference documentation.*
diff --git a/experiments/src/skills/scienceworld/scienceworld-container-item-retriever/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-container-item-retriever/SKILL.md
@@ -27,4 +27,8 @@ Execute the `pick up <ITEM>` action, where `<ITEM>` is the exact name of the tar
 *   **Ambiguity:** If multiple identical items exist (e.g., "avocado seed, avocado seed, avocado seed"), the `pick up` action will typically retrieve one. The skill does not handle selecting a specific instance.
 *   **Post-condition:** After successful execution, the item is in the agent's inventory and can be used in subsequent steps.
 
-For detailed examples and edge cases, see the reference documentation.
+## Example
+**Task:** Retrieve an avocado seed from a jar for planting.
+1. `look around` — observe: "a jar (containing an avocado seed)"
+2. `pick up avocado seed`
+3. Expected observation: "You move the avocado seed to the inventory."
diff --git a/experiments/src/skills/scienceworld/scienceworld-container-relocator/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-container-relocator/SKILL.md
@@ -1,23 +1,14 @@
 ---
 name: scienceworld-container-relocator
-description: Moves an object from inventory to a specified container in a target room. Triggered when the task requires placing an item into a particular receptacle (e.g., 'move it to the orange box').
+description: Moves an object from inventory to a specified container in a target room. Use when the task requires placing an item into a particular receptacle (e.g., 'move it to the orange box').
 ---
 # Skill: Container Relocator
 
-## Purpose
-This skill handles the final delivery step in scienceWorld experiments where you must place a specific object into a designated container located in a target room.
-
-## Core Logic
-1.  **Identify the Target:** The task will specify a destination container (e.g., "the orange box") and a room (e.g., "in the workshop").
-2.  **Confirm Inventory:** Ensure the required object is already in your inventory. If not, you must first acquire it.
-3.  **Navigate:** Teleport to the target room if you are not already there.
-4.  **Execute Delivery:** Use the `move OBJ to OBJ` action to transfer the object from your inventory to the target container.
-
-## Key Instructions
-*   Use this skill **only** when the task explicitly states a "move it to [CONTAINER] in [ROOM]" objective.
-*   The object to be moved must be in your inventory. Use `focus on OBJ` to confirm the correct target if needed.
-*   Always verify your location before attempting the move action. Use `teleport to LOC` to reach the correct room.
-*   The primary action is `move [OBJECT] to [CONTAINER]`. Ensure the object name matches your inventory and the container name matches the room's description.
+## Procedure
+1. Confirm the object is in your inventory. If not, acquire it first.
+2. `teleport to <ROOM>` — navigate to the room containing the target container.
+3. `move <OBJECT> to <CONTAINER>` — transfer the object to the destination.
+4. `look at <CONTAINER>` — verify the object is now inside.
 
 ## Example Flow (from trajectory)
 1.  Task: "move it to the orange box in the workshop."
diff --git a/experiments/src/skills/scienceworld/scienceworld-container-transfer/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-container-transfer/SKILL.md
@@ -1,33 +1,33 @@
 ---
 name: scienceworld-container-transfer
-description: Moves a substance or object from one container to another (e.g., moving lead to a metal pot). Triggered when the agent needs to prepare materials for processing, such as transferring a substance into a heat-resistant container for heating experiments.
+description: Moves a substance or object from one container to another (e.g., moving lead to a metal pot). Use this skill when you need to prepare materials for processing, such as transferring a substance into a heat-resistant container before heating, or reorganizing materials between vessels for mixing or measurement.
 ---
 # Skill: Container Transfer
 
 ## Purpose
-This skill orchestrates the transfer of a target substance or object from a source container to a destination container. It is a foundational step for preparing materials for subsequent operations like heating, mixing, or measurement.
+Transfer a target substance or object from a source container to a destination container. This is a foundational step for preparing materials for heating, mixing, or measurement.
 
-## Core Logic
-The skill is executed when the agent's goal requires moving a material to a more suitable container. The primary sequence, derived from the trajectory, is:
-1.  **Identify & Locate:** Confirm the presence of the target substance and the destination container in the current environment.
-2.  **Execute Transfer:** Use the `move OBJ to OBJ` action, where the first object is the target substance and the second is the destination container.
-3.  **Verify:** Confirm the transfer was successful by examining the destination container's contents.
+## Core Workflow
+1. **Assess Need:** Determine if the current container is unsuitable for the next operation (e.g., tin cup is not heat-resistant for a furnace).
+2. **Locate Items:** Use `look around` and `look at OBJ` to find the target substance and a suitable destination container.
+3. **Execute Transfer:** `move <SUBSTANCE> to <DESTINATION>`.
+4. **Verify:** `look at <DESTINATION>` to confirm the substance is now inside.
 
-## Instructions
-Follow this decision flow to perform a container transfer:
+## Key Actions
+| Action | Purpose |
+|--------|---------|
+| `look around` | Survey room for containers and substances |
+| `look at OBJ` | Inspect container contents |
+| `move OBJ to OBJ` | Transfer substance to destination |
 
-1.  **Assess the need for transfer.** Is the target substance in a container unsuitable for the next planned operation (e.g., a tin cup is not heat-resistant for a furnace)?
-2.  **Locate the target substance and a suitable destination container** (e.g., `lead` in a `tin cup` and an empty `metal pot`). Use `look around` and `look at OBJ` actions.
-3.  **Execute the transfer command:** `move <SUBSTANCE_NAME> to <DESTINATION_CONTAINER>`.
-    *   Example: `move lead to metal pot`
-4.  **Verify the transfer** by looking at the destination container: `look at <DESTINATION_CONTAINER>`.
-    *   Expected observation: The container now lists the target substance in its contents.
+## Example
+**Task:** Transfer lead from a tin cup to a heat-resistant metal pot for furnace heating.
 
-## Key Parameters
-*   `<SUBSTANCE_NAME>`: The name of the substance or object to be moved (e.g., `lead`).
-*   `<DESTINATION_CONTAINER>`: The name of the container to receive the substance (e.g., `metal pot`).
+1. `look around` — spot `tin cup (containing lead)` and `metal pot`
+2. `move lead to metal pot`
+3. `look at metal pot` — confirms: "a metal pot (containing a substance called lead)"
 
-## Notes
-*   This skill assumes containers are already open, as per the environment rules.
-*   The skill is context-aware; the destination container should be chosen based on the properties needed for the next step (e.g., heat resistance for a furnace).
-*   If the transfer fails (e.g., "You can't do that"), check the object names and ensure the destination container is accessible and capable of holding the substance.
+## Important Notes
+* All containers are pre-opened. Do not use `open` or `close` actions.
+* Choose the destination container based on properties needed for the next step (e.g., heat resistance for furnace use).
+* If the transfer fails ("You can't do that"), verify object names with `look around` and ensure the destination is accessible.
diff --git a/experiments/src/skills/scienceworld/scienceworld-controlled-waiting/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-controlled-waiting/SKILL.md
@@ -1,38 +1,26 @@
 ---
 name: controlled-waiting
-description: Executes timed waiting to allow processes like plant growth or pollination to progress. Use this skill when you need to advance time for biological or mechanical processes to reach their next stages. This enables progression in tasks that require temporal development rather than immediate actions.
+description: Executes timed waiting using 'wait' or 'wait1' actions to advance the simulation clock. Use when a time-dependent process like plant growth, chemical reaction, or mechanical cycle must progress before you can continue the task.
 ---
 # Skill: Controlled Waiting
 
-## Purpose
-This skill orchestrates a strategic waiting pattern to allow time-dependent processes (e.g., plant growth, chemical reactions, mechanical cycles) to complete. It is triggered when the agent's primary task is blocked, pending the natural progression of a state.
+## When to Use
+After initiating a process with a time delay, when no other productive actions are possible.
 
-## Core Logic
-The skill follows a **Monitor-Wait-Check** cycle:
-1.  **Assess State:** Confirm the process requiring time is active (e.g., seeds are planted, device is activated).
-2.  **Execute Wait:** Use the `wait` action (for long periods) or `wait1` (for single steps) to advance the simulation.
-3.  **Verify Progress:** After waiting, check the environment (`look around` or `examine`) to see if the target state has been reached.
-4.  **Repeat or Exit:** If the target state is not yet achieved, loop back to step 2. If achieved, exit the skill and resume the main task.
+## Procedure
+1. Confirm the process is active (seeds planted, device activated, etc.).
+2. `wait` (advances 10 steps) for long processes, or `wait1` (1 step) for fine-grained observation.
+3. `look around` or `examine <OBJECT>` to check if the target state has been reached.
+4. If not reached, repeat steps 2-3. If reached, exit and resume the main task.
 
-## Key Parameters & Decisions
-*   **Wait Duration:** Use `wait` (10 steps) for significant biological/mechanical stages. Use `wait1` for fine-grained control or to observe rapid changes.
-*   **Monitoring Frequency:** The interval between checks. Derived from the trajectory: after 2-3 `wait` actions, a `look around` is performed. Adjust based on the estimated time of the process.
-*   **Exit Condition:** Clearly defined by the main task goal (e.g., "banana is present", "device status is 'ready'").
+**Duration guidance:** Use `wait` for biological growth stages. Use `wait1` when observing rapid changes or when close to the expected transition.
 
-## When to Use This Skill
-*   After initiating a process that has a known or unknown delay.
-*   When the environment state is stable and no other preparatory actions are possible.
-*   When prompted by task context (e.g., "give them time to grow", "wait for the reaction to complete").
-
-## When NOT to Use This Skill
-*   When you can perform other productive actions in parallel.
-*   When the process is instantaneous or requires a specific trigger (e.g., pressing a button).
-*   If waiting would cause a negative outcome (e.g., a timer expires, an object decays).
-
-## Integration with Main Task
-This skill is a **subroutine**. The main task should:
-1.  Set up the necessary conditions for the time-based process.
-2.  Invoke this skill.
-3.  Upon skill completion, verify the outcome and proceed with the next task step (e.g., harvest the grown banana).
+## Example
+**Task:** Wait for a banana tree to produce fruit after planting.
+1. Confirm seeds are planted and watered.
+2. `wait` (advances 10 steps)
+3. `look around` — check if banana is visible on the tree.
+4. No banana yet → `wait` again.
+5. `look around` — observe: "a banana tree (with a banana)" → exit skill and proceed to harvest.
 
 Refer to `references/botanical_growth_patterns.md` for common plant growth stage timings.
diff --git a/experiments/src/skills/scienceworld/scienceworld-device-activator/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-device-activator/SKILL.md
@@ -1,37 +1,38 @@
 ---
 name: scienceworld-device-activator
-description: This skill activates a device (e.g., blast furnace, stove) to initiate a process like heating. It should be triggered when the agent has placed materials in a device and needs to start the device's operation. The skill takes a device name as input and outputs a confirmation of activation, which is critical for progressing tasks that require energy or processing.
+description: Activates a device (e.g., blast furnace, stove) to initiate a process like heating. Use this skill when you have placed materials inside a device and need to start its operation. Takes a device name as input and outputs a confirmation of activation, enabling tasks that require energy input or material processing to progress.
 ---
-# Device Activation Skill
+# Skill: Device Activator
 
 ## Purpose
-Activate a specific device to begin its operation (e.g., heating, processing). This is a critical step when materials have been placed into a device and require energy input to proceed with an experiment or task.
-
-## When to Use
-- You have confirmed that the target materials are properly placed inside the device.
-- The device is in a deactivated or "off" state.
-- The next step in your task requires the device to be operating (e.g., heating lead in a blast furnace).
-
-## Core Instruction
-Execute the `activate` action on the target device.
-
-**Action Format:** `activate <DEVICE_NAME>`
-
-**Example:** `activate blast furnace`
-
-## Prerequisites
-1. **Material Placement:** Ensure the target material(s) are inside the device. Use `look at <DEVICE_NAME>` to verify contents.
-2. **Device State:** Confirm the device is deactivated. The observation will typically indicate "which is turned off" or "which is deactivated."
-3. **Safety Check:** Ensure the device door is open if required for loading. Most devices in this environment are pre-opened.
-
-## Post-Activation Steps
-1. **Verification:** After activation, check the device state with `look at <DEVICE_NAME>` or `examine <DEVICE_NAME>` to confirm it's now "turned on" or "activated."
-2. **Monitoring:** Use appropriate measurement tools (e.g., thermometer) on the materials inside the device to track progress.
-3. **Deactivation:** Remember to deactivate the device when the process is complete using `deactivate <DEVICE_NAME>`.
-
-## Common Devices & Context
-- **Blast Furnace:** For high-temperature melting (e.g., metals like lead).
-- **Stove/Oven:** For general heating tasks.
-- **Other Devices:** Any device with an observable on/off state that requires activation to function.
-
-For detailed device specifications and safety guidelines, see the reference documentation.
+Activate a device (turn it on, start it, fire it up) to begin its operation — typically heating, processing, or powering a task step.
+
+## Core Workflow
+1. **Verify Contents:** `look at <DEVICE_NAME>` to confirm materials are placed inside.
+2. **Check State:** Observation should show "which is turned off" or "which is deactivated."
+3. **Activate:** `activate <DEVICE_NAME>`
+4. **Verify Activation:** `look at <DEVICE_NAME>` — confirm it now reads "turned on" or "activated."
+5. **Monitor (if needed):** Use measurement tools (e.g., `use thermometer on <MATERIAL>`) to track progress.
+6. **Deactivate When Done:** `deactivate <DEVICE_NAME>`
+
+## Key Actions
+| Action | Purpose |
+|--------|---------|
+| `look at <DEVICE>` | Verify contents and device state |
+| `activate <DEVICE>` | Turn on / start the device |
+| `deactivate <DEVICE>` | Turn off the device when done |
+| `use TOOL on OBJ` | Monitor material state during processing |
+
+## Example
+**Task:** Melt lead in a blast furnace.
+
+1. `look at blast furnace` — confirms: metal pot with lead inside, furnace is turned off
+2. `activate blast furnace`
+3. `look at blast furnace` — confirms: "which is turned on"
+4. `use thermometer on lead` — monitor temperature
+5. `look at blast furnace` — observe: "a substance called liquid lead" (melting complete)
+6. `deactivate blast furnace`
+
+## Important Notes
+* Most devices are pre-opened. Do not use `open` or `close` unless the observation indicates a closed door.
+* Always verify activation succeeded before proceeding to the next task step.
diff --git a/experiments/src/skills/scienceworld/scienceworld-environment-isolation/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-environment-isolation/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-environment-isolation
-description: Closes doors or openings to create a contained environment for controlled processes. Trigger this when you need to isolate a space (like a greenhouse) to optimize conditions for pollination or other environmental-sensitive tasks. This modifies room connectivity to create optimal conditions for specific processes.
+description: Use when you need to isolate a space (like a greenhouse) by closing doors or openings to create a contained environment. Trigger before starting pollination, temperature-sensitive experiments, or other environmental-sensitive tasks that require controlled conditions. Modifies room connectivity to optimize conditions for specific processes.
 ---
 # Instructions
 
@@ -26,3 +26,15 @@ Trigger this skill when you need to:
 *   This skill modifies the **connectivity** of a space, not its internal state (like temperature controls).
 *   The primary observed benefit in the trajectory was enhancing bee-mediated pollination by preventing bee escape.
 *   Reversal (re-opening doors) is not part of this skill's core function but can be done using standard `open` commands if needed later.
+
+## Example
+
+**Scenario:** You need to cross-pollinate two plants in the greenhouse using bees.
+
+1. You have placed both plants and a bee jar in the `greenhouse`.
+2. Run `look around` — you see: "door to outside (open)", "door to hallway (open)".
+3. Run `close door to outside` — output: "You close the door to outside."
+4. Run `close door to hallway` — output: "You close the door to hallway."
+5. Run `look around` — confirm both doors now show as closed. The greenhouse is fully isolated.
+6. Release the bee by running `open bee jar`. The bee cannot escape and will pollinate both plants.
+7. Run `wait` several times to allow pollination to complete.
diff --git a/experiments/src/skills/scienceworld/scienceworld-growth-focuser/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-growth-focuser/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-growth-focuser
-description: This skill applies a 'focus on' action to a specific plant or biological entity to signal intent and monitor its development. It should be triggered after planting or when the agent needs to track the growth stage of a plant (e.g., to observe sprouting, flowering, or reproduction). The skill outputs a confirmation of focus, which may be necessary for triggering or tracking life cycle progression in the environment.
+description: Use when you have planted a seed or need to track a plant's growth stage (sprouting, flowering, reproduction). Applies the 'focus on' action to a specific plant or biological entity to signal intent and monitor its development. Trigger after planting or when you need to observe life cycle progression in the ScienceWorld environment.
 ---
 # Skill: Growth Focuser
 
@@ -25,6 +25,18 @@ Use this skill when:
 *   **Prerequisites:** The `focus on` action typically follows preparatory steps like `teleport to <location>`, `pick up <item>`, and `move <seed> to <pot>`.
 *   **Patience is Required:** Growth is not instantaneous. The `focus on` action signals intent, but you must follow it with `wait` actions to observe results.
 
+## Example
+
+**Scenario:** You need to grow an avocado plant from seed to maturity.
+
+1. You have already moved `avocado seed` into `flower pot 1` which contains soil and water.
+2. Run `focus on avocado seed in flower pot 1` — output: "You focus on the avocado seed."
+3. Run `wait` — the environment processes one time step.
+4. Run `focus on avocado seed in flower pot 1` again — output may now show: "avocado sprout" indicating growth progression.
+5. Continue alternating `focus on` and `wait` until the plant reaches the desired life stage (sprout, mature plant, flowering, reproduction).
+
+**Note:** Always include the `in <CONTAINER>` clause when multiple pots or seeds exist to avoid disambiguation prompts.
+
 ## Quick Reference
 **Trigger Condition:** Seed/Plant is in a growth-ready state.
 **Primary Action:** `focus on <PLANT_OBJECT> [in <CONTAINER>]`
diff --git a/experiments/src/skills/scienceworld/scienceworld-instruction-reader/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-instruction-reader/SKILL.md
@@ -1,19 +1,32 @@
 ---
 name: scienceworld-instruction-reader
-description: This skill reads a recipe or note from the inventory using the 'read' action. It should be triggered after acquiring a recipe or document to extract explicit instructions, ingredient lists, or procedural steps. The skill parses the text content and outputs the key information needed to execute the task, such as required components and their combinations.
+description: Reads a recipe or note from the inventory using the 'read' action and extracts key information. Use this skill when you have acquired a recipe, note, or readable document in your inventory and need to extract explicit instructions, ingredient lists, or procedural steps before executing a task.
 ---
-# Instructions
-Use this skill when you have acquired a recipe, note, or any readable document in your inventory and need to understand its contents to proceed with a task.
+# Skill: Instruction Reader
 
-## Core Action
-1.  **Read the Document:** Use the `read OBJ` action on the document in your inventory.
-    *   **Example:** `read recipe in inventory`
+## Purpose
+Read and parse a document (recipe, note, or instructions) from your inventory to extract the information needed to execute the current task.
 
-## Skill Logic
-After reading, analyze the text to identify:
-*   **Goal:** The final product or objective (e.g., "make salt water").
-*   **Required Components:** A list of items or substances needed (e.g., "sodium chloride, water").
-*   **Procedural Steps:** Any explicit actions or combinations described (e.g., "mix sodium chloride, water").
+## When to Use
+- After picking up a recipe, note, or readable document.
+- When the task requires following written instructions (e.g., mixing chemicals, assembling components).
+- Before starting a multi-step procedure that depends on written directions.
 
-## Output Format
-Present the extracted information clearly. For example:
+## Core Workflow
+1. **Read the Document:** `read OBJ` on the document in your inventory.
+2. **Extract Key Information:**
+   - **Goal:** The final product or objective (e.g., "make salt water").
+   - **Required Components:** Items or substances needed (e.g., "sodium chloride, water").
+   - **Procedural Steps:** Actions or combinations described (e.g., "mix sodium chloride, water").
+3. **Plan Next Actions:** Use the extracted information to determine which skills and actions to invoke next.
+
+## Example
+**Task:** Follow a recipe to make salt water.
+
+1. `pick up recipe` — acquire the document
+2. `read recipe in inventory` — output: "To make salt water, mix sodium chloride and water in a glass jar."
+3. **Extracted info:**
+   - Goal: salt water
+   - Components: sodium chloride, water
+   - Procedure: mix in glass jar
+4. Proceed to fetch sodium chloride, water, and glass jar, then mix.
diff --git a/experiments/src/skills/scienceworld/scienceworld-inventory-focus/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-inventory-focus/SKILL.md
@@ -1,36 +1,62 @@
 ---
 name: scienceworld-inventory-focus
-description: This skill focuses on a specific item within the agent's inventory to confirm its identity or prepare it for use. It should be triggered before using an inventory item in an experiment or when verifying that the correct item has been collected. The skill helps ensure operational readiness and intentional task progression.
+description: Use when the agent needs to confirm and prepare a specific inventory item before using it in an experiment or task step. This "focus on [ITEM] in inventory" action verifies the correct item has been collected and signals intent, ensuring operational readiness for subsequent actions like measurement, combination, or placement.
 ---
-# Skill: Inventory Focus
+# Skill: scienceworld-inventory-focus
 
 ## Purpose
-Use this skill to intentionally examine and prepare an item from your inventory before using it in a task. This act of "focusing" confirms the item's presence, state, and readiness, reducing errors in multi-step procedures.
-
-## Primary Trigger
-Trigger this skill when you have picked up a required item and need to:
-1.  Verify it is the correct object for the next step.
-2.  Signal your intent to use it.
-3.  Prepare it for a subsequent action (e.g., measurement, combination).
-
-## Core Instruction
-Execute the `focus on [ITEM] in inventory` action. Replace `[ITEM]` with the exact name of the object you have collected.
-
-## Standard Operating Procedure (SOP)
-Follow this sequence when an item from your inventory is needed for a critical task:
-
-1.  **Acquire:** First, ensure the target item is in your inventory (e.g., `pick up thermometer`).
-2.  **Focus:** Execute this skill: `focus on [ITEM] in inventory`.
-3.  **Proceed:** After receiving confirmation, proceed with the intended use of the item (e.g., `use thermometer on unknown substance B`).
-
-## Example from Trajectory
-*   **Goal:** Measure the temperature of `unknown substance B`.
-*   **Procedure:**
-    1.  `pick up thermometer`
-    2.  `focus on thermometer in inventory` *(This skill)*
-    3.  `pick up unknown substance B`
-    4.  `focus on unknown substance B in inventory` *(This skill)*
-    5.  `use thermometer on unknown substance B`
-
-## Key Principle
-Treat `focus on` as a deliberate checkpoint. It does not change the state of the object but changes the agent's state of awareness and intent, leading to more reliable task execution.
+
+Confirm and prepare an inventory item before using it in a ScienceWorld task. The `focus on [ITEM] in inventory` action verifies the item's presence and signals intent, reducing errors in multi-step experimental procedures.
+
+## When to Use
+
+- After picking up an item that will be used in a subsequent critical action (measurement, combination, connection)
+- When verifying the correct object has been collected before proceeding
+- Before using a tool on a target object, to prepare both tool and target
+
+## Workflow
+
+1. **Acquire the item** -- Ensure the target item is in inventory (e.g., `pick up thermometer`).
+2. **Focus on the item** -- Execute: `focus on [ITEM] in inventory` (replace `[ITEM]` with the exact object name).
+3. **Confirm readiness** -- Wait for system response: `"You focus on the [ITEM]."`.
+4. **Proceed** -- Execute the intended action (e.g., `use thermometer on unknown substance B`).
+
+## Examples
+
+### Example 1: Preparing tool and target for temperature measurement
+
+```
+> pick up thermometer
+You pick up the thermometer.
+
+> focus on thermometer in inventory
+You focus on the thermometer.
+
+> pick up unknown substance B
+You pick up the unknown substance B.
+
+> focus on unknown substance B in inventory
+You focus on the unknown substance B.
+
+> use thermometer on unknown substance B
+The thermometer measures a temperature of 42 degrees celsius.
+```
+
+### Example 2: Preparing an item for placement
+
+```
+> pick up metal fork
+You pick up the metal fork.
+
+> focus on metal fork in inventory
+You focus on the metal fork.
+
+> move metal fork to blue box
+You move the metal fork to the blue box.
+```
+
+## Important Notes
+
+- The `focus on` action does not change the object's state; it is a declarative checkpoint that changes the agent's awareness and intent.
+- Always use the exact object name as it appears in the inventory.
+- If the item is not in inventory, use `pick up [ITEM]` first before attempting to focus.
diff --git a/experiments/src/skills/scienceworld/scienceworld-inventory-manager/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-inventory-manager/SKILL.md
@@ -1,37 +1,37 @@
 ---
 name: scienceworld-inventory-manager
-description: This skill handles picking up objects from the environment into the agent's inventory or moving them out. It should be triggered when the agent needs to acquire an object for later use or place an object into a container. The input is an object name and location, and the output is the object being transferred to or from inventory.
+description: Handles picking up objects from the environment into the agent's inventory or moving them out to containers. Use this skill when you need to acquire an object for later use (pick up) or place an object into a specific container as part of a task requirement (move). Takes an object name and location as input and confirms the transfer to or from inventory.
 ---
-# Instructions
+# Skill: Inventory Manager
 
 ## Purpose
-Use this skill to manage the agent's inventory by picking up objects from the environment or placing them into containers. This is a foundational action for acquiring tools, materials, or evidence needed for tasks.
-
-## When to Use
-- You need to acquire an object for later use in an experiment or task.
-- You need to place an object into a specific container (e.g., a box, a table, a room) as part of a task requirement.
-- The object's location is known or can be inferred from context.
-
-## Core Action Pattern
-The primary action is `pick up OBJ` to acquire an object or `move OBJ to OBJ` to place it into a container. The exact syntax may vary slightly based on the environment's action space (e.g., `pick up metal pot containing nothing in kitchen` vs. `move metal pot to blue box`).
-
-## Procedure
-1.  **Locate the Object:** Ensure you are in the correct room or that the object is in your immediate vicinity. Use `look around` or `examine` if needed.
-2.  **Acquire the Object:** If the object is not in your inventory, use the `pick up` action with the correct object identifier and location.
-3.  **Place the Object (if required):** If the task requires placing the object into a container, use the `move` action with the target container's name.
-
-## Key Considerations
-- **Object State:** Some objects may be described as "containing nothing." Include this in the action if the environment's grammar requires it (e.g., `pick up metal pot containing nothing in kitchen`).
-- **Container Targets:** When moving an object to a container like a box, use the container's name and color if specified (e.g., `blue box`, `orange box`).
-- **Inventory Management:** You can only hold one item in your inventory at a time in the provided trajectory. Plan your actions accordingly.
-
-## Example from Trajectory
-**Goal:** Acquire the metal pot from the kitchen.
-- Action: `pick up metal pot containing nothing in kitchen`
-- Result: "You move the metal pot to the inventory."
-
-**Goal:** Place the conductive metal pot into the correct box.
-- Action: `move metal pot to blue box`
-- Result: The object is transferred from inventory (or the room) to the specified container.
-
-For complex object interactions or environment-specific grammar, consult the bundled reference.
+Manage the agent's inventory: pick up objects from the environment or place them into containers.
+
+## Core Workflow
+1. **Locate Object:** Use `look around` to confirm the object is present and note its exact name.
+2. **Acquire:** `pick up OBJ` to move the object into your inventory.
+3. **Place (if needed):** `move OBJ to OBJ` to transfer the object to a container.
+4. **Verify:** Check the observation feedback to confirm the action succeeded. If it fails, verify exact object names with `look around`.
+
+## Key Actions
+| Action | Purpose |
+|--------|---------|
+| `look around` | Find objects and confirm names |
+| `pick up OBJ` | Move object to inventory |
+| `move OBJ to OBJ` | Place object into a container |
+
+## Examples
+
+**Acquiring an object:**
+1. `look around` — see "a metal pot containing nothing" in the kitchen
+2. `pick up metal pot containing nothing in kitchen`
+3. Result: "You move the metal pot to the inventory."
+
+**Placing an object:**
+1. `move metal pot to blue box`
+2. Result: Object transferred to the blue box.
+
+## Important Notes
+* Some objects include state descriptions in their name (e.g., "metal pot containing nothing"). Use the full name as shown in the environment.
+* Use container color and name as specified in the task (e.g., `blue box`, `orange box`).
+* Inventory capacity is limited — plan pick up and place actions to avoid conflicts.
diff --git a/experiments/src/skills/scienceworld/scienceworld-item-fetcher/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-item-fetcher/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-item-fetcher
-description: This skill picks up a specified object from the environment and moves it into the agent's inventory. It should be triggered when the agent identifies a required tool or material (e.g., thermometer, metal pot) that needs to be collected for later use. The skill takes an object name as input and confirms the item's transfer to inventory, facilitating object manipulation across locations.
+description: Picks up a specified object from the environment and moves it into the agent's inventory. Use this skill when you identify a required tool or material (e.g., thermometer, metal pot) that needs to be collected for later use in an experiment or task. Takes an object name as input and confirms the item's transfer to inventory.
 ---
 # Skill: Fetch and Inventory Item
 
diff --git a/experiments/src/skills/scienceworld/scienceworld-liquid-pourer/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-liquid-pourer/SKILL.md
@@ -1,27 +1,39 @@
 ---
 name: scienceworld-liquid-pourer
-description: This skill transfers the contents of a source liquid container into a target container for mixing or preparation. It should be triggered when combining multiple substances, such as paints or chemicals, into a single vessel.
+description: Transfers the contents of a source liquid container into a target container for mixing or preparation. Use this skill when you need to combine multiple substances (such as paints or chemicals) into a single vessel, or when a liquid must be moved from one container to another before processing.
 ---
-# Instructions for Liquid Pouring
+# Skill: Liquid Pourer
 
-This skill orchestrates the transfer of a liquid from a source container to a target container, typically as a preparatory step for mixing or chemical combination.
+## Purpose
+Transfer a liquid from a source container to a target container, typically as a preparatory step for mixing or chemical combination.
 
-## Core Action
-The primary action is `pour OBJ into OBJ`. Use this to transfer the contents.
+## When to Use
+- Combining multiple liquids or substances into one vessel for mixing.
+- Moving a liquid to a more suitable container before heating or processing.
+- Preparing ingredients for a recipe that requires pouring.
 
-## Execution Flow
-1.  **Identify Containers:** Locate the source container (holding the liquid to be transferred) and the target container (the destination vessel).
-2.  **Perform Transfer:** Execute the `pour` action with the correct object identifiers.
-3.  **Verify (Optional):** If necessary, examine the target container to confirm the transfer was successful.
+## Core Workflow
+1. **Identify Containers:** Use `look around` to locate the source container (with the liquid) and the target container (destination vessel).
+2. **Perform Transfer:** `pour OBJ into OBJ` with precise object identifiers.
+3. **Verify:** `look at OBJ` on the target container to confirm the transfer succeeded.
 
-## Key Considerations
-*   Ensure the target container is empty or can receive the new substance without adverse reaction (e.g., contamination).
-*   The skill is often used in sequence with other skills, such as `mix`, to achieve a final compound.
-*   Object identifiers (e.g., `wood cup (containing red paint)`) must be precise. Use `look around` and `examine` actions to confirm object states and contents if unsure.
+## Key Actions
+| Action | Purpose |
+|--------|---------|
+| `look around` | Locate source and target containers |
+| `pour OBJ into OBJ` | Transfer liquid contents |
+| `look at OBJ` | Verify transfer success |
+| `mix OBJ` | Combine contents (separate skill, used after pouring) |
 
-## Example Usage
-*   **Goal:** Create orange paint by mixing red and yellow.
-*   **Procedure:**
-    1.  `pour wood cup (containing red paint) into jug`
-    2.  `pour wood cup (containing yellow paint) into jug`
-    3.  `mix jug` (This is a separate mixing skill, not part of the pour operation).
+## Example
+**Task:** Create orange paint by mixing red and yellow paint.
+
+1. `look around` — find `wood cup (containing red paint)`, `wood cup (containing yellow paint)`, and `jug`
+2. `pour wood cup (containing red paint) into jug`
+3. `pour wood cup (containing yellow paint) into jug`
+4. `mix jug` — produces orange paint
+
+## Important Notes
+* Object identifiers must be precise (e.g., `wood cup (containing red paint)`). Use `look around` or `examine` to confirm exact names.
+* Ensure the target container can receive the substance without contamination.
+* Pouring only transfers contents — use `mix` as a separate step to combine them.
diff --git a/experiments/src/skills/scienceworld/scienceworld-living-entity-identifier/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-living-entity-identifier/SKILL.md
@@ -1,25 +1,40 @@
 ---
 name: scienceworld-living-entity-identifier
-description: Analyzes room observations to identify potential living things (e.g., eggs, plants, animals) among listed objects. Processes observation text, flags candidate living items based on domain knowledge, and outputs a focused target for subsequent actions.
+description: Analyzes room observations to identify potential living things (e.g., eggs, plants, animals) among listed objects. Use this skill when a task involves finding, focusing on, or interacting with a living thing, biological entity, or organism. Processes observation text, flags candidate living items based on domain knowledge, and outputs a focused target for subsequent actions like focus on or pick up.
 ---
 # Skill: Living Entity Identifier
 
 ## Purpose
-Use this skill when the task involves finding, focusing on, or interacting with a "living thing," "biological entity," "organism," or similar target. The skill analyzes the textual observation of a room to identify candidate objects that are likely to be living or contain life (e.g., eggs, plants, animals).
+Identify living things (eggs, plants, animals) from room observations and focus on them for task progression.
 
-## Core Logic
-1.  **Trigger:** The task description mentions a living entity.
-2.  **Analyze:** Parse the current room's observation text.
-3.  **Identify:** Flag objects from a known list of living entity indicators (see `references/living_indicators.md`).
-4.  **Output:** Select the most suitable candidate and formulate the next action (typically `focus on [TARGET]` or `examine [TARGET]`).
+## Core Workflow
+1. **Survey Room:** `look around` to get the observation text listing all objects.
+2. **Identify Candidates:** Scan the object list for living entity indicators:
+   - **Animals:** dove, giant tortoise, bee, frog, fish
+   - **Eggs:** dove egg, chicken egg, turtle egg
+   - **Plants:** flower, tree, moss, fern, algae
+   - **Other biological:** mushroom, seed, pollen
+3. **Focus on Target:** `focus on [IDENTIFIED_OBJECT]` to signal task progress.
+4. **Transport (if needed):** `pick up [OBJECT]` then `move [OBJECT] to [CONTAINER]`.
 
-## Primary Workflow
-1.  **Look Around:** First, use `look around` to get the room's observation text.
-2.  **Run Analysis:** Process the observation using the logic in `scripts/analyze_observation.py`.
-3.  **Execute Focus:** If a candidate is found, perform `focus on [IDENTIFIED_OBJECT]`.
-4.  **Handle Inventory/Transport:** If the task requires moving the entity, proceed with `pick up` and `move` actions to the specified destination.
+## Key Actions
+| Action | Purpose |
+|--------|---------|
+| `look around` | Survey room for objects |
+| `teleport to LOC` | Move to rooms with biological likelihood |
+| `focus on OBJ` | Signal identification to task system |
+| `pick up OBJ` | Acquire entity for transport |
 
-## Key Rules
-*   Prioritize explicit living things (e.g., "dove egg," "giant tortoise") over ambiguous substances (e.g., "air," "water").
-*   If the initial room lacks candidates, teleport to rooms with higher biological likelihood (e.g., `outside`, `greenhouse`, `bedroom`).
-*   The `focus on` action is critical for signaling task progress. Use it immediately after identification.
+## Example
+**Task:** "Find a living thing in the environment."
+
+1. `teleport to outside`
+2. `look around` — observation lists: "a dove egg", "a rock", "soil"
+3. Identify "dove egg" as the living entity candidate
+4. `focus on dove egg`
+5. If transport required: `pick up dove egg` then `move dove egg to blue box`
+
+## Important Notes
+* Prioritize explicit living things (e.g., "dove egg," "giant tortoise") over ambiguous substances (e.g., "air," "water").
+* If the current room lacks candidates, `teleport to` rooms with higher biological likelihood: `outside`, `greenhouse`, `bedroom`.
+* Always use `focus on` immediately after identification — it signals task progress.
diff --git a/experiments/src/skills/scienceworld/scienceworld-material-classifier/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-material-classifier/SKILL.md
@@ -5,22 +5,19 @@ description: This skill makes a determination about a material's property (e.g.,
 # Material Classification Skill
 
 ## When to Use
-Activate this skill when:
-1. Direct experimental testing of a material property (conductivity, magnetism, etc.) fails due to invalid actions or unavailable equipment.
-2. You need to make a logical inference based on observed properties or domain knowledge.
-3. A final disposition decision (e.g., placing in specific container) is required.
+Activate when direct experimental testing of a material property (conductivity, magnetism, etc.) fails or equipment is unavailable, and you need to classify the material by inference to complete a sorting task.
 
-## Core Logic
-1. **Identify Material**: Focus on the target object and note its composition (e.g., "glass jar").
-2. **Attempt Direct Testing**: First try standard experimental actions if equipment exists (e.g., connecting to circuit).
-3. **Fallback to Inference**: When direct testing fails:
-   - Consult material properties in `references/material_properties.md`
-   - Use common-sense reasoning (e.g., glass is typically nonconductive)
-   - Consider observed contents (e.g., sodium chloride is conductive but container material dominates)
-4. **Execute Disposition**: Place the object in the appropriate container based on classification.
+## Procedure
+1. `focus on <OBJECT>` — identify the target and note its material composition.
+2. Attempt direct testing if equipment exists (e.g., `connect <OBJECT> terminal 1 to <WIRE> terminal 2`).
+3. If testing fails, infer the property from the object's material. Consult `references/material_properties.md` for lookup.
+4. `move <OBJECT> to <CONTAINER>` — place in the appropriate classification container.
+5. `look at <CONTAINER>` — verify the object was placed correctly.
 
-## Critical Notes
-- Glass containers are generally electrical insulators regardless of contents
-- Metal objects are typically conductive unless specified otherwise
-- When in doubt, use the most common material property from domain knowledge
-- Always verify the target object is properly identified before classification
+## Example
+**Task:** Classify a glass jar for electrical conductivity when the circuit test is unavailable.
+1. `focus on glass jar`
+2. `connect glass jar terminal 1 to yellow wire terminal 2` — action fails (invalid connection).
+3. Inference: glass is an electrical insulator → non-conductive.
+4. `move glass jar to orange box`
+5. `look at orange box` — observation: "containing a glass jar" — classification complete.
diff --git a/experiments/src/skills/scienceworld/scienceworld-measurement-taker/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-measurement-taker/SKILL.md
@@ -1,24 +1,74 @@
 ---
 name: scienceworld-measurement-taker
-description: This skill uses a measurement tool (like a thermometer) on a target substance or object to obtain a quantitative reading. It should be triggered when the task requires assessing a property (e.g., temperature) to make a conditional decision. The skill outputs the measured value, which determines subsequent actions such as classification or placement.
+description: Use when the agent needs to measure a quantitative property (temperature, weight, pH) of a target object or substance using a measurement tool. This skill covers acquiring the tool, preparing both tool and target with focus actions, executing the measurement via "use [TOOL] on [TARGET]", and interpreting the resulting value for conditional decisions such as classification or placement.
 ---
-# Measurement Taker Skill
+# Skill: scienceworld-measurement-taker
 
 ## Purpose
-Use this skill when you need to measure a quantitative property (e.g., temperature, weight, pH) of a target object or substance to inform a subsequent decision or action.
 
-## Core Workflow
-1.  **Identify & Acquire Tool:** Locate and obtain the correct measurement tool (e.g., thermometer, scale).
-2.  **Identify & Acquire Target:** Locate and obtain the target object or substance to be measured.
-3.  **Prepare Measurement Environment:** Move to a location suitable for the measurement and any required follow-up actions (e.g., near classification bins).
-4.  **Execute Measurement:** Use the tool on the target to obtain the numerical reading.
-5.  **Interpret & Act:** Based on the measured value and the task's conditional logic, execute the appropriate follow-up action (e.g., place the target in a specific container).
+Measure a quantitative property of a target object or substance in the ScienceWorld environment using the appropriate measurement tool, then interpret the result for subsequent decision-making.
+
+## When to Use
+
+- When a task requires obtaining a numerical reading (temperature, weight, pH) from an object or substance
+- When a measured value determines a conditional next action (e.g., classify based on temperature threshold)
+- When the agent needs to compare properties across multiple objects
+
+## Workflow
+
+1. **Identify and acquire the tool** -- Locate the correct measurement instrument (e.g., thermometer, scale) and `pick up` the tool.
+2. **Focus on the tool** -- Execute `focus on [TOOL] in inventory` to confirm readiness.
+3. **Identify and acquire the target** -- Locate the target object or substance and `pick up` the target.
+4. **Focus on the target** -- Execute `focus on [TARGET] in inventory` to confirm readiness.
+5. **Position for follow-up** -- If the task requires a follow-up action (e.g., placing in a bin), `teleport to` the appropriate location before measuring.
+6. **Execute measurement** -- Use the tool on the target: `use [TOOL] on [TARGET]`.
+7. **Interpret and act** -- Read the numerical result and execute the appropriate conditional action.
+
+## Examples
+
+### Example 1: Measure temperature and classify
+
+```
+> teleport to kitchen
+You teleport to the kitchen.
+
+> pick up thermometer
+You pick up the thermometer.
+
+> focus on thermometer in inventory
+You focus on the thermometer.
+
+> pick up unknown substance B
+You pick up the unknown substance B.
+
+> focus on unknown substance B in inventory
+You focus on the unknown substance B.
+
+> teleport to hallway
+You teleport to the hallway.
+
+> use thermometer on unknown substance B
+The thermometer measures a temperature of 56 degrees celsius.
+
+> move unknown substance B to orange box
+You move the unknown substance B to the orange box.
+```
+
+### Example 2: Measure and compare two objects
+
+```
+> use thermometer on metal fork
+The thermometer measures a temperature of 23 degrees celsius.
+
+> use thermometer on glass cup
+The thermometer measures a temperature of 87 degrees celsius.
+```
+
+The glass cup (87) is hotter than the metal fork (23).
 
 ## Key Principles
-*   **Tool First:** Secure the measurement tool before handling the target, unless the task specifies otherwise.
-*   **Environmental Awareness:** Proactively identify where follow-up actions (like placement) will occur and position yourself accordingly before measuring.
-*   **Verification:** Use `focus on` actions to confirm you have the correct tool and target in your inventory before proceeding.
-*   **Conditional Logic:** The measured value directly determines the next action. Clearly map out the decision thresholds (e.g., "above 100.0", "below 100.0") before measuring.
 
-## Common Actions Sequence
-`look around` → `teleport to [Room]` → `pick up [Tool]` → `focus on [Tool]` → `pick up [Target]` → `focus on [Target]` → `teleport to [Action Room]` → `use [Tool] on [Target]` → `[Conditional Action based on reading]`
+- **Tool first** -- Secure the measurement tool before handling the target.
+- **Focus before use** -- Always `focus on` both tool and target in inventory before measuring.
+- **Plan ahead** -- Identify where follow-up actions occur and position accordingly before measuring.
+- **Map thresholds** -- Clarify decision thresholds (e.g., "above 100.0" vs. "below 100.0") before executing the measurement.
diff --git a/experiments/src/skills/scienceworld/scienceworld-mixture-creator/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-mixture-creator/SKILL.md
@@ -1,27 +1,23 @@
 ---
 name: scienceworld-mixture-creator
-description: This skill chemically mixes the contents of a container using the 'mix' action. It should be triggered when all required ingredients (e.g., sodium chloride and water) are present inside a container and the agent needs to combine them to produce a new substance. The skill performs the mixing operation and outputs the resulting product, completing the synthesis step of the task.
+description: This skill chemically mixes the contents of a container using the 'mix' action. Use when all required ingredients (e.g., sodium chloride and water) are present inside a container and the agent needs to combine them to produce a new substance. The skill performs the mixing operation and outputs the resulting product, completing the synthesis step of the task.
 ---
 # Skill: Chemical Mixture Creator
 
-## Purpose
-Execute the `mix` action on a container to chemically combine its contents into a new substance, as defined by the environment's chemistry system. This skill is the final step in a synthesis task after all required ingredients have been gathered into a single container.
-
 ## When to Use
-- **Trigger Condition:** You have confirmed that a container in your inventory or the environment holds all the required chemical ingredients for a target substance.
-- **Prerequisite:** You have already used `move` or `pour` actions to place the correct ingredients into the target container.
-- **Verification:** You have used `examine <container>` and observed the required ingredients listed in its contents.
+All required ingredients are confirmed inside a single container and you need to combine them into a new substance.
 
-## Core Instruction
-1.  Ensure the target container is in your inventory or accessible in the current room.
-2.  Execute the action: `mix <container>`.
-3.  The environment will process the chemistry and output the resulting substance.
+## Procedure
+1. `examine <CONTAINER>` — verify all required ingredients are present.
+2. `mix <CONTAINER>` — the environment processes the chemistry and produces the result.
+3. `examine <CONTAINER>` or `focus on <NEW_SUBSTANCE>` — confirm the synthesis succeeded.
 
-## Important Notes
-- This skill only performs the final `mix` action. Locating ingredients, finding containers, and combining them are separate exploration and manipulation tasks.
-- The `mix` action is deterministic. If the correct ingredients are present, the reaction will always succeed.
-- After mixing, you may need to `focus on <new_substance>` or `examine <container>` to confirm the task is complete.
-- Do not attempt to `mix` a container that does not contain the precise ingredients listed in the recipe.
+Do not `mix` unless the container holds the exact ingredients required by the recipe.
+## Example
+**Task:** Create salt water by mixing sodium chloride and water.
+1. `examine glass cup` — observe: "containing water, sodium chloride"
+2. `mix glass cup`
+3. Expected result: the environment produces "salt water" inside the glass cup.
+4. `focus on salt water` to confirm the synthesis is complete.
 
-## Related Reference
 For common chemical recipes (e.g., salt water = sodium chloride + water), see `references/common_recipes.md`.
diff --git a/experiments/src/skills/scienceworld/scienceworld-object-classifier/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-object-classifier/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-object-classifier
-description: Moves a tested or examined object into a designated container (e.g., a specific colored box) based on a determined property. Trigger this skill after completing a test or inspection to fulfill a classification or sorting subtask. It takes the object and target container as inputs and performs the move action.
+description: Moves a tested or examined object into a designated container (e.g., a specific colored box) based on a determined property. Use when you have completed a test or inspection and need to fulfill a classification or sorting subtask. It takes the object and target container as inputs and performs the move action.
 ---
 # Instructions
 
@@ -26,3 +26,9 @@ Execute the `move` command to transfer the object into the correct container.
 *   This skill is for the **final sorting action only**. Do not use it to perform the initial test or inspection.
 *   Ensure the object is not in your inventory. If it is, drop it first (`drop <OBJECT>`).
 *   The skill assumes the classification logic (e.g., interpreting a circuit test) has already been handled by a prior process.
+
+## Example
+**Task:** Sort a metal pot after a conductivity test determined it is conductive.
+1. `look around` — confirm metal pot and yellow box are in the room.
+2. `move metal pot to yellow box`
+3. `look at yellow box` — verify: "containing a metal pot".
diff --git a/experiments/src/skills/scienceworld/scienceworld-object-focuser/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-object-focuser/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-object-focuser
-description: This skill selects and focuses on a specific object to signal task intent or prepare it for manipulation. It is triggered after identifying a target object that meets task criteria (e.g., a living thing). The skill uses the 'focus on OBJ' action, taking the object name as input, which is often required before performing actions like moving or using the object in scienceWorld tasks.
+description: This skill selects and focuses on a specific object to signal task intent or prepare it for manipulation. Use when you have identified a target object that meets task criteria (e.g., a living thing) and need to formally select it before performing actions like moving or using the object in ScienceWorld tasks. The skill uses the 'focus on OBJ' action, taking the object name as input.
 ---
 # Skill: Object Focuser
 
@@ -23,4 +23,8 @@ Use this skill to formally select a target object in the ScienceWorld environmen
 *   **Timing:** Focus is typically performed *after* exploration/identification and *before* the main manipulation action.
 *   **Task Logic:** This action is a procedural formality within ScienceWorld. It does not change the object's state but informs the task tracker of your selected target.
 
-For detailed examples and common patterns, see the reference documentation.
+## Example
+**Task:** Focus on a dove egg before picking it up for a biology task.
+1. `look around` — observe: "a dove egg on the table"
+2. `focus on dove egg`
+3. Confirmation received → proceed with `pick up dove egg`.
diff --git a/experiments/src/skills/scienceworld/scienceworld-object-locator/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-object-locator/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-object-locator
-description: This skill searches for a specific target object across multiple rooms by systematically teleporting to likely locations and examining each room. It should be triggered when the agent needs to find an object whose exact location is unknown. The skill involves iterating through candidate rooms, using room exploration to check for the object, and continues until the target is found, providing the object's location as output.
+description: Searches for a specific target object across multiple rooms by systematically teleporting to likely locations and examining each room. Use this skill when you need to find an object whose exact location is unknown. Iterates through candidate rooms using teleport and look around, checks for the object, and continues until found, returning the object's location.
 ---
 # Instructions
 
@@ -28,6 +28,15 @@ Locate a specific target object within the ScienceWorld environment when its loc
 - `examine <OBJECT>` (if more detail is needed to confirm identity)
 - `pick up <OBJECT>` (if the goal is to acquire the object, not just locate it)
 
+## Example
+**Task:** Find the thermometer in the environment.
+
+1. `teleport to kitchen`
+2. `look around` — no thermometer found
+3. `teleport to workshop`
+4. `look around` — observation includes "a thermometer, currently reading a temperature of 10 degrees celsius"
+5. Thermometer located in workshop. `pick up thermometer` if needed.
+
 ## Notes & Best Practices
 - **Efficiency:** Always `look around` immediately after teleporting to get the full room state.
 - **Parsing:** Observations list objects after "you see:". Check this list for the target object's name.
diff --git a/experiments/src/skills/scienceworld/scienceworld-object-placer/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-object-placer/SKILL.md
@@ -1,32 +1,34 @@
 ---
 name: scienceworld-object-placer
-description: Moves a specified object from the environment or inventory into a target container based on a classification decision. It should be triggered when a task requires sorting or storing an object in a specific location after an assessment.
+description: Moves a specified object from the environment or inventory into a target container based on a classification decision. Use this skill when a task requires sorting or storing an object in a specific location after an assessment (e.g., placing a conductive object in the blue box or a non-conductive object in the orange box).
 ---
-# Instructions
+# Skill: Object Placer
 
-This skill orchestrates the final step of a conditional workflow: moving an object to a designated container after its properties have been assessed.
+## Purpose
+Move an object into the correct container based on a prior classification or assessment result. This is the final step in conditional sorting workflows.
 
-## When to Use
-Use this skill when the primary task involves:
-1.  **Classifying an object** (e.g., testing for conductivity, checking material type, verifying a state).
-2.  **Conditionally placing the object** based on the classification result (e.g., "if property X, place in Container A; else, place in Container B").
+## Core Workflow
+1. **Confirm Assessment Result:** Know which container corresponds to which classification (e.g., "blue box" = conductive, "orange box" = non-conductive).
+2. **Acquire Object (if needed):** `pick up OBJ` if the target is not already in inventory.
+3. **Execute Placement:** `move OBJ to OBJ` — place the object in the correct container.
+4. **Verify Placement:** `look at <CONTAINER>` to confirm the object is now inside.
 
-## Core Action
-The skill's primary action is `move OBJ to OBJ`. Ensure the target object is identified and the correct destination container is selected based on the prior assessment.
+## Key Actions
+| Action | Purpose |
+|--------|---------|
+| `pick up OBJ` | Acquire object if not in inventory |
+| `move OBJ to OBJ` | Place object into destination container |
+| `look at OBJ` | Verify placement succeeded |
 
-## Prerequisites
-Before executing this skill, the following must be true:
-*   The target object has been located and is accessible (in the environment or inventory).
-*   The classification test or assessment has been completed.
-*   The result of the assessment is known and the corresponding destination container has been identified.
+## Example
+**Task:** "Determine if metal pot is electrically conductive. If conductive, place in the blue box. If nonconductive, place in the orange box."
 
-## Execution Flow
-1.  **Confirm Context:** Verify the assessment result and the identity of the destination container (e.g., "blue box" for conductive, "orange box" for non-conductive).
-2.  **Acquire Object:** If the target object is not already in your inventory, use `pick up OBJ` to acquire it.
-3.  **Execute Placement:** Use the `move OBJ to OBJ` action to transfer the object to the correct container.
-4.  **Verify:** Optionally, look at the container to confirm the object was placed inside.
+1. Assessment complete: circuit test confirmed metal pot is conductive.
+2. `pick up metal pot` (if not already held)
+3. `move metal pot to blue box`
+4. `look at blue box` — confirms: "In the blue box is: a metal pot"
 
-## Example from Trajectory
-*   **Task:** "Determine if metal pot is electrically conductive. If conductive, place it in the blue box. If nonconductive, place it in the orange box."
-*   **Assessment:** A circuit test confirmed the metal pot was conductive.
-*   **Skill Execution:** `move metal pot to blue box`
+## Important Notes
+* The classification or assessment must be completed before invoking this skill.
+* Always verify placement with `look at` — do not assume success.
+* Container names vary per task (blue box, orange box, etc.) — match them to the task instructions.
diff --git a/experiments/src/skills/scienceworld/scienceworld-object-retriever/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-object-retriever/SKILL.md
@@ -1,20 +1,33 @@
 ---
 name: scienceworld-object-retriever
-description: This skill acquires a specified object by moving it from the environment into the agent's inventory. It should be triggered when a task requires an object to be manipulated, tested, or transported. The skill uses the 'pick up OBJ' action on a target object identified in the room, making it available for further actions in the inventory.
+description: Acquires a specified object by moving it from the environment into the agent's inventory using 'pick up OBJ'. Use this skill when a task requires an object to be manipulated, tested, or transported and it is not yet in your inventory. Makes the object available for further actions like testing, measuring, or placing.
 ---
-# Instructions
+# Skill: Object Retriever
 
-## Primary Objective
-Acquire a specified target object from the environment and place it into your inventory.
+## Purpose
+Acquire a target object from the environment and place it into your inventory for further use.
 
-## Core Procedure
-1.  **Locate the Object:** Use the `look around` action to survey the current room. Identify the target object from the description.
-2.  **Acquire the Object:** Use the `pick up OBJ` action on the identified target object. Replace `OBJ` with the exact name of the object as seen in the environment description.
-3.  **Verification:** Confirm the object is now in your inventory by checking the observation feedback from the `pick up` action.
+## When to Use
+- You need an object for testing, measuring, or transporting.
+- The object is visible in the room but not yet in your inventory.
+- A downstream skill (e.g., tool-user, object-placer) requires the object in inventory.
 
-## Key Notes
-*   This skill is the foundational step for any task requiring physical interaction with an object (e.g., testing, moving, using).
-*   Ensure you are in the correct room containing the object before attempting to pick it up. Use `teleport to LOC` if necessary.
-*   The object must be accessible and not inside a closed container. If a container is closed, use `open OBJ` first.
-*   If the initial `look around` does not reveal the object, you may need to `examine` specific containers or furniture (e.g., `examine table`) to find it.
-*   After acquisition, the object is ready for the next skill in the task sequence (e.g., testing conductivity, placing in a specific box).
+## Core Workflow
+1. **Navigate:** `teleport to LOC` if needed to reach the room containing the object.
+2. **Survey:** `look around` to confirm the object is present and identify its exact name.
+3. **Acquire:** `pick up OBJ` using the exact name from the environment description.
+4. **Verify:** Check the observation feedback confirms "You move the [object] to the inventory."
+
+## Example
+**Task:** Retrieve a metal fork from the kitchen for conductivity testing.
+
+1. `teleport to kitchen`
+2. `look around` — see "a metal fork" on the counter
+3. `pick up metal fork`
+4. Observation: "You move the metal fork to the inventory."
+
+## Important Notes
+* Ensure you are in the correct room before attempting `pick up`. Use `teleport to LOC` if necessary.
+* If `look around` does not reveal the object, use `examine` on containers or furniture (e.g., `examine table`).
+* If a container is closed, use `open OBJ` first.
+* After acquisition, the object is ready for the next skill in the task sequence.
diff --git a/experiments/src/skills/scienceworld/scienceworld-object-selector/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-object-selector/SKILL.md
@@ -1,24 +1,65 @@
 ---
 name: scienceworld-object-selector
-description: Selects appropriate objects from available options based on task criteria. Use this skill when you need to choose a specific object type (e.g., non-living thing) from multiple candidates. It evaluates object properties against task requirements and selects the most suitable candidate for further manipulation.
+description: Use when the agent needs to choose a specific object from multiple candidates in the environment based on task criteria such as object type (non-living thing, electrical component, container), properties, or category. This skill surveys visible objects with "look around", evaluates each against the task requirements, selects the most suitable candidate, and signals intent with "focus on [OBJECT]".
 ---
-# Instructions
+# Skill: scienceworld-object-selector
 
-Use this skill to identify and select an object from a list of candidates that matches a given task requirement (e.g., "non-living thing", "electrical component", "container").
+## Purpose
 
-## Core Workflow
-1.  **Observe & Parse:** Use `look around` to get a list of all visible objects in your current location.
-2.  **Evaluate Candidates:** For each object, determine if it matches the task's criteria. Refer to the `references/object_properties.md` for common classifications.
-3.  **Select & Focus:** Choose the most suitable candidate. Use `focus on [OBJECT]` to signal your intent and proceed with the next task step (e.g., `pick up`, `move`, `use`).
+Identify and select the correct object from visible candidates in the ScienceWorld environment based on task-defined criteria (e.g., "non-living thing", "electrical component", "container"), then signal intent with a `focus on` action.
 
-## Key Principles
-*   **Conciseness:** Choose the first suitable object unless the task implies a specific preference (e.g., "largest", "closest").
-*   **Verification:** If uncertain about an object's properties, use `examine [OBJECT]` for more detail before selecting.
-*   **Task Alignment:** Your selection should enable the *next action* in the task sequence.
+## When to Use
+
+- When a task requires choosing a specific type of object from multiple visible options
+- When the agent must classify objects by property (living/non-living, material type, function) to select one
+- When the task instructs finding and interacting with a particular category of object
+
+## Workflow
+
+1. **Survey the environment** -- Use `look around` to list all visible objects in the current location.
+2. **Evaluate candidates** -- For each visible object, determine if it matches the task criteria. Exclude target containers (e.g., destination boxes) and fixed furniture from candidates.
+3. **Select the best match** -- Choose the first suitable, portable object unless the task specifies a preference (e.g., "largest", "closest").
+4. **Signal intent** -- Execute `focus on [OBJECT]` to confirm selection.
+5. **Execute the task action** -- Proceed with the required action (e.g., `pick up`, `move`, `use`).
+
+## Examples
+
+### Example 1: Find a non-living thing and move it
 
-## Example (from trajectory)
 **Task:** "Find a non-living thing. First, focus on the thing. Then, move it to the purple box."
-1.  `look around` reveals: `purple box`, `table`, `battery`, `black wire`, `blue light bulb`, `red light bulb`, `red wire`, `switch`, `violet light bulb`, `yellow wire`, `ultra low temperature freezer`.
-2.  Evaluate: The `purple box` is the target location. The `table` and `freezer` are furniture. All other items (`battery`, `wires`, `bulbs`, `switch`) are non-living.
-3.  Select: `black wire` is a straightforward, portable non-living object.
-4.  Action: `focus on black wire` -> `move black wire to purple box`.
+
+```
+> look around
+You see: purple box, table, battery, black wire, blue light bulb, red light bulb, red wire, switch, violet light bulb, yellow wire, ultra low temperature freezer.
+```
+
+**Evaluation:** Purple box is the destination. Table and freezer are fixed furniture. Remaining items (battery, wires, bulbs, switch) are all non-living and portable.
+
+```
+> focus on black wire
+You focus on the black wire.
+
+> move black wire to purple box
+You move the black wire to the purple box.
+```
+
+### Example 2: Find an electrical component
+
+**Task:** "Find an electrical component and place it on the workbench."
+
+```
+> look around
+You see: workbench, chair, battery, glass cup, red wire, notebook.
+
+> focus on battery
+You focus on the battery.
+
+> move battery to workbench
+You move the battery to the workbench.
+```
+
+## Key Principles
+
+- **Exclude destinations** -- Never select the target container or destination as the candidate object.
+- **Verify if uncertain** -- Use `examine [OBJECT]` for more detail about an object's properties before selecting.
+- **Task alignment** -- The selection should enable the next action in the task sequence.
diff --git a/experiments/src/skills/scienceworld/scienceworld-process-monitor/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-process-monitor/SKILL.md
@@ -1,35 +1,26 @@
 ---
 name: scienceworld-process-monitor
-description: This skill observes the state of an active apparatus and its contents to track progress. It should be triggered periodically during a heating or reaction process to check for state changes (e.g., solid to liquid). The skill uses 'look at' or 'examine' actions on the apparatus and substance.
+description: This skill observes the state of an active apparatus and its contents to track progress. Use when you need to periodically check for state changes (e.g., solid to liquid) during a heating or reaction process. The skill uses 'look at' or 'examine' actions on the apparatus and substance.
 ---
 # Process Monitoring Protocol
 
-## Purpose
-Monitor an ongoing scientific process (e.g., heating, reaction) to detect state changes in the target substance and track progress toward a goal.
+## When to Use
+Activate when an apparatus (stove, burner) is active and you need to check whether a substance has undergone a state change (e.g., solid to liquid, liquid to gas).
 
-## Trigger Conditions
-Activate this skill when:
-1. An apparatus (e.g., stove, burner) is **active** (`activated` state).
-2. A target substance is contained within or on the apparatus.
-3. You need to determine if a phase/state transition has occurred (e.g., solid → liquid).
+## Procedure
+1. `look at <APPARATUS>` — verify it is active and contains the target substance.
+   - If apparatus is not active, use `activate <APPARATUS>` first.
+   - If substance is missing, check inventory or nearby containers.
+2. `examine <SUBSTANCE>` — check its current state description.
+3. Compare the observed state to the previous state. If changed (e.g., "chocolate" to "liquid chocolate"), proceed to the next task step.
+4. If no change, use `wait` then repeat from step 1.
 
-## Core Procedure
-1.  **Observe the Apparatus**: Use `look at <APPARATUS>` to verify the apparatus is active and contains the target substance.
-2.  **Inspect the Substance**: Use `examine <SUBSTANCE>` to check its current state description.
-3.  **Record Observations**: Note any change in the substance's state description (e.g., "chocolate" → "liquid chocolate").
+Run every few steps during an active process. This skill only observes — it does not modify the apparatus or handle substances.
 
-## Key Principles
-*   **Periodic Execution**: Run this skill every few steps during an active process. Do not spam actions.
-*   **State-Driven**: The skill's findings (state change detected or not) should inform the next step in the overarching experiment.
-*   **Non-Destructive**: This skill only observes. It does not modify temperatures, turn equipment on/off, or handle substances.
-
-## Integration with Other Skills
-The output of this skill (e.g., "substance melted") should be passed to a decision-making skill (e.g., `scienceworld-measurement`) to take the next appropriate action, such as taking a final temperature reading or deactivating the apparatus.
-
-## Example from Trajectory
-*   **Apparatus**: `stove`
-*   **Substance**: `chocolate`
-*   **Initial State**: `chocolate`
-*   **Monitoring Action**: `examine chocolate`
-*   **Observed State Change**: `liquid chocolate`
-*   **Next Action**: Trigger a temperature measurement skill.
+## Example
+**Task:** Monitor chocolate melting on a stove.
+1. `look at stove` — observation: "a stove (activated), containing: chocolate"
+2. `examine chocolate` — observation: "chocolate"
+3. No change yet. `wait`
+4. `examine chocolate` — observation: "liquid chocolate"
+5. State change detected. Proceed to take a temperature measurement.
diff --git a/experiments/src/skills/scienceworld/scienceworld-process-pauser/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-process-pauser/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-process-pauser
-description: This skill introduces deliberate pauses in task execution. It should be triggered when the agent needs to consider next steps, evaluate intermediate results, or wait for processes to complete. The skill uses the 'wait1' or 'wait' actions to temporarily halt activity, preventing rushed decisions in complex experimental procedures.
+description: This skill introduces deliberate pauses in task execution. Use when the agent needs to consider next steps, evaluate intermediate results, or wait for processes to complete. The skill uses the 'wait1' or 'wait' actions to temporarily halt activity, preventing rushed decisions in complex experimental procedures.
 ---
 # Skill: Process Pauser
 
diff --git a/experiments/src/skills/scienceworld/scienceworld-recipe-retriever/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-recipe-retriever/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-recipe-retriever
-description: This skill locates and acquires a recipe or instruction document by using 'pick up' on the recipe object. It should be triggered when the task involves following a specific procedure (e.g., crafting, mixing) and the agent needs to obtain the written instructions. The skill assumes the recipe is visible in the current room and moves it to the inventory, allowing the agent to read it later to understand required ingredients and steps.
+description: This skill locates and acquires a recipe or instruction document by using 'pick up' on the recipe object. Use when the task involves following a specific procedure (e.g., crafting, mixing) and the agent needs to obtain the written instructions. The skill assumes the recipe is visible in the current room and moves it to the inventory, allowing the agent to read it later to understand required ingredients and steps.
 ---
 # Skill: Recipe Retriever
 
@@ -27,3 +27,10 @@ Use this skill when:
 ## Error Handling
 - If `pick up` fails (e.g., "You cannot pick that up"), examine the object first to verify it's a recipe.
 - If no recipe is found after looking around, expand your search to adjacent rooms.
+
+## Example
+**Task:** Obtain the recipe for crafting red paint.
+1. `look around` — observe: "a recipe for red paint on the counter"
+2. `pick up recipe for red paint`
+3. Expected observation: "You move the recipe for red paint to the inventory."
+4. Later: `read recipe for red paint` to learn the required ingredients.
diff --git a/experiments/src/skills/scienceworld/scienceworld-room-explorer/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-room-explorer/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-room-explorer
-description: This skill performs an initial survey of a specified room to identify all visible objects and their states. It should be triggered when the agent first enters a new location or needs to refresh its understanding of the environment. The skill uses the 'look around' action and returns a detailed observation of the room's contents, which serves as the foundational context for subsequent object interaction tasks.
+description: Performs an initial survey of a room to identify all visible objects, containers, devices, and their states using the 'look around' action. Use this skill when you first enter a new location, need to refresh your understanding of the environment, or must identify available resources before planning a sequence of actions. Returns a detailed observation that serves as foundational context for subsequent tasks.
 ---
 # Instructions
 
@@ -25,6 +25,14 @@ Execute the `look around` action. This is the only action required for this skil
     *   **Connections:** Note any pre-existing wire connections or object placements.
     *   **Exits:** Identify doors to other rooms and their state (open/closed).
 
+## Example
+**Scenario:** Agent teleports to the kitchen and needs to identify available resources.
+
+1. `teleport to kitchen`
+2. `look around`
+3. Observation: "This room is called the kitchen. In it, you see: a fridge (containing chocolate, milk), a metal pot, a thermometer, a counter, a stove (which is turned off). You also see: a door to the hallway (which is open)."
+4. **Parsed inventory:** fridge (open, contains chocolate and milk), metal pot, thermometer, counter, stove (off), exit to hallway.
+
 ## Integration with Other Skills
 The observation generated by this skill is essential context for downstream tasks. Before performing actions like `pick up`, `connect`, or `use`, always ensure your understanding of object locations and states is current by running this skill if needed.
 
diff --git a/experiments/src/skills/scienceworld/scienceworld-room-navigator/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-room-navigator/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-room-navigator
-description: Teleports the agent to a specified room within the ScienceWorld environment. It should be triggered when the agent needs to move between different locations to locate objects or access specific facilities. The input is a target room name, and the output is the agent arriving at that room, ready for further interaction.
+description: Teleports the agent to a specified room within the ScienceWorld environment. Use when the agent needs to move between different locations to locate objects or access specific facilities. The input is a target room name, and the output is the agent arriving at that room, ready for further interaction.
 ---
 # Instructions
 
@@ -20,3 +20,9 @@ Use this skill to instantly move the agent to a different room. This is the prim
 *   Teleportation is a single-step action. There is no need for intermediate movement.
 *   All standard room connections (doors) remain, but teleportation bypasses them.
 *   After teleporting, the agent's inventory and any held items remain unchanged.
+
+## Example
+**Task:** Move to the kitchen to find a metal pot.
+1. `teleport to kitchen`
+2. Observation: "You teleport to the kitchen."
+3. `look around` to survey the room and locate the metal pot.
diff --git a/experiments/src/skills/scienceworld/scienceworld-room-scanner/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-room-scanner/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-room-scanner
-description: This skill performs a 'look around' action to scan and describe the current room's contents, including visible objects, containers, and doors. It should be triggered upon entering a new room or when the agent needs to locate specific items or assess the environment state. The skill outputs a detailed room description, which is essential for inventory discovery and situational awareness.
+description: This skill performs a 'look around' action to scan and describe the current room's contents, including visible objects, containers, and doors. Use when entering a new room or when the agent needs to locate specific items or assess the environment state. The skill outputs a detailed room description, which is essential for inventory discovery and situational awareness.
 ---
 # Skill: Room Scanner
 
@@ -31,3 +31,9 @@ The observation from `look around` will contain:
 *   This is a low-level, atomic skill. It should often be the first action in a sequence.
 *   The observation it generates is critical context for subsequent decision-making. Refer back to it.
 *   Do not overuse it. Once you have a recent description of a room, rely on that knowledge until you have reason to believe the state has changed.
+
+## Example
+**Task:** Survey the workshop after teleporting there.
+1. `look around`
+2. Observation: "This room is called the workshop. In it, you see: a table. On the table is: a battery, a blue light bulb, an orange wire, a yellow wire, a green wire. You also see: a blue box, an orange box. There is a door to the hallway."
+3. Parse: available components include battery, light bulb, three wires; classification containers are blue box and orange box.
diff --git a/experiments/src/skills/scienceworld/scienceworld-substance-cooler/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-substance-cooler/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-substance-cooler
-description: This skill initiates the cooling of a substance by moving it into a cooling appliance like a freezer. It should be triggered when a task requires lowering the temperature of a specific material to observe phase changes. The skill takes the substance (often in a container) and the target appliance as inputs, using the 'move OBJ to OBJ' action. It outputs confirmation of the new location.
+description: This skill initiates the cooling of a substance by moving it into a cooling appliance like a freezer. Use when a task requires lowering the temperature of a specific material to observe phase changes. The skill takes the substance (often in a container) and the target appliance as inputs, using the 'move OBJ to OBJ' action. It outputs confirmation of the new location.
 ---
 # Skill: Substance Cooler
 
diff --git a/experiments/src/skills/scienceworld/scienceworld-substance-fetcher/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-substance-fetcher/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-substance-fetcher
-description: This skill locates and retrieves a target substance or material from a container in the environment. It should be triggered when the core task involves processing a specific substance (e.g., chocolate, a chemical). The skill finds the substance, often inside a fridge or cupboard, and acquires it via a pick-up or move action.
+description: Locates and retrieves a target substance or material from a container in the environment. Use this skill when the task requires processing a specific substance (e.g., chocolate, sodium chloride, a chemical) and you need to find and acquire it. Searches rooms and containers (fridge, cupboard, counter) and retrieves the substance via pick up or move actions.
 ---
 # Skill: Substance Fetcher
 
diff --git a/experiments/src/skills/scienceworld/scienceworld-substance-preparator/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-substance-preparator/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-substance-preparator
-description: This skill transfers a target substance into an appropriate container for processing (e.g., a pot for heating, a beaker for mixing). It should be triggered after acquiring the substance and before setting up an apparatus. The skill selects a suitable empty container and moves the substance into it.
+description: Use when you need to transfer a target substance into an appropriate container for processing (e.g., a pot for heating, a beaker for mixing). Trigger after acquiring the substance and before setting up an apparatus. Selects a suitable empty container and moves the substance into it.
 ---
 # Substance Preparation Skill
 
@@ -28,9 +28,15 @@ Prepare a target substance for subsequent processing (e.g., heating, mixing) by
 *   **Substance Integrity:** If the substance is temperature-sensitive (e.g., chocolate in a fridge), moving it to a room-temperature container is part of preparation.
 *   **Error Handling:** If the transfer fails (e.g., container not found), `look around` again and consult the bundled reference for common container names.
 
-## Example from Trajectory
-> **Substance:** `chocolate` (found in fridge).
-> **Action:** `move chocolate to metal pot` (metal pot was empty in cupboard).
-> **Verification:** Subsequent `look at stove` showed "metal pot (containing chocolate)".
+## Example
+
+**Scenario:** You need to melt chocolate as part of a heating task.
+
+1. You have already located `chocolate` in the `fridge` in the kitchen.
+2. Run `look around` to scan for containers. You see: `metal pot` (empty, on counter), `glass beaker` (empty, on shelf), `ceramic cup` (contains water).
+3. Select `metal pot` as the best option (metal, empty, suitable for heating).
+4. Run `examine metal pot` to confirm it is empty.
+5. Run `move chocolate to metal pot`.
+6. Run `examine metal pot` — output confirms: "metal pot (containing chocolate)".
 
 **Proceed to the next skill (e.g., apparatus setup) only after this verification.**
diff --git a/experiments/src/skills/scienceworld/scienceworld-target-locator/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-target-locator/SKILL.md
@@ -1,19 +1,25 @@
 ---
 name: scienceworld-target-locator
-description: This skill determines the most likely location for a target object based on domain knowledge and environmental clues. Trigger this when the agent needs to find a specific item (like an animal) but it is not in the current room. It analyzes the environment description and suggests a room to teleport to for further investigation.
+description: This skill determines the most likely location for a target object based on domain knowledge and environmental clues. Use when the agent needs to find a specific item (like an animal) but it is not in the current room. It analyzes the environment description and suggests a room to teleport to for further investigation.
 ---
 # Skill: Target Locator
 
 **Trigger:** When the agent needs to find a specific object (e.g., an animal, a tool, a chemical) and a preliminary `look around` in the current room does not reveal it.
 
-## Core Logic
+## Procedure
 
-1.  **Analyze the Target:** Classify the target object based on its type (e.g., `animal`, `tool`, `container`, `chemical`).
-2.  **Consult Domain Knowledge:** Use the bundled reference (`target_location_heuristics.md`) to map the object type to the most probable room(s) in the ScienceWorld environment.
-3.  **Evaluate Current Context:** Briefly review the recent `look around` observation. If doors to high-probability rooms are visible and open, prioritize them.
-4.  **Output Decision:** Output a single, clear `teleport to LOC` action command, choosing the most promising location to search next.
-
-**Primary Instruction:** Do not overthink. Rely on the heuristics. The goal is to make an efficient, educated guess to continue the search.
+1. Classify the target object by type.
+2. Map to the most probable room using these heuristics:
+   | Object Type | Likely Room(s) |
+   |-------------|---------------|
+   | animal | outside, garden |
+   | tool/wire/battery | workshop |
+   | food/cooking item | kitchen |
+   | chemical/substance | lab, foundry |
+   | plant/seed | garden, greenhouse |
+   | container/box | workshop, kitchen |
+3. Execute: `teleport to <ROOM>`
+4. `look around` to verify the target is present. If not, try the next likely room.
 
 ## Example Flow (From Trajectory)
 *   **Task:** "find a(n) animal."
diff --git a/experiments/src/skills/scienceworld/scienceworld-task-focuser/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-task-focuser/SKILL.md
@@ -1,33 +1,60 @@
 ---
 name: scienceworld-task-focuser
-description: This skill directs the agent's attention to a specific object, either in the environment or inventory, to signal intent or prepare for an operation. It should be triggered before performing a critical action on an object, such as measuring or using it, to ensure the agent is properly aligned with the task. The skill outputs a confirmation of focus, which often is required for subsequent interactive steps in experimental procedures.
+description: Use when the agent needs to direct attention to a specific object in the environment or inventory before performing a critical action such as measuring, using, or connecting. This preparatory "focus on" step signals intent to the ScienceWorld system, often unlocking required state changes for subsequent interactive steps in experimental procedures.
 ---
 # Skill: scienceworld-task-focuser
 
 ## Purpose
-Use this skill to formally declare your intent to interact with a specific object. This is a crucial preparatory step in scientific workflows within the ScienceWorld environment. Focusing on an object signals to the system that subsequent actions (like `use`, `measure`, `connect`) are targeted and deliberate, often unlocking necessary state changes or measurement capabilities.
+
+Formally declare intent to interact with a specific object in the ScienceWorld environment. The `focus on` action is a required preparatory step that signals to the system which object subsequent actions (`use`, `measure`, `connect`) will target, often unlocking necessary state changes or measurement capabilities.
 
 ## When to Use
-*   **Before Measurement:** Before using a tool (e.g., a thermometer) on a target object.
-*   **Before Complex Operations:** Prior to connecting, mixing, or using one object on another.
-*   **Task Alignment:** When a task description explicitly instructs you to "focus on" an object.
-*   **Inventory Management:** To confirm you have the correct item in your inventory before proceeding.
-
-## Core Instruction
-1.  **Identify the Target Object:** Determine the exact name of the object you need to focus on (e.g., `thermometer`, `metal fork`).
-2.  **Locate the Object:** The object may be in the environment (`on table`) or in your inventory (`in inventory`). Use `look around` and `examine` to find it.
-3.  **Execute the Focus Action:** Use the exact action format:
-    *   If the object is in the environment: `focus on <OBJECT_NAME>`
-    *   If the object is in your inventory: `focus on <OBJECT_NAME> in inventory`
-4.  **Verify Confirmation:** The environment will respond with "You focus on the `<OBJECT_NAME>`." This is your confirmation to proceed.
-
-## Example from Trajectory
-**Scenario:** Measuring the temperature of a metal fork.
-1.  **Focus on the tool:** `focus on thermometer in inventory` (Confirms intent to use the thermometer).
-2.  **Focus on the target:** `focus on metal fork in inventory` (Confirms the object to be measured).
+
+- Before using a measurement tool (e.g., thermometer) on a target object
+- Before complex operations such as connecting, mixing, or combining objects
+- When a task description explicitly instructs "focus on" an object
+- To confirm the correct item is in inventory before proceeding with an action
+
+## Workflow
+
+1. **Identify the target object** -- Determine the exact name as it appears in the environment (e.g., `thermometer`, `metal fork`).
+2. **Locate the object** -- Use `look around` or `inventory` to confirm the object's location (environment or inventory).
+3. **Execute the focus action** -- Issue the appropriate command:
+   - Object in the environment: `focus on <OBJECT_NAME>`
+   - Object in inventory: `focus on <OBJECT_NAME> in inventory`
+4. **Verify confirmation** -- Wait for the system response: `"You focus on the <OBJECT_NAME>."` before proceeding to the next step.
+
+## Examples
+
+### Example 1: Preparing to measure temperature of a metal fork
+
+```
+> focus on thermometer in inventory
+You focus on the thermometer.
+
+> focus on metal fork in inventory
+You focus on the metal fork.
+
+> use thermometer on metal fork
+The thermometer measures a temperature of 23 degrees celsius.
+```
+
+### Example 2: Focusing on an environmental object before moving it
+
+```
+> look around
+You see: a table, a blue box, a red box, a metal fork (on table).
+
+> focus on metal fork
+You focus on the metal fork.
+
+> move metal fork to blue box
+You move the metal fork to the blue box.
+```
 
 ## Important Notes
-*   This skill does not perform the main action (e.g., measuring). It only prepares for it.
-*   The `focus` action has no physical effect on the object; it is a declarative meta-action.
-*   Always wait for the confirmation observation before attempting the next step in your procedure.
-*   If an object is not found, revisit your search logic before attempting to focus.
+
+- This skill does **not** perform the main action (e.g., measuring). It only prepares for it.
+- The `focus` action has no physical effect on the object; it is a declarative meta-action.
+- Always wait for the confirmation observation before attempting the next step.
+- If the object is not found, use `look around`, `examine`, or `teleport to` to locate it before attempting to focus.
diff --git a/experiments/src/skills/scienceworld/scienceworld-task-parser/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-task-parser/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: scienceworld-task-parser
-description: Analyzes user instructions in ScienceWorld environments to extract specific task requirements and constraints. Use this skill when receiving a new task to identify required objects, target locations, and action sequences.
+description: Analyzes user instructions in ScienceWorld environments to extract specific task requirements and constraints. Use when receiving a new task to identify required objects, target locations, and action sequences before taking any environment actions.
 ---
 # Instructions for ScienceWorld Task Parsing
 
@@ -34,4 +34,11 @@ Immediately analyze the user's natural language instruction. Extract the followi
 *   **Clarity:** Structure your internal reasoning using the "Thought:" prefix before each action, as shown in the trajectory.
 *   **Verification:** If an initial `look around` is insufficient, a second `look around` is acceptable to confirm the environment state before proceeding.
 
-For detailed examples and common task patterns, consult the reference documentation.
+## Example
+**Task instruction:** "Find a non-living thing in the workshop and move it to the purple box."
+1. **Parse:** Target = non-living object, Location = workshop, Container = purple box.
+2. `teleport to workshop`
+3. `look around` — observe: "a battery, a blue light bulb, an orange wire..."
+4. Select: battery (non-living, portable).
+5. `focus on battery`
+6. `move battery to purple box`
diff --git a/experiments/src/skills/scienceworld/scienceworld-threshold-evaluator/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-threshold-evaluator/SKILL.md
@@ -1,26 +1,68 @@
 ---
 name: scienceworld-threshold-evaluator
-description: This skill compares a measured numerical value (e.g., temperature, weight) against a predefined threshold to determine a binary outcome. It should be triggered immediately after obtaining a measurement that has an associated conditional instruction. The skill evaluates if the value is above/below the threshold to guide the next action.
+description: Use when the agent has just obtained a numerical measurement (temperature, weight, pH) and must compare it against a predefined threshold to determine a binary outcome. This skill extracts the measured value, evaluates it against the threshold condition (above/below), and executes the corresponding branch action such as classification or placement.
 ---
-# Threshold Evaluation Skill
+# Skill: scienceworld-threshold-evaluator
+
+## Purpose
+
+Compare a measured numerical value against a predefined threshold to determine which of two conditional actions to execute. This is the decision-making step that immediately follows a measurement in ScienceWorld experimental workflows.
 
 ## When to Use
-Trigger this skill **immediately** after you obtain a numerical measurement (e.g., temperature reading) and you have a conditional instruction that depends on that measurement (e.g., "If value > X, do A; if value < X, do B").
 
-## Core Logic
-1.  **Extract the Measurement:** Identify the numerical value from the observation (e.g., "the thermometer measures a temperature of 56 degrees celsius" -> `56`).
-2.  **Identify the Threshold & Condition:** Parse the user's instruction to find the threshold value and the comparison operator (e.g., "above 50.0 degrees" -> `threshold=50.0`, `operator=">"`).
-3.  **Evaluate:** Perform the comparison (`measured_value > threshold` or `measured_value < threshold`).
-4.  **Execute Branch:** Based on the boolean result, perform the corresponding action specified in the instruction.
+- Immediately after obtaining a numerical measurement (e.g., temperature reading from a thermometer)
+- When the task includes a conditional instruction like "if above X, do A; if below X, do B"
+- When classifying or sorting objects based on measured properties
+
+## Workflow
+
+1. **Extract the measurement** -- Parse the numerical value from the observation (e.g., `"the thermometer measures a temperature of 56 degrees celsius"` yields `56`).
+2. **Identify the threshold and condition** -- From the task instruction, determine the threshold value and comparison operator (e.g., `"above 50.0 degrees"` means `threshold=50.0`, `operator=">"`).
+3. **Evaluate the comparison** -- Compare: `measured_value > threshold` or `measured_value < threshold`.
+4. **Execute the correct branch** -- Perform the action specified for the satisfied condition.
+
+## Examples
+
+### Example 1: Temperature-based classification
+
+**Task:** "Measure the temperature. If above 50.0 degrees, move to the orange box. If below 50.0 degrees, move to the blue box."
+
+```
+> use thermometer on unknown substance B
+The thermometer measures a temperature of 56 degrees celsius.
+```
+
+**Evaluation:** 56 > 50.0 is TRUE, so execute the "above" branch.
+
+```
+> move unknown substance B to orange box
+You move the unknown substance B to the orange box.
+```
+
+### Example 2: Weight-based sorting
+
+**Task:** "If the object weighs more than 200 grams, place in the red bin. Otherwise, place in the green bin."
+
+```
+> use scale on rock sample
+The scale measures a weight of 145 grams.
+```
+
+**Evaluation:** 145 > 200 is FALSE, so execute the "otherwise" branch.
+
+```
+> move rock sample to green bin
+You move the rock sample to the green bin.
+```
 
 ## Key Principles
-*   **Immediate Execution:** Do not perform any other actions between obtaining the measurement and running this evaluation.
-*   **Precision:** Use the exact numerical value from the observation. Do not estimate or round unless specified.
-*   **Binary Decision:** The outcome is strictly one of two paths. If the measurement equals the threshold, re-examine the instruction for guidance (e.g., "above" typically means `>`, not `>=`).
 
-## Common Pitfalls (from Trajectory)
-*   **Incorrect Branching:** Do not execute the branch for the opposite condition (e.g., focusing on the blue box when the value is above the threshold).
-*   **Premature Evaluation:** Ensure the measurement is complete and valid before evaluating.
-*   **Action Confusion:** The final action (e.g., `focus on OBJ`) must target the correct object specified for the satisfied condition.
+- **Immediate execution** -- Do not perform other actions between obtaining the measurement and evaluating the threshold.
+- **Precision** -- Use the exact numerical value from the observation; do not estimate or round.
+- **Binary decision** -- The outcome is strictly one of two paths. If the measurement equals the threshold, re-examine the instruction for boundary guidance ("above" typically means `>`, not `>=`).
+
+## Common Pitfalls
 
-For detailed examples and the evaluation script, see the reference documentation.
+- **Incorrect branching** -- Executing the action for the opposite condition (e.g., blue box when value is above threshold).
+- **Premature evaluation** -- Attempting to evaluate before the measurement is complete and valid.
+- **Action confusion** -- Targeting the wrong object in the post-evaluation action.
diff --git a/experiments/src/skills/scienceworld/scienceworld-tool-user/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-tool-user/SKILL.md
@@ -1,14 +1,38 @@
 ---
 name: scienceworld-tool-user
-description: Uses a tool from inventory on a target object or location to perform a specific environmental interaction, such as digging or cutting. Activate this skill when a task requires modifying the environment or manipulating materials, like using a shovel to dig soil. It takes the tool and target as inputs and outputs the result of the interaction, enabling physical task progression.
+description: Uses a tool from inventory on a target object or location to perform a specific environmental interaction, such as digging, cutting, or measuring. Use this skill when a task requires modifying the environment or manipulating materials with a tool (e.g., using a shovel to dig soil, a thermometer to measure temperature, or an axe to cut wood). Takes the tool and target as inputs and outputs the result of the interaction.
 ---
-# Instructions
+# Skill: Tool User
 
-Use this skill when you need to perform a physical action on the environment using a tool you possess. The core action is `use TOOL on TARGET`.
+## Purpose
+Perform a physical action on the environment using a tool from your inventory. The core action is `use TOOL on TARGET`.
 
-## 1. Prerequisites
-*   **Tool in Inventory:** Ensure the required tool (e.g., `shovel`, `axe`) is in your inventory. Use `pick up OBJ` if it is not.
-*   **Clear Target:** Identify the exact target object or location name (e.g., `ground`, `tree`).
+## When to Use
+- A task requires modifying the environment (digging, cutting, heating).
+- You need to measure a property of an object (temperature, conductivity).
+- A tool-based interaction is the next step in your experiment workflow.
 
-## 2. Core Action
-Execute the interaction with the command:
+## Core Workflow
+1. **Ensure Tool in Inventory:** The required tool (e.g., `shovel`, `thermometer`, `axe`) must be in your inventory. Use `pick up OBJ` if it is not.
+2. **Identify Target:** Determine the exact target object or location name (e.g., `ground`, `tree`, `metal fork`).
+3. **Execute:** `use TOOL on TARGET`.
+4. **Interpret Result:** Read the observation output to determine the outcome (e.g., temperature reading, state change).
+
+## Key Actions
+| Action | Purpose |
+|--------|---------|
+| `pick up OBJ` | Acquire tool if not in inventory |
+| `use OBJ on OBJ` | Perform tool interaction |
+| `look around` | Confirm target identity and location |
+
+## Example
+**Task:** Measure the temperature of a metal fork using a thermometer.
+
+1. `pick up thermometer` — ensure tool is in inventory
+2. `use thermometer on metal fork`
+3. Observation: "a thermometer, currently reading a temperature of 72 degrees celsius"
+
+## Important Notes
+* The tool must be in your inventory before use. The `pick up` action is a prerequisite.
+* Use exact object names as they appear in the environment description.
+* Some tools produce measurable outputs (thermometer readings); others produce state changes (shovel digs soil). Interpret accordingly.
diff --git a/experiments/src/skills/scienceworld/scienceworld-tool-validator/SKILL.md b/experiments/src/skills/scienceworld/scienceworld-tool-validator/SKILL.md
@@ -1,26 +1,62 @@
 ---
 name: scienceworld-tool-validator
-description: This skill performs a basic functionality check on a tool in the agent's inventory. It should be triggered after acquiring a tool and before its first use in a critical task step to ensure it is operational. The skill typically uses a 'focus' or 'examine' action on the tool and confirms its readiness state.
+description: Use when the agent has acquired a tool or instrument and needs to verify it is operational before first use in a critical task step. This skill performs a lightweight pre-use check via "focus on [TOOL] in inventory" and confirms readiness based on the system's response, ensuring the tool is functional before measurement, activation, or connection operations.
 ---
-# Tool Validation Protocol
+# Skill: scienceworld-tool-validator
 
 ## Purpose
-Execute a pre-use functionality check on a tool or instrument to confirm it is operational before employing it in a critical task step.
 
-## Core Workflow
-1.  **Acquire Tool:** Ensure the target tool is in your inventory. If not, retrieve it from the environment.
-2.  **Execute Validation:** Use the `focus on [TOOL]` action on the tool in your inventory. This is the standard validation action.
-3.  **Confirm Readiness:** Observe the system's response. A successful focus action (e.g., "You focus on the [tool].") confirms the tool is ready for use. No further diagnostic steps are required unless an error is observed.
+Perform a pre-use functionality check on a tool or instrument to confirm it is operational before employing it in a critical ScienceWorld task step such as measurement, activation, or connection.
+
+## When to Use
+
+- Immediately after acquiring a tool (e.g., `pick up thermometer`) and before its first use
+- When switching to a different tool mid-task and needing to confirm readiness
+- When resuming a task after navigation and needing to re-confirm tool availability
+
+## Workflow
+
+1. **Acquire the tool** -- Ensure the target tool is in inventory. If not, locate it with `look around` and retrieve it with `pick up [TOOL]`.
+2. **Execute validation** -- Run: `focus on [TOOL] in inventory`.
+3. **Confirm readiness** -- A successful response (`"You focus on the [TOOL]."`) confirms the tool is operational. No further diagnostic steps are needed unless an error is observed.
+4. **Proceed** -- Use the validated tool in the task operation (e.g., `use thermometer on [TARGET]`).
+
+## Examples
+
+### Example 1: Validating a thermometer before measurement
+
+```
+> pick up thermometer
+You pick up the thermometer.
+
+> focus on thermometer in inventory
+You focus on the thermometer.
+```
+
+The thermometer is validated. Proceed with measurement:
+
+```
+> use thermometer on unknown substance B
+The thermometer measures a temperature of 42 degrees celsius.
+```
+
+### Example 2: Validating a scale after teleporting to a new room
+
+```
+> teleport to workshop
+You teleport to the workshop.
+
+> pick up scale
+You pick up the scale.
+
+> focus on scale in inventory
+You focus on the scale.
+```
+
+The scale is validated and ready to weigh objects.
 
 ## Key Principles
-*   **Timing:** Perform this check immediately after acquiring a tool and *before* its first application in a task-sensitive operation (e.g., measuring, activating, connecting).
-*   **Simplicity:** The `focus` action is the primary, lightweight validation method. Avoid unnecessary `examine` or `use` actions during the check.
-*   **State Awareness:** The skill assumes the environment's containers are open and items are accessible. Teleportation is available for efficient navigation.
-
-## Example Application
-*   **Scenario:** You need to measure the temperature of a substance.
-*   **Application:**
-    1.  Locate and `pick up thermometer`.
-    2.  **Trigger Skill:** `focus on thermometer in inventory`.
-    3.  **Confirmation:** Observe "You focus on the thermometer." The tool is now validated for use.
-    4.  Proceed with `use thermometer on [SUBSTANCE]`.
+
+- **Timing** -- Validate immediately after acquisition, before any task-sensitive operation.
+- **Simplicity** -- The `focus on` action is the primary, lightweight validation method. Avoid unnecessary `examine` or `use` actions during the check.
+- **State awareness** -- Ensure containers are open and items are accessible before attempting to pick up tools. Use `teleport to` for efficient navigation.
diff --git a/experiments/src/skills/scienceworld/task-completion-focus/SKILL.md b/experiments/src/skills/scienceworld/task-completion-focus/SKILL.md
@@ -1,29 +1,20 @@
 ---
 name: task-completion-focus
-description: Focuses on a specific target object to signal task completion. Execute this skill when you have produced the required final object (like a grown banana) and need to formally complete the assigned task. This handles the 'focus on OBJ' action that typically marks successful task execution in the environment.
+description: Focuses on a specific target object to signal task completion. Use when you have produced the required final object (like a grown banana) and need to formally complete the assigned task. This handles the 'focus on OBJ' action that typically marks successful task execution in the environment.
 ---
 # Skill: Task Completion Focus
 
-## Purpose
-This skill is the final step in a task execution chain. It is triggered **only** when the primary objective of a task has been successfully achieved and the target object is present and observable in the environment. Its sole function is to execute the `focus on OBJ` action on the correct object, which formally signals task completion to the environment.
-
 ## When to Use
-*   **Prerequisite:** The final, required object (e.g., a grown banana, a crafted item, a repaired device) must be visibly present in the environment.
-*   **Trigger:** You have verified the object's presence and your goal is to complete the task.
-*   **Do Not Use** for intermediate steps, exploration, or object manipulation.
-
-## Execution Protocol
-
-1.  **Verification:** Before execution, confirm the target object is in the scene. Use `look around` or `examine` if necessary.
-2.  **Action Execution:** Perform the `focus on <OBJECT>` action.
-3.  **Ambiguity Resolution:** The environment may present multiple valid targets (e.g., bananas on different trees). If an "Ambiguous request" observation is received, you **must** select the correct target by number.
-    *   **Selection Rule:** Choose the target that is most directly associated with the main task goal. If multiple are identical, select the first option (e.g., `0`).
+The final required object (e.g., grown banana, crafted item) is visibly present and you need to formally signal task completion. Do not use for intermediate steps.
 
-## Example from Trajectory
-**Scenario:** Task was to "grow a banana". After successful cultivation, multiple bananas are visible.
-*   **Observation:** "On the banana tree you see: a banana, a flower."
-*   **Correct Action:** `focus on banana on banana tree`
-*   **If Ambiguous:** Select option `0` (or the first instance of the target banana).
+## Procedure
+1. `look around` — confirm the target object is visible in the scene.
+2. `focus on <OBJECT>` — signal task completion.
+3. **Ambiguity handling:** If the environment returns "Ambiguous request" with numbered options, respond with the option number (e.g., `0`) for the target most directly associated with your task goal.
 
-## Key Principle
-This skill is a **low-freedom, terminal action**. Its logic is simple and deterministic. The creative and complex work (growing the plant, crafting the item) belongs to other skills. This skill exists solely to "press the final button."
+## Example
+**Task:** "Grow a banana." After successful cultivation:
+1. `look around` — observation: "On the banana tree you see: a banana, a flower."
+2. `focus on banana on banana tree`
+3. If ambiguous prompt appears listing multiple bananas, select `0` (first instance).
+4. Observation confirms task completion.
diff --git a/experiments/src/skills/webshop/webshop-attribute-verifier/SKILL.md b/experiments/src/skills/webshop/webshop-attribute-verifier/SKILL.md
@@ -1,24 +1,71 @@
 ---
 name: webshop-attribute-verifier
-description: This skill confirms specific product attributes on a detailed product page. It is triggered when navigating to an individual product listing to verify details such as color options, exact price, or specifications. The skill checks available selections or displayed information against the user's requirements, ensuring the product matches before proceeding to purchase.
+description: >
+  Verifies product attributes on a web shop detail page by extracting price, comparing color availability,
+  validating specifications, and confirming option selections against user requirements before purchase.
+  Use when you need to check if a product matches requirements, verify product details before buying,
+  confirm item specifications on an online store product page, or validate that price, color, size,
+  or other attributes satisfy the user's constraints. Outputs a `Thought:` assessment followed by a
+  `click[value]` action to select the matching option and proceed, or navigates back to search if
+  the product does not match.
 ---
+
 # Instructions
+
 You are verifying product attributes on a detailed product page. Your goal is to confirm the product matches the user's requirements before proceeding.
 
+## Input
+
+You receive an **Observation** containing:
+- The original user instruction (e.g., "find a black leather wallet, price lower than 40.00 dollars")
+- Product details: Title, Price, Rating
+- Available options (e.g., color buttons like "black", "brown")
+- Available actions (e.g., "Buy Now", "Back to Search", "Description")
+
 ## Core Workflow
-1.  **Parse Requirements:** Extract the user's target attributes (e.g., color, max price) from the instruction.
-2.  **Inspect Page:** Examine the observation for the product's details, available options (like color buttons), price, and specifications.
-3.  **Verify Match:** Systematically check if the product's attributes satisfy all user requirements.
-4.  **Act Accordingly:**
-    *   If the product matches **all** requirements, proceed to select the correct option (e.g., click the correct color) and then initiate the purchase (e.g., click 'Buy Now').
-    *   If the product **does not match** a requirement (e.g., wrong color, price too high), navigate back to search.
-
-## Action Guidelines
-*   Use `click[value]` to interact with page elements. The `value` must exactly match a clickable item from the observation.
-*   Use `search[keywords]` only if you need to find a new product because the current one does not meet requirements.
-*   Your `Thought:` must explicitly state which requirement you are checking and the result of the check.
+
+1. **Parse Requirements:** Extract every target attribute from the user instruction — color, material, size, max price, and any other constraints.
+2. **Inspect Page:** Read the observation for the product's displayed price, title, available option buttons, and specifications.
+3. **Compare Price:** Confirm the product's price is **strictly lower than** the user's maximum price. If not, navigate back immediately.
+4. **Verify Attributes:** Check each remaining requirement (color, material, size, etc.) against the product's details and available options.
+5. **Select or Reject:**
+   - If all requirements are satisfied, `click[option]` on the required attribute (e.g., `click[black]`) **first**, then `click[Buy Now]`.
+   - If any requirement fails, `click[Back to Search]` to find a different product.
+
+## Action Format
+
+- `click[value]` — interact with a page element. The `value` must exactly match a clickable item from the observation.
+- `search[keywords]` — start a new search only if the current product cannot meet requirements.
+- Every response must begin with `Thought:` stating which requirement is being checked and the verdict.
 
 ## Critical Rules
-*   **Price Check:** The product's price must be **strictly lower than** the user's specified maximum price.
-*   **Attribute Selection:** If a specific attribute (like color) is required, you **must** click the corresponding option button (e.g., `click[black]`) before proceeding to purchase.
-*   **Sequential Actions:** Do not skip the attribute selection step. The purchase action should only follow a successful verification and selection.
+
+- **Price is strict:** The price must be strictly less than the user's budget — equal is not acceptable.
+- **Select before buying:** Always click the required attribute option (e.g., `click[black]`) before clicking `click[Buy Now]`. Never skip this step.
+- **One action per turn:** Output exactly one action after your `Thought:`.
+
+## Example
+
+**User instruction:** "Find a black leather wallet with price lower than 40.00 dollars"
+
+**Observation:**
+```
+[Back to Search] [< Prev]
+Title: Genuine Leather Bifold Wallet - Multiple Colors
+Price: $35.99
+Rating: ★★★★☆
+Options: [black] [brown] [tan]
+Actions: [Buy Now] [Description] [Back to Search]
+```
+
+**Response:**
+```
+Thought: The user wants a black leather wallet under $40. The price is $35.99, which is strictly less than $40 — price check passes. The title mentions "Leather" which matches the material requirement. The color "black" is available as a selectable option. All requirements are satisfied. I will select the black option first.
+Action: click[black]
+```
+
+**Next turn — after selecting black:**
+```
+Thought: The black option is now selected. All requirements verified. Proceeding to purchase.
+Action: click[Buy Now]
+```
diff --git a/experiments/src/skills/webshop/webshop-initial-search/SKILL.md b/experiments/src/skills/webshop/webshop-initial-search/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: webshop-initial-search
-description: Performs the first search on an e-commerce platform using keywords derived from parsed user requirements. Trigger this skill when starting product discovery or when previous search results are insufficient. It formulates a search query from the criteria (e.g., '24 pack of 7.5 ounce bottles of non-gmo classic tonic') and executes the search action, returning the initial result page.
+description: Performs the first search on an e-commerce platform using keywords derived from parsed user requirements. Use when starting product discovery from a user instruction or when previous search results are insufficient and a new query is needed. It formulates a search query from the criteria (e.g., '24 pack of 7.5 ounce bottles of non-gmo classic tonic') and executes the search[] action, returning the initial result page.
 ---
 # Instructions
 1.  **Parse Requirements:** Extract the core product criteria from the user's instruction. Focus on:
@@ -17,3 +17,13 @@ description: Performs the first search on an e-commerce platform using keywords
     *   The action output will be the initial search results page observation.
 
 4.  **Next Steps:** After executing this skill, proceed to evaluate the search results. The next actions will typically involve clicking on a promising product listing or refining the search.
+
+## Example
+
+**User instruction:** "I would like to find a 24 pack of 7.5 ounce bottles of non-gmo classic tonic, and target price lower than 50.00 dollars"
+
+**Thought:** I need to search for the product using the key attributes. I will omit the price constraint from the search keywords.
+
+**Action:** `search[24 pack of 7.5 ounce bottles of non-gmo classic tonic]`
+
+**Observation:** The platform returns the initial search results page with matching product listings.
diff --git a/experiments/src/skills/webshop/webshop-product-detail-check/SKILL.md b/experiments/src/skills/webshop/webshop-product-detail-check/SKILL.md
@@ -1,6 +1,11 @@
 ---
 name: webshop-product-detail-check
-description: This skill examines a specific product's detailed page to verify it matches the user's requirements, checking price, description, features, and reviews. Trigger when a candidate product is selected from search results. It confirms alignment with constraints and provides a final suitability assessment before purchase.
+description: >-
+  Examines a specific product's detailed page to verify it matches the user's requirements,
+  checking price, description, features, and reviews. Use when you have navigated to a
+  product detail page from search results and need to confirm the product meets all
+  user-specified constraints before purchasing. It provides a final suitability assessment
+  with a clear proceed-or-reject recommendation.
 ---
 # Skill: Product Detail Verification
 
@@ -36,6 +41,22 @@ Your response must use the following format:
 **Thought:** [Your reasoning, summarizing the user's constraints, the product details found, and the result of the verification check.]
 **Action:** [The single, valid action to take: `click[buy now]` or `click[back to search]`]
 
+## Example
+
+**Instruction:** "i need a long clip-in hair extension which is natural looking, and price lower than 40.00 dollars"
+
+**Observation:** Product page for "22 Inch Long Natural Looking Clip-In Hair Extension" — Price: $34.99, Description mentions "clip-in", "natural looking", "synthetic fiber".
+
+**Thought:** The user needs a long, natural-looking, clip-in hair extension under $40. This product is priced at $34.99 (< $40.00), the title confirms "long" and "natural looking", and the description confirms "clip-in". All constraints are satisfied.
+**Action:** `click[buy now]`
+
+---
+
+**Observation:** Product page for "Premium Human Hair Extension" — Price: $45.99, Description mentions "clip-in", "natural".
+
+**Thought:** The user's budget is under $40. This product is priced at $45.99, which exceeds the $40 limit. Price constraint fails.
+**Action:** `click[back to search]`
+
 ## Notes
 *   Prioritize information explicitly on the product page. Assume missing information (like a Rating of "N.A.") does not disqualify a product unless specified by the user.
 *   The "Buy Now" button must be present in the available actions list for the purchase action to be valid.
diff --git a/experiments/src/skills/webshop/webshop-product-evaluator/SKILL.md b/experiments/src/skills/webshop/webshop-product-evaluator/SKILL.md
@@ -1,6 +1,11 @@
 ---
 name: webshop-product-evaluator
-description: This skill evaluates product listings against user requirements, such as price limits and feature matches, to identify viable options. It should be triggered when presented with a search results page containing multiple products. The skill analyzes product titles, prices, and brief descriptions to select the most promising candidate for detailed inspection.
+description: >-
+  Evaluates product listings against user requirements such as price limits and feature
+  matches to identify viable options. Use when you are on a search results page containing
+  multiple products and need to select the most promising candidate for detailed inspection.
+  The skill analyzes product titles, prices, and brief descriptions to rank and choose
+  the best match.
 ---
 # Instructions
 
@@ -22,3 +27,18 @@ Activate this skill when you are on a **search results page** in a web shopping
 
 ## Thought Process Format
 Always structure your internal reasoning and final action using this format:
+
+**Thought:** [Summarize the user's constraints, evaluate each product against them, and justify your selection.]
+**Action:** `click[<product_id>]`
+
+## Example
+
+**Instruction:** "i need a teeth whitening toothpaste that also freshens breath, and price lower than 15.00 dollars"
+
+**Observation (Search Results Page):**
+- B09NYFDNVX: "Whitening Toothpaste with Breath Freshener" — $12.99
+- B08KZPTL3M: "Professional Teeth Whitening Kit" — $24.99
+- B07HQRJ4WP: "Mint Fresh Whitening Toothpaste" — $9.49
+
+**Thought:** The user needs a teeth whitening toothpaste that freshens breath, under $15. Product B09NYFDNVX at $12.99 mentions both "whitening" and "breath freshener" in the title — meets all criteria. B08KZPTL3M exceeds the budget at $24.99. B07HQRJ4WP is within budget and mentions "whitening" but does not explicitly mention breath freshening. Selecting B09NYFDNVX as the best match.
+**Action:** `click[B09NYFDNVX]`
diff --git a/experiments/src/skills/webshop/webshop-product-search/SKILL.md b/experiments/src/skills/webshop/webshop-product-search/SKILL.md
@@ -1,27 +1,27 @@
 ---
 name: webshop-product-search
-description: This skill performs an initial product search using a web interface by generating appropriate search keywords based on interpreted query criteria. It is triggered when starting a product discovery task or when returning to search results. The skill inputs structured search parameters and outputs a list of candidate products from the search results page.
+description: >-
+  Performs an initial product search using a web interface by generating appropriate search
+  keywords based on interpreted query criteria. Use when starting a product discovery task,
+  when returning to search results after rejecting a product, or when the observation contains
+  a search interface prompt. The skill inputs structured search parameters and outputs a list
+  of candidate products from the search results page.
 ---
 # Skill: WebShop Product Search
 
-## Primary Function
-Generate a targeted search query and execute it on a web shopping interface to retrieve a list of candidate products that match the user's criteria.
-
 ## Core Workflow
-1.  **Interpret Criteria:** Analyze the user's instruction to identify key product attributes (e.g., "long clip-in hair extension", "natural looking", "price lower than 40.00 dollars").
-2.  **Formulate Query:** Construct a concise, effective search string that prioritizes the most critical attributes. The primary goal is to balance specificity with recall.
-3.  **Execute Search:** Use the `search[keywords]` action to submit the query.
-4.  **Parse Results:** The skill's success is marked by the system returning a "Page 1" observation containing a list of products (ASINs, titles, prices).
+1.  **Interpret Criteria:** Extract key product attributes from the user's instruction (e.g., product type, features, price constraints).
+2.  **Formulate Query:** Construct a concise search string prioritizing the core product type and critical attributes. Start broad; refine if results are poor.
+3.  **Execute Search:** Use the `search[keywords]` action to submit the query. Keywords must be a single string enclosed in brackets.
+4.  **Validate Results:** Success is marked by a "Page 1" observation containing product listings. If 0 results are returned, re-invoke with a broader or alternative query. If all results exceed the user's price constraint, refine with additional terms.
 
 ## Key Decision Logic
-*   **Query Formulation:** Start with a broad query containing the core product type. If the initial results are poor, the skill may be re-invoked with a more refined query (e.g., adding "synthetic" or "human hair" based on observed results).
-*   **Trigger Condition:** This skill is the entry point for a new product discovery task. It is also the correct action when the observation contains "[SEP] Search" or "[SEP] Back to Search", indicating the agent is on a search page.
-*   **Output Handoff:** The output of this skill is the search results page. Subsequent skills (e.g., `product-evaluation`) should be used to analyze individual items from this list.
+*   **Trigger Condition:** This skill is the entry point for a new product discovery task. Also activate when the observation contains "[SEP] Search" or "[SEP] Back to Search".
+*   **Output Handoff:** The search results page is passed to downstream skills (e.g., `webshop-result-filter`, `webshop-product-evaluator`) for individual product analysis.
 
-## Error Handling / Edge Cases
-*   If no search action is available in the current state, this skill is not applicable.
-*   If the observation does not contain a clear search interface prompt, do not use this skill.
-*   The search keywords must be a single string enclosed in brackets after `search[`. Do not include multiple actions or extra formatting.
+## Constraints
+*   Do not use this skill if no search action is available in the current state.
+*   Do not include multiple actions or extra formatting in the search keywords.
 
 ## Example from Trajectory
 **Instruction:** "i need a long clip-in hair extension which is natural looking, and price lower than 40.00 dollars"
diff --git a/experiments/src/skills/webshop/webshop-product-selector/SKILL.md b/experiments/src/skills/webshop/webshop-product-selector/SKILL.md
@@ -1,6 +1,10 @@
 ---
 name: webshop-product-selector
-description: Selects the most promising product candidate from a filtered shortlist for detailed inspection. Use this skill when multiple items seem viable; it makes a final selection based on a heuristic (e.g., best feature match, lowest price) and triggers the action to navigate to that product's detail page (click[product_id]).
+description: >-
+  Selects the most promising product candidate from a filtered shortlist for detailed
+  inspection. Use when you are on a search results page with multiple viable items and need
+  to make a final selection based on a heuristic such as best feature match or lowest price.
+  Triggers navigation to the selected product's detail page via click[product_id].
 ---
 # Instructions
 Use this skill when you are on a search results page with multiple product options that appear to meet the user's core requirements.
@@ -15,3 +19,18 @@ Use this skill when you are on a search results page with multiple product optio
 
 ## Thought Process Template
 Structure your reasoning before acting using this template:
+
+**Thought:** [List the user's requirements, evaluate each candidate product against them, explain why the selected product is the best match.]
+**Action:** `click[<product_id>]`
+
+## Example
+
+**Instruction:** "i need a portable double horn bluetooth speaker that is easy to carry, and price lower than 50.00 dollars"
+
+**Observation (Search Results):**
+- B093C1THVP: "Portable Double Horn Bluetooth Speaker — Compact & Easy to Carry" — $32.99
+- B08XYZ1234: "Double Horn Wireless Speaker — Premium Sound" — $55.00
+- B07ABC5678: "Mini Portable Bluetooth Speaker" — $19.99
+
+**Thought:** The user needs a portable, double horn bluetooth speaker that is easy to carry, under $50. B093C1THVP at $32.99 matches "portable", "double horn", and "easy to carry" — all keywords present in the title. B08XYZ1234 exceeds the $50 budget. B07ABC5678 is within budget but lacks "double horn". Selecting B093C1THVP as the best match.
+**Action:** `click[B093C1THVP]`
diff --git a/experiments/src/skills/webshop/webshop-purchase-executor/SKILL.md b/experiments/src/skills/webshop/webshop-purchase-executor/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: webshop-purchase-executor
-description: This skill executes the purchase action for a confirmed suitable product on an e-commerce page. It is triggered after product verification when the user decision is to buy. The skill clicks the purchase button (e.g., 'Buy Now') to complete the transaction.
+description: Executes the purchase action for a confirmed suitable product on an e-commerce page. Use when a product has been verified against the user's requirements (price, attributes) and the decision is to buy. Performs a click[Buy Now] action on the purchase button to complete the transaction.
 ---
 # Skill: webshop-purchase-executor
 
@@ -28,3 +28,13 @@ Perform a `click` action on the purchase button.
 - Do not use this skill for browsing, searching, or product comparison.
 - The skill assumes price and specification validation occurred in a previous step.
 - If multiple purchase options exist (e.g., "Buy Now", "Add to Cart & Checkout"), prefer the most direct path to complete the transaction, typically "Buy Now".
+
+## Example
+
+**Scenario:** The user wants a natural-looking wig priced under $40.00. You are on a product detail page for "Natural Looking Human Hair Wig - $34.99" and have verified it meets all criteria.
+
+**Thought:** The product matches the user's requirements (natural looking, price $34.99 < $40.00). I should proceed with the purchase.
+
+**Action:** `click[Buy Now]`
+
+**Observation:** The purchase is confirmed and the transaction is complete.
diff --git a/experiments/src/skills/webshop/webshop-purchase-initiator/SKILL.md b/experiments/src/skills/webshop/webshop-purchase-initiator/SKILL.md
@@ -1,6 +1,11 @@
 ---
 name: webshop-purchase-initiator
-description: This skill initiates the purchase process by clicking the buy button once a product and its options have been selected and verified against requirements. It should be triggered when all selection criteria are satisfied and the user is ready to proceed to checkout. The skill confirms the final price meets any budget constraints before executing the purchase action.
+description: >-
+  Initiates the purchase process by clicking the buy button once a product and its options
+  have been selected and verified against requirements. Use when you are on a product detail
+  page, all selection criteria (price, features, options) are satisfied, and the user is
+  ready to proceed to checkout. Confirms the final price meets budget constraints before
+  executing click[buy now].
 ---
 # Instructions
 
@@ -22,8 +27,14 @@ Before clicking "Buy Now", you **must** perform these checks:
 
 If any check fails, do not use this skill. Instead, revert to selecting the correct option or searching for a different product.
 
-## Trajectory Example
-Refer to `references/trajectory_example.md` for a detailed walkthrough of a successful skill execution.
+## Example
+
+**Instruction:** "i need a teeth whitening toothpaste that also freshens breath, and price lower than 15.00 dollars"
+
+**Observation:** Product page for "Whitening Toothpaste with Breath Freshener" — Price: $12.99, Size: 4oz (selected), Flavor: Mint (selected). Available actions: click[buy now], click[back to search].
+
+**Thought:** The user needs a teeth whitening toothpaste that freshens breath, under $15. The current product is priced at $12.99 (< $15.00), matches "whitening" and "breath freshener" in the title, and all required options (size, flavor) are selected. All checks pass — proceeding to purchase.
+**Action:** `click[buy now]`
 
 ## Error Handling
 - If the "Buy Now" button is not present in the list of clickable actions, the action will be invalid. Do not force the action.
diff --git a/experiments/src/skills/webshop/webshop-query-interpreter/SKILL.md b/experiments/src/skills/webshop/webshop-query-interpreter/SKILL.md
@@ -1,6 +1,11 @@
 ---
 name: webshop-query-interpreter
-description: This skill interprets a user's shopping query to extract key product requirements such as item type, attributes, and constraints. It should be triggered when a new shopping instruction is received, parsing natural language into structured criteria (e.g., product category, desired features, price limits). The output is a clear set of search parameters for use in subsequent product lookup steps.
+description: >-
+  Interprets a user's shopping query to extract key product requirements such as item type,
+  attributes, and constraints. Use when a new shopping instruction is received and you need
+  to parse natural language into structured criteria (product category, desired features,
+  price limits) before performing a search. The output is a clear set of search parameters
+  for use in subsequent product lookup steps.
 ---
 # Instructions
 
@@ -15,4 +20,41 @@ Activate this skill when a new shopping instruction is received from the user. T
     *   **Constraints:** Hard limits, especially price (e.g., "price lower than 40.00 dollars").
 
 2.  **Structure the Output:** Format the extracted information into a clear, structured set of search parameters. Use the following template:
+
+    ```
+    Product Type: <primary item>
+    Attributes: <comma-separated features>
+    Constraints: <price limits or other hard requirements>
+    Search Query: <recommended search string>
+    ```
+
+3.  **Hand Off:** Pass the structured parameters to the search execution skill (e.g., `webshop-search-executor` or `webshop-product-search`) to perform the actual query.
+
+## Example
+
+**Instruction:** "i need a long clip-in hair extension which is natural looking, and price lower than 40.00 dollars"
+
+**Thought:** The user wants a hair extension. Key attributes are "long", "clip-in", and "natural looking". The hard constraint is price under $40.00.
+
+**Structured Output:**
+```
+Product Type: clip-in hair extension
+Attributes: long, natural looking
+Constraints: price < $40.00
+Search Query: long clip-in natural looking hair extension
+```
+
+---
+
+**Instruction:** "i want a pack of 6 moisturizing body wash bars with shea butter, price less than 20 dollars"
+
+**Thought:** The user wants body wash bars. Key attributes are "moisturizing", "shea butter", quantity "6 pack". Hard constraint is price under $20.00.
+
+**Structured Output:**
+```
+Product Type: body wash bars
+Attributes: moisturizing, shea butter, 6 pack
+Constraints: price < $20.00
+Search Query: moisturizing body wash bars shea butter 6 pack
+```
     
\ No newline at end of file
diff --git a/experiments/src/skills/webshop/webshop-result-filter/SKILL.md b/experiments/src/skills/webshop/webshop-result-filter/SKILL.md
@@ -1,6 +1,11 @@
 ---
 name: webshop-result-filter
-description: This skill filters search results by evaluating product listings against specific user constraints like price, features, or ratings. It should be triggered when reviewing a page of search results to identify items that match all given criteria. The skill takes a list of products with their details and outputs a subset that meets the defined requirements for closer inspection.
+description: >-
+  Filters search results by evaluating product listings against specific user constraints
+  like price, features, or ratings. Use when you are on a search results page and need to
+  systematically identify which products meet all given criteria before selecting one for
+  closer inspection. Takes a list of products with their details and outputs a filtered
+  subset that meets the defined requirements.
 ---
 # Skill: webshop-result-filter
 
@@ -13,18 +18,18 @@ Activate this skill when you are on a search results page in a web shopping envi
     *   **Features:** Specific attributes or keywords (e.g., `natural looking`, `long`, `clip-in`).
     *   **Ratings:** A minimum rating threshold (if available in the observation).
 
-2.  **Parse the Observation:** Extract the list of products from the search results page. Each product listing typically contains:
-    *   A Product ID/ASIN (e.g., `B09C337K8S`).
-    *   A Title/Description.
-    *   A Price.
-    *   A Rating (if available).
+2.  **Validate Constraints:** Confirm you have at least one constraint extracted before proceeding. If the instruction contains no filterable criteria, skip filtering and select the first available product.
 
-3.  **Apply Filters:** For each product in the list, check it against **all** extracted user constraints.
-    *   **Price Filter:** Compare the product's price to the user's maximum price. Convert prices to numerical values for comparison.
-    *   **Keyword/Feature Filter:** Check if the product's title/description contains keywords related to the required features (e.g., "natural").
-    *   **Rating Filter:** If a rating constraint exists and the product has a rating, ensure it meets the minimum.
+3.  **Parse the Observation:** Extract the list of products from the search results page (Product ID, Title, Price, Rating if available).
 
-4.  **Output Decision:** Identify the **first product** in the filtered list that passes all criteria. This becomes the primary candidate for the next action (`click[product_id]`). If no product passes all filters, you may need to refine the search.
+4.  **Apply Filters:** For each product, check it against **all** extracted constraints:
+    *   **Price Filter:** Is the product price strictly below the user's maximum?
+    *   **Keyword/Feature Filter:** Does the title/description contain the required feature keywords?
+    *   **Rating Filter:** If a rating constraint exists, does the product meet the minimum?
+
+5.  **Output Decision:** Select the **first product** that passes all criteria as the primary candidate for `click[product_id]`. If no product passes:
+    *   Try `click[Next >]` to check additional result pages.
+    *   If no more pages, use `search[refined keywords]` with adjusted terms.
 
 ## Example from Trajectory
 *   **User Instruction:** `i need a long clip-in hair extension which is natural looking, and price lower than 40.00 dollars`
@@ -39,6 +44,7 @@ Activate this skill when you are on a search results page in a web shopping envi
 *   **Result:** `B09C337K8S` is selected as the top matching candidate.
 
 ## Next Action
-After identifying a matching product, the recommended action is to click on it for more details: `click[<matching_product_id>]`.
+After identifying a matching product, click on it for more details:
 
-For complex filtering logic or to process large result sets, use the bundled script.
+**Thought:** [Summarize which constraints each product passed or failed, justify your selection.]
+**Action:** `click[<matching_product_id>]`
diff --git a/experiments/src/skills/webshop/webshop-search-executor/SKILL.md b/experiments/src/skills/webshop/webshop-search-executor/SKILL.md
@@ -1,14 +1,45 @@
 ---
 name: webshop-search-executor
-description: Executes a search on an e-commerce platform using parsed keywords. Trigger when you need to find products matching specific criteria from a user query. This skill takes structured search terms and performs a search action, returning a list of product results for evaluation.
+description: >-
+  Executes a search on an e-commerce platform using parsed keywords. Use when you have
+  extracted search terms from a user query and need to perform the actual search[] action
+  on the WebShop interface. Takes structured search terms and performs a search action,
+  returning a list of product results for evaluation.
 ---
 # Instructions
 
-## Core Function
-When triggered, this skill executes a product search on a simulated e-commerce platform (WebShop). Your primary goal is to translate a user's product request into an effective search query, execute it, and return the parsed results for further action.
-
 ## 1. Trigger Condition
-Activate this skill when the user provides an instruction to find or buy a product with specific attributes (e.g., ingredients, price range, features). The instruction will be provided in the `Observation`.
+Activate when the user provides an instruction to find or buy a product with specific attributes. The instruction will be in the `Observation`.
+
+## Edge Cases
+*   If the search returns 0 results, retry with a broader query (e.g., drop the least critical attribute).
+*   If all results exceed the user's price constraint, try adding price-related terms or narrowing the product category.
 
 ## 2. Action Protocol
 You must respond using **only** the following two action formats. Your final response must be in the exact structure:
+
+**Thought:** [Your reasoning about the search terms to use based on the user's requirements.]
+**Action:** `search[<keywords>]`
+
+Or, if selecting a product from results:
+
+**Thought:** [Your reasoning about which product best matches.]
+**Action:** `click[<product_id>]`
+
+## 3. Example
+
+**Instruction:** "i need a long clip-in hair extension which is natural looking, and price lower than 40.00 dollars"
+
+**Observation:** WebShop search page is displayed with a search bar.
+
+**Thought:** The user needs a clip-in hair extension that is long and natural looking, under $40. I will search for the core product type with key attributes to get relevant results.
+**Action:** `search[long natural looking clip-in hair extension]`
+
+---
+
+**Instruction:** "i want a pack of organic green tea bags, price lower than 10.00 dollars"
+
+**Observation:** WebShop search page is displayed with a search bar.
+
+**Thought:** The user wants organic green tea bags under $10. I will search with the key product terms.
+**Action:** `search[organic green tea bags]`
PATCH

echo "Gold patch applied."
