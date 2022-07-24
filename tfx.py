import re, os
from types import FunctionType, BuiltinFunctionType, MethodType # to check for function types

class Reader():
    '''
    TFX parser class

    :param anchor_left str: Left anchor, defaults to "<<"
    :param anchor_right str: Right anchor, defaults to ">>"
    :param buffer int: File buffer to use when dealing with files, defaults to "16777216"
    :param debug bool: Wether to print additional info, defaults to "False"
    :param encoding str: File encoding, defaults to "utf-8"

    :usage: Example:
    ```
    tfx = Reader()
    tfx.register_variable('name', 'nexus')
    print(tfx.execute('Hello <<$name>>, i like your name'))
    ```

    or

    ```
    def minus(integer_one, integer_two):
        return integer_one - integer_two

    tfx = Reader()
    tfx.register_function('minus', minus)

    print(tfx.execute('1-1 = <<minus(1, 1)>>'))
    ```
    '''

    def __init__(self, user, theme, anchor_left='<<', anchor_right='>>', buffer=16*1024*1024, debug=False, encoding='utf-8'):

        self.user = user
        self.theme = theme
        self.variables = {}
        self.functions = {}
        self.anchor_left = anchor_left
        self.anchor_right = anchor_right
        self.buffer = buffer
        self.debug = debug
        self.encoding = encoding

    def __debug(self, msg) -> None:
        '''
        __debug(message to display) -> None

        Displays a message to the screen, but only if Debug mode is enabled

        :param msg str: The text to show
        :returns None: Nothing
        '''

        if not self.debug: 
            return

        print(f'[DEBUG] {str(msg)}')
    
    def __strip_prefix(self, text, prefix=' ') -> str:
        '''
        __strip_prefix(text to clean, prefix to strip) -> str

        Strips a text's prefix until its completely stripped

        :param text str: Text to be stripped
        :param prefix str: Prefix to strip
        :return str: Stripped text
        '''

        final=text
        while final.startswith(prefix):
            final=final.removeprefix(prefix)
        
        return final
    
    def __strip_suffix(self, text, suffix=' ') -> str:
        '''
        __strip_suffix(text to clean, suffix to strip) -> str

        Strips a text's suffix until its completely stripped

        :param text str: Text to be stripped
        :param suffix str: Suffix to strip
        :return str: Stripped text
        '''

        final=text
        while final.endswith(suffix):
            final=final.removesuffix(suffix)
        
        return final

    def register_variable(self, name, value) -> None:
        '''
        register_variable(variable name, variable value) -> None

        Registers a variable

        :param name str: Name of the variable
        :param value str: Value of the variable
        :returns None: Nothing
        '''

        if type(name) != str:
            self.__debug(f'Type of name is not str, throwing error')
            raise Exception(f'ERROR, name should be of type "str", and not "{str(type(name))}"!')
        
        if type(value) != str:
            self.__debug(f'Type of value is not str, throwing error')
            raise Exception(f'ERROR, value should be of type "str", and not "{str(type(value))}"!')

        if name in self.variables.keys():
            self.__debug(f'Duplicate variable name found, throwing error')
            raise Exception(f"ERROR, a variable with the name {name} already exists.")

        self.variables[name] = value

    def register_function(self, name, func):
        '''
        register_function(function name, actual function) -> None

        Registers a function

        :param name str: Name of the function
        :param function function: Actual function
        :returns None: Nothing
        '''

        if type(name) != str:
            self.__debug(f'Type of name is not str, throwing error')
            raise Exception(f'ERROR, name should be of type "str", and not "{str(type(name))}"!')
        
        if type(func) not in [FunctionType, BuiltinFunctionType, MethodType]:
            self.__debug(f'Type of func is not function, throwing error')
            raise Exception(f'ERROR, func should be of type "function", and not "{str(type(func))}"!')

        if name in self.functions.keys():
            self.__debug(f'Duplicate function name found, throwing error')
            raise Exception(f"ERROR, a function with the name {name} already exists.")

        self.functions[name] = func
    
    def register_dict(self, data) -> None:
        '''
        register_dict(dictionary with variables) -> None

        Registers a dictionary full of variables

        :param data dict: Dictionary with the variables and their respective values
        :returns None: Nothing
        '''

        if type(data) != dict:
            self.__debug(f'Type of data is not dict, throwing error')

            raise Exception(f'ERROR, data should be of type "dict", and not "{str(type(data))}"!')

        for name, value in data.items():
            self.register_variable(name, value)

    def stripper(self, string) -> str:
        '''
        stripper(string) -> str

        Strips string characters from the specified string

        :param string str: String to be stripped
        :returns str: Stripped string
        '''

        for x in ['"', "'"]:
            string=string.replace(x, "")

        return string
   

    def execute_file(self, theme, file) -> str:
        '''
        execute_file(file path) -> str

        Executes a file at once

        :param file str: Location of the file to execute
        :returns str: Executed file contents
        '''

        if not os.path.isfile(file):
            self.__debug(f'Could not find file "{file}", throwing exception')
            raise Exception('ERROR, file not found!')

        with open(file, buffering=self.buffer, encoding=self.encoding) as f:
            output = self.execute(f.read())

        return output

    def execute_realtime(self, theme, file, func) -> None:
        '''
        execute_realtime(file path) -> None

        Executes a file line by line, and calls the specified function with the output

        :param file str: Location of the file to execute
        :param func function: Function to call with the executed line
        :returns None: Nothing
        '''

        if not os.path.isfile(file):
            self.__debug(f'Could not find file "{file}", throwing exception')
            raise Exception('ERROR, file not found!')

        with open(file, buffering=self.buffer, encoding=self.encoding) as f:
            for line in f.read().split("\n"):
                func(self.execute(line))

    def anchor(self, text) -> str:
        '''
        anchor(text to anchorify) -> str

        Appends the anchors to the text

        :param text str: Text to put between the anchors
        :return str: Anchorified text
        '''

        return f'{self.anchor_left}{text}{self.anchor_right}'

    def execute(self, string) -> str:
        '''
        execute(string to execute) -> str

        This is where the magic happens, basically runs over a string and replaces the variables and functions with the registered output

        :param string str: String to execute
        :returns str: Output of the "compiled"/"executed" string
        '''

        output = string

        for line in re.findall(self.anchor(r'(.*?)'), string): # grab everything in between the anchors

            value = line[0] if type(line) == list else line # somehow i had lists instead of strings when i was debugging it a while ago, so this is just a safety measure
            value_stripped = self.__strip_prefix(self.__strip_suffix(value)) # strip extra whitespace

            if value_stripped.removeprefix('$') in self.variables.keys() or ('$' in value_stripped): # variable

                name = self.variables.get(value_stripped.removeprefix('$'))
                if not name: # not found? we ignore it
                    self.__debug('Variable does not exist, silently ignoring.')
                    continue

                self.__debug(f'Found variable "{value_stripped}"')

                output = output.replace(self.anchor(value), str(name))

            elif value_stripped in self.functions.keys() or ('(' in value_stripped and ')' in value_stripped): # function

                getfunc = self.functions.get(value_stripped.split("(")[0])
                if not getfunc: # didn't find anything? if so, skip
                    self.__debug('Function does not exist, silently ignoring.')
                    continue

                self.__debug(f'Found function "{value_stripped}"')

                arguments = value_stripped.split("(")[1].split(")")[0]
                arglist = arguments.split(",") if len(arguments.split(",")) > 1 else [arguments]

                arguments = []
                for x in arglist:
                    x = self.__strip_prefix(self.__strip_suffix(x)) # remove extra whitespace, can lead to errors when checking for type if not stripped
                    arguments.append(int(x) if x.isdigit() else float(x) if bool(re.match(r"^-?\d+(?:\.\d+)$", x)) else self.stripper(x))

                # run with or without arguments
                if arglist[0] == "" or len(arglist) <= 0: func_output = getfunc()
                else: func_output = getfunc(*arguments)
                
                output = output.replace(self.anchor(value), "" if func_output is None else str(func_output))

        return output # return the output
