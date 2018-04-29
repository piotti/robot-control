# Queueing File Format

## Actions

### Setup
* `REACTORSETUP`
    * Links the specified reactor to the specified reactor bay. This must be done before any BLE communication, or before moving a reactor to/from the bay
    * Arguments
        1. Reactor ID (Set in config file)
        2. Reactor bay, in format `x y`
* `PUMPSETUP`
    * Links a pump to the specified port on the specified reactor. Must call `REACTORSETUP` first. To have the robot move the tube, call `PUMPCONNECT` or `PUMPDISCONNECT` after calling `PUMPSETUP`.
    * Arguments
        1. Reactor ID
        2. Port number (1, 2, 3, or 4)
        3. Tube number, correlating to a pump (see config file)

### Moving Reactors
* `REACTORMOVE`
    * Moves a reactor with the specified ID from storage to the reactor stack and vise-versa. Must call `REACTORSETUP` first to link reactor to reactor bay.
    * Arguments
        1. Reactor ID
        2. Direction, one of the following:
            * `TOBAY` - move from storage to stack
            * `TOSTORAGE` - move from stack to storage

### Pumps and valves
* `PUMPCONNECT`
    * Connects the pump tube. Must have previously initialized pump with `PUMPSETUP`.
    * Arguments
        1. Reactor ID
        2. Port number (1, 2, 3, or 4)
* `PUMPDISCONNECT`
    * Disconnects the pump tube. Must have previously initialized pump with `PUMPSETUP`.
    * Arguments
        1. Reactor ID
        2. Port number (1, 2, 3, or 4)
* `PUMPFLOWSET`
    * Sets the flow of the pump. Must have previously initialized pump with `PUMPSETUP`.
    * Arguments
        1. Reactor ID
        2. Port number (1, 2, 3, or 4)
        3. Flow value
* `PORTOPEN`
    * Opens the valve of the specified port on the specified reactor.
     * Arguments
        1. Reactor ID
        2. Port number (1, 2, 3, or 4)
* `PORTCLOSE`
    * Closes the valve of the specified port on the specified reactor.
     * Arguments
        1. Reactor ID
        2. Port number (1, 2, 3, or 4)
* `OUTLETOPEN`
    * Opens the outlet valve of the specified reactor.
     * Arguments
        1. Reactor ID
* `OUTLETCLOSE`
    * Closes the outlet valve of the specified reactor.
     * Arguments
        1. Reactor ID
* `SEPOPEN`
    * Opens the separator valve of the specified reactor.
     * Arguments
        1. Reactor ID
* `SEPCLOSE`
    * Closes the separator valve on the specified reactor.
     * Arguments
        1. Reactor ID

### Opening and Closing Jaws/Actuators
* `JAWCLOSE`
    * Closes the jaw of the specified reactor bay
    * Arguments
        1. Reactor bay, in format `x y`
* `REACTORJAWCLOSE`
    * Same as `JAWCLOSE`, but takes in reactor ID as argument
    * Arguments
        1. Reactor ID
* `JAWOPEN`
    * Opens the jaw of the specified reactor bay
    * Arguments
        1. Reactor bay, in format `x y`
* `REACTORJAWOPEN`
    * Same as `JAWOPEN`, but takes in reactor ID as argument
    * Arguments
        1. Reactor ID
* `STACKCLOSE`
    * Closes (compresses) specified reactor stack
    * Arguments
        1. Stack number (same as `x` coordinate of reactor bays)
* `STACKOPEN`
    * Opens (decompresses) specified reactor stack
    * Arguments
        1. Stack number (same as `x` coordinate of reactor bays)
* `FITTINGCLOSE`
    * Closes fitting actuator of specified reactor stack
    * Arguments
        1. Stack number (same as `x` coordinate of reactor bays)
* `FITTINGOPEN`
    * Opens fitting actuator of specified reactor stack
    * Arguments
        1. Stack number (same as `x` coordinate of reactor bays)

### BLE
* `BLECONNECT`
    * Connects via Bluetooth to specified reactor
    * Arguments
        1. Reactor ID
* `BLEDISCONNECT`
    * Disconnects to specified reactor
    * Arguments
        1. Reactor ID
* `TEMPNOTIFSON`
    * Turns on temperature notifications
    * Arguments
        1. Reactor ID
* `TEMPNOTIFSOFF`
    * Turns off temperature notifications
    * Arguments
        1. Reactor ID
* `PRESSURENOTIFSON`
    * Turns on pressure notifications
    * Arguments
        1. Reactor ID
* `PRESSURENOTIFSOFF`
    * Turns off pressure notifications
    * Arguments
        1. Reactor ID
* `SETPOINT`
    * Sets thermocontroller setpoint
    * Arguments
        1. Reactor ID
        2. Setpoint, integer between 0 and 255
* `TEMPCONTROLON`
    * Turns on thermocontroller
    * Arguments
        1. Reactor ID
* `TEMPCONTROLOFF`
    * Turns off thermocontroller
    * Arguments
        1. Reactor ID
* `MIXINGSPEED`
    * Sets motor speed of specified reactor
    * Arguments
        1. Reactor ID
        2. Motor speed, integer from 0-100

### Time

* `TIMEOUT`
    * Pauses for specified time
    * Arguments
        1. Timeout in milliseconds



