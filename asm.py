def get(num: int):
    return f"GET {num}"

def set(num: int):
    return f"SET {num}"

def put(num: int):
    return f"PUT {num}"

def load(num: int):
    return f"LOAD {num}"

def loadi(num: int):
    return f"LOADI {num}"

def sub(num: int):
    return f"SUB {num}"

def subi(num: int):
    return f"SUBI {num}"

def add(num: int):
    return f"ADD {num}"

def addi(num: int):
    return f"ADDI {num}"

def jzero():
    return f"JZERO "

def jpos():
    return f"JPOS "

def jump():
    return f"JUMP "

def store(num: int):
    return f"STORE {num}"

def storei(num: int):
    return f"STOREI {num}"

def half():
    return f"HALF"