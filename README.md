# TerminalFX
Terminal FX parser

# Usage
```py
tfx = Reader()
tfx.register_variable('name', 'nexus')
print(tfx.execute('Hello <<$name>>, i like your name'))
```

or

```py
def minus(integer_one, integer_two):
    return integer_one - integer_two

tfx = Reader()
tfx.register_function('minus', minus)
print(tfx.execute('1-1 = <<minus(1, 1)>>'))
```
