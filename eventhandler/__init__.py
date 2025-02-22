import collections
import sys
import types

__version__ = '1.2.1'
__author__ = 'David Vicente Ranz'


class EventHandler:
    """Universal, simple and effective syncronous event handler class, based in callbacks.

    Use as any classic event handler based in callbacks.

    eh = EventHandler('MyCoolEvent')
    eh.link(callback, 'MyCoolEvent')
    eh.fite('MyCoolEvent')

    Attributes:
        verbose (bool): Set True will output some messages, False will be silent.
        stream_output (IoStream): Set the stream to output messages.
        tolerate_exceptions (bool): Set True to ignore callbacks exceptions, False to raises it.
    """

    class Exceptions:
        """Custom error classes definition."""

        class EventNotAllowedError(Exception):
            """Will raise when tries to link a callback to unexistent event."""
            pass

    def __init__(self, *event_names, verbose=False, stream_output=sys.stdout, tolerate_callbacks_exceptions=False):
        """EventHandler initiazition recibes a list of allowed event names as arguments.

        Args:
            *event_names (str): Events names.
            verbose (bool): Set True to output warning messages.
            stream_output (IoStream): Set to send the output to specfic IO Stream object.
            tolerate_callbacks_exceptions (bool):
                False will raise any callback exception, stopping the execution.
                True will ignore any callbacks exceptions.
        """
        self.__events = {}
        self.__event_queue = collections.deque()
        self.verbose = verbose
        self.tolerate_exceptions = tolerate_callbacks_exceptions
        self.stream_output = stream_output

        if event_names:
            for event in event_names:
                self.register_event(str(event))  # cast as str to be safe

        print(f'{self.__str__()} has been init.', file=self.stream_output) if self.verbose else None

    @property
    def events(self) -> dict:
        """Return events as dict."""
        return self.__events

    def clear_events(self) -> bool:
        """Clear all events."""
        self.__events = {}
        return True

    @property
    def event_list(self) -> [str]:
        """Retun  list of regitered events."""
        return self.__events.keys()

    @property
    def count_events(self) -> int:
        """Return number of registered events."""
        return len(self.event_list)

    def is_event_registered(self, event_name: str) -> bool:
        """Return if an event is current registered.

        Args:
            event_name (str): The event you want to consult.
        """
        return event_name in self.__events

    def register_event(self, event_name: str) -> bool:
        """Register an event name.

        Args:
            event_name (str): Event name as string.
        """
        # print('registering event', event_name, self.events)
        if self.is_event_registered(event_name):
            print(f'Omiting event {event_name} registration, already implemented',
                  file=self.stream_output) if self.verbose else None
            return False

        self.__events[event_name] = []
        return True

    def unregister_event(self, event_name: str) -> bool:
        """Unregister an event name.

        Args:
            event_name (str): Remove an event from events dict.
        """
        if event_name in self.__events:
            del self.__events[event_name]
            return True
        print(f'Omiting unregister_event. {event_name} '
              f'is not implemented.', file=self.stream_output) if self.verbose else None
        return False

    @staticmethod
    def is_callable(func: any) -> bool:
        """Return true if func is a callable variable.

        Args:
            func (callable): Object to validates as a callable.
        """
        return isinstance(func,
                          (types.FunctionType, types.BuiltinFunctionType, types.MethodType, types.BuiltinMethodType))

    def is_callback_in_event(self, event_name: str, callback: callable) -> bool:
        """Return if a given callback is already registered on the events dict.

        Args:
            event_name (str): The event name to look up for the callback inside.
            callback (callable): The callback function to check.
        """
        return callback in self.__events[event_name]

    def link(self, callback: callable, event_name: str) -> bool:
        """Link a callback to be executed on fired event..

        Args:
            callback (callable): function to link.
            event_name (str): The event that will trigger the callback execution.
        """

        if not self.is_callable(callback):
            print(f'Callback not registered. Type {type(callback)} '
                  f'is not a callable function.', file=self.stream_output) if self.verbose else None
            return False

        if not self.is_event_registered(event_name):
            raise EventHandler.Exceptions.EventNotAllowedError(
                f'Can not link event {event_name}, not registered. Registered events are:'
                f' {", ".join(self.__events.keys())}. Please register event {event_name} before link callbacks.')

        if callback not in self.__events[event_name]:
            self.__events[event_name].append(callback)
            return True

        print(f'Can not link callback {str(callback.__name__)}, already registered in '
              f'{event_name} event.', file=self.stream_output) if self.verbose else None
        return False

    def unlink(self, callback: callable, event_name: str) -> bool:
        """Unlink a callback execution fro especific event.

        Args:
            callback (callable): function to link.
            event_name (str): The event that will trigger the callback execution.
        """
        if not self.is_event_registered(event_name):
            print(f'Can not unlink event {event_name}, not registered. Registered events '
                  f'are: {", ".join(self.__events.keys())}. '
                  f'Please register event {event_name} before unlink callbacks.', file=self.stream_output)
            return False

        if callback in self.__events[event_name]:
            self.__events[event_name].remove(callback)
            return True

        print(f'Can not unlink callback {str(callback.__name__)}, is not registered in '
              f'{event_name} event.', file=self.stream_output) if self.verbose else None

        return False

    def fire(self, event_name: str, *args, **kwargs) -> bool:
        """Triggers all callbacks executions linked to given event.

        Args:
            event_name (str): Event to trigger.
            *args: Arguments to be passed to callback functions execution.
            *kwargs: Keyword arguments to be passed to callback functions execution.
        """
        all_ok = True
        for callback in self.__events[event_name]:
            try:
                callable(callback(*args, **kwargs))
            except Exception as e:
                if not self.tolerate_exceptions:
                    raise e
                else:
                    if self.verbose:
                        print(f'WARNING: {str(callback.__name__)} produces an exception error.',
                              file=self.stream_output)
                        print('Arguments', args, file=self.stream_output)
                        print(e, file=self.stream_output)
                    all_ok = False
                    continue

        return all_ok

    def append(self, event_name: str, args, kwargs) -> None:
        '''Appends an event to the event queue without firing it immediatelly.

        Args:
            event_name (str): Event to trigger.
            args: Arguments to be passed to callback functions execution.
            kwargs: Keyword arguments to be passed to callback functions execution.
        '''
        self.__event_queue.append((event_name, args, kwargs))
    
    def loop(self) -> bool:
        '''Loop through the event queue firing each event in sequence. Returns True
        if all events fired without raising an exception or False otherwise.'''
        all_ok = True
        while self.__event_queue:
            event = self.__event_queue.popleft()
            event_name, args, kwargs = event
            all_ok = self.fire(event_name, *args, **kwargs) and all_ok
        return all_ok

    def __str__(self) -> str:
        """Return a string representation."""

        mem_address = str(hex(id(self)))

        event_related = \
            [f"{event}:[{', '.join([callback.__name__ for callback in self.__events[event]])}]" for event in
             self.__events]

        return f'<class {self.__class__.__name__} at ' \
            f'{mem_address}: {", ".join(event_related)}, verbose={self.verbose}, ' \
            f'tolerate_exceptions={self.tolerate_exceptions}>'

    def __repr__(self) -> str:
        """Return python object representation."""
        return self.__str__()
