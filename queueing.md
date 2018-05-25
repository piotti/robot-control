# Queueing File Format

## General Format

Queueing files should be in CSV (comma separated values) format. There are five columns: `Step`, `Action`, `Arg1`, `Arg2`, and `Arg3`. Every file should start out with one header line that lists these five columns.

* `Step`
   * An integer which denotes the line number. Step should start at 1 and increase by 1 every line.
* `Action`
   * Denotes the command. All actions are a single string with capital lettters and no spaces.
* `Arg1`, `Arg2`, and `Arg3`
   * The arguments of the command. Commands may take 1, 2, or 3 arguments. If the command takes fewer than 3 arguments, the remaining argument fields may be left blank.

## Comments

Files can contain comments that won't get processed. Any line starting with `#` will not be executed.

## Example file

Here is an example queueing file, which brings Reactor 1 from storage to bay (0, 0), connects via BLE, sets the setpoint to 100 deg. C, waits 2 minutes, then disconnects and moves the reactor back to storage.

```
Step,Action,Arg1,Arg2,Arg3

# Link Reactor 1 to bay (0; 0)
1,REACTORSETUP,1,0 0

# Move reactor to bay (0; 0). This line will block until the robot has completed the move.
2,REACTORMOVE,1,TOBAY

# Close the jaw to power up the reactor
3,REACTORJAWCLOSE,1

# Wait 3 seconds for jaw to close and for PSoC to power up
4,TIMEOUT,3000

# Initiate Bluetooth connection
5,BLECONNECT,1

# Start heating to 100 degrees C
6,SETPOINT,1,100

# Wait 2 minutes (120000 ms)
7,TIMEOUT,120000

# Turn off heater
8,SETPOINT,1,0

# Bluetooth disconnect
9,BLEDISCONNECT,1

# Open jaw
10,REACTORJAWOPEN,1

# Wait for jaw to open
11,TIMEOUT,2000

# Move back to storage
12,REACTORMOVE,1,TOSTORAGE
```

## Settings
These commands globally affect the processing environment.

* `ERRORHANDLE`
    * Sets how the program handles errors thrown by a certain command.
    * Arguments
        1. The command you want to handle errors for (e.g., `REACTORMOVE`)
        2. What the program should do if the command fails. Must be either STOP or CONTINUE. By default, commands will stop the program after failing.
        3. (Integer) Optional number of times to retry the command before stopping or continuing. Default is 0.
    * Example usage: `1,ERRORHANDLE,PUMPCONNECT,STOP,2`

## Actions

### General

* `ECHO`
    * Echoes the given text to the console
    * Arguments
        1. The text to be displayed on screen (make sure it doesn't contain any commas) 
* `TIMEOUT`
    * Pauses for specified time then continues
    * Arguments
        1. Timeout in milliseconds
* `PAUSE`
    * Switches control to manual mode, meaning the user will have to continue the program through the user interface
    * Arguments:
        None

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
        3. Tube coords, correlating to a pump (see config file), in format `x y`
* 'PRESSURESET'
    * Sets the Back Pressure of the stack
        * Arguments
            1. Stack number (same as `x` coordinate of reactor bays)
            2. Pressure in psi

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






