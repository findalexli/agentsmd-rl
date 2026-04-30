"""Behavioral checks for skillnet-improveskill-review-optimization (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skillnet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-appliance-navigator/SKILL.md')
    assert 'description: Navigates the agent to a target appliance (microwave, stove, fridge, or sinkbasin) needed for object processing. Use when you are holding an object that needs heating, cooling, or cleanin' in text, "expected to find: " + 'description: Navigates the agent to a target appliance (microwave, stove, fridge, or sinkbasin) needed for object processing. Use when you are holding an object that needs heating, cooling, or cleanin'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-appliance-navigator/SKILL.md')
    assert '4. **Prepare Appliance (if needed):** Upon arrival, check if the appliance requires preparation (e.g., opening a closed microwave or fridge door). If so, perform `open {appliance}` before proceeding.' in text, "expected to find: " + '4. **Prepare Appliance (if needed):** Upon arrival, check if the appliance requires preparation (e.g., opening a closed microwave or fridge door). If so, perform `open {appliance}` before proceeding.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-appliance-navigator/SKILL.md')
    assert '1. **Identify the Target Appliance:** Determine which appliance is required for the task. Map the action to the appliance: `heat` -> microwave/stoveburner, `cool` -> fridge, `clean` -> sinkbasin.' in text, "expected to find: " + '1. **Identify the Target Appliance:** Determine which appliance is required for the task. Map the action to the appliance: `heat` -> microwave/stoveburner, `cool` -> fridge, `clean` -> sinkbasin.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-appliance-preparer/SKILL.md')
    assert 'description: Prepares a household appliance (microwave, oven, toaster, fridge) for use by ensuring it is in the correct open/closed state. Use when the agent needs to heat, cool, or cook an item and m' in text, "expected to find: " + 'description: Prepares a household appliance (microwave, oven, toaster, fridge) for use by ensuring it is in the correct open/closed state. Use when the agent needs to heat, cool, or cook an item and m'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-appliance-preparer/SKILL.md')
    assert '1. `go to microwave 1` → Observation: "You are at microwave 1. The microwave 1 is closed."' in text, "expected to find: " + '1. `go to microwave 1` → Observation: "You are at microwave 1. The microwave 1 is closed."'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-appliance-preparer/SKILL.md')
    assert '2. `open microwave 1` → Observation: "You open the microwave 1. The microwave 1 is open."' in text, "expected to find: " + '2. `open microwave 1` → Observation: "You open the microwave 1. The microwave 1 is open."'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-clean-object/SKILL.md')
    assert 'description: Cleans a specified object using an appropriate cleaning receptacle (e.g., sinkbasin). Use when a task requires an object to be in a clean state (e.g., "clean potato", "wash apple") before' in text, "expected to find: " + 'description: Cleans a specified object using an appropriate cleaning receptacle (e.g., sinkbasin). Use when a task requires an object to be in a clean state (e.g., "clean potato", "wash apple") before'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-clean-object/SKILL.md')
    assert 'After successful execution, the object will be in a clean state. You may proceed with the next step of your task (e.g., placing the clean object on a shelf or in a microwave).' in text, "expected to find: " + 'After successful execution, the object will be in a clean state. You may proceed with the next step of your task (e.g., placing the clean object on a shelf or in a microwave).'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-clean-object/SKILL.md')
    assert '- "Nothing happened": Check (1) you are holding the object, (2) you are at the sinkbasin, (3) object and receptacle names are correct' in text, "expected to find: " + '- "Nothing happened": Check (1) you are holding the object, (2) you are at the sinkbasin, (3) object and receptacle names are correct'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-device-operator/SKILL.md')
    assert 'description: Operates a device or appliance (like a desklamp, microwave, or fridge) to interact with another object. Use when the task requires using a tool on a target item (e.g., "look at laptop und' in text, "expected to find: " + 'description: Operates a device or appliance (like a desklamp, microwave, or fridge) to interact with another object. Use when the task requires using a tool on a target item (e.g., "look at laptop und'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-device-operator/SKILL.md')
    assert '**Result:** The laptop is now being examined under the desklamp, completing the task.' in text, "expected to find: " + '**Result:** The laptop is now being examined under the desklamp, completing the task.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-device-operator/SKILL.md')
    assert "Thought: I need to find the desklamp first. It's likely on a sidetable or desk." in text, "expected to find: " + "Thought: I need to find the desklamp first. It's likely on a sidetable or desk."[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-environment-scanner/SKILL.md')
    assert 'description: Performs an initial scan of the ALFWorld environment to identify all visible objects and receptacles. Use when you first enter an environment and need to build a mental map for task plann' in text, "expected to find: " + 'description: Performs an initial scan of the ALFWorld environment to identify all visible objects and receptacles. Use when you first enter an environment and need to build a mental map for task plann'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-heat-object-with-appliance/SKILL.md')
    assert 'description: Uses a heating appliance (microwave, stoveburner, oven) to apply heat to a specified object. Use when the task requires warming or cooking an item (e.g., "heat some egg", "warm the mug") ' in text, "expected to find: " + 'description: Uses a heating appliance (microwave, stoveburner, oven) to apply heat to a specified object. Use when the task requires warming or cooking an item (e.g., "heat some egg", "warm the mug") '[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-heat-object-with-appliance/SKILL.md')
    assert '7. `put egg 1 in/on diningtable 1` → Observation: "You put the egg 1 in/on the diningtable 1."' in text, "expected to find: " + '7. `put egg 1 in/on diningtable 1` → Observation: "You put the egg 1 in/on the diningtable 1."'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-heat-object-with-appliance/SKILL.md')
    assert '5. `heat egg 1 with microwave 1` → Observation: "You heat the egg 1 using the microwave 1."' in text, "expected to find: " + '5. `heat egg 1 with microwave 1` → Observation: "You heat the egg 1 using the microwave 1."'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-inventory-management/SKILL.md')
    assert 'description: Use when the agent must collect and track multiple instances of the same object type in ALFWorld (e.g., "put two cellphone in bed"). This skill maintains a count of collected versus neede' in text, "expected to find: " + 'description: Use when the agent must collect and track multiple instances of the same object type in ALFWorld (e.g., "put two cellphone in bed"). This skill maintains a count of collected versus neede'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-inventory-management/SKILL.md')
    assert '**Critical Rule:** After finding an object, immediately place it at the target location before searching for the next one. Do not attempt to carry multiple objects simultaneously.' in text, "expected to find: " + '**Critical Rule:** After finding an object, immediately place it at the target location before searching for the next one. Do not attempt to carry multiple objects simultaneously.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-inventory-management/SKILL.md')
    assert '- **Counter mismatch**: Re-examine the target receptacle to confirm how many objects are already placed' in text, "expected to find: " + '- **Counter mismatch**: Re-examine the target receptacle to confirm how many objects are already placed'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-locate-target-object/SKILL.md')
    assert 'description: Navigates to a suspected location and identifies a target object. Use when your goal requires finding a specific object (e.g., "potato", "plate") and its location is not immediately known' in text, "expected to find: " + 'description: Navigates to a suspected location and identifies a target object. Use when your goal requires finding a specific object (e.g., "potato", "plate") and its location is not immediately known'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-locate-target-object/SKILL.md')
    assert '**Result:** The potato has been located in `fridge 1`. You can now `take potato 1 from fridge 1` and proceed.' in text, "expected to find: " + '**Result:** The potato has been located in `fridge 1`. You can now `take potato 1 from fridge 1` and proceed.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-locate-target-object/SKILL.md')
    assert 'Observation: You open the fridge 1. The fridge 1 is open. In it, you see a potato 1, a lettuce 2.' in text, "expected to find: " + 'Observation: You open the fridge 1. The fridge 1 is open. In it, you see a potato 1, a lettuce 2.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-cooler/SKILL.md')
    assert 'description: Cools a held object using an appropriate cooling appliance such as a fridge or freezer. Use when the task requires reducing the temperature of an object (e.g., "cool some pot", "chill the' in text, "expected to find: " + 'description: Cools a held object using an appropriate cooling appliance such as a fridge or freezer. Use when the task requires reducing the temperature of an object (e.g., "cool some pot", "chill the'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-heater/SKILL.md')
    assert 'description: Heats a specified object using an available heating appliance (e.g., microwave, stoveburner). Use when you are holding an object that requires heating and need to navigate to and operate ' in text, "expected to find: " + 'description: Heats a specified object using an available heating appliance (e.g., microwave, stoveburner). Use when you are holding an object that requires heating and need to navigate to and operate '[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-heater/SKILL.md')
    assert '2. **Check state:** If observation says appliance is closed, execute `open {appliance}` -- verify observation confirms it is now open' in text, "expected to find: " + '2. **Check state:** If observation says appliance is closed, execute `open {appliance}` -- verify observation confirms it is now open'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-heater/SKILL.md')
    assert '- "Nothing happened" on heat: Check (1) you are holding the object, (2) appliance is open, (3) appliance name is correct' in text, "expected to find: " + '- "Nothing happened" on heat: Check (1) you are holding the object, (2) appliance is open, (3) appliance name is correct'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-locator/SKILL.md')
    assert 'description: Use when the agent needs to find a specific object in ALFWorld that is not currently in inventory and whose location is unknown. This skill parses the environment observation, ranks recep' in text, "expected to find: " + 'description: Use when the agent needs to find a specific object in ALFWorld that is not currently in inventory and whose location is unknown. This skill parses the environment observation, ranks recep'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-locator/SKILL.md')
    assert '**Observation:** "You are in the middle of a room. Looking quickly around you, you see a countertop 1, a drawer 1, a drawer 2, a fridge 1, a sinkbasin 1, a stoveburner 1."' in text, "expected to find: " + '**Observation:** "You are in the middle of a room. Looking quickly around you, you see a countertop 1, a drawer 1, a drawer 2, a fridge 1, a sinkbasin 1, a stoveburner 1."'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-locator/SKILL.md')
    assert 'Maintain a list of already-searched receptacles to avoid revisiting them. If all high-probability locations are exhausted, expand the search to remaining receptacles.' in text, "expected to find: " + 'Maintain a list of already-searched receptacles to avoid revisiting them. If all high-probability locations are exhausted, expand the search to remaining receptacles.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-state-inspector/SKILL.md')
    assert 'description: Inspects a receptacle\'s contents by navigating to it and reading the observation. Use when you need to check what is on or inside a receptacle (e.g., "what\'s on the shelf", "is the holder' in text, "expected to find: " + 'description: Inspects a receptacle\'s contents by navigating to it and reading the observation. Use when you need to check what is on or inside a receptacle (e.g., "what\'s on the shelf", "is the holder'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-state-inspector/SKILL.md')
    assert '2. **Read observation:** The environment automatically reports what is on/in the receptacle -- no additional inspection action is needed' in text, "expected to find: " + '2. **Read observation:** The environment automatically reports what is on/in the receptacle -- no additional inspection action is needed'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-state-inspector/SKILL.md')
    assert "Inspect the state or contents of a target receptacle by navigating to it and parsing the environment's observation feedback." in text, "expected to find: " + "Inspect the state or contents of a target receptacle by navigating to it and parsing the environment's observation feedback."[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-state-modifier/SKILL.md')
    assert "description: Uses an appliance to change the state of an object (cooling, heating, or cleaning). Use when the task requires altering an object's temperature or cleanliness using a specific device (e.g" in text, "expected to find: " + "description: Uses an appliance to change the state of an object (cooling, heating, or cleaning). Use when the task requires altering an object's temperature or cleanliness using a specific device (e.g"[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-state-modifier/SKILL.md')
    assert "Change an object's state (cool, heat, or clean) using a household appliance. You must be holding the target object before executing the state change." in text, "expected to find: " + "Change an object's state (cool, heat, or clean) using a household appliance. You must be holding the target object before executing the state change."[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-state-modifier/SKILL.md')
    assert '- "Nothing happened": Check (1) you are holding the object, (2) appliance is open/ready, (3) object and appliance names are correct' in text, "expected to find: " + '- "Nothing happened": Check (1) you are holding the object, (2) appliance is open/ready, (3) object and appliance names are correct'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-storer/SKILL.md')
    assert 'description: Use when the agent is holding an object and needs to place it into a target receptacle in ALFWorld. This skill checks receptacle suitability, opens closed containers if needed, and execut' in text, "expected to find: " + 'description: Use when the agent is holding an object and needs to place it into a target receptacle in ALFWorld. This skill checks receptacle suitability, opens closed containers if needed, and execut'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-storer/SKILL.md')
    assert '- **"Nothing happened"**: The agent may not be holding the object, or the receptacle name is incorrect. Verify with `inventory` and re-check the receptacle identifier.' in text, "expected to find: " + '- **"Nothing happened"**: The agent may not be holding the object, or the receptacle name is incorrect. Verify with `inventory` and re-check the receptacle identifier.'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-storer/SKILL.md')
    assert '- **Receptacle unsuitable**: If the receptacle is not appropriate for the object, search for an alternative using the object-locator skill.' in text, "expected to find: " + '- **Receptacle unsuitable**: If the receptacle is not appropriate for the object, search for an alternative using the object-locator skill.'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-transporter/SKILL.md')
    assert 'description: Picks up a target object from its current receptacle and moves it to a specified destination receptacle. Use when you have located an object and need to relocate it to complete a task (e.' in text, "expected to find: " + 'description: Picks up a target object from its current receptacle and moves it to a specified destination receptacle. Use when you have located an object and need to relocate it to complete a task (e.'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-transporter/SKILL.md')
    assert '- "Nothing happened" on take: verify you are at the correct receptacle and the object name matches the observation' in text, "expected to find: " + '- "Nothing happened" on take: verify you are at the correct receptacle and the object name matches the observation'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-object-transporter/SKILL.md')
    assert '1. **Navigate to source:** `go to {source_receptacle}` -- verify observation shows the target object' in text, "expected to find: " + '1. **Navigate to source:** `go to {source_receptacle}` -- verify observation shows the target object'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-receptacle-closer/SKILL.md')
    assert 'description: Closes an open receptacle to maintain environment tidiness after inspection. Use when you have finished searching a container (drawer, cabinet, fridge) and no longer need it open. Takes a' in text, "expected to find: " + 'description: Closes an open receptacle to maintain environment tidiness after inspection. Use when you have finished searching a container (drawer, cabinet, fridge) and no longer need it open. Takes a'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-receptacle-finder/SKILL.md')
    assert 'description: Searches for a suitable empty or appropriately occupied receptacle (like a shelf or table) to place an object. Use when you are holding an object that needs to be stored or placed and mus' in text, "expected to find: " + 'description: Searches for a suitable empty or appropriately occupied receptacle (like a shelf or table) to place an object. Use when you are holding an object that needs to be stored or placed and mus'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-receptacle-finder/SKILL.md')
    assert 'For a detailed example including handling object pre-cleaning and sequential shelf evaluation, refer to `references/example_trajectory.md`.' in text, "expected to find: " + 'For a detailed example including handling object pre-cleaning and sequential shelf evaluation, refer to `references/example_trajectory.md`.'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-receptacle-finder/SKILL.md')
    assert '**Scenario:** You are holding `soapbar 1` (clean) and need to find an empty shelf to place it.' in text, "expected to find: " + '**Scenario:** You are holding `soapbar 1` (clean) and need to find an empty shelf to place it.'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-receptacle-navigator/SKILL.md')
    assert 'description: Plans and executes movement to a target receptacle within the ALFWorld environment. Use when the agent needs to reach a specific location before interacting with objects there (e.g., go t' in text, "expected to find: " + 'description: Plans and executes movement to a target receptacle within the ALFWorld environment. Use when the agent needs to reach a specific location before interacting with objects there (e.g., go t'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-receptacle-navigator/SKILL.md')
    assert '**Output:** Agent has arrived at fridge 1 and can now interact with it (open, take items, cool objects, etc.).' in text, "expected to find: " + '**Output:** Agent has arrived at fridge 1 and can now interact with it (open, take items, cool objects, etc.).'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-receptacle-navigator/SKILL.md')
    assert '1. `go to fridge 1` → Observation: "You are at fridge 1. On the fridge 1, you see nothing."' in text, "expected to find: " + '1. `go to fridge 1` → Observation: "You are at fridge 1. On the fridge 1, you see nothing."'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-search-pattern-executor/SKILL.md')
    assert 'description: Systematically searches a sequence of likely locations for a target object based on common sense. Use when you need to find a specific object and know which receptacles to check but not w' in text, "expected to find: " + 'description: Systematically searches a sequence of likely locations for a target object based on common sense. Use when you need to find a specific object and know which receptacles to check but not w'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-search-pattern-executor/SKILL.md')
    assert '**Result:** First remotecontrol found and picked up. Proceed to place it in `armchair 1`, then re-activate search for the second one.' in text, "expected to find: " + '**Result:** First remotecontrol found and picked up. Proceed to place it in `armchair 1`, then re-activate search for the second one.'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-search-pattern-executor/SKILL.md')
    assert '5. **If not found:** If you opened the receptacle, execute `close {receptacle}`, then continue to the next candidate' in text, "expected to find: " + '5. **If not found:** If you opened the receptacle, execute `close {receptacle}`, then continue to the next candidate'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-search-verifier/SKILL.md')
    assert 'description: Re-examines previously visited locations to confirm the absence of a target object or to check for overlooked items. Use when an initial search fails to find enough objects or when double' in text, "expected to find: " + 'description: Re-examines previously visited locations to confirm the absence of a target object or to check for overlooked items. Use when an initial search fails to find enough objects or when double'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-search-verifier/SKILL.md')
    assert '**Scenario:** You need two cellphones but only found one. Revisiting previously searched locations.' in text, "expected to find: " + '**Scenario:** You need two cellphones but only found one. Revisiting previously searched locations.'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-search-verifier/SKILL.md')
    assert 'Thought: I only found 1 cellphone but need 2. Let me revisit sidetable 1 which I checked earlier.' in text, "expected to find: " + 'Thought: I only found 1 cellphone but need 2. Let me revisit sidetable 1 which I checked earlier.'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-storage-explorer/SKILL.md')
    assert 'description: Systematically explores storage receptacles (drawers, cabinets, shelves) to find an appropriate placement location for an object. Use when the agent needs to store an item but the exact t' in text, "expected to find: " + 'description: Systematically explores storage receptacles (drawers, cabinets, shelves) to find an appropriate placement location for an object. Use when the agent needs to store an item but the exact t'[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-storage-explorer/SKILL.md')
    assert '2. `open drawer 1` → Observation: "You open the drawer 1. The drawer 1 is open. You see nothing."' in text, "expected to find: " + '2. `open drawer 1` → Observation: "You open the drawer 1. The drawer 1 is open. You see nothing."'[:80]


def test_signal_56():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-storage-explorer/SKILL.md')
    assert '3. `put sponge 1 in/on drawer 1` → Observation: "You put the sponge 1 in/on the drawer 1."' in text, "expected to find: " + '3. `put sponge 1 in/on drawer 1` → Observation: "You put the sponge 1 in/on the drawer 1."'[:80]


def test_signal_57():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-task-verifier/SKILL.md')
    assert 'description: Use when the agent needs to check whether an ALFWorld task objective has been met after completing a sub-action (e.g., placing an object). This skill parses the task goal, evaluates the l' in text, "expected to find: " + 'description: Use when the agent needs to check whether an ALFWorld task objective has been met after completing a sub-action (e.g., placing an object). This skill parses the task goal, evaluates the l'[:80]


def test_signal_58():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-task-verifier/SKILL.md')
    assert '- **Ambiguous observation**: If the observation does not clearly confirm or deny placement, navigate to the target receptacle and re-examine it to get an updated state.' in text, "expected to find: " + '- **Ambiguous observation**: If the observation does not clearly confirm or deny placement, navigate to the target receptacle and re-examine it to get an updated state.'[:80]


def test_signal_59():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-task-verifier/SKILL.md')
    assert '| Object placed in wrong receptacle | Incorrect | `Verification: Object placed in wrong location. Retrieve and redirect to {correct receptacle}.` |' in text, "expected to find: " + '| Object placed in wrong receptacle | Incorrect | `Verification: Object placed in wrong location. Retrieve and redirect to {correct receptacle}.` |'[:80]


def test_signal_60():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-temperature-regulator/SKILL.md')
    assert "description: Manages the temperature state of an object by placing it into an appropriate appliance (fridge for cooling, microwave for heating). Use when the task requires modifying an object's temper" in text, "expected to find: " + "description: Manages the temperature state of an object by placing it into an appropriate appliance (fridge for cooling, microwave for heating). Use when the task requires modifying an object's temper"[:80]


def test_signal_61():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-temperature-regulator/SKILL.md')
    assert '**Input:** `object: bread 1`, `temperature_receptacle: fridge 1`, `target_receptacle: diningtable 1`' in text, "expected to find: " + '**Input:** `object: bread 1`, `temperature_receptacle: fridge 1`, `target_receptacle: diningtable 1`'[:80]


def test_signal_62():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-temperature-regulator/SKILL.md')
    assert '2. `take bread 1 from countertop 1` → Observation: "You pick up the bread 1 from the countertop 1."' in text, "expected to find: " + '2. `take bread 1 from countertop 1` → Observation: "You pick up the bread 1 from the countertop 1."'[:80]


def test_signal_63():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-tool-locator/SKILL.md')
    assert 'description: Searches for a specified tool or device (e.g., a desklamp, knife, or sponge) within the ALFWorld environment by checking relevant surfaces. Use when you need a tool to interact with anoth' in text, "expected to find: " + 'description: Searches for a specified tool or device (e.g., a desklamp, knife, or sponge) within the ALFWorld environment by checking relevant surfaces. Use when you need a tool to interact with anoth'[:80]


def test_signal_64():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-tool-locator/SKILL.md')
    assert '- If tool not found after all likely spots: expand search to every receptacle from the initial environment scan' in text, "expected to find: " + '- If tool not found after all likely spots: expand search to every receptacle from the initial environment scan'[:80]


def test_signal_65():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-tool-locator/SKILL.md')
    assert 'Locate a specified tool or device by systematically checking receptacles where it is likely stored.' in text, "expected to find: " + 'Locate a specified tool or device by systematically checking receptacles where it is likely stored.'[:80]


def test_signal_66():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-tool-user/SKILL.md')
    assert 'description: Use when the agent needs to apply a tool to a target object in ALFWorld to accomplish an interaction such as cleaning, heating, cooling, or examining. This skill handles locating both the' in text, "expected to find: " + 'description: Use when the agent needs to apply a tool to a target object in ALFWorld to accomplish an interaction such as cleaning, heating, cooling, or examining. This skill handles locating both the'[:80]


def test_signal_67():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-tool-user/SKILL.md')
    assert '- **"Nothing happened"**: Reassess whether the agent is at the correct location and holding the correct object. Verify the action verb matches the task context.' in text, "expected to find: " + '- **"Nothing happened"**: Reassess whether the agent is at the correct location and holding the correct object. Verify the action verb matches the task context.'[:80]


def test_signal_68():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/alfworld/alfworld-tool-user/SKILL.md')
    assert '- **Wrong tool**: If the tool does not match the interaction type, search for the correct appliance (e.g., use `sinkbasin` for cleaning, not `bathtub`).' in text, "expected to find: " + '- **Wrong tool**: If the tool does not match the interaction type, search for the correct appliance (e.g., use `sinkbasin` for cleaning, not `bathtub`).'[:80]


def test_signal_69():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-ambiguous-action-resolution/SKILL.md')
    assert 'description: Use when the ScienceWorld environment returns an "Ambiguous request" prompt with a numbered list of identical action options. This skill resolves the disambiguation by selecting the lowes' in text, "expected to find: " + 'description: Use when the ScienceWorld environment returns an "Ambiguous request" prompt with a numbered list of identical action options. This skill resolves the disambiguation by selecting the lowes'[:80]


def test_signal_70():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-ambiguous-action-resolution/SKILL.md')
    assert 'Resolve system disambiguation prompts that block task progression when the ScienceWorld environment cannot determine which identical object instance the agent intends to act upon. This is a mechanical' in text, "expected to find: " + 'Resolve system disambiguation prompts that block task progression when the ScienceWorld environment cannot determine which identical object instance the agent intends to act upon. This is a mechanical'[:80]


def test_signal_71():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-ambiguous-action-resolution/SKILL.md')
    assert '- When the environment returns an observation containing `"Ambiguous request: Please enter the number for the action you intended (or blank to cancel):"` followed by a numbered list' in text, "expected to find: " + '- When the environment returns an observation containing `"Ambiguous request: Please enter the number for the action you intended (or blank to cancel):"` followed by a numbered list'[:80]


def test_signal_72():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-animal-identifier/SKILL.md')
    assert 'description: Use when the agent needs to locate, identify, and focus on a specific animal or biological entity in the ScienceWorld environment. This skill handles tasks involving animal comparison, ex' in text, "expected to find: " + 'description: Use when the agent needs to locate, identify, and focus on a specific animal or biological entity in the ScienceWorld environment. This skill handles tasks involving animal comparison, ex'[:80]


def test_signal_73():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-animal-identifier/SKILL.md')
    assert 'Locate and focus on a specified animal or biological entity within the ScienceWorld environment for tasks involving animal comparison, examination, or interaction (e.g., determining lifespan extremes,' in text, "expected to find: " + 'Locate and focus on a specified animal or biological entity within the ScienceWorld environment for tasks involving animal comparison, examination, or interaction (e.g., determining lifespan extremes,'[:80]


def test_signal_74():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-animal-identifier/SKILL.md')
    assert '- **Exact names** -- The `focus on` action requires the precise object name as it appears in `look around` (e.g., `"baby dragonfly"`, not just `"dragonfly"`).' in text, "expected to find: " + '- **Exact names** -- The `focus on` action requires the precise object name as it appears in `look around` (e.g., `"baby dragonfly"`, not just `"dragonfly"`).'[:80]


def test_signal_75():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-circuit-builder/SKILL.md')
    assert 'description: This skill constructs a simple electrical circuit by connecting components like batteries, wires, and light bulbs. Use when the agent needs to test electrical conductivity or create a fun' in text, "expected to find: " + 'description: This skill constructs a simple electrical circuit by connecting components like batteries, wires, and light bulbs. Use when the agent needs to test electrical conductivity or create a fun'[:80]


def test_signal_76():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-circuit-builder/SKILL.md')
    assert '10. Light bulb is on → `move metal pot to blue box` (conductive)' in text, "expected to find: " + '10. Light bulb is on → `move metal pot to blue box` (conductive)'[:80]


def test_signal_77():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-circuit-builder/SKILL.md')
    assert '**Task:** Test whether a metal pot is electrically conductive.' in text, "expected to find: " + '**Task:** Test whether a metal pot is electrically conductive.'[:80]


def test_signal_78():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-circuit-connector/SKILL.md')
    assert 'description: This skill connects two electrical components (e.g., wires, batteries, devices) by their terminals to build or modify a circuit. Use when constructing electrical setups for testing, such ' in text, "expected to find: " + 'description: This skill connects two electrical components (e.g., wires, batteries, devices) by their terminals to build or modify a circuit. Use when constructing electrical setups for testing, such '[:80]


def test_signal_79():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-conditional-focus-executor/SKILL.md')
    assert "description: Executes a 'focus on OBJ' action on a specific object based on the outcome of a prior conditional evaluation. Use when you have a measurement result and task instructions specify focusing" in text, "expected to find: " + "description: Executes a 'focus on OBJ' action on a specific object based on the outcome of a prior conditional evaluation. Use when you have a measurement result and task instructions specify focusing"[:80]


def test_signal_80():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-conditional-focus-executor/SKILL.md')
    assert 'Use after completing a measurement (temperature, pH, mass) when the task specifies a conditional rule like "If result > X, focus on A; otherwise, focus on B."' in text, "expected to find: " + 'Use after completing a measurement (temperature, pH, mass) when the task specifies a conditional rule like "If result > X, focus on A; otherwise, focus on B."'[:80]


def test_signal_81():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-conditional-focus-executor/SKILL.md')
    assert 'If the focus action fails (e.g., object not found), use `look around` to verify the target object name matches exactly.' in text, "expected to find: " + 'If the focus action fails (e.g., object not found), use `look around` to verify the target object name matches exactly.'[:80]


def test_signal_82():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-conditional-placer/SKILL.md')
    assert 'description: Places an object into one of several designated containers based on a measured condition, such as a temperature threshold. Use this skill when you have completed a measurement or assessme' in text, "expected to find: " + 'description: Places an object into one of several designated containers based on a measured condition, such as a temperature threshold. Use this skill when you have completed a measurement or assessme'[:80]


def test_signal_83():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-conditional-placer/SKILL.md')
    assert 'Place a target object into the correct container based on a measured condition (e.g., temperature threshold, conductivity result). This skill executes the full measure-then-sort workflow.' in text, "expected to find: " + 'Place a target object into the correct container based on a measured condition (e.g., temperature threshold, conductivity result). This skill executes the full measure-then-sort workflow.'[:80]


def test_signal_84():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-conditional-placer/SKILL.md')
    assert '5. **Evaluate Condition & Place:** Compare the measured value against the threshold, then `move OBJ to OBJ` to place the object in the correct container.' in text, "expected to find: " + '5. **Evaluate Condition & Place:** Compare the measured value against the threshold, then `move OBJ to OBJ` to place the object in the correct container.'[:80]


def test_signal_85():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-container-inspector/SKILL.md')
    assert "description: Inspects the contents of a container or device using the 'look at' action. Use this skill when you need to verify what is inside a container (e.g., checking if lead is in the blast furnac" in text, "expected to find: " + "description: Inspects the contents of a container or device using the 'look at' action. Use this skill when you need to verify what is inside a container (e.g., checking if lead is in the blast furnac"[:80]


def test_signal_86():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-container-item-retriever/SKILL.md')
    assert '3. Expected observation: "You move the avocado seed to the inventory."' in text, "expected to find: " + '3. Expected observation: "You move the avocado seed to the inventory."'[:80]


def test_signal_87():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-container-item-retriever/SKILL.md')
    assert '1. `look around` — observe: "a jar (containing an avocado seed)"' in text, "expected to find: " + '1. `look around` — observe: "a jar (containing an avocado seed)"'[:80]


def test_signal_88():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-container-item-retriever/SKILL.md')
    assert '**Task:** Retrieve an avocado seed from a jar for planting.' in text, "expected to find: " + '**Task:** Retrieve an avocado seed from a jar for planting.'[:80]


def test_signal_89():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-container-relocator/SKILL.md')
    assert "description: Moves an object from inventory to a specified container in a target room. Use when the task requires placing an item into a particular receptacle (e.g., 'move it to the orange box')." in text, "expected to find: " + "description: Moves an object from inventory to a specified container in a target room. Use when the task requires placing an item into a particular receptacle (e.g., 'move it to the orange box')."[:80]


def test_signal_90():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-container-relocator/SKILL.md')
    assert '2. `teleport to <ROOM>` — navigate to the room containing the target container.' in text, "expected to find: " + '2. `teleport to <ROOM>` — navigate to the room containing the target container.'[:80]


def test_signal_91():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-container-relocator/SKILL.md')
    assert '3. `move <OBJECT> to <CONTAINER>` — transfer the object to the destination.' in text, "expected to find: " + '3. `move <OBJECT> to <CONTAINER>` — transfer the object to the destination.'[:80]


def test_signal_92():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-container-transfer/SKILL.md')
    assert 'description: Moves a substance or object from one container to another (e.g., moving lead to a metal pot). Use this skill when you need to prepare materials for processing, such as transferring a subs' in text, "expected to find: " + 'description: Moves a substance or object from one container to another (e.g., moving lead to a metal pot). Use this skill when you need to prepare materials for processing, such as transferring a subs'[:80]


def test_signal_93():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-container-transfer/SKILL.md')
    assert 'Transfer a target substance or object from a source container to a destination container. This is a foundational step for preparing materials for heating, mixing, or measurement.' in text, "expected to find: " + 'Transfer a target substance or object from a source container to a destination container. This is a foundational step for preparing materials for heating, mixing, or measurement.'[:80]


def test_signal_94():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-container-transfer/SKILL.md')
    assert '1. **Assess Need:** Determine if the current container is unsuitable for the next operation (e.g., tin cup is not heat-resistant for a furnace).' in text, "expected to find: " + '1. **Assess Need:** Determine if the current container is unsuitable for the next operation (e.g., tin cup is not heat-resistant for a furnace).'[:80]


def test_signal_95():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-controlled-waiting/SKILL.md')
    assert "description: Executes timed waiting using 'wait' or 'wait1' actions to advance the simulation clock. Use when a time-dependent process like plant growth, chemical reaction, or mechanical cycle must pr" in text, "expected to find: " + "description: Executes timed waiting using 'wait' or 'wait1' actions to advance the simulation clock. Use when a time-dependent process like plant growth, chemical reaction, or mechanical cycle must pr"[:80]


def test_signal_96():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-controlled-waiting/SKILL.md')
    assert '**Duration guidance:** Use `wait` for biological growth stages. Use `wait1` when observing rapid changes or when close to the expected transition.' in text, "expected to find: " + '**Duration guidance:** Use `wait` for biological growth stages. Use `wait1` when observing rapid changes or when close to the expected transition.'[:80]


def test_signal_97():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-controlled-waiting/SKILL.md')
    assert '2. `wait` (advances 10 steps) for long processes, or `wait1` (1 step) for fine-grained observation.' in text, "expected to find: " + '2. `wait` (advances 10 steps) for long processes, or `wait1` (1 step) for fine-grained observation.'[:80]


def test_signal_98():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-device-activator/SKILL.md')
    assert 'description: Activates a device (e.g., blast furnace, stove) to initiate a process like heating. Use this skill when you have placed materials inside a device and need to start its operation. Takes a ' in text, "expected to find: " + 'description: Activates a device (e.g., blast furnace, stove) to initiate a process like heating. Use this skill when you have placed materials inside a device and need to start its operation. Takes a '[:80]


def test_signal_99():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-device-activator/SKILL.md')
    assert 'Activate a device (turn it on, start it, fire it up) to begin its operation — typically heating, processing, or powering a task step.' in text, "expected to find: " + 'Activate a device (turn it on, start it, fire it up) to begin its operation — typically heating, processing, or powering a task step.'[:80]


def test_signal_100():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-device-activator/SKILL.md')
    assert '5. **Monitor (if needed):** Use measurement tools (e.g., `use thermometer on <MATERIAL>`) to track progress.' in text, "expected to find: " + '5. **Monitor (if needed):** Use measurement tools (e.g., `use thermometer on <MATERIAL>`) to track progress.'[:80]


def test_signal_101():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-environment-isolation/SKILL.md')
    assert 'description: Use when you need to isolate a space (like a greenhouse) by closing doors or openings to create a contained environment. Trigger before starting pollination, temperature-sensitive experim' in text, "expected to find: " + 'description: Use when you need to isolate a space (like a greenhouse) by closing doors or openings to create a contained environment. Trigger before starting pollination, temperature-sensitive experim'[:80]


def test_signal_102():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-environment-isolation/SKILL.md')
    assert '6. Release the bee by running `open bee jar`. The bee cannot escape and will pollinate both plants.' in text, "expected to find: " + '6. Release the bee by running `open bee jar`. The bee cannot escape and will pollinate both plants.'[:80]


def test_signal_103():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-environment-isolation/SKILL.md')
    assert '5. Run `look around` — confirm both doors now show as closed. The greenhouse is fully isolated.' in text, "expected to find: " + '5. Run `look around` — confirm both doors now show as closed. The greenhouse is fully isolated.'[:80]


def test_signal_104():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-growth-focuser/SKILL.md')
    assert "description: Use when you have planted a seed or need to track a plant's growth stage (sprouting, flowering, reproduction). Applies the 'focus on' action to a specific plant or biological entity to si" in text, "expected to find: " + "description: Use when you have planted a seed or need to track a plant's growth stage (sprouting, flowering, reproduction). Applies the 'focus on' action to a specific plant or biological entity to si"[:80]


def test_signal_105():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-growth-focuser/SKILL.md')
    assert '5. Continue alternating `focus on` and `wait` until the plant reaches the desired life stage (sprout, mature plant, flowering, reproduction).' in text, "expected to find: " + '5. Continue alternating `focus on` and `wait` until the plant reaches the desired life stage (sprout, mature plant, flowering, reproduction).'[:80]


def test_signal_106():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-growth-focuser/SKILL.md')
    assert '4. Run `focus on avocado seed in flower pot 1` again — output may now show: "avocado sprout" indicating growth progression.' in text, "expected to find: " + '4. Run `focus on avocado seed in flower pot 1` again — output may now show: "avocado sprout" indicating growth progression.'[:80]


def test_signal_107():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-instruction-reader/SKILL.md')
    assert "description: Reads a recipe or note from the inventory using the 'read' action and extracts key information. Use this skill when you have acquired a recipe, note, or readable document in your inventor" in text, "expected to find: " + "description: Reads a recipe or note from the inventory using the 'read' action and extracts key information. Use this skill when you have acquired a recipe, note, or readable document in your inventor"[:80]


def test_signal_108():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-instruction-reader/SKILL.md')
    assert 'Read and parse a document (recipe, note, or instructions) from your inventory to extract the information needed to execute the current task.' in text, "expected to find: " + 'Read and parse a document (recipe, note, or instructions) from your inventory to extract the information needed to execute the current task.'[:80]


def test_signal_109():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-instruction-reader/SKILL.md')
    assert '3. **Plan Next Actions:** Use the extracted information to determine which skills and actions to invoke next.' in text, "expected to find: " + '3. **Plan Next Actions:** Use the extracted information to determine which skills and actions to invoke next.'[:80]


def test_signal_110():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-inventory-focus/SKILL.md')
    assert 'description: Use when the agent needs to confirm and prepare a specific inventory item before using it in an experiment or task step. This "focus on [ITEM] in inventory" action verifies the correct it' in text, "expected to find: " + 'description: Use when the agent needs to confirm and prepare a specific inventory item before using it in an experiment or task step. This "focus on [ITEM] in inventory" action verifies the correct it'[:80]


def test_signal_111():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-inventory-focus/SKILL.md')
    assert "Confirm and prepare an inventory item before using it in a ScienceWorld task. The `focus on [ITEM] in inventory` action verifies the item's presence and signals intent, reducing errors in multi-step e" in text, "expected to find: " + "Confirm and prepare an inventory item before using it in a ScienceWorld task. The `focus on [ITEM] in inventory` action verifies the item's presence and signals intent, reducing errors in multi-step e"[:80]


def test_signal_112():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-inventory-focus/SKILL.md')
    assert "- The `focus on` action does not change the object's state; it is a declarative checkpoint that changes the agent's awareness and intent." in text, "expected to find: " + "- The `focus on` action does not change the object's state; it is a declarative checkpoint that changes the agent's awareness and intent."[:80]


def test_signal_113():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-inventory-manager/SKILL.md')
    assert "description: Handles picking up objects from the environment into the agent's inventory or moving them out to containers. Use this skill when you need to acquire an object for later use (pick up) or p" in text, "expected to find: " + "description: Handles picking up objects from the environment into the agent's inventory or moving them out to containers. Use this skill when you need to acquire an object for later use (pick up) or p"[:80]


def test_signal_114():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-inventory-manager/SKILL.md')
    assert '* Some objects include state descriptions in their name (e.g., "metal pot containing nothing"). Use the full name as shown in the environment.' in text, "expected to find: " + '* Some objects include state descriptions in their name (e.g., "metal pot containing nothing"). Use the full name as shown in the environment.'[:80]


def test_signal_115():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-inventory-manager/SKILL.md')
    assert '4. **Verify:** Check the observation feedback to confirm the action succeeded. If it fails, verify exact object names with `look around`.' in text, "expected to find: " + '4. **Verify:** Check the observation feedback to confirm the action succeeded. If it fails, verify exact object names with `look around`.'[:80]


def test_signal_116():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-item-fetcher/SKILL.md')
    assert "description: Picks up a specified object from the environment and moves it into the agent's inventory. Use this skill when you identify a required tool or material (e.g., thermometer, metal pot) that " in text, "expected to find: " + "description: Picks up a specified object from the environment and moves it into the agent's inventory. Use this skill when you identify a required tool or material (e.g., thermometer, metal pot) that "[:80]


def test_signal_117():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-liquid-pourer/SKILL.md')
    assert 'description: Transfers the contents of a source liquid container into a target container for mixing or preparation. Use this skill when you need to combine multiple substances (such as paints or chemi' in text, "expected to find: " + 'description: Transfers the contents of a source liquid container into a target container for mixing or preparation. Use this skill when you need to combine multiple substances (such as paints or chemi'[:80]


def test_signal_118():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-liquid-pourer/SKILL.md')
    assert '1. **Identify Containers:** Use `look around` to locate the source container (with the liquid) and the target container (destination vessel).' in text, "expected to find: " + '1. **Identify Containers:** Use `look around` to locate the source container (with the liquid) and the target container (destination vessel).'[:80]


def test_signal_119():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-liquid-pourer/SKILL.md')
    assert '* Object identifiers must be precise (e.g., `wood cup (containing red paint)`). Use `look around` or `examine` to confirm exact names.' in text, "expected to find: " + '* Object identifiers must be precise (e.g., `wood cup (containing red paint)`). Use `look around` or `examine` to confirm exact names.'[:80]


def test_signal_120():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-living-entity-identifier/SKILL.md')
    assert 'description: Analyzes room observations to identify potential living things (e.g., eggs, plants, animals) among listed objects. Use this skill when a task involves finding, focusing on, or interacting' in text, "expected to find: " + 'description: Analyzes room observations to identify potential living things (e.g., eggs, plants, animals) among listed objects. Use this skill when a task involves finding, focusing on, or interacting'[:80]


def test_signal_121():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-living-entity-identifier/SKILL.md')
    assert '* If the current room lacks candidates, `teleport to` rooms with higher biological likelihood: `outside`, `greenhouse`, `bedroom`.' in text, "expected to find: " + '* If the current room lacks candidates, `teleport to` rooms with higher biological likelihood: `outside`, `greenhouse`, `bedroom`.'[:80]


def test_signal_122():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-living-entity-identifier/SKILL.md')
    assert '* Prioritize explicit living things (e.g., "dove egg," "giant tortoise") over ambiguous substances (e.g., "air," "water").' in text, "expected to find: " + '* Prioritize explicit living things (e.g., "dove egg," "giant tortoise") over ambiguous substances (e.g., "air," "water").'[:80]


def test_signal_123():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-material-classifier/SKILL.md')
    assert 'Activate when direct experimental testing of a material property (conductivity, magnetism, etc.) fails or equipment is unavailable, and you need to classify the material by inference to complete a sor' in text, "expected to find: " + 'Activate when direct experimental testing of a material property (conductivity, magnetism, etc.) fails or equipment is unavailable, and you need to classify the material by inference to complete a sor'[:80]


def test_signal_124():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-material-classifier/SKILL.md')
    assert "3. If testing fails, infer the property from the object's material. Consult `references/material_properties.md` for lookup." in text, "expected to find: " + "3. If testing fails, infer the property from the object's material. Consult `references/material_properties.md` for lookup."[:80]


def test_signal_125():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-material-classifier/SKILL.md')
    assert '2. Attempt direct testing if equipment exists (e.g., `connect <OBJECT> terminal 1 to <WIRE> terminal 2`).' in text, "expected to find: " + '2. Attempt direct testing if equipment exists (e.g., `connect <OBJECT> terminal 1 to <WIRE> terminal 2`).'[:80]


def test_signal_126():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-measurement-taker/SKILL.md')
    assert 'description: Use when the agent needs to measure a quantitative property (temperature, weight, pH) of a target object or substance using a measurement tool. This skill covers acquiring the tool, prepa' in text, "expected to find: " + 'description: Use when the agent needs to measure a quantitative property (temperature, weight, pH) of a target object or substance using a measurement tool. This skill covers acquiring the tool, prepa'[:80]


def test_signal_127():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-measurement-taker/SKILL.md')
    assert 'Measure a quantitative property of a target object or substance in the ScienceWorld environment using the appropriate measurement tool, then interpret the result for subsequent decision-making.' in text, "expected to find: " + 'Measure a quantitative property of a target object or substance in the ScienceWorld environment using the appropriate measurement tool, then interpret the result for subsequent decision-making.'[:80]


def test_signal_128():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-measurement-taker/SKILL.md')
    assert '5. **Position for follow-up** -- If the task requires a follow-up action (e.g., placing in a bin), `teleport to` the appropriate location before measuring.' in text, "expected to find: " + '5. **Position for follow-up** -- If the task requires a follow-up action (e.g., placing in a bin), `teleport to` the appropriate location before measuring.'[:80]


def test_signal_129():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-mixture-creator/SKILL.md')
    assert "description: This skill chemically mixes the contents of a container using the 'mix' action. Use when all required ingredients (e.g., sodium chloride and water) are present inside a container and the " in text, "expected to find: " + "description: This skill chemically mixes the contents of a container using the 'mix' action. Use when all required ingredients (e.g., sodium chloride and water) are present inside a container and the "[:80]


def test_signal_130():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-mixture-creator/SKILL.md')
    assert 'All required ingredients are confirmed inside a single container and you need to combine them into a new substance.' in text, "expected to find: " + 'All required ingredients are confirmed inside a single container and you need to combine them into a new substance.'[:80]


def test_signal_131():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-mixture-creator/SKILL.md')
    assert '3. `examine <CONTAINER>` or `focus on <NEW_SUBSTANCE>` — confirm the synthesis succeeded.' in text, "expected to find: " + '3. `examine <CONTAINER>` or `focus on <NEW_SUBSTANCE>` — confirm the synthesis succeeded.'[:80]


def test_signal_132():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-classifier/SKILL.md')
    assert 'description: Moves a tested or examined object into a designated container (e.g., a specific colored box) based on a determined property. Use when you have completed a test or inspection and need to f' in text, "expected to find: " + 'description: Moves a tested or examined object into a designated container (e.g., a specific colored box) based on a determined property. Use when you have completed a test or inspection and need to f'[:80]


def test_signal_133():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-classifier/SKILL.md')
    assert '**Task:** Sort a metal pot after a conductivity test determined it is conductive.' in text, "expected to find: " + '**Task:** Sort a metal pot after a conductivity test determined it is conductive.'[:80]


def test_signal_134():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-classifier/SKILL.md')
    assert '1. `look around` — confirm metal pot and yellow box are in the room.' in text, "expected to find: " + '1. `look around` — confirm metal pot and yellow box are in the room.'[:80]


def test_signal_135():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-focuser/SKILL.md')
    assert 'description: This skill selects and focuses on a specific object to signal task intent or prepare it for manipulation. Use when you have identified a target object that meets task criteria (e.g., a li' in text, "expected to find: " + 'description: This skill selects and focuses on a specific object to signal task intent or prepare it for manipulation. Use when you have identified a target object that meets task criteria (e.g., a li'[:80]


def test_signal_136():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-focuser/SKILL.md')
    assert '**Task:** Focus on a dove egg before picking it up for a biology task.' in text, "expected to find: " + '**Task:** Focus on a dove egg before picking it up for a biology task.'[:80]


def test_signal_137():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-focuser/SKILL.md')
    assert '3. Confirmation received → proceed with `pick up dove egg`.' in text, "expected to find: " + '3. Confirmation received → proceed with `pick up dove egg`.'[:80]


def test_signal_138():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-locator/SKILL.md')
    assert 'description: Searches for a specific target object across multiple rooms by systematically teleporting to likely locations and examining each room. Use this skill when you need to find an object whose' in text, "expected to find: " + 'description: Searches for a specific target object across multiple rooms by systematically teleporting to likely locations and examining each room. Use this skill when you need to find an object whose'[:80]


def test_signal_139():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-locator/SKILL.md')
    assert '4. `look around` — observation includes "a thermometer, currently reading a temperature of 10 degrees celsius"' in text, "expected to find: " + '4. `look around` — observation includes "a thermometer, currently reading a temperature of 10 degrees celsius"'[:80]


def test_signal_140():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-locator/SKILL.md')
    assert '5. Thermometer located in workshop. `pick up thermometer` if needed.' in text, "expected to find: " + '5. Thermometer located in workshop. `pick up thermometer` if needed.'[:80]


def test_signal_141():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-placer/SKILL.md')
    assert 'description: Moves a specified object from the environment or inventory into a target container based on a classification decision. Use this skill when a task requires sorting or storing an object in ' in text, "expected to find: " + 'description: Moves a specified object from the environment or inventory into a target container based on a classification decision. Use this skill when a task requires sorting or storing an object in '[:80]


def test_signal_142():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-placer/SKILL.md')
    assert '1. **Confirm Assessment Result:** Know which container corresponds to which classification (e.g., "blue box" = conductive, "orange box" = non-conductive).' in text, "expected to find: " + '1. **Confirm Assessment Result:** Know which container corresponds to which classification (e.g., "blue box" = conductive, "orange box" = non-conductive).'[:80]


def test_signal_143():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-placer/SKILL.md')
    assert 'Move an object into the correct container based on a prior classification or assessment result. This is the final step in conditional sorting workflows.' in text, "expected to find: " + 'Move an object into the correct container based on a prior classification or assessment result. This is the final step in conditional sorting workflows.'[:80]


def test_signal_144():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-retriever/SKILL.md')
    assert "description: Acquires a specified object by moving it from the environment into the agent's inventory using 'pick up OBJ'. Use this skill when a task requires an object to be manipulated, tested, or t" in text, "expected to find: " + "description: Acquires a specified object by moving it from the environment into the agent's inventory using 'pick up OBJ'. Use this skill when a task requires an object to be manipulated, tested, or t"[:80]


def test_signal_145():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-retriever/SKILL.md')
    assert '* If `look around` does not reveal the object, use `examine` on containers or furniture (e.g., `examine table`).' in text, "expected to find: " + '* If `look around` does not reveal the object, use `examine` on containers or furniture (e.g., `examine table`).'[:80]


def test_signal_146():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-retriever/SKILL.md')
    assert '* Ensure you are in the correct room before attempting `pick up`. Use `teleport to LOC` if necessary.' in text, "expected to find: " + '* Ensure you are in the correct room before attempting `pick up`. Use `teleport to LOC` if necessary.'[:80]


def test_signal_147():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-selector/SKILL.md')
    assert 'description: Use when the agent needs to choose a specific object from multiple candidates in the environment based on task criteria such as object type (non-living thing, electrical component, contai' in text, "expected to find: " + 'description: Use when the agent needs to choose a specific object from multiple candidates in the environment based on task criteria such as object type (non-living thing, electrical component, contai'[:80]


def test_signal_148():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-selector/SKILL.md')
    assert 'Identify and select the correct object from visible candidates in the ScienceWorld environment based on task-defined criteria (e.g., "non-living thing", "electrical component", "container"), then sign' in text, "expected to find: " + 'Identify and select the correct object from visible candidates in the ScienceWorld environment based on task-defined criteria (e.g., "non-living thing", "electrical component", "container"), then sign'[:80]


def test_signal_149():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-object-selector/SKILL.md')
    assert '2. **Evaluate candidates** -- For each visible object, determine if it matches the task criteria. Exclude target containers (e.g., destination boxes) and fixed furniture from candidates.' in text, "expected to find: " + '2. **Evaluate candidates** -- For each visible object, determine if it matches the task criteria. Exclude target containers (e.g., destination boxes) and fixed furniture from candidates.'[:80]


def test_signal_150():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-process-monitor/SKILL.md')
    assert 'description: This skill observes the state of an active apparatus and its contents to track progress. Use when you need to periodically check for state changes (e.g., solid to liquid) during a heating' in text, "expected to find: " + 'description: This skill observes the state of an active apparatus and its contents to track progress. Use when you need to periodically check for state changes (e.g., solid to liquid) during a heating'[:80]


def test_signal_151():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-process-monitor/SKILL.md')
    assert 'Activate when an apparatus (stove, burner) is active and you need to check whether a substance has undergone a state change (e.g., solid to liquid, liquid to gas).' in text, "expected to find: " + 'Activate when an apparatus (stove, burner) is active and you need to check whether a substance has undergone a state change (e.g., solid to liquid, liquid to gas).'[:80]


def test_signal_152():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-process-monitor/SKILL.md')
    assert '3. Compare the observed state to the previous state. If changed (e.g., "chocolate" to "liquid chocolate"), proceed to the next task step.' in text, "expected to find: " + '3. Compare the observed state to the previous state. If changed (e.g., "chocolate" to "liquid chocolate"), proceed to the next task step.'[:80]


def test_signal_153():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-process-pauser/SKILL.md')
    assert 'description: This skill introduces deliberate pauses in task execution. Use when the agent needs to consider next steps, evaluate intermediate results, or wait for processes to complete. The skill use' in text, "expected to find: " + 'description: This skill introduces deliberate pauses in task execution. Use when the agent needs to consider next steps, evaluate intermediate results, or wait for processes to complete. The skill use'[:80]


def test_signal_154():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-recipe-retriever/SKILL.md')
    assert "description: This skill locates and acquires a recipe or instruction document by using 'pick up' on the recipe object. Use when the task involves following a specific procedure (e.g., crafting, mixing" in text, "expected to find: " + "description: This skill locates and acquires a recipe or instruction document by using 'pick up' on the recipe object. Use when the task involves following a specific procedure (e.g., crafting, mixing"[:80]


def test_signal_155():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-recipe-retriever/SKILL.md')
    assert '3. Expected observation: "You move the recipe for red paint to the inventory."' in text, "expected to find: " + '3. Expected observation: "You move the recipe for red paint to the inventory."'[:80]


def test_signal_156():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-recipe-retriever/SKILL.md')
    assert '4. Later: `read recipe for red paint` to learn the required ingredients.' in text, "expected to find: " + '4. Later: `read recipe for red paint` to learn the required ingredients.'[:80]


def test_signal_157():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-room-explorer/SKILL.md')
    assert "description: Performs an initial survey of a room to identify all visible objects, containers, devices, and their states using the 'look around' action. Use this skill when you first enter a new locat" in text, "expected to find: " + "description: Performs an initial survey of a room to identify all visible objects, containers, devices, and their states using the 'look around' action. Use this skill when you first enter a new locat"[:80]


def test_signal_158():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-room-explorer/SKILL.md')
    assert '3. Observation: "This room is called the kitchen. In it, you see: a fridge (containing chocolate, milk), a metal pot, a thermometer, a counter, a stove (which is turned off). You also see: a door to t' in text, "expected to find: " + '3. Observation: "This room is called the kitchen. In it, you see: a fridge (containing chocolate, milk), a metal pot, a thermometer, a counter, a stove (which is turned off). You also see: a door to t'[:80]


def test_signal_159():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-room-explorer/SKILL.md')
    assert '4. **Parsed inventory:** fridge (open, contains chocolate and milk), metal pot, thermometer, counter, stove (off), exit to hallway.' in text, "expected to find: " + '4. **Parsed inventory:** fridge (open, contains chocolate and milk), metal pot, thermometer, counter, stove (off), exit to hallway.'[:80]


def test_signal_160():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-room-navigator/SKILL.md')
    assert 'description: Teleports the agent to a specified room within the ScienceWorld environment. Use when the agent needs to move between different locations to locate objects or access specific facilities. ' in text, "expected to find: " + 'description: Teleports the agent to a specified room within the ScienceWorld environment. Use when the agent needs to move between different locations to locate objects or access specific facilities. '[:80]


def test_signal_161():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-room-navigator/SKILL.md')
    assert '3. `look around` to survey the room and locate the metal pot.' in text, "expected to find: " + '3. `look around` to survey the room and locate the metal pot.'[:80]


def test_signal_162():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-room-navigator/SKILL.md')
    assert '**Task:** Move to the kitchen to find a metal pot.' in text, "expected to find: " + '**Task:** Move to the kitchen to find a metal pot.'[:80]


def test_signal_163():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-room-scanner/SKILL.md')
    assert "description: This skill performs a 'look around' action to scan and describe the current room's contents, including visible objects, containers, and doors. Use when entering a new room or when the age" in text, "expected to find: " + "description: This skill performs a 'look around' action to scan and describe the current room's contents, including visible objects, containers, and doors. Use when entering a new room or when the age"[:80]


def test_signal_164():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-room-scanner/SKILL.md')
    assert '2. Observation: "This room is called the workshop. In it, you see: a table. On the table is: a battery, a blue light bulb, an orange wire, a yellow wire, a green wire. You also see: a blue box, an ora' in text, "expected to find: " + '2. Observation: "This room is called the workshop. In it, you see: a table. On the table is: a battery, a blue light bulb, an orange wire, a yellow wire, a green wire. You also see: a blue box, an ora'[:80]


def test_signal_165():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-room-scanner/SKILL.md')
    assert '3. Parse: available components include battery, light bulb, three wires; classification containers are blue box and orange box.' in text, "expected to find: " + '3. Parse: available components include battery, light bulb, three wires; classification containers are blue box and orange box.'[:80]


def test_signal_166():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-substance-cooler/SKILL.md')
    assert 'description: This skill initiates the cooling of a substance by moving it into a cooling appliance like a freezer. Use when a task requires lowering the temperature of a specific material to observe p' in text, "expected to find: " + 'description: This skill initiates the cooling of a substance by moving it into a cooling appliance like a freezer. Use when a task requires lowering the temperature of a specific material to observe p'[:80]


def test_signal_167():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-substance-fetcher/SKILL.md')
    assert 'description: Locates and retrieves a target substance or material from a container in the environment. Use this skill when the task requires processing a specific substance (e.g., chocolate, sodium ch' in text, "expected to find: " + 'description: Locates and retrieves a target substance or material from a container in the environment. Use this skill when the task requires processing a specific substance (e.g., chocolate, sodium ch'[:80]


def test_signal_168():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-substance-preparator/SKILL.md')
    assert 'description: Use when you need to transfer a target substance into an appropriate container for processing (e.g., a pot for heating, a beaker for mixing). Trigger after acquiring the substance and bef' in text, "expected to find: " + 'description: Use when you need to transfer a target substance into an appropriate container for processing (e.g., a pot for heating, a beaker for mixing). Trigger after acquiring the substance and bef'[:80]


def test_signal_169():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-substance-preparator/SKILL.md')
    assert '2. Run `look around` to scan for containers. You see: `metal pot` (empty, on counter), `glass beaker` (empty, on shelf), `ceramic cup` (contains water).' in text, "expected to find: " + '2. Run `look around` to scan for containers. You see: `metal pot` (empty, on counter), `glass beaker` (empty, on shelf), `ceramic cup` (contains water).'[:80]


def test_signal_170():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-substance-preparator/SKILL.md')
    assert '6. Run `examine metal pot` — output confirms: "metal pot (containing chocolate)".' in text, "expected to find: " + '6. Run `examine metal pot` — output confirms: "metal pot (containing chocolate)".'[:80]


def test_signal_171():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-target-locator/SKILL.md')
    assert 'description: This skill determines the most likely location for a target object based on domain knowledge and environmental clues. Use when the agent needs to find a specific item (like an animal) but' in text, "expected to find: " + 'description: This skill determines the most likely location for a target object based on domain knowledge and environmental clues. Use when the agent needs to find a specific item (like an animal) but'[:80]


def test_signal_172():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-target-locator/SKILL.md')
    assert '4. `look around` to verify the target is present. If not, try the next likely room.' in text, "expected to find: " + '4. `look around` to verify the target is present. If not, try the next likely room.'[:80]


def test_signal_173():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-target-locator/SKILL.md')
    assert '2. Map to the most probable room using these heuristics:' in text, "expected to find: " + '2. Map to the most probable room using these heuristics:'[:80]


def test_signal_174():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-task-focuser/SKILL.md')
    assert 'description: Use when the agent needs to direct attention to a specific object in the environment or inventory before performing a critical action such as measuring, using, or connecting. This prepara' in text, "expected to find: " + 'description: Use when the agent needs to direct attention to a specific object in the environment or inventory before performing a critical action such as measuring, using, or connecting. This prepara'[:80]


def test_signal_175():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-task-focuser/SKILL.md')
    assert 'Formally declare intent to interact with a specific object in the ScienceWorld environment. The `focus on` action is a required preparatory step that signals to the system which object subsequent acti' in text, "expected to find: " + 'Formally declare intent to interact with a specific object in the ScienceWorld environment. The `focus on` action is a required preparatory step that signals to the system which object subsequent acti'[:80]


def test_signal_176():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-task-focuser/SKILL.md')
    assert '1. **Identify the target object** -- Determine the exact name as it appears in the environment (e.g., `thermometer`, `metal fork`).' in text, "expected to find: " + '1. **Identify the target object** -- Determine the exact name as it appears in the environment (e.g., `thermometer`, `metal fork`).'[:80]


def test_signal_177():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-task-parser/SKILL.md')
    assert 'description: Analyzes user instructions in ScienceWorld environments to extract specific task requirements and constraints. Use when receiving a new task to identify required objects, target locations' in text, "expected to find: " + 'description: Analyzes user instructions in ScienceWorld environments to extract specific task requirements and constraints. Use when receiving a new task to identify required objects, target locations'[:80]


def test_signal_178():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-task-parser/SKILL.md')
    assert '**Task instruction:** "Find a non-living thing in the workshop and move it to the purple box."' in text, "expected to find: " + '**Task instruction:** "Find a non-living thing in the workshop and move it to the purple box."'[:80]


def test_signal_179():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-task-parser/SKILL.md')
    assert '1. **Parse:** Target = non-living object, Location = workshop, Container = purple box.' in text, "expected to find: " + '1. **Parse:** Target = non-living object, Location = workshop, Container = purple box.'[:80]


def test_signal_180():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-threshold-evaluator/SKILL.md')
    assert 'description: Use when the agent has just obtained a numerical measurement (temperature, weight, pH) and must compare it against a predefined threshold to determine a binary outcome. This skill extract' in text, "expected to find: " + 'description: Use when the agent has just obtained a numerical measurement (temperature, weight, pH) and must compare it against a predefined threshold to determine a binary outcome. This skill extract'[:80]


def test_signal_181():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-threshold-evaluator/SKILL.md')
    assert 'Compare a measured numerical value against a predefined threshold to determine which of two conditional actions to execute. This is the decision-making step that immediately follows a measurement in S' in text, "expected to find: " + 'Compare a measured numerical value against a predefined threshold to determine which of two conditional actions to execute. This is the decision-making step that immediately follows a measurement in S'[:80]


def test_signal_182():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-threshold-evaluator/SKILL.md')
    assert '2. **Identify the threshold and condition** -- From the task instruction, determine the threshold value and comparison operator (e.g., `"above 50.0 degrees"` means `threshold=50.0`, `operator=">"`).' in text, "expected to find: " + '2. **Identify the threshold and condition** -- From the task instruction, determine the threshold value and comparison operator (e.g., `"above 50.0 degrees"` means `threshold=50.0`, `operator=">"`).'[:80]


def test_signal_183():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-tool-user/SKILL.md')
    assert 'description: Uses a tool from inventory on a target object or location to perform a specific environmental interaction, such as digging, cutting, or measuring. Use this skill when a task requires modi' in text, "expected to find: " + 'description: Uses a tool from inventory on a target object or location to perform a specific environmental interaction, such as digging, cutting, or measuring. Use this skill when a task requires modi'[:80]


def test_signal_184():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-tool-user/SKILL.md')
    assert '1. **Ensure Tool in Inventory:** The required tool (e.g., `shovel`, `thermometer`, `axe`) must be in your inventory. Use `pick up OBJ` if it is not.' in text, "expected to find: " + '1. **Ensure Tool in Inventory:** The required tool (e.g., `shovel`, `thermometer`, `axe`) must be in your inventory. Use `pick up OBJ` if it is not.'[:80]


def test_signal_185():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-tool-user/SKILL.md')
    assert '* Some tools produce measurable outputs (thermometer readings); others produce state changes (shovel digs soil). Interpret accordingly.' in text, "expected to find: " + '* Some tools produce measurable outputs (thermometer readings); others produce state changes (shovel digs soil). Interpret accordingly.'[:80]


def test_signal_186():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-tool-validator/SKILL.md')
    assert 'description: Use when the agent has acquired a tool or instrument and needs to verify it is operational before first use in a critical task step. This skill performs a lightweight pre-use check via "f' in text, "expected to find: " + 'description: Use when the agent has acquired a tool or instrument and needs to verify it is operational before first use in a critical task step. This skill performs a lightweight pre-use check via "f'[:80]


def test_signal_187():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-tool-validator/SKILL.md')
    assert 'Perform a pre-use functionality check on a tool or instrument to confirm it is operational before employing it in a critical ScienceWorld task step such as measurement, activation, or connection.' in text, "expected to find: " + 'Perform a pre-use functionality check on a tool or instrument to confirm it is operational before employing it in a critical ScienceWorld task step such as measurement, activation, or connection.'[:80]


def test_signal_188():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/scienceworld-tool-validator/SKILL.md')
    assert '3. **Confirm readiness** -- A successful response (`"You focus on the [TOOL]."`) confirms the tool is operational. No further diagnostic steps are needed unless an error is observed.' in text, "expected to find: " + '3. **Confirm readiness** -- A successful response (`"You focus on the [TOOL]."`) confirms the tool is operational. No further diagnostic steps are needed unless an error is observed.'[:80]


def test_signal_189():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/task-completion-focus/SKILL.md')
    assert 'description: Focuses on a specific target object to signal task completion. Use when you have produced the required final object (like a grown banana) and need to formally complete the assigned task. ' in text, "expected to find: " + 'description: Focuses on a specific target object to signal task completion. Use when you have produced the required final object (like a grown banana) and need to formally complete the assigned task. '[:80]


def test_signal_190():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/task-completion-focus/SKILL.md')
    assert '3. **Ambiguity handling:** If the environment returns "Ambiguous request" with numbered options, respond with the option number (e.g., `0`) for the target most directly associated with your task goal.' in text, "expected to find: " + '3. **Ambiguity handling:** If the environment returns "Ambiguous request" with numbered options, respond with the option number (e.g., `0`) for the target most directly associated with your task goal.'[:80]


def test_signal_191():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/scienceworld/task-completion-focus/SKILL.md')
    assert 'The final required object (e.g., grown banana, crafted item) is visibly present and you need to formally signal task completion. Do not use for intermediate steps.' in text, "expected to find: " + 'The final required object (e.g., grown banana, crafted item) is visibly present and you need to formally signal task completion. Do not use for intermediate steps.'[:80]


def test_signal_192():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-attribute-verifier/SKILL.md')
    assert 'Thought: The user wants a black leather wallet under $40. The price is $35.99, which is strictly less than $40 — price check passes. The title mentions "Leather" which matches the material requirement' in text, "expected to find: " + 'Thought: The user wants a black leather wallet under $40. The price is $35.99, which is strictly less than $40 — price check passes. The title mentions "Leather" which matches the material requirement'[:80]


def test_signal_193():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-attribute-verifier/SKILL.md')
    assert '- **Select before buying:** Always click the required attribute option (e.g., `click[black]`) before clicking `click[Buy Now]`. Never skip this step.' in text, "expected to find: " + '- **Select before buying:** Always click the required attribute option (e.g., `click[black]`) before clicking `click[Buy Now]`. Never skip this step.'[:80]


def test_signal_194():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-attribute-verifier/SKILL.md')
    assert '1. **Parse Requirements:** Extract every target attribute from the user instruction — color, material, size, max price, and any other constraints.' in text, "expected to find: " + '1. **Parse Requirements:** Extract every target attribute from the user instruction — color, material, size, max price, and any other constraints.'[:80]


def test_signal_195():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-initial-search/SKILL.md')
    assert 'description: Performs the first search on an e-commerce platform using keywords derived from parsed user requirements. Use when starting product discovery from a user instruction or when previous sear' in text, "expected to find: " + 'description: Performs the first search on an e-commerce platform using keywords derived from parsed user requirements. Use when starting product discovery from a user instruction or when previous sear'[:80]


def test_signal_196():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-initial-search/SKILL.md')
    assert '**User instruction:** "I would like to find a 24 pack of 7.5 ounce bottles of non-gmo classic tonic, and target price lower than 50.00 dollars"' in text, "expected to find: " + '**User instruction:** "I would like to find a 24 pack of 7.5 ounce bottles of non-gmo classic tonic, and target price lower than 50.00 dollars"'[:80]


def test_signal_197():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-initial-search/SKILL.md')
    assert '**Thought:** I need to search for the product using the key attributes. I will omit the price constraint from the search keywords.' in text, "expected to find: " + '**Thought:** I need to search for the product using the key attributes. I will omit the price constraint from the search keywords.'[:80]


def test_signal_198():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-product-detail-check/SKILL.md')
    assert '**Thought:** The user needs a long, natural-looking, clip-in hair extension under $40. This product is priced at $34.99 (< $40.00), the title confirms "long" and "natural looking", and the description' in text, "expected to find: " + '**Thought:** The user needs a long, natural-looking, clip-in hair extension under $40. This product is priced at $34.99 (< $40.00), the title confirms "long" and "natural looking", and the description'[:80]


def test_signal_199():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-product-detail-check/SKILL.md')
    assert '**Observation:** Product page for "22 Inch Long Natural Looking Clip-In Hair Extension" — Price: $34.99, Description mentions "clip-in", "natural looking", "synthetic fiber".' in text, "expected to find: " + '**Observation:** Product page for "22 Inch Long Natural Looking Clip-In Hair Extension" — Price: $34.99, Description mentions "clip-in", "natural looking", "synthetic fiber".'[:80]


def test_signal_200():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-product-detail-check/SKILL.md')
    assert "**Thought:** The user's budget is under $40. This product is priced at $45.99, which exceeds the $40 limit. Price constraint fails." in text, "expected to find: " + "**Thought:** The user's budget is under $40. This product is priced at $45.99, which exceeds the $40 limit. Price constraint fails."[:80]


def test_signal_201():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-product-evaluator/SKILL.md')
    assert '**Thought:** The user needs a teeth whitening toothpaste that freshens breath, under $15. Product B09NYFDNVX at $12.99 mentions both "whitening" and "breath freshener" in the title — meets all criteri' in text, "expected to find: " + '**Thought:** The user needs a teeth whitening toothpaste that freshens breath, under $15. Product B09NYFDNVX at $12.99 mentions both "whitening" and "breath freshener" in the title — meets all criteri'[:80]


def test_signal_202():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-product-evaluator/SKILL.md')
    assert '**Instruction:** "i need a teeth whitening toothpaste that also freshens breath, and price lower than 15.00 dollars"' in text, "expected to find: " + '**Instruction:** "i need a teeth whitening toothpaste that also freshens breath, and price lower than 15.00 dollars"'[:80]


def test_signal_203():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-product-evaluator/SKILL.md')
    assert "**Thought:** [Summarize the user's constraints, evaluate each product against them, and justify your selection.]" in text, "expected to find: " + "**Thought:** [Summarize the user's constraints, evaluate each product against them, and justify your selection.]"[:80]


def test_signal_204():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-product-search/SKILL.md')
    assert '4.  **Validate Results:** Success is marked by a "Page 1" observation containing product listings. If 0 results are returned, re-invoke with a broader or alternative query. If all results exceed the u' in text, "expected to find: " + '4.  **Validate Results:** Success is marked by a "Page 1" observation containing product listings. If 0 results are returned, re-invoke with a broader or alternative query. If all results exceed the u'[:80]


def test_signal_205():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-product-search/SKILL.md')
    assert '*   **Trigger Condition:** This skill is the entry point for a new product discovery task. Also activate when the observation contains "[SEP] Search" or "[SEP] Back to Search".' in text, "expected to find: " + '*   **Trigger Condition:** This skill is the entry point for a new product discovery task. Also activate when the observation contains "[SEP] Search" or "[SEP] Back to Search".'[:80]


def test_signal_206():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-product-search/SKILL.md')
    assert '*   **Output Handoff:** The search results page is passed to downstream skills (e.g., `webshop-result-filter`, `webshop-product-evaluator`) for individual product analysis.' in text, "expected to find: " + '*   **Output Handoff:** The search results page is passed to downstream skills (e.g., `webshop-result-filter`, `webshop-product-evaluator`) for individual product analysis.'[:80]


def test_signal_207():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-product-selector/SKILL.md')
    assert '**Thought:** The user needs a portable, double horn bluetooth speaker that is easy to carry, under $50. B093C1THVP at $32.99 matches "portable", "double horn", and "easy to carry" — all keywords prese' in text, "expected to find: " + '**Thought:** The user needs a portable, double horn bluetooth speaker that is easy to carry, under $50. B093C1THVP at $32.99 matches "portable", "double horn", and "easy to carry" — all keywords prese'[:80]


def test_signal_208():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-product-selector/SKILL.md')
    assert "**Thought:** [List the user's requirements, evaluate each candidate product against them, explain why the selected product is the best match.]" in text, "expected to find: " + "**Thought:** [List the user's requirements, evaluate each candidate product against them, explain why the selected product is the best match.]"[:80]


def test_signal_209():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-product-selector/SKILL.md')
    assert '**Instruction:** "i need a portable double horn bluetooth speaker that is easy to carry, and price lower than 50.00 dollars"' in text, "expected to find: " + '**Instruction:** "i need a portable double horn bluetooth speaker that is easy to carry, and price lower than 50.00 dollars"'[:80]


def test_signal_210():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-purchase-executor/SKILL.md')
    assert "description: Executes the purchase action for a confirmed suitable product on an e-commerce page. Use when a product has been verified against the user's requirements (price, attributes) and the decis" in text, "expected to find: " + "description: Executes the purchase action for a confirmed suitable product on an e-commerce page. Use when a product has been verified against the user's requirements (price, attributes) and the decis"[:80]


def test_signal_211():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-purchase-executor/SKILL.md')
    assert '**Scenario:** The user wants a natural-looking wig priced under $40.00. You are on a product detail page for "Natural Looking Human Hair Wig - $34.99" and have verified it meets all criteria.' in text, "expected to find: " + '**Scenario:** The user wants a natural-looking wig priced under $40.00. You are on a product detail page for "Natural Looking Human Hair Wig - $34.99" and have verified it meets all criteria.'[:80]


def test_signal_212():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-purchase-executor/SKILL.md')
    assert "**Thought:** The product matches the user's requirements (natural looking, price $34.99 < $40.00). I should proceed with the purchase." in text, "expected to find: " + "**Thought:** The product matches the user's requirements (natural looking, price $34.99 < $40.00). I should proceed with the purchase."[:80]


def test_signal_213():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-purchase-initiator/SKILL.md')
    assert '**Thought:** The user needs a teeth whitening toothpaste that freshens breath, under $15. The current product is priced at $12.99 (< $15.00), matches "whitening" and "breath freshener" in the title, a' in text, "expected to find: " + '**Thought:** The user needs a teeth whitening toothpaste that freshens breath, under $15. The current product is priced at $12.99 (< $15.00), matches "whitening" and "breath freshener" in the title, a'[:80]


def test_signal_214():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-purchase-initiator/SKILL.md')
    assert '**Observation:** Product page for "Whitening Toothpaste with Breath Freshener" — Price: $12.99, Size: 4oz (selected), Flavor: Mint (selected). Available actions: click[buy now], click[back to search].' in text, "expected to find: " + '**Observation:** Product page for "Whitening Toothpaste with Breath Freshener" — Price: $12.99, Size: 4oz (selected), Flavor: Mint (selected). Available actions: click[buy now], click[back to search].'[:80]


def test_signal_215():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-purchase-initiator/SKILL.md')
    assert '**Instruction:** "i need a teeth whitening toothpaste that also freshens breath, and price lower than 15.00 dollars"' in text, "expected to find: " + '**Instruction:** "i need a teeth whitening toothpaste that also freshens breath, and price lower than 15.00 dollars"'[:80]


def test_signal_216():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-query-interpreter/SKILL.md')
    assert '3.  **Hand Off:** Pass the structured parameters to the search execution skill (e.g., `webshop-search-executor` or `webshop-product-search`) to perform the actual query.' in text, "expected to find: " + '3.  **Hand Off:** Pass the structured parameters to the search execution skill (e.g., `webshop-search-executor` or `webshop-product-search`) to perform the actual query.'[:80]


def test_signal_217():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-query-interpreter/SKILL.md')
    assert '**Thought:** The user wants body wash bars. Key attributes are "moisturizing", "shea butter", quantity "6 pack". Hard constraint is price under $20.00.' in text, "expected to find: " + '**Thought:** The user wants body wash bars. Key attributes are "moisturizing", "shea butter", quantity "6 pack". Hard constraint is price under $20.00.'[:80]


def test_signal_218():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-query-interpreter/SKILL.md')
    assert '**Thought:** The user wants a hair extension. Key attributes are "long", "clip-in", and "natural looking". The hard constraint is price under $40.00.' in text, "expected to find: " + '**Thought:** The user wants a hair extension. Key attributes are "long", "clip-in", and "natural looking". The hard constraint is price under $40.00.'[:80]


def test_signal_219():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-result-filter/SKILL.md')
    assert '2.  **Validate Constraints:** Confirm you have at least one constraint extracted before proceeding. If the instruction contains no filterable criteria, skip filtering and select the first available pr' in text, "expected to find: " + '2.  **Validate Constraints:** Confirm you have at least one constraint extracted before proceeding. If the instruction contains no filterable criteria, skip filtering and select the first available pr'[:80]


def test_signal_220():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-result-filter/SKILL.md')
    assert '5.  **Output Decision:** Select the **first product** that passes all criteria as the primary candidate for `click[product_id]`. If no product passes:' in text, "expected to find: " + '5.  **Output Decision:** Select the **first product** that passes all criteria as the primary candidate for `click[product_id]`. If no product passes:'[:80]


def test_signal_221():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-result-filter/SKILL.md')
    assert '3.  **Parse the Observation:** Extract the list of products from the search results page (Product ID, Title, Price, Rating if available).' in text, "expected to find: " + '3.  **Parse the Observation:** Extract the list of products from the search results page (Product ID, Title, Price, Rating if available).'[:80]


def test_signal_222():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-search-executor/SKILL.md')
    assert '**Thought:** The user needs a clip-in hair extension that is long and natural looking, under $40. I will search for the core product type with key attributes to get relevant results.' in text, "expected to find: " + '**Thought:** The user needs a clip-in hair extension that is long and natural looking, under $40. I will search for the core product type with key attributes to get relevant results.'[:80]


def test_signal_223():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-search-executor/SKILL.md')
    assert 'Activate when the user provides an instruction to find or buy a product with specific attributes. The instruction will be in the `Observation`.' in text, "expected to find: " + 'Activate when the user provides an instruction to find or buy a product with specific attributes. The instruction will be in the `Observation`.'[:80]


def test_signal_224():
    """Distinctive line from gold patch must be present."""
    text = _read('experiments/src/skills/webshop/webshop-search-executor/SKILL.md')
    assert "*   If all results exceed the user's price constraint, try adding price-related terms or narrowing the product category." in text, "expected to find: " + "*   If all results exceed the user's price constraint, try adding price-related terms or narrowing the product category."[:80]

